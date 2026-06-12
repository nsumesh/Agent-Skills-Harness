"""Seven deterministic checks on a raw report dict — 6 hard gates plus one soft check. Zero LLM, fully reproducible."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from core.schema import CONFIDENCE_RE, DECISION_RULE_RE, LIFT_RE, Pillar
from eval.score_model import CheckResult

REQUIRED_FIELDS = [
    "exp_id", "title", "pillar", "affected_surface", "url", "evidence",
    "hypothesis", "primary_change", "primary_kpi", "decision_rule",
    "expected_lift", "confidence",
]
PILLARS = {p.value for p in Pillar}


def _hard(name, passed, detail, failures=None) -> CheckResult:
    return CheckResult(name=name, passed=passed, severity="hard", detail=detail, failures=failures or [])


def _soft(name, passed, detail, failures=None) -> CheckResult:
    return CheckResult(name=name, passed=passed, severity="soft", detail=detail, failures=failures or [])


def _is_two_part(hypothesis: str) -> bool:
    """Return True if the hypothesis contains at least two sentences."""
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", hypothesis.strip()) if s.strip()]
    return len(sentences) >= 2


def _host(url: str) -> str:
    host = (urlsplit(url if "://" in url else f"https://{url}").hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def check_sections_present(report: dict) -> CheckResult:
    missing = []
    es = report.get("executive_summary")
    if not isinstance(es, list) or not (2 <= len(es) <= 3):
        missing.append("executive_summary (2-3 paragraphs)")
    if not isinstance(report.get("experiments"), list):
        missing.append("experiments")
    comps = report.get("competitors")
    if not isinstance(comps, list) or not (3 <= len(comps) <= 4):
        missing.append("competitors (3-4)")
    tech = report.get("tech_checks")
    if not isinstance(tech, list) or len(tech) < 10:
        missing.append("tech_checks (>=10)")
    return _hard("sections_present", not missing,
                 "All four sections present." if not missing else f"Missing/invalid: {missing}", missing)


def check_exactly_ten(report: dict) -> CheckResult:
    n = len(report.get("experiments") or [])
    return _hard("exactly_ten", n == 10, f"{n} experiments (need exactly 10).")


def check_all_fields(report: dict) -> CheckResult:
    failures = []
    for i, e in enumerate(report.get("experiments") or []):
        eid = e.get("exp_id", f"#{i}")
        for field in REQUIRED_FIELDS:
            if not str(e.get(field, "")).strip():
                failures.append(f"{eid}: missing {field}")
        if e.get("pillar") not in PILLARS:
            failures.append(f"{eid}: invalid pillar {e.get('pillar')!r}")
        if not DECISION_RULE_RE.match(str(e.get("decision_rule", "")).strip()):
            failures.append(f"{eid}: decision_rule has no guardrail")
        if not _is_two_part(str(e.get("hypothesis", ""))):
            failures.append(f"{eid}: hypothesis is not two-part")
        if not LIFT_RE.match(str(e.get("expected_lift", "")).strip()):
            failures.append(f"{eid}: expected_lift unparseable")
        if not CONFIDENCE_RE.match(str(e.get("confidence", "")).strip()):
            failures.append(f"{eid}: confidence unparseable")
    return _hard("all_fields", not failures,
                 "All experiments well-formed." if not failures else f"{len(failures)} field issue(s).", failures)


def check_pillar_floor(report: dict) -> CheckResult:
    present = {e.get("pillar") for e in (report.get("experiments") or [])}
    missing = sorted(PILLARS - present)
    return _hard("pillar_floor", not missing,
                 "All 5 pillars present." if not missing else f"Missing pillars: {missing}", missing)


def _citation_target(evidence: str) -> str:
    """Return the first whitespace-delimited token of an evidence string, with trailing punctuation stripped."""
    token = evidence.strip().split()[0] if evidence.strip() else ""
    return token.rstrip(":;,.")


def check_citation_resolution(report: dict, bundle_dir: Path) -> CheckResult:
    bundle_dir = Path(bundle_dir)
    failures = []
    for i, e in enumerate(report.get("experiments") or []):
        eid = e.get("exp_id", f"#{i}")
        ev = str(e.get("evidence", "")).strip()
        if not ev:
            failures.append(f"{eid}: no evidence cited")
            continue
        if ev.startswith(("http://", "https://")):
            continue  # URLs are accepted as-is
        target = _citation_target(ev)
        try:
            resolved = bool(target) and (bundle_dir / target).exists()
        except OSError:
            resolved = False  # guard against over-long path strings
        if not resolved:
            failures.append(f"{eid}: evidence '{ev[:48]}' does not resolve in the bundle")
    return _hard("citation_resolution", not failures,
                 "All citations resolve." if not failures else f"{len(failures)} unresolved citation(s).", failures)


def _cached_tech(bundle_dir: Path) -> dict:
    path = Path(bundle_dir) / "technical.json"
    if not path.exists():
        return {}
    return {row["name"]: row["status"] for row in json.loads(path.read_text())}


def check_fabrication(report: dict, bundle_dir: Path) -> CheckResult:
    """Flag any tech-check row that claims Pass when the cached probe recorded a different status."""
    cached = _cached_tech(bundle_dir)
    failures = []
    for row in report.get("tech_checks") or []:
        if row.get("status") != "Pass":
            continue
        name = row.get("name")
        observed = cached.get(name)
        if observed is None:
            failures.append(f"{name}: claims Pass but there is no probe result to verify it")
        elif observed != "Pass":
            failures.append(f"{name}: claims Pass but the probe found {observed}")
    return _hard("fabrication_detection", not failures,
                 "No fabricated passes." if not failures else f"{len(failures)} fabricated Pass(es).", failures)


def check_competitor_plausibility(report: dict) -> CheckResult:
    comps = report.get("competitors") or []
    failures = []
    if not (3 <= len(comps) <= 4):
        failures.append(f"{len(comps)} competitors (need 3-4)")
    domains = [str(c.get("domain", "")).lower() for c in comps]
    if len(set(domains)) != len(domains):
        failures.append("duplicate competitor domains")
    store_host = _host(report.get("store_url", ""))
    cells = ["competitor", "domain", "positioning", "what_they_make_easier", "store_edge", "pattern_to_adapt"]
    for c in comps:
        if not all(str(c.get(k, "")).strip() for k in cells):
            failures.append(f"{c.get('competitor', '?')}: has an empty cell")
        if store_host and store_host in str(c.get("domain", "")).lower():
            failures.append(f"{c.get('competitor', '?')}: self-referencing domain")
    return _soft("competitor_plausibility", not failures,
                 "Competitors plausible." if not failures else f"{len(failures)} issue(s).", failures)


def _count_artifacts(bundle_dir: Path) -> int:
    bundle_dir = Path(bundle_dir)
    n = sum(len(list((bundle_dir / sub).glob(pat))) for sub, pat in (("screenshots", "*.png"), ("content", "*.md")) if (bundle_dir / sub).exists())
    return n + sum((bundle_dir / f).exists() for f in ("catalog.json", "technical.json"))


def check_evidence_diversity(report: dict, bundle_dir: Path) -> CheckResult:
    """Soft: reward spreading citations across surfaces instead of leaning on one artifact."""
    cited = [str(e.get("evidence", "")).strip().split()[0] for e in (report.get("experiments") or []) if str(e.get("evidence", "")).strip()]
    counts: dict[str, int] = {}
    for c in cited:
        counts[c] = counts.get(c, 0) + 1
    distinct, max_reuse = len(counts), (max(counts.values()) if counts else 0)
    want = min(5, _count_artifacts(bundle_dir) or 5)
    failures = []
    if distinct < want:
        failures.append(f"only {distinct} distinct artifacts cited; aim for >= {want}")
    if max_reuse > 3:
        failures.append(f"one artifact cited {max_reuse}x; spread evidence across surfaces")
    return _soft("evidence_diversity", not failures,
                 "Evidence is well-spread." if not failures else f"{len(failures)} diversity issue(s).", failures)


def run_deterministic(report: dict, bundle_dir: Path) -> list[CheckResult]:
    bundle_dir = Path(bundle_dir)
    return [
        check_sections_present(report),
        check_exactly_ten(report),
        check_all_fields(report),
        check_pillar_floor(report),
        check_citation_resolution(report, bundle_dir),
        check_fabrication(report, bundle_dir),
        check_competitor_plausibility(report),
        check_evidence_diversity(report, bundle_dir),
    ]
