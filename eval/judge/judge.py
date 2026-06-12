"""Score the 3 rubric dimensions over captured artifact text. Three concurrent LLM calls share a cache-controlled prefix; inject a FakeAnthropic for offline use."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from eval.judge.rubrics import COMMON, RUBRICS
from eval.score_model import JudgeDimension

DEFAULT_MODEL = "claude-sonnet-4-6"


def _default_client():
    from dotenv import load_dotenv

    load_dotenv()
    import anthropic

    return anthropic.Anthropic()


def _load_artifact_text(bundle_dir: Path, max_chars: int = 12000) -> str:
    content_dir = Path(bundle_dir) / "content"
    chunks = []
    if content_dir.exists():
        for f in sorted(content_dir.glob("*.md")):
            chunks.append(f"### {f.name}\n{f.read_text()[:4000]}")
    text = "\n\n".join(chunks)
    return text[:max_chars] if text else "(no captured content)"


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip().strip("`").strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {"score": 0.0, "rationale": "unparseable", "per_item": [], "self_confidence": 0.0}
    return json.loads(m.group(0))


def _call(client, model: str, dimension: str, rubric: str, artifact: str, report_json: str) -> str:
    shared = (
        f"{COMMON}\n\nARTIFACT TEXT (verbatim captured content):\n{artifact}\n\n"
        f"REPORT_JSON:\n{report_json}"
    )
    system = [
        {"type": "text", "text": shared, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": rubric},
    ]
    user = f"DIMENSION = {dimension}\nScore only this dimension now. Return ONLY the JSON object."
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def run_judge(report, bundle_dir, *, client=None, model: str = DEFAULT_MODEL) -> list[JudgeDimension]:
    client = client or _default_client()
    data = report if isinstance(report, dict) else report.model_dump(mode="json")
    report_json = json.dumps(data, indent=2)
    artifact = _load_artifact_text(Path(bundle_dir))

    def score_one(dimension: str) -> JudgeDimension:
        raw = _call(client, model, dimension, RUBRICS[dimension], artifact, report_json)
        parsed = _parse_json(raw)
        return JudgeDimension(
            name=dimension,
            score=float(parsed.get("score", 0.0)),
            rationale=str(parsed.get("rationale", "")),
            per_item=[str(x) for x in parsed.get("per_item", [])],
            self_confidence=float(parsed.get("self_confidence", 0.0)),
        )

    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(score_one, list(RUBRICS)))
