import pymysql
from flask import abort, flash

from db import execute_write, fetch_one
from validation import positive_id


def require_record(sql, record_id):
    record = fetch_one(sql, (record_id,))
    if record is None:
        abort(404)
    return record


def save_record(sql, params, errors):
    try:
        execute_write(sql, params)
        return True
    except pymysql.IntegrityError as error:
        if error.args[0] == 1062:
            errors['general'] = 'A record with this unique name already exists.'
        elif error.args[0] in {1451, 1452}:
            errors['general'] = 'The related record changed or no longer exists. Check your selections.'
        else:
            errors['general'] = 'These values violate a database constraint. Please check the form.'
        return False


def delete_record(sql, record_id):
    try:
        execute_write(sql, (record_id,))
        flash('Record deleted.', 'success')
    except pymysql.IntegrityError:
        flash('This record has contributions. Delete or reassign those contributions first.', 'error')


def filter_id(value):
    if not value:
        return None
    result = positive_id(value)
    if result is None:
        abort(400, description='Choose a valid record for the filter.')
    return result
