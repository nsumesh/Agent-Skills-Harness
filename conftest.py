"""Root pytest config: marker gating + shared fixtures.

The backbone that keeps every phase gate deterministic. Live/LLM tests are skipped unless
explicitly opted into (``--run-live`` / ``--run-llm``), and the default ``addopts`` marker
expression already deselects them — belt and suspenders.

Fixtures here are imported lazily where they depend on optional packages (e.g. ``respx``)
so the offline tier never imports something that isn't installed.
"""

from __future__ import annotations

import copy
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

import pytest

from core.schema import AuditReport

ROOT = Path(__file__).parent
FIXTURES = ROOT / "tests" / "fixtures"


def pytest_addoption(parser):
    parser.addoption("--run-live", action="store_true", default=False, help="run live-marked tests")
    parser.addoption("--run-llm", action="store_true", default=False, help="run llm-marked tests")


def pytest_collection_modifyitems(config, items):
    run_live = config.getoption("--run-live")
    run_llm = config.getoption("--run-llm")
    skip_live = pytest.mark.skip(reason="needs --run-live")
    skip_llm = pytest.mark.skip(reason="needs --run-llm")
    for item in items:
        if "live" in item.keywords and not run_live:
            item.add_marker(skip_live)
        if "llm" in item.keywords and not run_llm:
            item.add_marker(skip_llm)


@pytest.fixture
def golden_data() -> dict:
    """The hand-authored valid report as a plain dict (fresh copy per test)."""
    return json.loads((FIXTURES / "golden_report.json").read_text())


@pytest.fixture
def golden_report(golden_data) -> AuditReport:
    """The hand-authored valid report, validated into an AuditReport."""
    return AuditReport.model_validate(golden_data)


@pytest.fixture
def broken_report(golden_data) -> Callable[[Callable[[dict], None]], dict]:
    """Factory: deep-copy the golden dict, apply a mutation, return the (now-invalid) dict.

    Usage::

        def test_x(broken_report):
            data = broken_report(lambda d: d["experiments"].pop())
    """

    def _make(mutate: Callable[[dict], None]) -> dict:
        data = copy.deepcopy(golden_data)
        mutate(data)
        return data

    return _make


@pytest.fixture
def cached_bundle():
    """Placeholder for the offline cached artifact bundle (populated in Phase 2)."""
    bundle = FIXTURES / "bundles"
    if not bundle.exists():
        pytest.skip("cached bundle fixtures not recorded yet (Phase 2)")
    return bundle


@pytest.fixture
def fake_anthropic():
    """Placeholder for the canned Anthropic client (implemented in Phase 5)."""
    pytest.skip("FakeAnthropic not implemented yet (Phase 5)")


@pytest.fixture
def http_fixtures():
    """Factory yielding a respx context that replays a store's recorded HTTP fixtures.

    Usage::

        def test_x(http_fixtures):
            with http_fixtures("zenrojas") as (manifest, router):
                ... call code that makes httpx requests ...

    Routes are matched by exact URL; anything not recorded falls through to a 404, so a
    probe hitting an un-captured path degrades honestly rather than erroring.
    """
    import httpx
    import respx

    base_dir = FIXTURES / "http"

    @contextmanager
    def _load(slug: str):
        store_dir = base_dir / slug
        manifest = json.loads((store_dir / "manifest.json").read_text())
        with respx.mock(assert_all_called=False) as router:
            for route in manifest["routes"]:
                url = route.get("url") or manifest["base"].rstrip("/") + route["path"]
                headers = {"content-type": route.get("content_type", "text/html")}
                headers.update({k.lower(): v for k, v in route.get("headers", {}).items()})
                body = route.get("body")
                content = (store_dir / body).read_bytes() if body else b""
                router.route(method=route.get("method", "GET"), url=url).mock(
                    return_value=httpx.Response(route["status"], headers=headers, content=content)
                )
            # Catch-all: un-recorded requests 404 instead of raising.
            router.route().mock(return_value=httpx.Response(404, content=b"not recorded"))
            yield manifest, router

    return _load
