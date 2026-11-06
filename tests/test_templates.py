"""Template checks focus on escaping, safe forms, and retained validation input."""
from decimal import Decimal
from html.parser import HTMLParser

import pytest
from flask import render_template

from app import create_app


class FormParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.forms = []
        self.current = None
        self.inputs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.current = {'attrs': attrs, 'inputs': []}
            self.forms.append(self.current)
        elif tag == 'input':
            self.inputs.append(attrs)
            if self.current is not None:
                self.current['inputs'].append(attrs)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.current = None


@pytest.fixture
def template_app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'template-tests-only'})


@pytest.fixture
def template_context():
    problem = {
        'problem_id': 1, 'problem_name': 'Riemann Hypothesis',
        'math_field': 'Number Theory', 'proposed_year': 1859,
        'status': 'Unsolved', 'prize_amount': Decimal('1000000.00'),
        'has_prize': 1,
    }
    person = {
        'mathematician_id': 1, 'mathematician_name': 'Bernhard Riemann',
        'country': 'Germany', 'birth_date': '1826-09-17',
        'specialization': 'Analysis',
    }
    contribution = {
        'contribution_id': 1, 'problem_id': 1, 'mathematician_id': 1,
        'contribution_year': 1859, 'contribution_type': 'Conjecture',
        'significance_score': None, 'problem_name': 'Riemann Hypothesis',
        'mathematician_name': 'Bernhard Riemann',
    }
    return {
        'filters': {}, 'form': {}, 'errors': {}, 'editing': None,
        'show_form': False, 'fields': ['Number Theory'],
        'problems': [problem], 'mathematicians': [person],
        'rows': {'problems.html': problem, 'mathematicians.html': person,
                 'contributions.html': contribution},
    }


@pytest.mark.parametrize('template', [
    'problems.html', 'mathematicians.html', 'contributions.html',
])
def test_every_mutation_form_contains_csrf(template_app, template_context, template):
    context = dict(template_context, show_form=True)
    context['records'] = [context['rows'][template]]
    with template_app.test_request_context('/'):
        parsed = FormParser(render_template(template, **context))
    post_forms = [f for f in parsed.forms if f['attrs'].get('method') == 'post']
    assert len(post_forms) == 2  # Add and delete; filters remain GET.
    for form in post_forms:
        tokens = [i for i in form['inputs'] if i.get('name') == 'csrf_token']
        assert len(tokens) == 1
        assert tokens[0]['type'] == 'hidden'
        assert tokens[0]['value']


@pytest.mark.parametrize('submitted,checked', [
    ('0', False), ('', False), (0, False), (False, False),
    ('1', True), ('true', True), ('on', True), (1, True), (True, True),
])
def test_prize_checkbox_matches_server_boolean_rules(
    template_app, template_context, submitted, checked,
):
    context = dict(template_context, records=[], show_form=True,
                   form={'has_prize': submitted})
    with template_app.test_request_context('/'):
        parsed = FormParser(render_template('problems.html', **context))
    checkbox = next(i for i in parsed.inputs if i.get('name') == 'has_prize')
    assert ('checked' in checkbox) is checked


def test_invalid_form_retains_input_without_executing_html(
    template_app, template_context,
):
    malicious_name = '\"><script>alert("unsafe")</script>'
    context = dict(template_context, records=[], show_form=True,
                   form={'problem_name': malicious_name, 'math_field': 'Geometry'},
                   errors={'problem_name': 'Use a shorter problem name.'})
    with template_app.test_request_context('/'):
        rendered = render_template('problems.html', **context)
    assert '<script>alert(' not in rendered
    assert 'Use a shorter problem name.' in rendered
    assert 'role="alert"' in rendered
    parsed = FormParser(rendered)
    name = next(i for i in parsed.inputs if i.get('name') == 'problem_name')
    assert name['value'] == malicious_name


def test_query_result_cells_escape_data_and_preserve_null(template_app):
    query = {
        'id': 'safe-select', 'title': 'Safe selection', 'concept': 'SELECT',
        'sql': 'SELECT problem_name, proposed_year FROM MATH_PROBLEM',
        'explanation': 'Read problem names and their proposal years.',
    }
    with template_app.test_request_context('/'):
        rendered = render_template(
            'query_lab.html', queries=[query], selected=query,
            columns=['problem_name', 'proposed_year'], elapsed_ms=1.0,
            results=[{'problem_name': '<img src=x onerror=alert(1)>',
                      'proposed_year': None}],
        )
    assert '<img src=x' not in rendered
    assert '&lt;img src=x' in rendered
    assert '<span class="null-value">NULL</span>' in rendered
