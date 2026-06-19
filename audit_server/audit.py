"""End-to-end auto-audit: crawl a live storefront, have the writer generate the report from
that capture, re-prompt it with any eval failures until it's clean (the pre-write critic), then
render. The whole harness as one call.

  python -m audit_server.audit https://store.com [https://other.com ...]
  (no args → audits gingerpeople + zenrojas into sample_output/)
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from core.eval_api import score_report
from core.render import to_html, to_markdown
from core.schema import AuditReport
from eval.deterministic.checks import run_deterministic
from eval.loop.writer import QUALITY_DIRECTIVES, generate, render_prompt

from .profile import DEFAULT_BUNDLE_ROOT, slug_for
from .tools.crawl import crawl_storefront


def _critique(report: dict, bundle_dir: Path) -> list[str]:
    """Every reason the report isn't acceptable — schema errors plus failed eval checks."""
    issues = []
    try:
        AuditReport.model_validate(report)
    except ValidationError as exc:
        issues += [f"schema {tuple(e['loc'])}: {e['msg']}" for e in exc.errors()[:12]]
    for check in run_deterministic(report, bundle_dir):
        if not check.passed:
            issues.append(f"[{check.severity}] {check.name}: {check.detail} {check.failures[:4]}")
    return issues


def run_audit(url: str, *, out_dir=None, bundle_root=None, max_attempts: int = 4, client=None):
    """Crawl `url`, generate + critic-loop a report, render it, and score. Returns
    (report, ScoreReport, remaining_issues, attempts_used)."""
    slug = slug_for(url)
    bundle_root = Path(bundle_root or DEFAULT_BUNDLE_ROOT)
    crawl_storefront(url, bundle_root=bundle_root)          # live crawl → fresh capture
    bundle = bundle_root / slug

    base = render_prompt(list(QUALITY_DIRECTIVES))
    prompt, report, attempt = base, {}, 0
    while attempt < max_attempts:
        attempt += 1
        report = generate(prompt, bundle, client=client)
        issues = _critique(report, bundle)
        if not issues:
            break
        prompt = base + "\n\nYour previous attempt FAILED these eval checks. Fix every one exactly:\n- " + "\n- ".join(issues)

    out = Path(out_dir) if out_dir else Path("sample_output") / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    try:
        model = AuditReport.model_validate(report)
        (out / "report.md").write_text(to_markdown(model))
        (out / "report.html").write_text(to_html(model))
    except ValidationError:
        pass  # invalid report still written as JSON for inspection; flagged via remaining issues

    return report, score_report(report, bundle), _critique(report, bundle), attempt


def main() -> None:
    import sys

    from dotenv import load_dotenv

    load_dotenv()
    urls = sys.argv[1:] or ["https://gingerpeople.com", "https://zenrojas.com"]
    for url in urls:
        _report, sr, remaining, attempts = run_audit(url)
        print(f"\n{url}: attempts={attempts}  hard_gate={sr.hard_gate_passed}  "
              f"deterministic={sr.deterministic_score:.2f}  remaining_issues={len(remaining)}")
        for issue in remaining[:6]:
            print(f"   - {issue}")


if __name__ == "__main__":
    main()
