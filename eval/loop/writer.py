"""Report writer: `generate(prompt, bundle_dir)` builds an AuditReport from a cached bundle via Anthropic. The client is injected so the offline tier can swap in a deterministic FakeWriter."""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-4-6"

BASE_PROMPT = (
    "You are Qosmic's CRO audit writer. Given a storefront's cached bundle, produce ONE "
    "schema-valid AuditReport as JSON. Ground every experiment in the captured artifacts."
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
    "OUTPUT CONTRACT: a JSON object with store_url, store_name, title, executive_summary "
    "(2-3 paragraphs), experiments (exactly 10, each with exp_id, title, pillar, "
    "affected_surface, url, evidence, hypothesis, primary_change, primary_kpi, decision_rule "
    "in the form 'Ship if <KPI> ... without <guardrail>', expected_lift like '+8-14%', "
    "confidence like '78%'), competitor_intro, competitors (3-4), tech_checks (~15)."
)


def render_prompt(directives) -> str:
    lines = [f"- {ALL_DIRECTIVES[d]}" for d in directives if d in ALL_DIRECTIVES]
    return BASE_PROMPT + ("\n\nDIRECTIVES:\n" + "\n".join(lines) if lines else "")


def _default_client():
    from dotenv import load_dotenv

    load_dotenv()
    import anthropic

    return anthropic.Anthropic()


def _bundle_context(bundle_dir: Path, max_chars: int = 9000) -> str:
    bundle_dir = Path(bundle_dir)
    parts = [f"SLUG: {bundle_dir.name}"]
    for name in ("profile.json", "catalog.json", "technical.json"):
        p = bundle_dir / name
        if p.exists():
            parts.append(f"{name}:\n{p.read_text()[:2500]}")
    content = bundle_dir / "content"
    if content.exists():
        for f in sorted(content.glob("*.md")):
            parts.append(f"content/{f.name}:\n{f.read_text()[:2000]}")
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
