"""Fixtures keep real database tests behind an explicit, guarded opt-in."""
import os
import sys
from pathlib import Path

import pymysql
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from config import Config


def pytest_addoption(parser):
    parser.addoption('--integration', action='store_true', default=False,
                     help='Run integration tests against disposable mathmyst_test only.')


def pytest_collection_modifyitems(config, items):
    if not config.getoption('--integration'):
        skip = pytest.mark.skip(reason='Use --integration with explicit TEST_DB_* settings.')
        for item in items:
            if 'integration' in item.keywords:
                item.add_marker(skip)


@pytest.fixture
def app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'mathmyst-unit-test-secret',
                       'CSRF_ENABLED': True})


@pytest.fixture
def client(app):
    return app.test_client()


def split_sql_script(script):
    """Split ordinary SQL while respecting comments and quoted semicolons.

    This small importer handles schema/seed files, not mysql client DELIMITER
    commands. Advanced routines are tested separately through the mysql client.
    """
    statements, current = [], []
    quote = None
    position = 0
    while position < len(script):
        char = script[position]
        following = script[position:position + 2]
        if quote:
            current.append(char)
            if char == '\\' and position + 1 < len(script):
                position += 1
                current.append(script[position])
            elif char == quote:
                if position + 1 < len(script) and script[position + 1] == quote:
                    position += 1
                    current.append(script[position])
                else:
                    quote = None
        elif following == '--' and (position + 2 == len(script) or script[position + 2].isspace()):
            newline = script.find('\n', position)
            position = len(script) if newline == -1 else newline
            current.append('\n')
        elif char == '#':
            newline = script.find('\n', position)
            position = len(script) if newline == -1 else newline
            current.append('\n')
        elif following == '/*':
            ending = script.find('*/', position + 2)
            if ending == -1:
                raise ValueError('Unterminated SQL comment.')
            position = ending + 1
            current.append(' ')
        elif char in ("'", '"', '`'):
            quote = char
            current.append(char)
        elif char == ';':
            statement = ''.join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)
        position += 1
    if quote:
        raise ValueError('Unterminated SQL string.')
    final = ''.join(current).strip()
    if final:
        statements.append(final)
    return statements


def execute_project_script(connection, filename):
    statements = split_sql_script((PROJECT_ROOT / 'database' / filename).read_text(encoding='utf-8'))
    with connection.cursor() as cursor:
        for statement in statements:
            # Never allow a project script to select/create the demonstration DB.
            upper = statement.upper()
            if upper.startswith('USE ') or upper.startswith('CREATE DATABASE '):
                continue
            cursor.execute(statement)


@pytest.fixture(scope='session')
def integration_settings(request):
    if not request.config.getoption('--integration'):
        pytest.skip('Integration tests are explicitly opt-in.')
    required = ['TEST_DB_HOST', 'TEST_DB_PORT', 'TEST_DB_USER', 'TEST_DB_PASSWORD', 'TEST_DB_NAME']
    missing = [name for name in required if name not in os.environ]
    if missing:
        pytest.fail('Integration tests require explicit environment settings: ' + ', '.join(missing))
    test_name = os.environ['TEST_DB_NAME']
    if test_name != 'mathmyst_test' or test_name.casefold() == Config.DB_NAME.casefold():
        pytest.fail('Refusing destructive tests: TEST_DB_NAME must be exactly mathmyst_test and differ from DB_NAME.')
    if not os.environ['TEST_DB_HOST'] or not os.environ['TEST_DB_USER']:
        pytest.fail('TEST_DB_HOST and TEST_DB_USER must be nonempty.')
    try:
        port = int(os.environ['TEST_DB_PORT'])
    except ValueError:
        pytest.fail('TEST_DB_PORT must be an integer.')
    return {
        'DB_HOST': os.environ['TEST_DB_HOST'], 'DB_PORT': port,
        'DB_USER': os.environ['TEST_DB_USER'],
        'DB_PASSWORD': os.environ['TEST_DB_PASSWORD'], 'DB_NAME': test_name,
    }


@pytest.fixture(scope='session')
def _integration_database(integration_settings):
    settings = integration_settings
    connection = pymysql.connect(
        host=settings['DB_HOST'], port=settings['DB_PORT'],
        user=settings['DB_USER'], password=settings['DB_PASSWORD'],
        database=settings['DB_NAME'], charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor, autocommit=False,
        connect_timeout=5,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT DATABASE() AS selected_database')
            assert cursor.fetchone()['selected_database'] == 'mathmyst_test'
            # These constant identifiers are restricted to the guarded test DB.
            for table in ('CONTRIBUTION', 'MATHEMATICIAN', 'MATH_PROBLEM'):
                cursor.execute('DROP TABLE IF EXISTS ' + table)
        execute_project_script(connection, 'schema.sql')
        connection.commit()
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture
def integration_connection(_integration_database):
    connection = _integration_database
    connection.rollback()
    with connection.cursor() as cursor:
        for table in ('CONTRIBUTION', 'MATHEMATICIAN', 'MATH_PROBLEM'):
            cursor.execute('DELETE FROM ' + table)
    connection.commit()
    execute_project_script(connection, 'seed.sql')
    try:
        yield connection
    finally:
        connection.rollback()


@pytest.fixture
def integration_app(integration_connection, integration_settings):
    return create_app({**integration_settings, 'TESTING': True,
                       'SECRET_KEY': 'mathmyst-integration-test-secret',
                       'CSRF_ENABLED': True})


@pytest.fixture
def integration_client(integration_app):
    return integration_app.test_client()
