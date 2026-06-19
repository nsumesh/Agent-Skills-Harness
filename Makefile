# The single source of "how to run a gate."
# PYTHON defaults to whatever python3 is on PATH; override with `make PYTHON=.venv/bin/python`.
PYTHON ?= python3
PYTEST  = $(PYTHON) -m pytest

.PHONY: install lint test eval loop cov clean

install:  ## Editable install with deps; install the crawl browser.
	$(PYTHON) -m pip install -e ".[dev,agent,crawl]"
	$(PYTHON) -m playwright install chromium

lint:  ## Static checks.
	$(PYTHON) -m ruff check core eval audit_server

test:  ## Offline test gate (this is CI): the eval system's full suite.
	$(PYTEST)

eval:  ## Run the eval suite (deterministic + judge + calibration + redteam + loop).
	$(PYTEST) eval

loop:  ## Self-improving loop demo (deterministic per decision 2; drop --fake-writer for the real Anthropic writer / scale path).
	$(PYTHON) -m eval.loop.run_loop --train gingerpeople --holdout zenrojas --fake-writer

cov:  ## Test suite + coverage report.
	$(PYTEST) --cov --cov-report=term-missing

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage .coverage.*
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
