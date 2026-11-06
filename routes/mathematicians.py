from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import fetch_all
from routes.common import delete_record, require_record, save_record
from validation import validate_mathematician

bp = Blueprint('mathematicians', __name__, url_prefix='/mathematicians')


def page(form=None, errors=None, editing=None, show_form=False):
    q = request.args.get('q', '').strip()
    sql, params = 'SELECT * FROM MATHEMATICIAN', ()
    if q:
        sql += ' WHERE mathematician_name LIKE %s OR country LIKE %s OR specialization LIKE %s'
        params = ('%' + q + '%',) * 3
    return render_template('mathematicians.html', records=fetch_all(sql + ' ORDER BY mathematician_name', params),
                           filters={'q': q}, form=form or {}, errors=errors or {}, editing=editing, show_form=show_form)


@bp.get('/')
def index():
    return page()


@bp.route('/new', methods=['GET', 'POST'])
def add():
    errors = {}
    if request.method == 'POST':
        values, errors = validate_mathematician(request.form)
        if not errors and save_record('INSERT INTO MATHEMATICIAN (mathematician_name,country,specialization,birth_date) VALUES (%s,%s,%s,%s)', tuple(values.values()), errors):
            flash('Mathematician added.', 'success')
            return redirect(url_for('mathematicians.index'))
    return page(request.form, errors, show_form=True), 422 if errors else 200


@bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
def edit(record_id):
    record = require_record('SELECT * FROM MATHEMATICIAN WHERE mathematician_id=%s', record_id)
    errors = {}
    if request.method == 'POST':
        values, errors = validate_mathematician(request.form)
        if not errors and save_record('UPDATE MATHEMATICIAN SET mathematician_name=%s,country=%s,specialization=%s,birth_date=%s WHERE mathematician_id=%s', (*values.values(), record_id), errors):
            flash('Mathematician updated.', 'success')
            return redirect(url_for('mathematicians.index'))
    return page(request.form if request.method == 'POST' else record, errors, record, True), 422 if errors else 200


@bp.post('/<int:record_id>/delete')
def delete(record_id):
    require_record('SELECT mathematician_id FROM MATHEMATICIAN WHERE mathematician_id=%s', record_id)
    delete_record('DELETE FROM MATHEMATICIAN WHERE mathematician_id=%s', record_id)
    return redirect(url_for('mathematicians.index'))
