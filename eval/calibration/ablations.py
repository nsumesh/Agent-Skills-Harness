"""Seven ablations of a known-good report: 5 trip hard gates, 2 are caught only by the judge."""

from __future__ import annotations

import copy


def _clone(report: dict) -> dict:
    return copy.deepcopy(report)


def drop_to_nine(report: dict) -> dict:
    r = _clone(report)
    r["experiments"] = r["experiments"][:9]
    return r


def drop_a_pillar(report: dict) -> dict:
    r = _clone(report)
    for e in r["experiments"]:
        if e["pillar"] == "Performance":
            e["pillar"] = "Conversion"
    return r


def break_a_citation(report: dict) -> dict:
    r = _clone(report)
    r["experiments"][0]["evidence"] = "screenshots/this-was-never-captured.png"
    return r


def fake_a_pass(report: dict) -> dict:
    r = _clone(report)
    for row in r["tech_checks"]:
        if row["name"] == "Page Speed Mobile":  # cached is Warn; claiming Pass is fabrication
            row["status"] = "Pass"
    return r


def strip_guardrail(report: dict) -> dict:
    r = _clone(report)
    r["experiments"][0]["decision_rule"] = "Ship if conversion rate improves."  # missing guardrail clause
    return r


def vague_hypothesis(report: dict) -> dict:
    r = _clone(report)
    for e in r["experiments"]:
        # Two sentences to pass the heuristic, but generic and number-free so specificity is low.
        e["hypothesis"] = "This change will help conversion. It is a good idea worth testing."
    return r


def overconfident_new_page(report: dict) -> dict:
    r = _clone(report)
    for e in r["experiments"]:
        if "(new)" in str(e.get("url", "")):
            e["confidence"] = "95%"  # too high for a new page
            break
    return r


def eleven_experiments(report: dict) -> dict:
    r = _clone(report)
    r["experiments"].append(copy.deepcopy(r["experiments"][0]))  # 11 -> exactly_ten fails
    return r


def single_pillar(report: dict) -> dict:
    r = _clone(report)
    for e in r["experiments"]:
        e["pillar"] = "Conversion"  # all one pillar -> pillar_floor fails
    return r


ABLATIONS = {
    "drop_to_nine": drop_to_nine,
    "drop_a_pillar": drop_a_pillar,
    "break_a_citation": break_a_citation,
    "fake_a_pass": fake_a_pass,
    "strip_guardrail": strip_guardrail,
    "vague_hypothesis": vague_hypothesis,
    "overconfident_new_page": overconfident_new_page,
    "eleven_experiments": eleven_experiments,
    "single_pillar": single_pillar,
}


def generate_ablations(good: dict) -> dict:
    """Return a dict mapping each ablation name to its modified report."""
    return {name: fn(good) for name, fn in ABLATIONS.items()}
