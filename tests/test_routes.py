import re
from unittest.mock import Mock

import pymysql
import pytest

from routes import contributions, mathematicians, problems


def token(client):
    with client.session_transaction() as session:
        session['_csrf_token'] = 'test-csrf-token'
    return {'csrf_token': 'test-csrf-token'}


def test_public_pages_and_headers(client):
    for path in ('/', '/query-lab/'):
        response = client.get(path)
        assert response.status_code == 200
        assert b'MathMyst' in response.data
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert "form-action 'self'" in response.headers['Content-Security-Policy']
    assert client.get('/missing-page').status_code == 404


@pytest.mark.parametrize('path', ['/problems/1/delete', '/mathematicians/1/delete', '/contributions/1/delete'])
def test_deletion_requires_post(client, path):
    assert client.get(path).status_code == 405


@pytest.mark.parametrize('submitted', ['', 'wrong', '\u2603'])
def test_csrf_rejects_missing_invalid_and_unicode_tokens(client, submitted):
    token(client)
    assert client.post('/problems/new', data={'csrf_token': submitted}).status_code == 400


def test_csrf_is_bound_to_session(app):
    first, second = app.test_client(), app.test_client()
    token(first)
    assert second.post('/problems/new', data={'csrf_token': 'test-csrf-token'}).status_code == 400


def test_database_errors_are_safe(client, monkeypatch):
    monkeypatch.setattr(problems, 'fetch_all', Mock(side_effect=pymysql.OperationalError(1045, 'password secret-host secret-password')))
    response = client.get('/problems/')
    assert response.status_code == 503
    assert b'secret-password' not in response.data
    assert b'OperationalError' not in response.data


@pytest.mark.parametrize('path,module', [('/problems/999/edit', problems), ('/mathematicians/999/edit', mathematicians), ('/contributions/999/edit', contributions)])
def test_missing_records_return_404(client, monkeypatch, path, module):
    import routes.common
    monkeypatch.setattr(routes.common, 'fetch_one', lambda *args: None)
    assert client.get(path).status_code == 404


def test_problem_filters_are_parameters_and_sort_is_allowlisted(client, monkeypatch):
    spy = Mock(return_value=[])
    monkeypatch.setattr(problems, 'fetch_all', spy)
    attack = "x' OR 1=1 --"
    response = client.get('/problems/', query_string={'q': attack, 'sort': 'problem_id; DROP TABLE MATH_PROBLEM'})
    assert response.status_code == 200
    sql, params = spy.call_args_list[0].args
    assert attack not in sql
    assert params == ['%' + attack + '%']
    assert sql.endswith('ORDER BY problem_name ASC')


@pytest.mark.parametrize('value', ['abc', '-1', '1 OR 1=1'])
def test_bad_relationship_filter_is_400(client, value):
    assert client.get('/contributions/', query_string={'problem_id': value}).status_code == 400


def test_invalid_problem_preserves_escaped_input(client, monkeypatch):
    monkeypatch.setattr(problems, 'fetch_all', lambda *args: [])
    response = client.post('/problems/new', data={**token(client), 'problem_name': '<script>alert(1)</script>', 'math_field': '', 'status': 'Unsolved'})
    assert response.status_code == 422
    assert b'&lt;script&gt;' in response.data
    assert b'<script>alert(1)</script>' not in response.data


@pytest.mark.integration
@pytest.mark.parametrize('path', ['/', '/dashboard/', '/problems/', '/problems/new', '/problems/1/edit', '/mathematicians/', '/mathematicians/new', '/mathematicians/1/edit', '/contributions/', '/contributions/new', '/contributions/1/edit', '/query-lab/'])
def test_live_pages(integration_client, path):
    assert integration_client.get(path).status_code == 200


@pytest.mark.integration
def test_live_crud_workflow(integration_client, integration_connection):
    client = integration_client
    csrf = token(client)
    # A new parent, a new researcher, and their linking contribution.
    assert client.post('/problems/new', data={**csrf, 'problem_name': 'Fictional examination problem', 'math_field': 'Demonstration', 'proposed_year': '2026', 'status': 'Unsolved'}).status_code == 302
    assert client.post('/mathematicians/new', data={**csrf, 'mathematician_name': 'Fictional demonstration researcher', 'country': 'India'}).status_code == 302
    integration_connection.commit()  # Refresh the test connection's snapshot.
    with integration_connection.cursor() as cursor:
        cursor.execute("SELECT problem_id FROM MATH_PROBLEM WHERE problem_name=%s", ('Fictional examination problem',))
        pid = cursor.fetchone()['problem_id']
        cursor.execute("SELECT mathematician_id FROM MATHEMATICIAN WHERE mathematician_name=%s", ('Fictional demonstration researcher',))
        mid = cursor.fetchone()['mathematician_id']
    data = {**csrf, 'problem_id': str(pid), 'mathematician_id': str(mid), 'contribution_year': '2026', 'contribution_type': 'Fictional demo', 'significance_score': '5.50'}
    assert client.post('/contributions/new', data=data).status_code == 302
    integration_connection.commit()
    with integration_connection.cursor() as cursor:
        cursor.execute('SELECT contribution_id FROM CONTRIBUTION WHERE problem_id=%s', (pid,))
        cid = cursor.fetchone()['contribution_id']
    assert client.post(f'/contributions/{cid}/edit', data={**data, 'significance_score': '6.25'}).status_code == 302
    assert client.post(f'/problems/{pid}/edit', data={**csrf, 'problem_name': 'Fictional revised problem', 'math_field': 'Demonstration', 'status': 'Solved'}).status_code == 302
    assert client.post(f'/mathematicians/{mid}/edit', data={**csrf, 'mathematician_name': 'Fictional revised researcher', 'country': 'India'}).status_code == 302
    response = client.post(f'/problems/{pid}/delete', data=csrf, follow_redirects=True)
    assert b'Delete or reassign' in response.data
    assert b'Fictional revised problem' in response.data
    assert client.post(f'/contributions/{cid}/delete', data=csrf).status_code == 302
    assert client.post(f'/problems/{pid}/delete', data=csrf).status_code == 302
    assert client.post(f'/mathematicians/{mid}/delete', data=csrf).status_code == 302
    assert client.get(f'/problems/{pid}/edit').status_code == 404


@pytest.mark.integration
def test_live_duplicate_and_nonexistent_relationship(integration_client):
    client = integration_client
    csrf = token(client)
    response = client.post('/problems/new', data={**csrf, 'problem_name': 'Riemann Hypothesis', 'math_field': 'Number Theory', 'status': 'Unsolved'})
    assert response.status_code == 422
    assert b'unique name already exists' in response.data
    response = client.post('/contributions/new', data={**csrf, 'problem_id': '999999', 'mathematician_id': '1', 'contribution_year': '2026'})
    assert response.status_code == 422
    assert b'no longer exists' in response.data


@pytest.mark.integration
def test_live_filters(integration_client):
    response = integration_client.get('/problems/', query_string={'q': 'Riemann', 'status': 'Unsolved', 'field': 'Number Theory', 'sort': 'year_asc'})
    assert response.status_code == 200
    assert b'Riemann Hypothesis' in response.data
    assert b'Collatz Conjecture' not in response.data
    assert b'Riemann Hypothesis' in integration_client.get('/contributions/?mathematician_id=1&problem_id=1').data
