"""Phase 4 gate: citation-resolution grounds every experiment in the bundle."""

from __future__ import annotations

import json

from eval import config
from eval.deterministic import checks

ZEN = config.SAMPLE_OUTPUT / "zenrojas" / "report.json"
BUNDLE = config.bundle_dir("zenrojas")


def _load():
    return json.loads(ZEN.read_text())


def test_sample_citations_resolve():
    assert checks.check_citation_resolution(_load(), BUNDLE).passed


def test_bogus_path_fails():
    rep = _load()
    rep["experiments"][0]["evidence"] = "screenshots/does-not-exist.png"
    result = checks.check_citation_resolution(rep, BUNDLE)
    assert not result.passed and result.failures


def test_url_evidence_is_accepted():
    rep = _load()
    rep["experiments"][0]["evidence"] = "https://zenrojas.com/products/unwind"
    assert checks.check_citation_resolution(rep, BUNDLE).passed


def test_empty_evidence_fails():
    rep = _load()
    rep["experiments"][0]["evidence"] = ""
    assert not checks.check_citation_resolution(rep, BUNDLE).passed


def test_path_with_trailing_prose_resolves():
    """Regression: trailing prose after the path must not prevent the leading token from resolving."""
    rep = _load()
    rep["experiments"][0]["evidence"] = "content/01-pdp.md: the PDP shows no reviews, which hurts trust."
    assert checks.check_citation_resolution(rep, BUNDLE).passed


def test_pathological_long_evidence_does_not_crash():
    """Regression: an over-long evidence string must degrade to False, not raise OSError."""
    rep = _load()
    rep["experiments"][0]["evidence"] = "technical.json: " + ("x" * 5000)
    result = checks.check_citation_resolution(rep, BUNDLE)
    assert result.passed  # leading token 'technical.json' resolves; the trailing prose is ignored
