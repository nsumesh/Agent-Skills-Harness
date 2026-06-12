"""Phase 5 gate: the judge returns valid, well-formed dimensions and runs only post-gate."""

from __future__ import annotations

import json

from core.eval_api import score_report
from eval import config
from eval.judge.fake import FakeAnthropic
from eval.judge.judge import run_judge
from eval.judge.rubrics import RUBRICS


def _zen():
    return json.loads((config.SAMPLE_OUTPUT / "zenrojas" / "report.json").read_text())


def test_judge_returns_three_valid_dimensions():
    dims = run_judge(_zen(), config.bundle_dir("zenrojas"), client=FakeAnthropic())
    assert [d.name for d in dims] == list(RUBRICS)
    for d in dims:
        assert 0.0 <= d.score <= 1.0
        assert 0.0 <= d.self_confidence <= 1.0
        assert isinstance(d.per_item, list)


def test_good_report_scores_high_on_all_dimensions():
    dims = {d.name: d.score for d in run_judge(_zen(), config.bundle_dir("zenrojas"), client=FakeAnthropic())}
    assert dims["groundedness"] >= 0.8
    assert dims["specificity"] >= 0.8
    assert dims["calibration"] >= 0.8


def test_judge_runs_only_after_the_gate_passes():
    calls = {"n": 0}
    client = FakeAnthropic()

    def judge(data, bundle):
        calls["n"] += 1
        return run_judge(data, bundle, client=client)

    broken = _zen()
    broken["experiments"].pop()  # 9 -> hard gate fails
    sr = score_report(broken, config.bundle_dir("zenrojas"), judge=judge)
    assert not sr.hard_gate_passed and calls["n"] == 0

    sr_ok = score_report(_zen(), config.bundle_dir("zenrojas"), judge=judge)
    assert sr_ok.hard_gate_passed and calls["n"] == 1 and len(sr_ok.judge) == len(RUBRICS)
