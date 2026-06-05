"""Phase 0 gate: the output contract validates the good and rejects the bad."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from core.schema import AuditReport, Pillar, export_json_schema


def test_golden_validates(golden_report):
    """The hand-authored fixture is a valid report with exactly 10 experiments spanning all 5 pillars."""
    assert len(golden_report.experiments) == 10
    assert golden_report.pillars_present == set(Pillar)
    assert 3 <= len(golden_report.competitors) <= 4
    assert len(golden_report.tech_checks) == 15


def test_experiment_helpers(golden_report):
    """Derived accessors parse the structured fields the eval reuses."""
    e = golden_report.experiments[0]
    lo, hi = e.lift_range
    assert lo <= hi
    assert 0 <= e.confidence_pct <= 100
    assert e.guardrail  # the clause after "without" is non-empty


# --- rejection cases: each mutation must raise ValidationError ----------------

def _mut(d, fn):
    fn(d)
    return d


REJECTIONS = {
    "missing_required_field": lambda d: d["experiments"][0].pop("hypothesis"),
    "empty_string_field": lambda d: d["experiments"][0].update(primary_kpi="   "),
    "bad_pillar": lambda d: d["experiments"][0].update(pillar="Growth"),
    "decision_rule_no_guardrail": lambda d: d["experiments"][0].update(
        decision_rule="Ship if CVR improves."
    ),
    "decision_rule_wrong_prefix": lambda d: d["experiments"][0].update(
        decision_rule="Launch if CVR improves without hurting bounce."
    ),
    "malformed_lift_no_range": lambda d: d["experiments"][0].update(expected_lift="20%"),
    "malformed_lift_text": lambda d: d["experiments"][0].update(expected_lift="a lot"),
    "lift_low_gt_high": lambda d: d["experiments"][0].update(expected_lift="+20–6%"),
    "malformed_confidence": lambda d: d["experiments"][0].update(confidence="high"),
    "confidence_out_of_range": lambda d: d["experiments"][0].update(confidence="150%"),
    "nine_experiments": lambda d: d["experiments"].pop(),
    "eleven_experiments": lambda d: d["experiments"].append(dict(d["experiments"][0])),
    "too_few_competitors": lambda d: d.__setitem__("competitors", d["competitors"][:2]),
    "too_few_tech_checks": lambda d: d.__setitem__("tech_checks", d["tech_checks"][:5]),
    "exec_summary_one_para": lambda d: d.__setitem__(
        "executive_summary", [d["executive_summary"][0]]
    ),
    "bad_check_status": lambda d: d["tech_checks"][0].update(status="Unknown"),
    "extra_field_forbidden": lambda d: d["experiments"][0].update(surprise="nope"),
}


@pytest.mark.parametrize("name", sorted(REJECTIONS))
def test_invalid_reports_are_rejected(broken_report, name):
    data = broken_report(REJECTIONS[name])
    with pytest.raises(ValidationError):
        AuditReport.model_validate(data)


# --- JSON-schema export round-trip --------------------------------------------

def test_json_schema_export():
    schema = export_json_schema()
    assert schema["type"] == "object"
    for key in ("experiments", "competitors", "tech_checks", "executive_summary"):
        assert key in schema["properties"]


def test_model_round_trips(golden_report):
    """dump -> JSON -> validate yields an equal model (lossless serialization)."""
    dumped = golden_report.model_dump_json()
    reloaded = AuditReport.model_validate_json(dumped)
    assert reloaded == golden_report
    # And the dumped form is real JSON.
    assert isinstance(json.loads(dumped), dict)
