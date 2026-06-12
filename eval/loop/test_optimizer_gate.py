"""Phase 7 gate: verifies the held-out gate accepts generalizing directives and rejects overfitting ones."""

from __future__ import annotations

from eval.judge.fake import FakeAnthropic
from eval.judge.judge import run_judge
from eval.loop.fake_writer import FakeWriterAnthropic
from eval.loop.optimizer import held_out_gate, optimize

WRITER = FakeWriterAnthropic.from_samples()


def _judge(data, bundle):
    return run_judge(data, bundle, client=FakeAnthropic())


def test_held_out_gate_logic():
    assert held_out_gate(0.80, 0.80, 0.80, 0.90)          # holdout up, trained held
    assert not held_out_gate(0.80, 0.80, 0.90, 0.70)      # holdout regressed
    assert not held_out_gate(0.80, 0.80, 0.60, 0.90)      # trained regressed


def test_accepts_a_generalizing_candidate():
    outcome = optimize(
        "gingerpeople", "zenrojas", writer_client=WRITER, judge=_judge,
        base_directives=["cite", "pillars", "specific"], candidates=["calibrate"], max_iters=1,
    )
    assert outcome.records[0].accepted
    assert outcome.best_holdout > outcome.base_holdout.combined_score


def test_rejects_an_overfitting_candidate_and_stops():
    outcome = optimize(
        "gingerpeople", "zenrojas", writer_client=WRITER, judge=_judge,
        base_directives=["cite", "pillars", "specific", "calibrate"], candidates=["overfit"],
        max_iters=1, patience=1,
    )
    assert not outcome.records[0].accepted
    assert outcome.best_holdout == outcome.base_holdout.combined_score  # unchanged
    assert outcome.stopped_early  # patience exhausted
    # The overfit candidate genuinely tanked the held-out store.
    assert outcome.records[0].holdout_score < outcome.base_holdout.combined_score
