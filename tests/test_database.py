"""Transaction helper tests and real InnoDB integrity checks."""
from decimal import Decimal
from unittest.mock import MagicMock

import pymysql
import pytest

import db
from conftest import split_sql_script


def mocked_connection(monkeypatch):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    monkeypatch.setattr(db, 'get_db', lambda: connection)
    return connection, cursor


def test_write_commits_and_returns_generated_id(monkeypatch):
    connection, cursor = mocked_connection(monkeypatch)
    cursor.lastrowid = 42
    sql, values = 'INSERT INTO MATH_PROBLEM (problem_name) VALUES (%s)', ("Euler's problem",)
    assert db.execute_write(sql, values) == 42
    cursor.execute.assert_called_once_with(sql, values)
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()


def test_failed_write_rolls_back_and_propagates(monkeypatch):
    connection, cursor = mocked_connection(monkeypatch)
    cursor.execute.side_effect = pymysql.IntegrityError(1062, 'Duplicate entry')
    with pytest.raises(pymysql.IntegrityError):
        db.execute_write('INSERT INTO MATH_PROBLEM VALUES (%s)', ('duplicate',))
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_request_connection_is_reused_and_closed(app, monkeypatch):
    connection = MagicMock()
    connect = MagicMock(return_value=connection)
    monkeypatch.setattr(db.pymysql, 'connect', connect)
    with app.app_context():
        assert db.get_db() is connection
        assert db.get_db() is connection
        assert connect.call_args.kwargs['autocommit'] is False
        assert connect.call_args.kwargs['charset'] == 'utf8mb4'
    connect.assert_called_once()
    connection.close.assert_called_once()


def test_close_without_connection_is_safe(app):
    with app.app_context():
        db.close_db()
        db.close_db()


def test_readonly_transaction_is_always_rolled_back(monkeypatch):
    connection, cursor = mocked_connection(monkeypatch)
    cursor.description = [('answer',)]
    cursor.fetchall.return_value = [{'answer': 7}]
    assert db.execute_readonly('SELECT 7 AS answer;') == (['answer'], [{'answer': 7}])
    assert cursor.execute.call_args_list[0].args == ('START TRANSACTION READ ONLY',)
    assert cursor.execute.call_args_list[1].args == ('SELECT 7 AS answer;',)
    assert connection.rollback.call_count == 2
    connection.commit.assert_not_called()


def test_readonly_error_still_ends_transaction(monkeypatch):
    connection, cursor = mocked_connection(monkeypatch)
    cursor.execute.side_effect = [None, pymysql.ProgrammingError(1064, 'invalid')]
    with pytest.raises(pymysql.ProgrammingError):
        db.execute_readonly('SELECT invalid;')
    assert connection.rollback.call_count == 2


def test_sql_importer_respects_quoted_semicolons_and_comments():
    script = "-- comment ;\nSELECT 'a;b', 'Euler''s'; /* ; */ SELECT 2; # ;\n"
    assert split_sql_script(script) == ["SELECT 'a;b', 'Euler''s'", 'SELECT 2']


@pytest.mark.integration
def test_live_connectivity_and_three_entities(integration_connection):
    with integration_connection.cursor() as cursor:
        cursor.execute('SELECT DATABASE() AS name, 1 AS connected')
        assert cursor.fetchone() == {'name': 'mathmyst_test', 'connected': 1}
        cursor.execute("SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'")
        rows = cursor.fetchall()
    assert {row['TABLE_NAME'].upper() for row in rows} == {'MATH_PROBLEM', 'MATHEMATICIAN', 'CONTRIBUTION'}
    assert all(row['ENGINE'] == 'InnoDB' for row in rows)


@pytest.mark.integration
@pytest.mark.parametrize('statement,params', [
    ('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', ('Riemann Hypothesis', 'Number Theory', 'Unsolved')),
    ('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', (None, 'Number Theory', 'Unsolved')),
    ('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', ('Invalid status', 'Analysis', 'Pending')),
    ('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', ('Invalid case', 'Analysis', 'solved')),
    ('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', ('Invalid trailing space', 'Analysis', 'Solved ')),
    ('UPDATE MATH_PROBLEM SET prize_amount = %s WHERE problem_id = 1', ('-1.00',)),
    ('UPDATE MATH_PROBLEM SET proposed_year = %s WHERE problem_id = 1', (0,)),
    ('UPDATE MATH_PROBLEM SET has_prize = %s WHERE problem_id = 1', (2,)),
    ('UPDATE MATHEMATICIAN SET mathematician_name = %s WHERE mathematician_id = 1', (None,)),
    ('UPDATE CONTRIBUTION SET contribution_year = %s WHERE contribution_id = 1', (-10,)),
    ('UPDATE CONTRIBUTION SET significance_score = %s WHERE contribution_id = 1', ('10.01',)),
    ('UPDATE CONTRIBUTION SET significance_score = %s WHERE contribution_id = 1', ('-0.01',)),
])
def test_live_constraints_reject_invalid_data(integration_connection, statement, params):
    with integration_connection.cursor() as cursor:
        with pytest.raises(pymysql.MySQLError):
            cursor.execute(statement, params)
    integration_connection.rollback()


@pytest.mark.integration
def test_defaults_nulls_and_exact_decimal(integration_connection):
    with integration_connection.cursor() as cursor:
        cursor.execute('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', ('Test default', 'Analysis', 'Unsolved'))
        record_id = cursor.lastrowid
        cursor.execute('SELECT prize_amount, has_prize, proposed_year FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,))
        assert cursor.fetchone() == {'prize_amount': Decimal('0.00'), 'has_prize': 0, 'proposed_year': None}
        cursor.execute('UPDATE MATH_PROBLEM SET prize_amount = %s WHERE problem_id = %s', (Decimal('123.45'), record_id))
        cursor.execute('SELECT prize_amount FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,))
        assert cursor.fetchone()['prize_amount'] == Decimal('123.45')
        cursor.execute('UPDATE CONTRIBUTION SET significance_score = NULL WHERE contribution_id = 1')
        cursor.execute('SELECT significance_score FROM CONTRIBUTION WHERE contribution_id = 1')
        assert cursor.fetchone()['significance_score'] is None


@pytest.mark.integration
@pytest.mark.parametrize('column', ['problem_id', 'mathematician_id'])
def test_foreign_keys_reject_orphan_children(integration_connection, column):
    with integration_connection.cursor() as cursor:
        with pytest.raises(pymysql.IntegrityError):
            cursor.execute('UPDATE CONTRIBUTION SET ' + column + ' = %s WHERE contribution_id = 1', (999999,))


@pytest.mark.integration
@pytest.mark.parametrize('table,key', [('MATH_PROBLEM', 'problem_id'), ('MATHEMATICIAN', 'mathematician_id')])
def test_referenced_parents_cannot_be_deleted(integration_connection, table, key):
    with integration_connection.cursor() as cursor:
        with pytest.raises(pymysql.IntegrityError):
            cursor.execute('DELETE FROM ' + table + ' WHERE ' + key + ' = %s', (1,))


@pytest.mark.integration
@pytest.mark.parametrize('table,key', [('MATH_PROBLEM', 'problem_id'), ('MATHEMATICIAN', 'mathematician_id')])
def test_parent_key_updates_cascade(integration_connection, table, key):
    with integration_connection.cursor() as cursor:
        cursor.execute('UPDATE ' + table + ' SET ' + key + ' = %s WHERE ' + key + ' = %s', (9999, 1))
        cursor.execute('SELECT ' + key + ' FROM CONTRIBUTION WHERE contribution_id = 1')
        assert cursor.fetchone()[key] == 9999


@pytest.mark.integration
def test_live_write_helper_commits_and_rollback_preserves_data(integration_app, integration_connection):
    with integration_app.app_context():
        record_id = db.execute_write('INSERT INTO MATH_PROBLEM (problem_name, math_field, status) VALUES (%s,%s,%s)', ('Transaction test', 'Analysis', 'Unsolved'))
        assert db.fetch_one('SELECT problem_name FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,))['problem_name'] == 'Transaction test'
        with pytest.raises(pymysql.MySQLError):
            db.execute_write('UPDATE MATH_PROBLEM SET prize_amount = %s WHERE problem_id = %s', (-100, record_id))
        assert db.fetch_one('SELECT prize_amount FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,))['prize_amount'] == Decimal('0.00')
        db.execute_write('UPDATE MATH_PROBLEM SET proposed_year = %s WHERE problem_id = %s', (2026, record_id))
        assert db.fetch_one('SELECT proposed_year FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,))['proposed_year'] == 2026
        db.execute_write('DELETE FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,))
        assert db.fetch_one('SELECT problem_id FROM MATH_PROBLEM WHERE problem_id = %s', (record_id,)) is None


@pytest.mark.integration
def test_explicit_rollback_reverts_innodb_changes(integration_connection):
    with integration_connection.cursor() as cursor:
        cursor.execute('UPDATE MATH_PROBLEM SET problem_name = %s WHERE problem_id = 1', ('Temporary renamed problem',))
    integration_connection.rollback()
    with integration_connection.cursor() as cursor:
        cursor.execute('SELECT problem_name FROM MATH_PROBLEM WHERE problem_id = 1')
        assert cursor.fetchone()['problem_name'] == 'Riemann Hypothesis'
