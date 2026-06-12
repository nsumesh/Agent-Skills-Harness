"""Persistent records for a loop run, keeping it auditable and reproducible."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IterationRecord(BaseModel):
    iteration: int
    directive_added: str
    trained_score: float
    holdout_score: float
    accepted: bool
    reason: str


class OptimizerRun(BaseModel):
    train_slug: str
    holdout_slug: str
    agreement: float
    accepted_directives: list[str]
    baseline_trained: float
    baseline_holdout: float
    final_trained: float
    final_holdout: float
    holdout_delta: float
    trained_delta: float
    stopped_early: bool
    # Human-review queue size; shrinks as writer quality and judge agreement both improve.
    queue_baseline: int
    queue_final: int
    queue_low_agreement: int
    queue_high_agreement: int
    iterations: list[IterationRecord] = Field(default_factory=list)
