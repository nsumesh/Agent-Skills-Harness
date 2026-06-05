# The single source of "how to run a gate." Each phase gate maps to one target.
# PYTHON defaults to whatever python3 is on PATH; override with `make PYTHON=.venv/bin/python`.
PYTHON ?= python3
PYTEST  = $(PYTHON) -m pytest

.PHONY: install lint test test-live test-llm smoke eval loop cov clean

install:  ## Editable install with dev deps; install the crawl browser.
	$(PYTHON) -m pip install -e ".[dev,agent,crawl]"
	$(PYTHON) -m playwright install chromium

lint:  ## Static checks.
	$(PYTHON) -m ruff check core eval mcp tests

test:  ## OFFLINE gate (this is CI): no live network, no paid APIs, no browser.
	$(PYTEST) -m "not live and not llm"

test-live:  ## Opt-in: hit real stores / PSI / Firecrawl / Playwright.
	$(PYTEST) -m live --run-live

test-llm:  ## Opt-in: real Anthropic judge/writer round-trips.
	$(PYTEST) -m llm --run-llm

smoke:  ## Live curl-block helper; records tests/fixtures/http/ (Phase 1).
	$(PYTHON) -m core.smoke

eval:  ## Score both sample outputs + run the eval/* suite (Phases 4-6).
	$(PYTEST) eval -m "not live and not llm"

loop:  ## Run the self-improving loop demo (Phase 7).
	$(PYTHON) -m eval.loop.run_loop --train gingerpeople --holdout zenrojas

cov:  ## Offline suite + coverage report (floor enforced from Phase 4 onward).
	$(PYTEST) -m "not live and not llm" --cov --cov-report=term-missing

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage .coverage.*
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
