"""The public lab accepts only known IDs and the SQL works on the seed data."""
from decimal import Decimal

import pytest

import db
from conftest import PROJECT_ROOT, split_sql_script
from query_catalog import QUERIES, QUERY_BY_ID


def test_catalog_contains_every_requested_concept():
    assert len(QUERIES) >= 25
    assert len(QUERY_BY_ID) == len(QUERIES)
    concepts = ' '.join(query['concept'].upper() for query in QUERIES)
    for required in ('SELECT', 'WHERE', 'DISTINCT', 'LIKE', 'BETWEEN', 'IN',
                     'ORDER BY', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
                     'GROUP BY', 'HAVING', 'INNER JOIN', 'LEFT JOIN',
                     'RIGHT JOIN', 'SELF JOIN', 'SUBQUERY', 'EXISTS', 'NOT EXISTS'):
        assert required in concepts
    for query in QUERIES:
        assert all(query.get(key) for key in ('id', 'title', 'concept', 'sql', 'explanation'))


def test_catalog_is_single_readonly_selects_and_matches_sql_script():
    catalog_statements = []
    for query in QUERIES:
        statements = split_sql_script(query['sql'])
        assert len(statements) == 1
        assert statements[0].upper().startswith('SELECT ')
        upper = statements[0].upper()
        for forbidden in ('INTO OUTFILE', 'INTO DUMPFILE', 'LOAD_FILE', 'SLEEP(', 'BENCHMARK(', 'FOR UPDATE'):
            assert forbidden not in upper
        catalog_statements.extend(statements)
    practice = split_sql_script((PROJECT_ROOT / 'database' / 'queries.sql').read_text(encoding='utf-8'))
    assert [sql for sql in practice if not sql.upper().startswith('USE ')] == catalog_statements


def test_unknown_query_id_never_reaches_database(client, monkeypatch):
    def unexpected_execution(_sql):
        pytest.fail('An unknown query ID must never execute SQL.')
    monkeypatch.setattr('routes.query_lab.execute_readonly', unexpected_execution)
    response = client.get('/query-lab/', query_string={'query_id': 'SELECT * FROM secrets; DROP TABLE MATH_PROBLEM;'})
    assert response.status_code == 404


def test_query_lab_executes_catalog_sql_only(client, monkeypatch):
    statements = []
    def execute(sql):
        statements.append(sql)
        return ['unsolved_problems'], [{'unsolved_problems': 7}]
    monkeypatch.setattr('routes.query_lab.execute_readonly', execute)
    response = client.get('/query-lab/', query_string={'query_id': 'count-unsolved', 'sql': 'DELETE FROM MATH_PROBLEM'})
    assert response.status_code == 200
    assert statements == [QUERY_BY_ID['count-unsolved']['sql']]
    assert b'unsolved_problems' in response.data


@pytest.mark.integration
@pytest.mark.parametrize('query', QUERIES, ids=lambda query: query['id'])
def test_every_approved_query_executes_on_mysql(integration_app, query):
    with integration_app.app_context():
        columns, rows = db.execute_readonly(query['sql'])
    assert columns
    assert isinstance(rows, list)
    assert all(set(row) == set(columns) for row in rows)


@pytest.mark.integration
def test_seed_query_results_have_expected_meaning(integration_app):
    with integration_app.app_context():
        run = lambda query_id: db.execute_readonly(QUERY_BY_ID[query_id]['sql'])[1]
        assert len(run('all-problems')) == 10
        assert run('count-unsolved') == [{'unsolved_problems': 7}]
        assert run('highest-prize') == [{'highest_prize': Decimal('1000000.00')}]
        assert run('total-prizes') == [{'total_prize_usd': Decimal('4000000.00')}]
        assert {row['problem_id'] for row in run('problems-without-contributions')} == {6, 9}
        assert run('people-without-contributions') == [{'mathematician_id': 10, 'mathematician_name': 'Srinivasa Ramanujan'}]
        assert run('multiple-problems') == [{'mathematician_id': 3, 'mathematician_name': 'Terence Tao', 'problem_count': 4}]
        assert run('most-contributions') == [{'mathematician_id': 3, 'mathematician_name': 'Terence Tao', 'contribution_count': 4}]
        assert run('earliest-problem') == [{'problem_name': "Fermat's Last Theorem", 'proposed_year': 1637}]
        assert len(run('research-relationships')) == 17
        counts = run('contributions-per-problem')
        assert len(counts) == 10
        assert sum(row['contribution_count'] for row in counts) == 17
        assert sum(row['contribution_count'] == 0 for row in counts) == 2
        right_join = run('right-join-people')
        assert len(right_join) == 18
        assert [row['mathematician_name'] for row in right_join if row['contribution_id'] is None] == ['Srinivasa Ramanujan']


@pytest.mark.integration
def test_all_tied_research_leaders_are_returned(integration_app, integration_connection):
    with integration_connection.cursor() as cursor:
        for year in (2024, 2025, 2026):
            cursor.execute('INSERT INTO CONTRIBUTION (problem_id, mathematician_id, contribution_year, contribution_type) VALUES (%s,%s,%s,%s)', (1, 1, year, 'Fictional integration test'))
    integration_connection.commit()
    with integration_app.app_context():
        _, rows = db.execute_readonly(QUERY_BY_ID['most-contributions']['sql'])
    assert {row['mathematician_name'] for row in rows} == {'Bernhard Riemann', 'Terence Tao'}
    assert {row['contribution_count'] for row in rows} == {4}


@pytest.mark.integration
def test_readonly_transaction_refuses_modifications(integration_app):
    import pymysql
    with integration_app.app_context():
        with pytest.raises(pymysql.MySQLError):
            db.execute_readonly('DELETE FROM CONTRIBUTION')
        assert db.fetch_one('SELECT COUNT(*) AS total FROM CONTRIBUTION')['total'] == 17
