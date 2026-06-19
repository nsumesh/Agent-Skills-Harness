"""Probe a store's platform signals and endpoint reachability to build a StoreProfile. The catalog branch is chosen based on what actually responds, not assumed."""

from __future__ import annotations

from core import probes

from ..profile import StoreProfile, slug_for


def _products_json_ok(url: str) -> tuple[bool, int | None]:
    resp = probes.fetch(probes.join(url, "products.json"))
    if resp is None:
        return False, None
    if resp.status_code != 200:
        return False, resp.status_code
    try:
        data = resp.json()
    except ValueError:
        return False, resp.status_code
    return isinstance(data, dict) and isinstance(data.get("products"), list), resp.status_code


def fingerprint_store(url: str) -> StoreProfile:
    home = probes.fetch_homepage(url)
    html = (home.text or "").lower()
    products_ok, products_status = _products_json_ok(url)
    cart = probes.probe_cart(url)
    sitemap = probes.fetch_sitemap(url)
    robots = probes.fetch_robots(url)

    signals = {
        "shopify_cdn": "cdn.shopify" in html,
        "myshopify": "myshopify" in html,
        "shopify_theme": "shopify.theme" in html,
        "wp_content": "wp-content" in html,
        "wp_json": "wp-json" in html,
        "woocommerce": "woocommerce" in html,
        "products_json": products_ok,
    }

    is_shopify = products_ok or signals["shopify_cdn"] or signals["myshopify"]
    if is_shopify:
        platform = "shopify"
    elif signals["woocommerce"]:
        platform = "woocommerce"
    elif signals["wp_content"] or signals["wp_json"]:
        platform = "wordpress"
    else:
        platform = "unknown"

    if products_ok:
        branch = "products_json"
    elif sitemap.ok:
        branch = "sitemap"
    else:
        branch = "dom"

    notes: list[str] = []
    if not products_ok:
        notes.append(f"products.json unusable (HTTP {products_status}); using '{branch}' fallback.")
    if cart.inspected and not cart.ok:
        notes.append(f"/cart returned HTTP {cart.status_code} (retailer-routed or non-transacting).")

    endpoints = {
        "homepage": home.status_code,
        "products.json": products_status,
        "cart": cart.status_code,
        "sitemap.xml": sitemap.status_code,
        "robots.txt": robots.status_code,
    }
    return StoreProfile(
        url=probes.base_url(url),
        slug=slug_for(url),
        platform=platform,
        is_shopify=is_shopify,
        catalog_branch=branch,
        endpoints=endpoints,
        signals=signals,
        notes=notes,
    )
