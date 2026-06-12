"""Phase 6 gate: adversarial inputs behave; the regression corpus replays clean."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.eval_api import score_report
from eval import config
from eval.deterministic import checks

REDTEAM = Path(__file__).resolve().parent
CASES = REDTEAM / "cases"
CASE_DIRS = sorted(p for p in CASES.iterdir() if p.is_dir())
CORPUS = [json.loads(line) for line in (REDTEAM / "regression_corpus.jsonl").read_text().splitlines() if line.strip()]

ZEN = json.loads((config.SAMPLE_OUTPUT / "zenrojas" / "report.json").read_text())


def _report_with_decision_rule(value: str) -> dict:
    rep = copy.deepcopy(ZEN)
    rep["experiments"][0]["decision_rule"] = value
    return rep


@pytest.mark.parametrize("case_dir", CASE_DIRS, ids=lambda p: p.name)
def test_adversarial_case_behaves(case_dir):
    case = json.loads((case_dir / "case.json").read_text())
    report = json.loads((case_dir / "report.json").read_text())

    # Must not raise — eval handles garbage, empty bundles, and non-English text.
    sr = score_report(report, case_dir / "bundle")

    assert sr.hard_gate_passed is case["expect_hard_gate"], case["description"]
    if case["expect_hard_gate"]:
        results = {c.name: c for c in sr.deterministic}
        assert results["citation_resolution"].passed  # grounded, no invented surfaces
        assert results["fabrication_detection"].passed  # no fabricated passes


def test_all_four_adversarial_archetypes_present():
    assert {p.name for p in CASE_DIRS} == {"malformed", "empty", "single_product", "non_english"}


def test_regression_corpus_replays_clean(tmp_path):
    assert CORPUS, "regression corpus must not be empty"
    for entry in CORPUS:
        if entry["type"] == "decision_rule":
            result = checks.check_all_fields(_report_with_decision_rule(entry["value"]))
            assert result.passed is entry["expect_pass"], f"{entry['name']}: {result.failures}"
        elif entry["type"] == "fabrication":
            bundle = tmp_path / entry["name"]
            bundle.mkdir()
            (bundle / "technical.json").write_text(
                json.dumps([{"name": "Check X", "status": entry["cached_status"], "detail": "d"}])
            )
            report = {"tech_checks": [{"name": "Check X", "status": entry["report_status"], "detail": "d"}]}
            result = checks.check_fabrication(report, bundle)
            assert (not result.passed) is entry["expect_fabrication"], entry["name"]
        else:
            raise AssertionError(f"unknown corpus entry type: {entry['type']}")
