"""The one public eval entrypoint, shared by the MCP score tool and the loop. Runs the
deterministic checks first and short-circuits (score 0, no judge) if a hard gate fails; the
judge is injected so this stays import-light and network-free."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from eval import config
from eval.deterministic.checks import run_deterministic
from eval.score_model import JudgeDimension, ScoreReport


def _to_dict(report) -> dict:
    if hasattr(report, "model_dump"):
        return report.model_dump(mode="json")
    if isinstance(report, (str, Path)):
        return json.loads(Path(report).read_text())
    return dict(report)


def _combine(deterministic_score: float, judge_dims: list[JudgeDimension]) -> float:
    if not judge_dims:
        return deterministic_score
    weights = config.WEIGHTS
    total = weights["deterministic"] * deterministic_score
    for dim in judge_dims:
        total += weights.get(dim.name, 0.0) * dim.score
    return total


def score_report(
    report,
    bundle_dir,
    *,
    judge: Callable[[dict, Path], list[JudgeDimension]] | None = None,
) -> ScoreReport:
    """Score one report against its cached bundle. ``report`` may be an AuditReport, a dict, or a path."""
    data = _to_dict(report)
    bundle_dir = Path(bundle_dir)
    slug = bundle_dir.name

    checks = run_deterministic(data, bundle_dir)
    hard_passed = all(c.passed for c in checks if c.severity == "hard")
    deterministic_score = sum(1 for c in checks if c.passed) / len(checks)

    if not hard_passed:
        return ScoreReport(
            slug=slug, hard_gate_passed=False, deterministic_score=deterministic_score,
            deterministic=checks, judge=[], combined_score=0.0,
            rubric_version=config.RUBRIC_VERSION,
        )

    judge_dims = judge(data, bundle_dir) if judge is not None else []
    return ScoreReport(
        slug=slug, hard_gate_passed=True, deterministic_score=deterministic_score,
        deterministic=checks, judge=judge_dims,
        combined_score=_combine(deterministic_score, judge_dims),
        rubric_version=config.RUBRIC_VERSION,
    )
