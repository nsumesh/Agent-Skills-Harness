"""Single source of truth for eval weights, thresholds, and paths."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

RUBRIC_VERSION = "v1"

# Blend used once the judge runs (Phase 5+). Must sum to 1.0.
WEIGHTS = {
    "deterministic": 0.35,
    "groundedness": 0.30,
    "specificity": 0.20,
    "calibration": 0.15,
}

PASS_THRESHOLD = 0.70  # combined_score at/above which a report is "good enough"

BUNDLE_ROOT = REPO_ROOT / "eval" / "fixtures" / "bundles"
REPORTS_DIR = REPO_ROOT / "eval" / "fixtures" / "reports"
SAMPLE_OUTPUT = REPO_ROOT / "sample_output"


def bundle_dir(slug: str) -> Path:
    return BUNDLE_ROOT / slug
