"""Phase 5 gate: agreement clears the floor, every ablation is penalized in its target,
and calibration_state.json links escalation_threshold to agreement."""

from __future__ import annotations

import json

from core.eval_api import score_report
from eval import config
from eval.calibration.calibrate import (
    DIM_FLOOR,
    build_items,
    compute_agreement,
    write_state,
)
from eval.judge.fake import FakeAnthropic
from eval.judge.judge import run_judge

KNOWN_GOOD = json.loads((config.REPORTS_DIR / "target_report.json").read_text())
LABELS = json.loads((config.REPO_ROOT / "eval" / "calibration" / "labels.json").read_text())
BUNDLE = config.bundle_dir("gingerpeople")


def _judge(data, bundle):
    return run_judge(data, bundle, client=FakeAnthropic())


def test_agreement_meets_floor():
    agreement, details = compute_agreement(_judge, KNOWN_GOOD, BUNDLE, LABELS)
    assert agreement >= 0.80, details


def test_every_ablation_penalized_in_its_target():
    items = build_items(KNOWN_GOOD)
    for label in LABELS["items"]:
        if label["name"] == "known_good":
            continue
        sr = score_report(items[label["name"]], BUNDLE, judge=_judge)
        target = label["target"]
        if target["type"] == "gate":
            assert not sr.hard_gate_passed, f"{label['name']} should fail the gate"
            failed = {c.name for c in sr.deterministic if not c.passed}
            assert target["check"] in failed, f"{label['name']}: expected {target['check']} in {failed}"
        else:
            assert sr.hard_gate_passed, f"{label['name']} should pass the gate but be judged down"
            scores = {d.name: d.score for d in sr.judge}
            assert scores[target["dimension"]] < DIM_FLOOR, f"{label['name']}: {scores}"


def test_known_good_passes_cleanly():
    sr = score_report(KNOWN_GOOD, BUNDLE, judge=_judge)
    assert sr.hard_gate_passed
    assert all(d.score >= DIM_FLOOR for d in sr.judge)


def test_calibration_state_links_escalation_to_agreement(tmp_path):
    agreement, _ = compute_agreement(_judge, KNOWN_GOOD, BUNDLE, LABELS)
    state = write_state(agreement, len(LABELS["items"]), tmp_path / "calibration_state.json", judge_source="fake_offline")
    assert state["escalation_threshold"] == state["agreement"] == round(agreement, 4)
    assert state["rubric_version"] == "v1"
    assert state["n_items"] == len(LABELS["items"])
