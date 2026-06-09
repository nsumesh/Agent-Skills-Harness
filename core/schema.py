"""The output contract: Pydantic models + validators that mirror target_report.md so a
malformed report can't pass (valid pillar, all fields present, a guardrail in the decision
rule, parseable lift and confidence)."""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator

# Decision rule must read "Ship if … without <guardrail>". We anchor on "without" (not
# "without hurting") because the target uses both forms.
DECISION_RULE_RE = re.compile(r"^Ship if .+\bwithout\b .+$")
# A percent range like "+12-20%" (hyphen or en/em dash).
LIFT_RE = re.compile(r"^\+?\s*(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*%$")
# A single percent like "78%".
CONFIDENCE_RE = re.compile(r"^\s*(\d{1,3})\s*%\s*$")


class Pillar(str, Enum):
    """The five CRO pillars the ten experiments must collectively span."""

    conversion = "Conversion"
    aov = "AOV"
    retention = "Retention"
    acquisition = "Acquisition"
    performance = "Performance"


class CheckStatus(str, Enum):
    """Honest tri-state for a technical check. Unverifiable degrades to Warn, never a fake Pass."""

    passed = "Pass"
    warn = "Warn"
    fail = "Fail"


def _require_non_empty(v: str) -> str:
    if v is None or not str(v).strip():
        raise ValueError("must be a non-empty string")
    return v


class Experiment(BaseModel):
    """One proposed CRO experiment; every field is required. The labels match target_report.md one-for-one."""

    model_config = ConfigDict(extra="forbid")

    exp_id: str
    title: str
    pillar: Pillar
    affected_surface: str
    url: str
    evidence: str
    hypothesis: str
    primary_change: str
    primary_kpi: str
    decision_rule: str
    expected_lift: str
    confidence: str

    @field_validator(
        "exp_id",
        "title",
        "affected_surface",
        "url",
        "evidence",
        "hypothesis",
        "primary_change",
        "primary_kpi",
        "decision_rule",
        "expected_lift",
        "confidence",
    )
    @classmethod
    def _non_empty(cls, v: str) -> str:
        return _require_non_empty(v)

    @field_validator("decision_rule")
    @classmethod
    def _check_decision_rule(cls, v: str) -> str:
        if not DECISION_RULE_RE.match(v.strip()):
            raise ValueError(
                "decision_rule must read 'Ship if <KPI> ... without <guardrail>' "
                "(a guardrail clause is mandatory)"
            )
        return v

    @field_validator("expected_lift")
    @classmethod
    def _check_lift(cls, v: str) -> str:
        m = LIFT_RE.match(v.strip())
        if not m:
            raise ValueError("expected_lift must be a percent range like '+12-20%'")
        lo, hi = float(m.group(1)), float(m.group(2))
        if lo > hi:
            raise ValueError("expected_lift low bound exceeds high bound")
        return v

    @field_validator("confidence")
    @classmethod
    def _check_confidence(cls, v: str) -> str:
        m = CONFIDENCE_RE.match(v.strip())
        if not m or not (0 <= int(m.group(1)) <= 100):
            raise ValueError("confidence must be a percent 0-100 like '78%'")
        return v

    @property
    def lift_range(self) -> tuple[float, float]:
        m = LIFT_RE.match(self.expected_lift.strip())
        return float(m.group(1)), float(m.group(2))

    @property
    def confidence_pct(self) -> int:
        return int(CONFIDENCE_RE.match(self.confidence.strip()).group(1))

    @property
    def guardrail(self) -> str:
        """The clause after 'without' — the metric the experiment promises not to harm."""
        return self.decision_rule.split("without", 1)[1].strip().rstrip(".")


class CompetitorRow(BaseModel):
    """One row of the competitor table."""

    model_config = ConfigDict(extra="forbid")

    competitor: str
    domain: str
    positioning: str
    what_they_make_easier: str
    store_edge: str
    pattern_to_adapt: str

    @field_validator(
        "competitor",
        "domain",
        "positioning",
        "what_they_make_easier",
        "store_edge",
        "pattern_to_adapt",
    )
    @classmethod
    def _non_empty(cls, v: str) -> str:
        return _require_non_empty(v)


class TechCheckRow(BaseModel):
    """One row of the technical-checks table: a named check, a status, and a one-line detail."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: CheckStatus
    detail: str

    @field_validator("name", "detail")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        return _require_non_empty(v)


class AuditReport(BaseModel):
    """A complete audit report: the four-section deliverable for one storefront."""

    model_config = ConfigDict(extra="forbid")

    store_url: str
    store_name: str
    title: str
    context: str | None = None
    executive_summary: list[str]
    experiments: list[Experiment]
    competitor_intro: str | None = None
    competitors: list[CompetitorRow]
    tech_checks: list[TechCheckRow]

    _non_empty = field_validator("store_url", "store_name", "title")(_require_non_empty)

    @field_validator("executive_summary")
    @classmethod
    def _check_summary(cls, v: list[str]) -> list[str]:
        if not (2 <= len(v) <= 3):
            raise ValueError("executive_summary must have 2-3 paragraphs")
        if any(not p.strip() for p in v):
            raise ValueError("executive_summary paragraphs must be non-empty")
        return v

    @field_validator("experiments")
    @classmethod
    def _check_experiments(cls, v: list[Experiment]) -> list[Experiment]:
        if len(v) != 10:
            raise ValueError(f"a report must contain exactly 10 experiments, got {len(v)}")
        return v

    @field_validator("competitors")
    @classmethod
    def _check_competitors(cls, v: list[CompetitorRow]) -> list[CompetitorRow]:
        if not (3 <= len(v) <= 4):
            raise ValueError("competitors must have 3-4 rows")
        return v

    @field_validator("tech_checks")
    @classmethod
    def _check_tech(cls, v: list[TechCheckRow]) -> list[TechCheckRow]:
        if len(v) < 10:
            raise ValueError("tech_checks must have at least 10 rows (~15 expected)")
        return v

    @property
    def pillars_present(self) -> set[Pillar]:
        return {e.pillar for e in self.experiments}


def export_json_schema() -> dict:
    """Export the report's JSON Schema (used by docs and by callers validating raw JSON)."""
    return AuditReport.model_json_schema()
