from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import fetch_all, fetch_one
from routes.common import delete_record, filter_id, require_record, save_record
from validation import validate_contribution

bp = Blueprint('contributions', __name__, url_prefix='/contributions')
JOIN_SQL = '''SELECT c.*, p.problem_name, m.mathematician_name
    FROM CONTRIBUTION c INNER JOIN MATH_PROBLEM p ON c.problem_id=p.problem_id
    INNER JOIN MATHEMATICIAN m ON c.mathematician_id=m.mathematician_id'''


def page(form=None, errors=None, editing=None, show_form=False):
    filters = {key: request.args.get(key, '') for key in ('problem_id', 'mathematician_id')}
    clauses, params = [], []
    for key in filters:
        value = filter_id(filters[key])
        if value is not None:
            clauses.append(f'c.{key}=%s')
            params.append(value)
    sql = JOIN_SQL + (' WHERE ' + ' AND '.join(clauses) if clauses else '')
    return render_template('contributions.html', records=fetch_all(sql + ' ORDER BY c.contribution_year DESC, c.contribution_id DESC', params),
                           problems=fetch_all('SELECT problem_id,problem_name FROM MATH_PROBLEM ORDER BY problem_name'),
                           mathematicians=fetch_all('SELECT mathematician_id,mathematician_name FROM MATHEMATICIAN ORDER BY mathematician_name'),
                           filters=filters, form=form or {}, errors=errors or {}, editing=editing, show_form=show_form)


def validate_parents(values, errors):
    for field, table in (('problem_id', 'MATH_PROBLEM'), ('mathematician_id', 'MATHEMATICIAN')):
        if field not in errors and fetch_one(f'SELECT {field} FROM {table} WHERE {field}=%s', (values[field],)) is None:
            errors[field] = 'The selected record no longer exists.'


@bp.get('/')
def index():
    return page()


@bp.route('/new', methods=['GET', 'POST'])
def add():
    errors = {}
    if request.method == 'POST':
        values, errors = validate_contribution(request.form)
        validate_parents(values, errors)
        if not errors and save_record('INSERT INTO CONTRIBUTION (problem_id,mathematician_id,contribution_year,contribution_type,significance_score) VALUES (%s,%s,%s,%s,%s)', tuple(values.values()), errors):
            flash('Research contribution added.', 'success')
            return redirect(url_for('contributions.index'))
    return page(request.form, errors, show_form=True), 422 if errors else 200


@bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
def edit(record_id):
    record = require_record('SELECT * FROM CONTRIBUTION WHERE contribution_id=%s', record_id)
    errors = {}
    if request.method == 'POST':
        values, errors = validate_contribution(request.form)
        validate_parents(values, errors)
        if not errors and save_record('UPDATE CONTRIBUTION SET problem_id=%s,mathematician_id=%s,contribution_year=%s,contribution_type=%s,significance_score=%s WHERE contribution_id=%s', (*values.values(), record_id), errors):
            flash('Research contribution updated.', 'success')
            return redirect(url_for('contributions.index'))
    return page(request.form if request.method == 'POST' else record, errors, record, True), 422 if errors else 200


@bp.post('/<int:record_id>/delete')
def delete(record_id):
    require_record('SELECT contribution_id FROM CONTRIBUTION WHERE contribution_id=%s', record_id)
    delete_record('DELETE FROM CONTRIBUTION WHERE contribution_id=%s', record_id)
    return redirect(url_for('contributions.index'))
