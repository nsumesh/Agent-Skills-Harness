"""Phase 4 gate: fabrication-detection catches a Pass the probe never observed."""

from __future__ import annotations

import json

from eval import config
from eval.deterministic import checks

GP = config.SAMPLE_OUTPUT / "gingerpeople" / "report.json"
BUNDLE = config.bundle_dir("gingerpeople")


def _load():
    return json.loads(GP.read_text())


def test_sample_has_no_fabrication():
    assert checks.check_fabrication(_load(), BUNDLE).passed


def test_flipping_a_warn_to_pass_is_fabrication():
    rep = _load()
    # Cached probe is Warn; claiming Pass is fabrication.
    for row in rep["tech_checks"]:
        if row["name"] == "Page Speed Mobile":
            row["status"] = "Pass"
    result = checks.check_fabrication(rep, BUNDLE)
    assert not result.passed
    assert any("Page Speed Mobile" in f for f in result.failures)


def test_flipping_a_fail_to_pass_is_fabrication():
    rep = _load()
    # Cached probe is Fail; claiming Pass is fabrication.
    for row in rep["tech_checks"]:
        if row["name"] == "Checkout Reachable":
            row["status"] = "Pass"
    assert not checks.check_fabrication(rep, BUNDLE).passed
