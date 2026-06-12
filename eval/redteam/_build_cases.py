"""Build the 4 adversarial test cases (malformed, empty, single_product, non_english) with synthesized bundles. Run once: python -m eval.redteam._build_cases"""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = Path(__file__).resolve().parent / "cases"
ZEN = json.loads((ROOT / "sample_output" / "zenrojas" / "report.json").read_text())

SPANISH_HYPOTHESIS = "La tasa de conversión mejora al añadir prueba social en la página. La página capturada no muestra reseñas ni valoraciones."
SPANISH_CHANGE = "Añadir un módulo de reseñas con valoración y comentarios bajo el título del producto."


def _evidence_paths(report: dict) -> set[str]:
    out = set()
    for e in report.get("experiments", []):
        ev = str(e.get("evidence", "")).strip()
        if ev and not ev.startswith("http"):
            out.add(ev)
    return out


def _synth_bundle(bundle_dir: Path, report: dict, *, lang: str = "en", catalog_count: int = 12) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    # Mirror the report's tech checks so no rows are flagged as fabricated.
    (bundle_dir / "technical.json").write_text(json.dumps(report["tech_checks"], indent=2))
    (bundle_dir / "catalog.json").write_text(
        json.dumps({"source": "products_json", "count": catalog_count,
                    "products": [{"handle": f"p{i}", "url": f"{report['store_url']}/products/p{i}"} for i in range(catalog_count)]})
    )
    body = "Hola, té orgánico de origen ético." if lang == "es" else "Hello, organic tea."
    for ev in _evidence_paths(report) | {"content/00-homepage.md"}:
        path = bundle_dir / ev
        path.parent.mkdir(parents=True, exist_ok=True)
        if ev.endswith(".json"):
            continue  # technical.json/catalog.json already written
        path.write_text(body if ev.endswith(".md") else "PLACEHOLDER")


def _write_case(name: str, report: dict, *, expect_hard_gate: bool, description: str,
                empty_bundle: bool = False, lang: str = "en", catalog_count: int = 12) -> None:
    case_dir = CASES / name
    bundle_dir = case_dir / "bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    if empty_bundle:
        (bundle_dir / ".gitkeep").write_text("")
    else:
        _synth_bundle(bundle_dir, report, lang=lang, catalog_count=catalog_count)
    (case_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (case_dir / "case.json").write_text(json.dumps(
        {"name": name, "expect_hard_gate": expect_hard_gate, "description": description}, indent=2) + "\n")


def build() -> None:
    # 1. malformed: structurally broken.
    malformed = {
        "store_url": "https://broken.example", "store_name": "Broken", "title": "x",
        "executive_summary": ["only one paragraph"],
        "experiments": [{"exp_id": "e1", "title": "t", "pillar": "Banana"}],  # bad pillar, missing fields, not 10
        "competitors": [], "tech_checks": [],
    }
    _write_case("malformed", malformed, expect_hard_gate=False,
                description="Broken structure: 1 experiment, bad pillar, missing fields, empty sections.")

    # 2. empty: valid report, empty bundle.
    _write_case("empty", copy.deepcopy(ZEN), expect_hard_gate=False, empty_bundle=True,
                description="Valid report scored against an empty bundle; citations cannot resolve.")

    # 3. single_product: valid report, 1-product bundle.
    sp = copy.deepcopy(ZEN)
    sp["store_name"] = "Solo Leaf"
    _write_case("single_product", sp, expect_hard_gate=True, catalog_count=1,
                description="Valid report against a single-product store; the eval must not penalize tiny catalogs.")

    # 4. non_english: Spanish prose with English contract fields.
    ne = copy.deepcopy(ZEN)
    ne["store_name"] = "Té Zen"
    ne["title"] = "Auditoría de Té Zen — una historia de bienestar que las páginas de producto no cierran"
    ne["executive_summary"] = [
        "**Té Zen tiene una historia de bienestar clara; las páginas de producto no la cierran.** "
        "La tienda organiza los tés por momento, pero la página de producto capturada no muestra reseñas.",
        "**El catálogo es pequeño y consumible.** Las páginas ofrecen solo compra única y no hay recordatorio de recompra, "
        "dejando ingresos recurrentes sobre la mesa.",
    ]
    for e in ne["experiments"]:
        e["title"] = "Mejora basada en evidencia"
        e["hypothesis"] = SPANISH_HYPOTHESIS
        e["primary_change"] = SPANISH_CHANGE
    _write_case("non_english", ne, expect_hard_gate=True, lang="es",
                description="Spanish prose with English contract fields; checks must be language-agnostic.")

    print(f"wrote cases under {CASES}: " + ", ".join(sorted(p.name for p in CASES.iterdir() if p.is_dir())))


if __name__ == "__main__":
    build()
