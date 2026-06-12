"""Capture representative surfaces into a cached artifact bundle and return its manifest. Capture functions are injectable so the offline tier can exercise manifest assembly without a browser or API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from core import checks as core_checks
from core import probes

from ..profile import DEFAULT_BUNDLE_ROOT, BundlePaths, StoreProfile
from .catalog import CatalogResult, fetch_catalog
from .fingerprint import fingerprint_store


@dataclass
class CaptureResult:
    ok: bool
    note: str = ""
    text: str | None = None


# Default live capture functions; lazily import heavy deps.

def _default_screenshot(url: str, out_path: Path) -> CaptureResult:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001 - any import/runtime issue degrades honestly
        return CaptureResult(False, f"Playwright unavailable: {exc}")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 1600})
            # Heavy, ad-laden storefronts rarely reach networkidle; wait for `load` and
            # screenshot whatever rendered even if the wait times out.
            try:
                page.goto(url, wait_until="load", timeout=45000)
            except Exception:  # noqa: BLE001
                pass
            page.wait_for_timeout(1500)
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()
        return CaptureResult(True, "screenshot captured")
    except Exception as exc:  # noqa: BLE001
        return CaptureResult(False, f"screenshot failed: {exc}")


def _default_content(url: str) -> CaptureResult:
    key = os.getenv("FIRECRAWL_API_KEY")
    if key:
        try:
            from firecrawl import Firecrawl

            doc = Firecrawl(api_key=key).scrape(url, formats=["markdown"], only_main_content=True)
            md = getattr(doc, "markdown", None) or (doc.get("markdown") if isinstance(doc, dict) else None)
            if md:
                return CaptureResult(True, "firecrawl markdown", text=md)
            return CaptureResult(False, "firecrawl returned no markdown")
        except Exception as exc:  # noqa: BLE001
            return CaptureResult(False, f"firecrawl failed: {exc}")
    # Fall back to raw HTML when no Firecrawl key is set.
    resp = probes.fetch(url)
    if resp is not None and resp.status_code == 200 and resp.text:
        return CaptureResult(True, "raw HTML (no Firecrawl key)", text=resp.text)
    return CaptureResult(False, "content not captured")


def _abs(base: str, href: str) -> str:
    if href.startswith("http"):
        return href
    return base.rstrip("/") + "/" + href.lstrip("/")


def _pdp_handle(purl: str) -> str | None:
    """The product handle in a URL, or None if it's a listing like `/products/`."""
    for marker in ("/products/", "/product/"):
        if marker in purl:
            seg = purl.split(marker, 1)[1].strip("/").split("?")[0].split("#")[0].split("/")[0]
            if seg and seg not in ("products", "product"):
                return seg
    return None


def _pick_pdp(catalog: CatalogResult, base: str) -> str | None:
    """The hero product page — the one the homepage features most. Skips the bare `/products/`
    index, and prefers a product whose slug is linked on the homepage (store-agnostic)."""
    candidates = []
    for p in catalog.products:
        handle = p.get("handle") or _pdp_handle(p.get("url", "") or "")
        purl = p.get("url") or (f"{base}/products/{p['handle']}" if p.get("handle") else None)
        if handle and purl:
            candidates.append((handle, _abs(base, purl)))
    if not candidates:
        return None

    home = probes.fetch_homepage(base)
    html = home.text or "" if home else ""
    low = html.lower()

    def score(handle: str, purl: str) -> int:
        s = 100 if purl.rstrip("/").rsplit("/", 1)[-1] in html else 0  # slug linked on homepage
        tokens = [t for t in handle.replace("_", "-").split("-") if len(t) > 2]
        return s + sum(low.count(t) for t in tokens)

    if low:
        candidates.sort(key=lambda c: score(c[0], c[1]), reverse=True)
    return candidates[0][1]


def representative_surfaces(url: str, profile: StoreProfile, catalog: CatalogResult) -> list[dict]:
    """A small, store-aware set of surfaces worth capturing for a CRO audit."""
    base = probes.base_url(url)
    surfaces = [{"type": "homepage", "url": base + "/"}]
    if catalog and catalog.products:
        pdp = _pick_pdp(catalog, base)
        if pdp:
            surfaces.append({"type": "pdp", "url": pdp})
    if catalog and catalog.collections:
        handle = catalog.collections[0].get("handle")
        if handle:
            surfaces.append({"type": "collection", "url": f"{base}/collections/{handle}"})
    surfaces.append({"type": "cart", "url": base + "/cart"})
    return surfaces


def crawl_storefront(
    url: str,
    *,
    bundle_root: Path | str | None = None,
    profile: StoreProfile | None = None,
    catalog: CatalogResult | None = None,
    surfaces: list[dict] | None = None,
    technical=None,
    screenshot_fn=None,
    content_fn=None,
    reach_fn=None,
) -> dict:
    """Crawl ``url`` and write a cached artifact bundle; return its manifest dict."""
    screenshot_fn = screenshot_fn or _default_screenshot
    content_fn = content_fn or _default_content
    reach_fn = reach_fn or probes.head_check

    profile = profile or fingerprint_store(url)
    catalog = catalog if catalog is not None else fetch_catalog(url, profile)
    surfaces = surfaces or representative_surfaces(url, profile, catalog)
    paths = BundlePaths(profile.slug, root=bundle_root or DEFAULT_BUNDLE_ROOT).ensure()

    reached, artifacts, not_captured = [], [], []
    for i, surface in enumerate(surfaces):
        surl = surface["url"]
        stype = surface["type"]

        reach = reach_fn(surl)
        reached.append(
            {"type": stype, "url": surl, "status": reach.status_code, "inspected": reach.inspected}
        )

        shot_path = paths.screenshots / f"{i:02d}-{stype}.png"
        shot = screenshot_fn(surl, shot_path)
        if shot.ok and shot_path.exists():
            artifacts.append(
                {"type": "screenshot", "surface": stype, "url": surl,
                 "path": str(shot_path.relative_to(paths.root))}
            )
        else:
            not_captured.append({"type": "screenshot", "surface": stype, "url": surl, "reason": shot.note})

        content = content_fn(surl)
        if content.ok and content.text:
            cpath = paths.content / f"{i:02d}-{stype}.md"
            cpath.write_text(content.text)
            artifacts.append(
                {"type": "content", "surface": stype, "url": surl,
                 "path": str(cpath.relative_to(paths.root))}
            )
        else:
            not_captured.append({"type": "content", "surface": stype, "url": surl, "reason": content.note})

    if technical is None:
        technical = core_checks.run_technical_checks(url)

    paths.profile.write_text(profile.model_dump_json(indent=2))
    paths.catalog.write_text(json.dumps(catalog.to_dict(), indent=2))
    paths.technical.write_text(
        json.dumps([r.model_dump(mode="json") for r in technical], indent=2)
    )

    manifest = {
        "store_url": probes.base_url(url),
        "slug": profile.slug,
        "platform": profile.platform,
        "catalog_branch": profile.catalog_branch,
        "catalog_source": catalog.source,
        "catalog_count": catalog.count,
        "reached_urls": reached,
        "artifacts": artifacts,
        "not_captured": not_captured,
        "counts": {
            "surfaces": len(surfaces),
            "artifacts": len(artifacts),
            "not_captured": len(not_captured),
        },
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2))
    return manifest
