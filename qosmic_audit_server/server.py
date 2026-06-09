"""FastMCP entrypoint: wraps each tools/ function as an MCP tool returning a JSON-serializable dict."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import catalog as catalog_tool
from .tools import crawl as crawl_tool
from .tools import fingerprint as fingerprint_tool
from .tools import score as score_tool
from .tools import technical as technical_tool

mcp = FastMCP("qosmic-audit")


@mcp.tool()
def fingerprint_store(url: str) -> dict:
    """Probe a storefront's platform + endpoint reachability and pick a catalog branch."""
    return fingerprint_tool.fingerprint_store(url).model_dump()


@mcp.tool()
def fetch_catalog(url: str) -> dict:
    """Discover the product catalog via the products.json -> sitemap -> DOM waterfall."""
    return catalog_tool.fetch_catalog(url).to_dict()


@mcp.tool()
def run_technical_checks(url: str) -> dict:
    """Run the 15 standard technical checks; unverifiable items honestly Warn."""
    rows = technical_tool.run_technical_checks(url)
    return {"checks": [r.model_dump(mode="json") for r in rows]}


@mcp.tool()
def crawl_storefront(url: str) -> dict:
    """Capture representative surfaces into a cached artifact bundle; return its manifest."""
    return crawl_tool.crawl_storefront(url)


@mcp.tool()
def score_report(report_json: dict, store_slug: str) -> dict:
    """Score an audit report against a store's cached bundle (deterministic eval)."""
    return score_tool.score_report(report_json, store_slug)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
