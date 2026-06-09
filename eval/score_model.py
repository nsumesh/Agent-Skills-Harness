"""Result types for the eval cascade. Hard gate failure sets combined_score=0.0 and skips the judge."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    name: str
    passed: bool
    severity: str  # "hard" or "soft"
    detail: str
    failures: list[str] = Field(default_factory=list)  # per-item specifics


class JudgeDimension(BaseModel):
    name: str                       # groundedness | specificity | calibration
    score: float                    # 0.0 - 1.0
    rationale: str
    per_item: list[str] = Field(default_factory=list)
    self_confidence: float = 0.0    # 0.0 - 1.0, the judge's confidence in its own score


class ScoreReport(BaseModel):
    slug: str
    hard_gate_passed: bool
    deterministic_score: float       # fraction of deterministic checks passed
    deterministic: list[CheckResult]
    judge: list[JudgeDimension] = Field(default_factory=list)
    combined_score: float = 0.0
    rubric_version: str = ""
    notes: list[str] = Field(default_factory=list)

    @property
    def hard_failures(self) -> list[CheckResult]:
        return [c for c in self.deterministic if c.severity == "hard" and not c.passed]
