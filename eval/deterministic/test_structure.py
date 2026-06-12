"""Phase 4 gate: structural checks pass on known-good reports and fail on broken ones."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval import config
from eval.deterministic import checks

KNOWN_GOOD = {
    "target": (config.REPORTS_DIR / "target_report.json", config.bundle_dir("gingerpeople")),
    "zenrojas_sample": (config.SAMPLE_OUTPUT / "zenrojas" / "report.json", config.bundle_dir("zenrojas")),
    "gingerpeople_sample": (config.SAMPLE_OUTPUT / "gingerpeople" / "report.json", config.bundle_dir("gingerpeople")),
}


def _load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


@pytest.mark.parametrize("key", list(KNOWN_GOOD))
def test_all_hard_gates_pass_on_known_goods(key):
    report_path, bundle = KNOWN_GOOD[key]
    results = checks.run_deterministic(_load(report_path), bundle)
    # Hard gates define validity; soft checks (competitor plausibility, evidence diversity) are
    # quality nudges a valid report may still trip.
    failed = [c.name for c in results if c.severity == "hard" and not c.passed]
    assert not failed, f"{key} unexpectedly failed a hard gate: {failed}"


def _results(report, bundle):
    return {c.name: c for c in checks.run_deterministic(report, bundle)}


def test_drop_to_nine_fails_exactly_ten():
    rep = _load(config.SAMPLE_OUTPUT / "gingerpeople" / "report.json")
    rep["experiments"].pop()
    res = _results(rep, config.bundle_dir("gingerpeople"))
    assert not res["exactly_ten"].passed


def test_dropping_a_pillar_fails_pillar_floor():
    rep = _load(config.SAMPLE_OUTPUT / "zenrojas" / "report.json")
    for e in rep["experiments"]:
        if e["pillar"] == "Performance":
            e["pillar"] = "Conversion"
    res = _results(rep, config.bundle_dir("zenrojas"))
    assert not res["pillar_floor"].passed


def test_stripped_guardrail_fails_all_fields():
    rep = _load(config.SAMPLE_OUTPUT / "zenrojas" / "report.json")
    rep["experiments"][0]["decision_rule"] = "Improve add-to-cart rate."
    res = _results(rep, config.bundle_dir("zenrojas"))
    assert not res["all_fields"].passed


def test_vague_hypothesis_fails_all_fields():
    rep = _load(config.SAMPLE_OUTPUT / "zenrojas" / "report.json")
    rep["experiments"][0]["hypothesis"] = "It will help."
    res = _results(rep, config.bundle_dir("zenrojas"))
    assert not res["all_fields"].passed


def test_missing_sections_fails():
    rep = _load(config.SAMPLE_OUTPUT / "zenrojas" / "report.json")
    rep["competitors"] = rep["competitors"][:1]
    res = _results(rep, config.bundle_dir("zenrojas"))
    assert not res["sections_present"].passed
