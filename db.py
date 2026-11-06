"""Small, explicit PyMySQL helpers. Each request owns one connection."""
import pymysql
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,
            autocommit=False, connect_timeout=5, read_timeout=10,
            write_timeout=10,
        )
    return g.db


def close_db(_error=None):
    connection = g.pop('db', None)
    if connection is not None:
        # Uncommitted work (including read snapshots) is discarded on close.
        connection.close()


def fetch_all(sql, params=()):
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return list(cursor.fetchall())


def fetch_one(sql, params=()):
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def execute_write(sql, params=()):
    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            inserted_id = cursor.lastrowid
        connection.commit()
        return inserted_id
    except pymysql.MySQLError:
        connection.rollback()
        raise


def execute_readonly(sql):
    """Called only with a statement selected from our server-side catalog."""
    connection = get_db()
    connection.rollback()
    try:
        with connection.cursor() as cursor:
            cursor.execute('START TRANSACTION READ ONLY')
            cursor.execute(sql)
            columns = [item[0] for item in cursor.description]
            return columns, list(cursor.fetchall())
    finally:
        connection.rollback()
