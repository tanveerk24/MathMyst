from flask import Blueprint, render_template
from db import fetch_all, fetch_one
from routes.contributions import JOIN_SQL

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.get('/')
def index():
    stats = fetch_one('''SELECT COUNT(*) AS total_problems,
        COALESCE(SUM(status='Solved'),0) AS solved,
        COALESCE(SUM(status='Unsolved'),0) AS unsolved,
        COALESCE(SUM(CASE WHEN has_prize THEN prize_amount ELSE 0 END),0) AS prize_total,
        (SELECT COUNT(*) FROM MATHEMATICIAN) AS total_mathematicians,
        (SELECT COUNT(*) FROM CONTRIBUTION) AS total_contributions FROM MATH_PROBLEM''')
    fields = fetch_all('SELECT math_field,COUNT(*) AS total FROM MATH_PROBLEM GROUP BY math_field ORDER BY total DESC,math_field')
    years = fetch_all('SELECT contribution_year,COUNT(*) AS total FROM CONTRIBUTION GROUP BY contribution_year ORDER BY contribution_year')
    return render_template('dashboard.html', stats=stats,
                           status_chart={'labels': ['Solved', 'Unsolved'], 'values': [int(stats['solved']), int(stats['unsolved'])]},
                           field_chart={'labels': [r['math_field'] for r in fields], 'values': [r['total'] for r in fields]},
                           year_chart={'labels': [r['contribution_year'] for r in years], 'values': [r['total'] for r in years]},
                           recent=fetch_all(JOIN_SQL + ' ORDER BY c.contribution_year DESC,c.contribution_id DESC LIMIT 5'))
