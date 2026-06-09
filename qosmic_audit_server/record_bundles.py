"""Live bundle recorder: crawl both calibration stores into ``eval/fixtures/bundles/``.

Run via ``python -m qosmic_audit_server.record_bundles``. Makes live calls (Playwright +
Firecrawl + PSI), so it's never imported by the offline test tier. The eval/loop read these
cached bundles back offline.
"""

from __future__ import annotations

from dotenv import load_dotenv

from .tools.crawl import crawl_storefront

STORES = {
    "gingerpeople": "https://gingerpeople.com",
    "zenrojas": "https://zenrojas.com",
}


def main() -> None:
    load_dotenv()
    print("Recording artifact bundles into eval/fixtures/bundles/\n" + "=" * 48)
    for slug, url in STORES.items():
        print(f"\n[{slug}] crawling {url} ...")
        m = crawl_storefront(url)
        c = m["counts"]
        print(
            f"  branch={m['catalog_branch']} catalog={m['catalog_source']}/{m['catalog_count']} "
            f"surfaces={c['surfaces']} artifacts={c['artifacts']} not_captured={c['not_captured']}"
        )
        for nc in m["not_captured"]:
            print(f"    not captured: {nc['type']} {nc['surface']} — {nc['reason']}")


if __name__ == "__main__":
    main()
