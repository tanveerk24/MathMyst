from time import perf_counter
from flask import Blueprint, abort, render_template, request
from db import execute_readonly
from query_catalog import QUERIES, QUERY_BY_ID

bp = Blueprint('query_lab', __name__, url_prefix='/query-lab')


@bp.get('/')
def index():
    selected = None
    columns, results, elapsed_ms = [], [], None
    query_id = request.args.get('query_id', '')
    if query_id:
        selected = QUERY_BY_ID.get(query_id)
        if selected is None:
            abort(404, description='That query is not in the approved query catalog.')
        start = perf_counter()
        columns, results = execute_readonly(selected['sql'])
        elapsed_ms = round((perf_counter() - start) * 1000, 2)
    return render_template('query_lab.html', queries=QUERIES, selected=selected,
                           columns=columns, results=results, elapsed_ms=elapsed_ms)
