from datetime import date, timedelta
from decimal import Decimal

import pytest
from validation import validate_contribution, validate_mathematician, validate_problem


def problem(**changes):
    return dict(problem_name='Test conjecture', math_field='Number Theory',
                proposed_year='1900', status='Unsolved', prize_amount='0', **changes)


@pytest.mark.parametrize('field,value', [
    ('problem_name', ''), ('problem_name', 'x' * 101), ('math_field', ''),
    ('math_field', 'x' * 51), ('status', 'solved'), ('status', "Unsolved' OR 1=1"),
    ('proposed_year', '0'), ('proposed_year', '10000'), ('proposed_year', '1.5'),
    ('prize_amount', '-1'), ('prize_amount', 'NaN'), ('prize_amount', 'Infinity'),
    ('prize_amount', '0.001'), ('prize_amount', '10000000000'),
])
def test_problem_rejects_bad_values(field, value):
    form = problem()
    form[field] = value
    assert field in validate_problem(form)[1]


def test_optional_values_and_prize_consistency():
    form = problem()
    form.update(proposed_year='', prize_amount='')
    values, errors = validate_problem(form)
    assert not errors
    assert values['proposed_year'] is None
    assert values['prize_amount'] == Decimal('0')
    form.update(prize_amount='99.99')
    assert 'has_prize' in validate_problem(form)[1]
    form.update(has_prize='on')
    assert not validate_problem(form)[1]


@pytest.mark.parametrize('birth_date', ['2024-02-30', 'not-a-date', (date.today() + timedelta(days=1)).isoformat()])
def test_invalid_birth_dates(birth_date):
    assert 'birth_date' in validate_mathematician({'mathematician_name': 'Ada', 'birth_date': birth_date})[1]


def test_optional_mathematician_values_are_null():
    values, errors = validate_mathematician({'mathematician_name': '  Ada  '})
    assert not errors
    assert values == {'mathematician_name': 'Ada', 'country': None, 'birth_date': None, 'specialization': None}


@pytest.mark.parametrize('score', ['-1', '10.01', 'NaN', '1.123'])
def test_significance_score_validation(score):
    assert 'significance_score' in validate_contribution(dict(problem_id='1', mathematician_id='1', contribution_year='2020', significance_score=score))[1]


def test_invalid_contribution_relationship_ids():
    values, errors = validate_contribution(dict(problem_id='-1', mathematician_id="1 OR 1=1", contribution_year='0'))
    assert set(errors) == {'problem_id', 'mathematician_id', 'contribution_year'}
