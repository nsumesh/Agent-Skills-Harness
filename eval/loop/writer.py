"""Report writer: `generate(prompt, bundle_dir)` builds an AuditReport from a cached bundle via Anthropic. The client is injected so the offline tier can swap in a deterministic FakeWriter."""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-4-6"

BASE_PROMPT = (
    "You are Qosmic's CRO audit writer. Given a storefront's cached bundle, produce ONE "
    "schema-valid AuditReport as JSON. Ground every experiment in the captured artifacts. "
    "Spread evidence across DISTINCT captured surfaces — do not cite the same artifact for more "
    "than three experiments. Anchor each experiment to a specific captured surface (a real PDP, the "
    "cart, a collection, a named page) and name the concrete element that is missing or weak there, "
    "rather than vague sitewide or 'improve the homepage' changes."
)

# Directives the optimizer can add; FakeWriter keys off this exact text to keep offline scoring deterministic.
QUALITY_DIRECTIVES = {
    "cite": "Cite a resolvable captured artifact (a bundle path) for every experiment.",
    "pillars": "Ensure the ten experiments span all five pillars (Conversion, AOV, Retention, Acquisition, Performance).",
    "specific": "Write a two-part hypothesis for each experiment with concrete numbers drawn from the captured content.",
    "calibrate": "Keep confidence for brand-new pages at or below 72%; reserve high confidence for structural fixes.",
}
OVERFIT_DIRECTIVE = ("overfit", "Maximize the trained store by always adding a retailer-handoff experiment.")
ALL_DIRECTIVES = {**QUALITY_DIRECTIVES, OVERFIT_DIRECTIVE[0]: OVERFIT_DIRECTIVE[1]}

CONTRACT = (
    "OUTPUT CONTRACT — return ONLY one JSON object (no prose around it) with keys: store_url, "
    "store_name, title, executive_summary, experiments, competitor_intro, competitors, tech_checks.\n"
    "- executive_summary: array of 2-3 paragraph strings, each opening with a **bold claim**.\n"
    "- experiments: EXACTLY 10, spanning all five pillars (Conversion, AOV, Retention, Acquisition, "
    "Performance). Each has exp_id, title, pillar, affected_surface, url, evidence, hypothesis, "
    "primary_change, primary_kpi, decision_rule, expected_lift, confidence.\n"
    "- evidence: a path from the AVAILABLE EVIDENCE PATHS list above, or a real URL — nothing else.\n"
    "- hypothesis: TWO sentences ending in periods — sentence 1 is the predicted mechanism, sentence 2 "
    "is a grounded observation from the captured content (include a number where possible).\n"
    "- decision_rule: starts with 'Ship if' and contains a 'without <guardrail>' clause, "
    "e.g. 'Ship if PDP add-to-cart improves without hurting bounce rate.'\n"
    "- expected_lift: EXACTLY a percent range like '+8-14%' (no extra words). confidence like '78%'; "
    "keep brand-new pages at or below 72%.\n"
    "- competitors: 3-4 objects, EACH with ALL of: competitor, domain, positioning, "
    "what_they_make_easier, store_edge, pattern_to_adapt.\n"
    "- tech_checks: copy the rows from the provided technical.json VERBATIM (same name, status, detail); "
    "never upgrade a Warn/Fail to Pass."
)


def render_prompt(directives) -> str:
    lines = [f"- {ALL_DIRECTIVES[d]}" for d in directives if d in ALL_DIRECTIVES]
    return BASE_PROMPT + ("\n\nDIRECTIVES:\n" + "\n".join(lines) if lines else "")


def _default_client():
    from dotenv import load_dotenv

    load_dotenv()
    import anthropic

    return anthropic.Anthropic()


def _bundle_context(bundle_dir: Path, max_chars: int = 14000) -> str:
    bundle_dir = Path(bundle_dir)
    parts = [f"SLUG: {bundle_dir.name}"]

    # The exact artifacts the report may cite — every `evidence` must be one of these or a URL.
    evidence = []
    for sub, pattern in (("screenshots", "*.png"), ("content", "*.md")):
        d = bundle_dir / sub
        if d.exists():
            evidence += [f"{sub}/{f.name}" for f in sorted(d.glob(pattern))]
    evidence += [n for n in ("catalog.json", "technical.json") if (bundle_dir / n).exists()]
    parts.append("AVAILABLE EVIDENCE PATHS (cite only these, or a real URL):\n" + "\n".join(evidence))

    for name in ("profile.json", "catalog.json", "technical.json"):
        p = bundle_dir / name
        if p.exists():
            parts.append(f"{name}:\n{p.read_text()[:2500]}")
    content = bundle_dir / "content"
    if content.exists():
        for f in sorted(content.glob("*.md")):
            parts.append(f"content/{f.name}:\n{f.read_text()[:3000]}")
    return "\n\n".join(parts)[:max_chars]


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip().strip("`").strip()
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {}


def generate(prompt: str, bundle_dir, *, client=None, model: str = DEFAULT_MODEL) -> dict:
    client = client or _default_client()
    context = _bundle_context(Path(bundle_dir))
    system = [
        {"type": "text", "text": context, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": prompt + "\n\n" + CONTRACT},
    ]
    user = "Write the AuditReport JSON for this store now. Return ONLY the JSON object."
    resp = client.messages.create(
        model=model, max_tokens=8000, temperature=0, system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _parse_json(resp.content[0].text)
