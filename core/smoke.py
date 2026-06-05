"""Live smoke recorder: capture real responses from the two stores into HTTP fixtures.

Run via ``make smoke`` (or ``python -m core.smoke``). Hits the real stores, prints the
"curl-block" facts the live tier asserts, and writes ``tests/fixtures/http/<slug>/`` (a
manifest + body files) that the offline tier replays with respx. Refreshing the fixtures
is exactly re-running this. This module makes live network calls and is never imported by
the offline test tier.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from . import probes

STORES = {
    "gingerpeople": "https://gingerpeople.com",
    "zenrojas": "https://zenrojas.com",
}

# (path, body-filename) pairs to capture per store. The http:// homepage is captured
# separately to record the redirect.
ENDPOINTS = [
    ("/", "home.html"),
    ("/cart", "cart.html"),
    ("/robots.txt", "robots.txt"),
    ("/sitemap.xml", "sitemap.xml"),
    ("/favicon.ico", "favicon.ico"),
    ("/products.json", "products.json"),
]

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "http"


def _record_route(out_dir: Path, url: str, body_name: str | None, *, follow: bool) -> dict:
    resp = probes.fetch(url, follow_redirects=follow)
    if resp is None:
        return {"url": url, "status": 0, "content_type": "", "error": "no response"}
    route = {
        "url": str(httpx.URL(url)),
        "status": resp.status_code,
        "content_type": resp.headers.get("content-type", ""),
    }
    if not follow and "location" in resp.headers:
        route["headers"] = {"location": resp.headers["location"]}
    if body_name and resp.content:
        (out_dir / body_name).write_bytes(resp.content)
        route["body"] = body_name
    return route


def record_store(slug: str, base: str) -> dict:
    out_dir = FIXTURE_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    routes = []
    # http:// homepage first, to capture the HTTPS redirect.
    routes.append(_record_route(out_dir, probes._with_scheme(base, "http"), None, follow=False))
    for path, body in ENDPOINTS:
        routes.append(_record_route(out_dir, probes.join(base, path) if path != "/" else base + "/", body, follow=True))
    manifest = {"base": base, "routes": routes}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    print("Recording live HTTP fixtures + curl-block facts\n" + "=" * 48)
    for slug, base in STORES.items():
        manifest = record_store(slug, base)
        by_url = {r["url"].rstrip("/"): r for r in manifest["routes"]}
        cart = by_url.get(base + "/cart", {})
        print(f"\n[{slug}] {base}")
        for r in manifest["routes"]:
            print(f"  {r['status']:>3}  {r['url']}")
        print(f"  => /cart status: {cart.get('status')}  "
              f"(expect non-200 for gingerpeople, 200 for zenrojas)")
    print(f"\nWrote fixtures under {FIXTURE_ROOT}")


if __name__ == "__main__":
    main()
