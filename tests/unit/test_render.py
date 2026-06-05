"""Phase 0 gate: the renderer reproduces the target_report layout, deterministically."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from core.render import to_html, to_markdown
from core.schema import Pillar

TARGET_REPORT = Path(__file__).parents[2] / "target_report.md"

SECTION_HEADINGS = [
    "## Executive summary",
    "## Proposed experiments",
    "## Competitor analysis",
    "## Technical checks",
]


def _level2_headings(markdown: str) -> list[str]:
    return [ln.rstrip() for ln in markdown.splitlines() if re.match(r"^## ", ln)]


def test_markdown_has_all_four_sections(golden_report):
    md = to_markdown(golden_report)
    assert md.startswith("# ")  # H1 title
    for heading in SECTION_HEADINGS:
        assert heading in md


def test_markdown_renders_exactly_ten_experiments(golden_report):
    md = to_markdown(golden_report)
    experiment_headings = [ln for ln in md.splitlines() if ln.startswith("### ")]
    assert len(experiment_headings) == 10
    # Each carries every required label.
    for label in (
        "**Pillar:**",
        "**Affected surface:**",
        "**URL:**",
        "**Evidence:**",
        "**Hypothesis:**",
        "**Primary change:**",
        "**Primary KPI:**",
        "**Decision rule:**",
        "**Expected lift:**",
        "**Confidence:**",
    ):
        assert md.count(label) == 10


def test_markdown_spans_all_pillars(golden_report):
    md = to_markdown(golden_report)
    for pillar in Pillar:
        assert pillar.value in md


def test_markdown_tables_present(golden_report):
    md = to_markdown(golden_report)
    assert f"| Competitor | Domain | Positioning | What they make easier | {golden_report.store_name} edge | Pattern to adapt |" in md
    assert "| Check | Status | Detail |" in md
    # Every competitor and tech-check row rendered.
    assert sum(1 for ln in md.splitlines() if ln.startswith("| ")) >= len(
        golden_report.competitors
    ) + len(golden_report.tech_checks)


def test_structure_matches_target_report(golden_report):
    """Our section headings match target_report.md's, so output is structurally on-bar."""
    target = TARGET_REPORT.read_text()
    assert _level2_headings(to_markdown(golden_report)) == _level2_headings(target)


def test_markdown_is_deterministic(golden_report):
    assert to_markdown(golden_report) == to_markdown(golden_report)


class _Balanced(HTMLParser):
    """Minimal well-formedness check: tags open and close in a consistent stack."""

    def __init__(self):
        super().__init__()
        self.stack: list[str] = []
        self.ok = True
        self._void = {"meta", "br", "img", "hr", "input", "link"}

    def handle_starttag(self, tag, attrs):
        if tag not in self._void:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self._void:
            return
        if not self.stack or self.stack[-1] != tag:
            self.ok = False
        else:
            self.stack.pop()


def test_html_well_formed(golden_report):
    html = to_html(golden_report)
    parser = _Balanced()
    parser.feed(html)
    assert parser.ok and not parser.stack
    assert "<h1>" in html
    assert html.count("<h2>") == 4
    assert html.count("<h3>") == 10
    assert html.count("<table>") == 2 and html.count("</table>") == 2
