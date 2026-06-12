"""Versioned rubric prompts for the three judge dimensions. Bump RUBRIC_VERSION on any wording change."""

from __future__ import annotations

RUBRIC_VERSION = "v2"

COMMON = (
    "You are a meticulous conversion-rate-optimization (CRO) audit reviewer. You are given the "
    "verbatim captured content of a storefront and a proposed audit report. Judge ONE dimension "
    "of the report on a 0.0-1.0 scale. Be strict and evidence-driven.\n\n"
    "Return ONLY a single JSON object, no prose around it:\n"
    '{"score": <float 0..1>, "rationale": "<one paragraph>", '
    '"per_item": ["<exp_id>: <short note>", ...], "self_confidence": <float 0..1>}\n'
    "`self_confidence` is YOUR confidence in this score given the evidence available."
)

RUBRICS = {
    "groundedness": (
        "DIMENSION = groundedness. Score how well each experiment is grounded in the captured "
        "evidence: does it cite a real artifact or URL, and do its claims tie to facts actually "
        "visible in the captured content rather than speculation? Penalize invented surfaces, "
        "claims with no support, and citations that don't match the content. 1.0 = every "
        "experiment is tightly grounded; 0.0 = mostly speculation."
    ),
    "specificity": (
        "DIMENSION = specificity. Score how specific and actionable each experiment is: a concrete "
        "primary change, a named primary KPI, and a TWO-PART hypothesis (a predicted mechanism AND "
        "a grounded current-state observation, ideally with numbers). Penalize vague, generic, or "
        "templated hypotheses and changes that could apply to any store. 1.0 = sharp and "
        "store-specific; 0.0 = vague boilerplate."
    ),
    "calibration": (
        "DIMENSION = calibration. Score whether each experiment's confidence tracks its "
        "speculativeness: structural fixes to observed problems should be high-confidence, while "
        "brand-new pages or net-new content should be lower-confidence. Penalize overconfident "
        "new pages and under-confident obvious fixes. 1.0 = confidence well-calibrated to risk; "
        "0.0 = confidence unrelated to risk."
    ),
    "surface_specificity": (
        "DIMENSION = surface_specificity. Score how precisely each experiment is anchored to a "
        "concrete captured surface and names a specific missing element — e.g. 'the GIN GINS PDP "
        "shows reviews but no add-to-cart' beats 'improve the homepage'. Reward experiments tied to "
        "a real PDP / cart / collection / named page with a concrete module to add or change; "
        "penalize ones aimed at vague, sitewide, or generic 'the homepage' targets. 1.0 = every "
        "experiment names a real surface and a concrete change; 0.0 = generic and unanchored."
    ),
}
