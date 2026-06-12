"""Thin MCP wrapper over core.eval_api.score_report; loads the cached bundle for the slug and delegates."""

from __future__ import annotations

from pathlib import Path

from core.eval_api import score_report as _score_report

from ..profile import DEFAULT_BUNDLE_ROOT


def score_report(report_json: dict, store_slug: str, *, bundle_root=None) -> dict:
    bundle_dir = Path(bundle_root or DEFAULT_BUNDLE_ROOT) / store_slug
    return _score_report(report_json, bundle_dir).model_dump()
