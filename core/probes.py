"""HTTP probes with a browser-like User-Agent, retries, and honest typed results.

Every probe returns a :class:`ProbeResult` that distinguishes three outcomes:
  - ``inspected=True, ok=True``  — we checked and it passed
  - ``inspected=True, ok=False`` — we checked and it failed (a real finding)
  - ``inspected=False``          — we could not reach a verdict (network/TLS error)

That third state is the whole point: ``checks.py`` maps "not inspected" to an honest
**Warn**, never a fake **Pass**. A probe never invents a result it didn't observe.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

import httpx

# A real desktop Chrome UA — some storefronts vary behaviour for default httpx UAs.
DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 10.0
_REDIRECT_CODES = {301, 302, 303, 307, 308}


@dataclass
class ProbeResult:
    name: str
    inspected: bool
    ok: bool
    detail: str
    status_code: int | None = None
    url: str | None = None
    text: str | None = None
    content_type: str | None = None


# --- url helpers -------------------------------------------------------------

def base_url(url: str) -> str:
    """Scheme + host (+ port), no path/query. Defaults missing scheme to https."""
    parts = urlsplit(url if "://" in url else f"https://{url}")
    scheme = parts.scheme or "https"
    return urlunsplit((scheme, parts.netloc, "", "", ""))


def _with_scheme(url: str, scheme: str) -> str:
    parts = urlsplit(url if "://" in url else f"https://{url}")
    return urlunsplit((scheme, parts.netloc, parts.path, parts.query, ""))


def join(url: str, path: str) -> str:
    return base_url(url).rstrip("/") + "/" + path.lstrip("/")


# --- core fetch --------------------------------------------------------------

def fetch(
    url: str,
    *,
    method: str = "GET",
    retries: int = 2,
    backoff: float = 0.4,
    timeout: float = DEFAULT_TIMEOUT,
    follow_redirects: bool = True,
    headers: dict | None = None,
) -> httpx.Response | None:
    """Fetch with retries/backoff. Returns the response, or ``None`` if it never completed."""
    hdrs = {"User-Agent": DEFAULT_UA, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    for attempt in range(retries + 1):
        try:
            with httpx.Client(
                headers=hdrs, follow_redirects=follow_redirects, timeout=timeout
            ) as client:
                return client.request(method, url)
        except httpx.HTTPError:
            if attempt < retries and backoff:
                time.sleep(backoff * (2**attempt))
    return None


# --- probes ------------------------------------------------------------------

def check_ssl(url: str) -> ProbeResult:
    """A completed HTTPS request means the TLS handshake (and cert verification) succeeded."""
    https = _with_scheme(base_url(url), "https")
    resp = fetch(https)
    if resp is None:
        return ProbeResult("SSL", False, False, "HTTPS request did not complete (TLS or network error).", url=https)
    detail = (
        "HTTPS storefront loaded successfully."
        if resp.status_code < 400
        else f"TLS handshake succeeded (HTTP {resp.status_code})."
    )
    return ProbeResult("SSL", True, True, detail, status_code=resp.status_code, url=https)


def check_https_redirect(url: str) -> ProbeResult:
    """http:// should 30x-redirect to https://, or the site should already be HTTPS-only."""
    http = _with_scheme(base_url(url), "http")
    resp = fetch(http, follow_redirects=False)
    if resp is None:
        return ProbeResult("HTTPS Redirect", False, False, "Could not inspect the HTTP-to-HTTPS redirect.", url=http)
    location = resp.headers.get("location", "")
    if resp.status_code in _REDIRECT_CODES and location.startswith("https://"):
        return ProbeResult(
            "HTTPS Redirect", True, True,
            f"http:// {resp.status_code}-redirected to HTTPS.", status_code=resp.status_code, url=http,
        )
    if resp.status_code < 400 and str(resp.url).startswith("https://"):
        return ProbeResult("HTTPS Redirect", True, True, "Request resolved over HTTPS.", status_code=resp.status_code, url=http)
    return ProbeResult(
        "HTTPS Redirect", True, False,
        f"http:// returned {resp.status_code} with no HTTPS redirect.", status_code=resp.status_code, url=http,
    )


def fetch_robots(url: str) -> ProbeResult:
    target = join(url, "robots.txt")
    resp = fetch(target)
    if resp is None:
        return ProbeResult("Robots.txt", False, False, "Could not fetch robots.txt.", url=target)
    if resp.status_code == 200 and resp.text.strip():
        return ProbeResult("Robots.txt", True, True, "robots.txt present.", status_code=200, url=target, text=resp.text)
    return ProbeResult("Robots.txt", True, False, f"robots.txt returned HTTP {resp.status_code}.", status_code=resp.status_code, url=target)


def fetch_sitemap(url: str) -> ProbeResult:
    target = join(url, "sitemap.xml")
    resp = fetch(target)
    if resp is None:
        return ProbeResult("Sitemap", False, False, "Could not fetch sitemap.xml.", url=target)
    body = resp.text if resp.status_code == 200 else ""
    if resp.status_code == 200 and ("<urlset" in body or "<sitemapindex" in body):
        return ProbeResult("Sitemap", True, True, "sitemap.xml present and well-formed.", status_code=200, url=target, text=body)
    return ProbeResult("Sitemap", True, False, f"sitemap.xml returned HTTP {resp.status_code}.", status_code=resp.status_code, url=target)


def probe_cart(url: str) -> ProbeResult:
    target = join(url, "cart")
    resp = fetch(target)
    if resp is None:
        return ProbeResult("Cart", False, False, "Could not reach the /cart URL.", url=target)
    ok = resp.status_code == 200
    detail = "/cart returned 200." if ok else f"/cart returned HTTP {resp.status_code}."
    return ProbeResult("Cart", True, ok, detail, status_code=resp.status_code, url=target)


def probe_favicon(url: str) -> ProbeResult:
    target = join(url, "favicon.ico")
    resp = fetch(target)
    if resp is None:
        return ProbeResult("Favicon", False, False, "Could not fetch favicon.", url=target)
    ctype = resp.headers.get("content-type", "")
    ok = resp.status_code == 200 and (ctype.startswith("image") or bool(resp.content))
    detail = "Favicon served." if ok else f"favicon.ico returned HTTP {resp.status_code}."
    return ProbeResult("Favicon", True, ok, detail, status_code=resp.status_code, url=target, content_type=ctype)


def head_check(url: str) -> ProbeResult:
    """Generic reachability probe: HEAD, falling back to GET when HEAD isn't allowed."""
    resp = fetch(url, method="HEAD")
    if resp is not None and resp.status_code == 405:
        resp = fetch(url, method="GET")
    if resp is None:
        return ProbeResult("Reachable", False, False, "URL did not respond.", url=url)
    ok = resp.status_code < 400
    return ProbeResult("Reachable", True, ok, f"HTTP {resp.status_code}.", status_code=resp.status_code, url=url,
                       content_type=resp.headers.get("content-type"))


def fetch_homepage(url: str) -> ProbeResult:
    """Fetch the storefront homepage HTML (used by the HTML-inspecting checks)."""
    target = base_url(url)
    resp = fetch(target)
    if resp is None:
        return ProbeResult("Homepage", False, False, "Homepage did not respond.", url=target)
    ok = resp.status_code == 200
    return ProbeResult(
        "Homepage", True, ok,
        f"Homepage returned HTTP {resp.status_code}.",
        status_code=resp.status_code, url=str(resp.url),
        text=resp.text if ok else None, content_type=resp.headers.get("content-type"),
    )
