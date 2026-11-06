"""Session-bound CSRF protection without an extra form framework."""
import secrets
from flask import abort, current_app, request, session


def csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return session['_csrf_token']


def protect_csrf():
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and current_app.config['CSRF_ENABLED']:
        expected = session.get('_csrf_token')
        submitted = request.form.get('csrf_token', '')
        if not expected or not secrets.compare_digest(expected.encode('utf-8'), submitted.encode('utf-8')):
            abort(400, description='The form expired or its security token is missing. Reload the page and try again.')
