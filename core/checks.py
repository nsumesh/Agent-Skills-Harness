"""Builds the 15-row technical-checks table from probes + PSI + homepage HTML. Never fakes a
Pass: anything we couldn't inspect is an honest Warn, and the 15 rows always come back in a
fixed order."""

from __future__ import annotations

import re

from . import probes, psi
from .schema import CheckStatus, TechCheckRow

Status = CheckStatus

# The 15 standard checks, in render order.
STANDARD_CHECKS = [
    "SSL Certificate",
    "HTTPS Redirect",
    "Sitemap",
    "Robots.txt",
    "Critical Pages Loading",
    "Meta Tags & Social Previews",
    "Structured Data",
    "Favicon",
    "Mobile-Friendly",
    "Page Speed Mobile",
    "Page Speed Desktop",
    "Broken Links",
    "Image Optimization",
    "Cookie/Privacy",
    "Checkout Reachable",
]


# --- tiny dependency-free HTML inspectors ------------------------------------

def _has(pattern: str, html: str) -> bool:
    return bool(re.search(pattern, html, re.I | re.S))


def _title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return m.group(1).strip() if m else None


# --- per-check derivations ----------------------------------------------------

def _from_probe(result: probes.ProbeResult, *, fail_detail: str | None = None) -> tuple[CheckStatus, str]:
    """Inspected+ok -> Pass; inspected+not-ok -> Fail; not inspected -> Warn."""
    if not result.inspected:
        return Status.warn, result.detail
    if result.ok:
        return Status.passed, result.detail
    return Status.fail, fail_detail or result.detail


def _sitemap_row(result: probes.ProbeResult) -> tuple[CheckStatus, str]:
    if not result.inspected:
        return Status.warn, result.detail
    if result.ok:
        return Status.passed, result.detail
    # A missing sitemap is a soft issue, not a hard failure.
    return Status.warn, result.detail


def _robots_row(result: probes.ProbeResult) -> tuple[CheckStatus, str]:
    if not result.inspected:
        return Status.warn, result.detail
    return (Status.passed, result.detail) if result.ok else (Status.warn, result.detail)


def _meta_row(html: str | None) -> tuple[CheckStatus, str]:
    if html is None:
        return Status.warn, "Homepage HTML not captured; meta tags not inspected."
    has_title = _title(html) is not None
    has_desc = _has(r'<meta[^>]+name=["\']description["\']', html)
    has_og = _has(r'<meta[^>]+property=["\']og:', html)
    if has_title and has_desc and has_og:
        return Status.passed, "Title, meta description, and Open Graph tags present."
    if has_title and has_desc:
        return Status.warn, "Title and description present; Open Graph/social tags missing."
    return Status.warn, "Title or meta description missing on the homepage."


def _structured_data_row(html: str | None) -> tuple[CheckStatus, str]:
    if html is None:
        return Status.warn, "Homepage HTML not captured; structured data not inspected."
    if _has(r'<script[^>]+type=["\']application/ld\+json["\']', html):
        return Status.passed, "JSON-LD structured data found on the homepage."
    return Status.warn, "No JSON-LD structured data found on the homepage."


def _mobile_row(html: str | None) -> tuple[CheckStatus, str]:
    if html is None:
        return Status.warn, "Homepage HTML not captured; viewport not inspected."
    if _has(r'<meta[^>]+name=["\']viewport["\']', html):
        return Status.passed, "Responsive viewport meta tag present."
    return Status.warn, "No responsive viewport meta tag found."


def _favicon_row(result: probes.ProbeResult) -> tuple[CheckStatus, str]:
    if not result.inspected:
        return Status.warn, result.detail
    if result.ok:
        return Status.passed, result.detail
    # A 404 at /favicon.ico is common (themes/Shopify define it in HTML) — soft, not a hard fail.
    return Status.warn, "No favicon at /favicon.ico (often theme-defined)."


def _psi_row(result: psi.PsiResult) -> tuple[CheckStatus, str]:
    if not result.inspected or result.score is None:
        return Status.warn, result.detail
    return (Status.passed if result.score >= 90 else Status.warn), result.detail


def _broken_links_row(cart: probes.ProbeResult, homepage: probes.ProbeResult) -> tuple[CheckStatus, str]:
    if cart.inspected and not cart.ok:
        return Status.fail, f"Broken link found: {cart.detail}"
    if homepage.inspected and cart.inspected:
        return Status.passed, "No broken links among the homepage and /cart checks."
    return Status.warn, "Only a sample of links was checked; no full crawl performed."


def _cookie_row(html: str | None) -> tuple[CheckStatus, str]:
    if html is None:
        return Status.warn, "Homepage HTML not captured; privacy/consent not inspected."
    if _has(r'href=["\'][^"\']*privacy', html) or _has(r">\s*privacy", html):
        return Status.warn, "Privacy policy link present; consent mechanics not inspected."
    return Status.warn, "Privacy/consent mechanics not inspected in this pass."


def _checkout_row(cart: probes.ProbeResult) -> tuple[CheckStatus, str]:
    if not cart.inspected:
        return Status.warn, "Checkout reachability not inspected."
    if cart.ok:
        return Status.passed, "/cart reachable (200)."
    return Status.fail, f"Checkout edge not reachable: {cart.detail}"


def run_technical_checks(url: str, *, enable_psi: bool = True) -> list[TechCheckRow]:
    """Run all checks for ``url`` and return exactly the 15 standard rows in order."""
    homepage = probes.fetch_homepage(url)
    html = homepage.text
    ssl = probes.check_ssl(url)
    redirect = probes.check_https_redirect(url)
    sitemap = probes.fetch_sitemap(url)
    robots = probes.fetch_robots(url)
    cart = probes.probe_cart(url)
    favicon = probes.probe_favicon(url)

    # Critical pages: homepage + cart.
    if not homepage.inspected:
        critical = (Status.warn, "Could not load the homepage to assess critical pages.")
    elif homepage.ok and cart.ok:
        critical = (Status.passed, "Homepage and /cart returned 200.")
    elif homepage.ok:
        critical = (Status.warn, f"Homepage loaded; {cart.detail}")
    else:
        critical = (Status.fail, f"Homepage returned HTTP {homepage.status_code}.")

    if enable_psi:
        psi_mobile = _psi_row(psi.run_psi(url, "mobile"))
        psi_desktop = _psi_row(psi.run_psi(url, "desktop"))
    else:
        psi_mobile = (Status.warn, "Mobile page speed not run in this pass.")
        psi_desktop = (Status.warn, "Desktop page speed not run in this pass.")

    rows_by_name: dict[str, tuple[CheckStatus, str]] = {
        "SSL Certificate": _from_probe(ssl),
        "HTTPS Redirect": _from_probe(redirect),
        "Sitemap": _sitemap_row(sitemap),
        "Robots.txt": _robots_row(robots),
        "Critical Pages Loading": critical,
        "Meta Tags & Social Previews": _meta_row(html),
        "Structured Data": _structured_data_row(html),
        "Favicon": _favicon_row(favicon),
        "Mobile-Friendly": _mobile_row(html),
        "Page Speed Mobile": psi_mobile,
        "Page Speed Desktop": psi_desktop,
        "Broken Links": _broken_links_row(cart, homepage),
        "Image Optimization": (Status.warn, "Byte-level image weight not measured in this pass."),
        "Cookie/Privacy": _cookie_row(html),
        "Checkout Reachable": _checkout_row(cart),
    }

    return [
        TechCheckRow(name=name, status=rows_by_name[name][0], detail=rows_by_name[name][1])
        for name in STANDARD_CHECKS
    ]
