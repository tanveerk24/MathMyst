"""MathMyst: run locally with python app.py, or import create_app in tests."""
import pymysql
from flask import Flask, current_app, render_template
from werkzeug.exceptions import HTTPException

from config import Config
from db import close_db
from security import csrf_token, protect_csrf


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    app.teardown_appcontext(close_db)
    app.before_request(protect_csrf)
    app.jinja_env.globals['csrf_token'] = csrf_token

    from routes import contributions, dashboard, mathematicians, problems, query_lab
    for module in (problems, mathematicians, contributions, dashboard, query_lab):
        app.register_blueprint(module.bp)

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.errorhandler(pymysql.MySQLError)
    def database_error(error):
        # Log only the error class/code, never connection strings or user values.
        current_app.logger.error('Database operation failed: %s (code %s)', type(error).__name__, error.args[0] if error.args else 'unknown')
        return render_template('error.html', code=503, title='Database unavailable',
                               message='Check that MySQL or MariaDB is running and that your .env settings and database setup are complete.'), 503

    @app.errorhandler(HTTPException)
    def http_error(error):
        return render_template('error.html', code=error.code, title=error.name,
                               message=error.description), error.code

    @app.errorhandler(500)
    def server_error(_error):
        return render_template('error.html', code=500, title='Something went wrong',
                               message='The request could not be completed. Please try again.'), 500

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'"
        )
        response.headers['Cache-Control'] = 'no-store'
        return response

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
