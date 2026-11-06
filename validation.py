"""Validation mirrors database limits, with field messages for HTML forms."""
from datetime import date
from decimal import Decimal, InvalidOperation


def text_field(form, name, maximum, errors, required=False):
    value = form.get(name, '').strip()
    if required and not value:
        errors[name] = 'This field is required.'
    elif len(value) > maximum:
        errors[name] = f'Use at most {maximum} characters.'
    return value or None


def integer_field(form, name, errors, required=False):
    value = form.get(name, '').strip()
    if not value and not required:
        return None
    try:
        number = int(value)
        if not 1 <= number <= 9999:
            raise ValueError
        return number
    except (ValueError, TypeError):
        errors[name] = 'Enter a whole year between 1 and 9999.'
        return None


def decimal_field(form, name, errors, maximum, required=False):
    value = form.get(name, '').strip()
    if not value and not required:
        return None
    try:
        number = Decimal(value)
        if not number.is_finite() or not 0 <= number <= maximum or number != number.quantize(Decimal('.01')):
            raise InvalidOperation
        return number
    except (InvalidOperation, ValueError):
        errors[name] = f'Enter a number from 0 to {maximum} with at most two decimal places.'
        return None


def validate_problem(form):
    errors = {}
    values = {
        'problem_name': text_field(form, 'problem_name', 100, errors, True),
        'math_field': text_field(form, 'math_field', 50, errors, True),
        'proposed_year': integer_field(form, 'proposed_year', errors),
        'status': form.get('status', ''),
        'prize_amount': decimal_field(form, 'prize_amount', errors, Decimal('9999999999.99')),
        'has_prize': form.get('has_prize', '') in {'1', 'true', 'on'},
    }
    if values['status'] not in {'Solved', 'Unsolved'}:
        errors['status'] = 'Choose Solved or Unsolved.'
    if values['prize_amount'] is None and 'prize_amount' not in errors:
        values['prize_amount'] = Decimal('0')
    if values['prize_amount'] and not values['has_prize']:
        errors['has_prize'] = 'Select Has prize when entering a positive prize amount.'
    return values, errors


def validate_mathematician(form):
    errors = {}
    values = {
        'mathematician_name': text_field(form, 'mathematician_name', 80, errors, True),
        'country': text_field(form, 'country', 40, errors),
        'specialization': text_field(form, 'specialization', 50, errors),
        'birth_date': None,
    }
    if form.get('birth_date', '').strip():
        try:
            values['birth_date'] = date.fromisoformat(form['birth_date'])
            if values['birth_date'] > date.today():
                raise ValueError
        except ValueError:
            errors['birth_date'] = 'Enter a valid birth date that is not in the future.'
    return values, errors


def positive_id(value):
    try:
        result = int(value)
        return result if 1 <= result <= 2147483647 else None
    except (TypeError, ValueError):
        return None


def validate_contribution(form):
    errors = {}
    values = {
        'problem_id': positive_id(form.get('problem_id')),
        'mathematician_id': positive_id(form.get('mathematician_id')),
        'contribution_year': integer_field(form, 'contribution_year', errors, True),
        'contribution_type': text_field(form, 'contribution_type', 40, errors),
        'significance_score': decimal_field(form, 'significance_score', errors, Decimal('10')),
    }
    for name in ('problem_id', 'mathematician_id'):
        if values[name] is None:
            errors[name] = 'Select an existing record.'
    return values, errors
