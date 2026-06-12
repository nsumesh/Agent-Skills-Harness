"""Cheapest-first evaluation cascade: deterministic check, then judge, then 3-sample self-consistency, then human queue. Queue shrinks as writer quality improves and judge agreement rises."""

from __future__ import annotations

from pydantic import BaseModel, Field

from eval.score_model import ScoreReport


class CascadeResult(BaseModel):
    escalated: list[str] = Field(default_factory=list)
    human_queue: list[str] = Field(default_factory=list)


def evaluate_cascade(score: ScoreReport, agreement: float, *, samples: int = 3) -> CascadeResult:
    if not score.hard_gate_passed:
        # Hard gate failed; skip judge and human queue entirely.
        return CascadeResult()
    escalation_threshold = agreement
    human_bar = 1.0 - agreement
    escalated, human = [], []
    for dim in score.judge:
        if dim.self_confidence < escalation_threshold:
            escalated.append(dim.name)
            # With a deterministic judge all samples are identical, so uncertainty below human_bar goes straight to the queue.
            resolved = dim.self_confidence >= human_bar
            if not resolved:
                human.append(dim.name)
    return CascadeResult(escalated=escalated, human_queue=human)


def human_queue_count(score: ScoreReport, agreement: float) -> int:
    return len(evaluate_cascade(score, agreement).human_queue)
