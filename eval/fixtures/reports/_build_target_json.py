"""Parse target_report.md into a schema-valid JSON, remapping internal artifact paths to real gingerpeople bundle artifacts. Run once: python -m eval.fixtures.reports._build_target_json"""

from __future__ import annotations

import json
import re
from pathlib import Path

from core.schema import AuditReport

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "target_report.md"
OUT = Path(__file__).resolve().parent / "target_report.json"


def _section(src: str, start: str, end: str | None) -> str:
    tail = rf"(?=\n## {re.escape(end)})" if end else r"\Z"
    return re.search(rf"## {re.escape(start)}\s*\n(.*?){tail}", src, re.S).group(1)


def _field(chunk: str, label: str) -> str:
    m = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$", chunk, re.M)
    return m.group(1).strip().strip("`") if m else ""


def _remap_evidence(surface: str, title: str) -> str:
    """Return the closest matching artifact path in the gingerpeople bundle for a given surface/title."""
    s = f"{surface} {title}".lower()
    if "cart" in s:
        return "screenshots/02-cart.png"
    if "kit" in s or "sampler" in s or "flavor" in s:
        return "catalog.json"
    if "glp" in s or "pregnancy" in s or "morning" in s or "routine" in s:
        return "content/00-homepage.md"
    if "product" in s or "buying box" in s:
        return "screenshots/01-pdp.png"
    return "screenshots/00-homepage.png"


def build() -> dict:
    src = SRC.read_text()
    title = re.search(r"^# (.+)$", src, re.M).group(1).strip()

    exec_block = _section(src, "Executive summary", "Proposed experiments")
    exec_paras = [p.strip() for p in re.split(r"\n\s*\n", exec_block.strip()) if p.strip()]

    exp_block = _section(src, "Proposed experiments", "Competitor analysis")
    experiments = []
    for chunk in re.split(r"(?m)^### ", exp_block):
        chunk = chunk.strip()
        head = chunk.splitlines()[0] if chunk else ""
        m = re.match(r"(\S+)\s+—\s+(.+)$", head)
        if not m:
            continue
        surface = _field(chunk, "Affected surface")
        title_x = m.group(2).strip()
        experiments.append(
            {
                "exp_id": m.group(1),
                "title": title_x,
                "pillar": _field(chunk, "Pillar"),
                "affected_surface": surface,
                "url": _field(chunk, "URL"),
                "evidence": _remap_evidence(surface, title_x),
                "hypothesis": _field(chunk, "Hypothesis"),
                "primary_change": _field(chunk, "Primary change"),
                "primary_kpi": _field(chunk, "Primary KPI"),
                "decision_rule": _field(chunk, "Decision rule"),
                "expected_lift": _field(chunk, "Expected lift"),
                "confidence": _field(chunk, "Confidence"),
            }
        )

    comp_block = _section(src, "Competitor analysis", "Technical checks").strip()
    comp_lines = comp_block.splitlines()
    intro = comp_lines[0].strip()
    comp_rows = [line for line in comp_lines if line.strip().startswith("|")]
    competitors = []
    for row in comp_rows[2:]:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 6:
            competitors.append(
                {
                    "competitor": cells[0],
                    "domain": cells[1],
                    "positioning": cells[2],
                    "what_they_make_easier": cells[3],
                    "store_edge": cells[4],
                    "pattern_to_adapt": cells[5],
                }
            )

    tech_rows = [line for line in _section(src, "Technical checks", None).strip().splitlines() if line.strip().startswith("|")]
    tech = []
    for row in tech_rows[2:]:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 3:
            tech.append({"name": cells[0], "status": cells[1], "detail": cells[2]})

    return {
        "store_url": "https://gingerpeople.com",
        "store_name": "Ginger People",
        "title": title,
        "executive_summary": exec_paras[:3],
        "experiments": experiments,
        "competitor_intro": intro,
        "competitors": competitors,
        "tech_checks": tech,
    }


def main() -> None:
    report = build()
    AuditReport.model_validate(report)  # fail loudly if the parse drifts from the contract
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {OUT} — {len(report['experiments'])} experiments, {len(report['tech_checks'])} checks")


if __name__ == "__main__":
    main()
