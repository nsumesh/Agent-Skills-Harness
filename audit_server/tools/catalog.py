"""Fetch the product catalog via a products.json -> sitemap -> DOM waterfall. The result records which source succeeded so downstream reasoning knows how trustworthy the data is."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from core import probes

PAGE_LIMIT = 250
MAX_PAGES = 10  # safety cap; 2500 products is enough for an audit


@dataclass
class CatalogResult:
    source: str                      # products_json | sitemap | dom | none
    products: list[dict]
    collections: list[dict] = field(default_factory=list)
    count: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "count": self.count,
            "products": self.products,
            "collections": self.collections,
            "notes": self.notes,
        }


def _norm_product(p: dict, base: str) -> dict:
    handle = p.get("handle")
    url = p.get("url") or (f"{base}/products/{handle}" if handle else None)
    return {
        "title": p.get("title"),
        "handle": handle,
        "product_type": p.get("product_type"),
        "url": url,
    }


def _fetch_json_list(url: str, endpoint: str, key: str) -> list[dict]:
    items: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        resp = probes.fetch(probes.join(url, f"{endpoint}?limit={PAGE_LIMIT}&page={page}"))
        if resp is None or resp.status_code != 200:
            break
        try:
            batch = resp.json().get(key, [])
        except ValueError:
            break
        if not batch:
            break
        items.extend(batch)
        if len(batch) < PAGE_LIMIT:
            break
    return items


def _locs(xml: str) -> list[str]:
    return [m.strip() for m in re.findall(r"<loc>(.*?)</loc>", xml, re.I | re.S)]


def _products_from_sitemap(url: str) -> list[str]:
    sm = probes.fetch_sitemap(url)
    if not sm.ok or not sm.text:
        return []
    locs = _locs(sm.text)
    product_urls = [u for u in locs if "/products/" in u or "/product/" in u]
    if not product_urls and "<sitemapindex" in sm.text:
        # Follow product-related child sitemaps.
        for child in [u for u in locs if "product" in u.lower()]:
            resp = probes.fetch(child)
            if resp is not None and resp.status_code == 200:
                product_urls += [u for u in _locs(resp.text) if "/products/" in u or "/product/" in u]
    return product_urls


def _products_from_dom(url: str) -> list[str]:
    home = probes.fetch_homepage(url)
    if not home.text:
        return []
    hrefs = re.findall(r'href=["\']([^"\']*/products?/[^"\']+)["\']', home.text, re.I)
    seen, out = set(), []
    for h in hrefs:
        h = h.split("?")[0]
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def fetch_catalog(url: str, profile=None) -> CatalogResult:
    base = probes.base_url(url)
    notes: list[str] = []

    products = _fetch_json_list(url, "products.json", "products")
    if products:
        collections = _fetch_json_list(url, "collections.json", "collections")
        return CatalogResult(
            "products_json",
            [_norm_product(p, base) for p in products],
            [{"title": c.get("title"), "handle": c.get("handle")} for c in collections],
            len(products),
            notes,
        )

    notes.append("products.json empty/unavailable; trying sitemap.")
    sitemap_urls = _products_from_sitemap(url)
    if sitemap_urls:
        return CatalogResult("sitemap", [{"url": u} for u in sitemap_urls], [], len(sitemap_urls), notes)

    notes.append("sitemap had no product URLs; trying DOM.")
    dom_urls = _products_from_dom(url)
    if dom_urls:
        return CatalogResult("dom", [{"url": u} for u in dom_urls], [], len(dom_urls), notes)

    notes.append("No catalog discovered by any method.")
    return CatalogResult("none", [], [], 0, notes)
