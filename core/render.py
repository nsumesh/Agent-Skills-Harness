"""Deterministic AuditReport-to-Markdown/HTML renderer. The Markdown reproduces the
target_report.md four-section layout; whitespace is normalised so output is stable."""

from __future__ import annotations

import re

from jinja2 import Environment

from .schema import AuditReport

# Markdown is plain text — never escape. HTML escapes to stay injection-safe.
_md_env = Environment(
    autoescape=False, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True
)
_html_env = Environment(
    autoescape=True, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True
)

_MARKDOWN_TEMPLATE = """\
# {{ report.title }}
{% if report.context %}

> {{ report.context }}
{% endif %}

## Executive summary
{% for para in report.executive_summary %}

{{ para }}
{% endfor %}

## Proposed experiments
{% for e in report.experiments %}

### {{ e.exp_id }} — {{ e.title }}

**Pillar:** {{ e.pillar.value }}
**Affected surface:** {{ e.affected_surface }}
**URL:** {{ e.url }}
**Evidence:** {{ e.evidence }}
**Hypothesis:** {{ e.hypothesis }}
**Primary change:** {{ e.primary_change }}
**Primary KPI:** {{ e.primary_kpi }}
**Decision rule:** {{ e.decision_rule }}
**Expected lift:** {{ e.expected_lift }}
**Confidence:** {{ e.confidence }}
{% endfor %}

## Competitor analysis
{% if report.competitor_intro %}

{{ report.competitor_intro }}
{% endif %}

| Competitor | Domain | Positioning | What they make easier | {{ report.store_name }} edge | Pattern to adapt |
|---|---|---|---|---|---|
{% for c in report.competitors %}
| {{ c.competitor }} | {{ c.domain }} | {{ c.positioning }} | {{ c.what_they_make_easier }} | {{ c.store_edge }} | {{ c.pattern_to_adapt }} |
{% endfor %}

## Technical checks

| Check | Status | Detail |
|---|---|---|
{% for t in report.tech_checks %}
| {{ t.name }} | {{ t.status.value }} | {{ t.detail }} |
{% endfor %}
"""

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ report.title }}</title>
</head>
<body>
<h1>{{ report.title }}</h1>
{% if report.context %}<blockquote>{{ report.context }}</blockquote>{% endif %}
<h2>Executive summary</h2>
{% for para in report.executive_summary %}<p>{{ para }}</p>{% endfor %}
<h2>Proposed experiments</h2>
{% for e in report.experiments %}
<section class="experiment">
<h3>{{ e.exp_id }} — {{ e.title }}</h3>
<ul>
<li><strong>Pillar:</strong> {{ e.pillar.value }}</li>
<li><strong>Affected surface:</strong> {{ e.affected_surface }}</li>
<li><strong>URL:</strong> {{ e.url }}</li>
<li><strong>Evidence:</strong> {{ e.evidence }}</li>
<li><strong>Hypothesis:</strong> {{ e.hypothesis }}</li>
<li><strong>Primary change:</strong> {{ e.primary_change }}</li>
<li><strong>Primary KPI:</strong> {{ e.primary_kpi }}</li>
<li><strong>Decision rule:</strong> {{ e.decision_rule }}</li>
<li><strong>Expected lift:</strong> {{ e.expected_lift }}</li>
<li><strong>Confidence:</strong> {{ e.confidence }}</li>
</ul>
</section>
{% endfor %}
<h2>Competitor analysis</h2>
{% if report.competitor_intro %}<p>{{ report.competitor_intro }}</p>{% endif %}
<table>
<thead><tr><th>Competitor</th><th>Domain</th><th>Positioning</th><th>What they make easier</th><th>{{ report.store_name }} edge</th><th>Pattern to adapt</th></tr></thead>
<tbody>
{% for c in report.competitors %}<tr><td>{{ c.competitor }}</td><td>{{ c.domain }}</td><td>{{ c.positioning }}</td><td>{{ c.what_they_make_easier }}</td><td>{{ c.store_edge }}</td><td>{{ c.pattern_to_adapt }}</td></tr>
{% endfor %}</tbody>
</table>
<h2>Technical checks</h2>
<table>
<thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
<tbody>
{% for t in report.tech_checks %}<tr><td>{{ t.name }}</td><td>{{ t.status.value }}</td><td>{{ t.detail }}</td></tr>
{% endfor %}</tbody>
</table>
</body>
</html>
"""


def _normalize_blank_lines(text: str) -> str:
    """Collapse 3+ consecutive newlines to 2 and ensure a single trailing newline."""
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def to_markdown(report: AuditReport) -> str:
    """Render the report as Markdown matching the ``target_report.md`` layout."""
    rendered = _md_env.from_string(_MARKDOWN_TEMPLATE).render(report=report)
    return _normalize_blank_lines(rendered)


def to_html(report: AuditReport) -> str:
    """Render the report as a standalone HTML document."""
    rendered = _html_env.from_string(_HTML_TEMPLATE).render(report=report)
    return rendered.strip() + "\n"
