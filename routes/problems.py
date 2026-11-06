from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import fetch_all
from routes.common import delete_record, require_record, save_record
from validation import validate_problem

bp = Blueprint('problems', __name__, url_prefix='/problems')
SORTS = {'year_asc': 'proposed_year ASC, problem_name ASC',
         'year_desc': 'proposed_year DESC, problem_name ASC',
         'name': 'problem_name ASC'}


def page(form=None, errors=None, editing=None, show_form=False):
    filters = {key: request.args.get(key, '').strip() for key in ('q', 'field', 'status', 'sort')}
    clauses, params = [], []
    for key, column in (('q', 'problem_name'), ('field', 'math_field'), ('status', 'status')):
        if filters[key]:
            clauses.append(f'{column} LIKE %s' if key == 'q' else f'{column} = %s')
            params.append('%' + filters[key] + '%' if key == 'q' else filters[key])
    sql = 'SELECT * FROM MATH_PROBLEM'
    if clauses:
        sql += ' WHERE ' + ' AND '.join(clauses)
    # SQL identifiers come exclusively from this developer-defined mapping.
    sql += ' ORDER BY ' + SORTS.get(filters['sort'], SORTS['name'])
    return render_template('problems.html', records=fetch_all(sql, params),
                           fields=[r['math_field'] for r in fetch_all('SELECT DISTINCT math_field FROM MATH_PROBLEM ORDER BY math_field')],
                           filters=filters, form=form or {}, errors=errors or {},
                           editing=editing, show_form=show_form)


@bp.get('/')
def index():
    return page()


@bp.route('/new', methods=['GET', 'POST'])
def add():
    errors = {}
    if request.method == 'POST':
        values, errors = validate_problem(request.form)
        if not errors and save_record('INSERT INTO MATH_PROBLEM (problem_name, math_field, proposed_year, status, prize_amount, has_prize) VALUES (%s,%s,%s,%s,%s,%s)', tuple(values.values()), errors):
            flash('Mathematical problem added.', 'success')
            return redirect(url_for('problems.index'))
    return page(request.form, errors, show_form=True), 422 if errors else 200


@bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
def edit(record_id):
    record = require_record('SELECT * FROM MATH_PROBLEM WHERE problem_id=%s', record_id)
    errors = {}
    if request.method == 'POST':
        values, errors = validate_problem(request.form)
        if not errors and save_record('UPDATE MATH_PROBLEM SET problem_name=%s, math_field=%s, proposed_year=%s, status=%s, prize_amount=%s, has_prize=%s WHERE problem_id=%s', (*values.values(), record_id), errors):
            flash('Mathematical problem updated.', 'success')
            return redirect(url_for('problems.index'))
    return page(request.form if request.method == 'POST' else record, errors, record, True), 422 if errors else 200


@bp.post('/<int:record_id>/delete')
def delete(record_id):
    require_record('SELECT problem_id FROM MATH_PROBLEM WHERE problem_id=%s', record_id)
    delete_record('DELETE FROM MATH_PROBLEM WHERE problem_id=%s', record_id)
    return redirect(url_for('problems.index'))
