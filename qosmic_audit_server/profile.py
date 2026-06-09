"""StoreProfile (fingerprint output) and BundlePaths (cached artifact layout) for one storefront."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, Field

# Default root for recorded artifact bundles read back by the eval/loop.
DEFAULT_BUNDLE_ROOT = Path("eval/fixtures/bundles")


def slug_for(url: str) -> str:
    """Return a stable, filesystem-safe slug from a store URL (e.g. https://www.gingerpeople.com -> gingerpeople)."""
    host = urlsplit(url if "://" in url else f"https://{url}").hostname or "store"
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(".")[0] or "store"


class StoreProfile(BaseModel):
    """Platform fingerprint + endpoint reachability for one storefront."""

    url: str
    slug: str
    platform: str            # shopify | woocommerce | wordpress | unknown
    is_shopify: bool
    catalog_branch: str      # products_json | sitemap | dom
    endpoints: dict          # {name: status_code | None}
    signals: dict            # {signal_name: bool}
    notes: list[str] = Field(default_factory=list)


class BundlePaths:
    """Filesystem layout for one store's cached artifact bundle."""

    def __init__(self, slug: str, root: Path | str = DEFAULT_BUNDLE_ROOT):
        self.slug = slug
        self.root = Path(root) / slug

    @property
    def manifest(self) -> Path:
        return self.root / "manifest.json"

    @property
    def profile(self) -> Path:
        return self.root / "profile.json"

    @property
    def catalog(self) -> Path:
        return self.root / "catalog.json"

    @property
    def technical(self) -> Path:
        return self.root / "technical.json"

    @property
    def screenshots(self) -> Path:
        return self.root / "screenshots"

    @property
    def content(self) -> Path:
        return self.root / "content"

    def ensure(self) -> BundlePaths:
        self.screenshots.mkdir(parents=True, exist_ok=True)
        self.content.mkdir(parents=True, exist_ok=True)
        return self
