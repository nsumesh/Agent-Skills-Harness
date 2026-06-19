"""Crawl the calibration stores and write their artifact bundles to eval/fixtures/bundles/. Makes live network calls; never imported by offline tests."""

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
