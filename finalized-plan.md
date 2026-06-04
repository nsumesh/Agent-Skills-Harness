# Qosmic CRO Audit Harness — File-by-File Implementation Plan (test-gated)

## Context

This is a founding-engineer take-home for **Qosmic**. The deliverable is a **runtime harness** that turns any coding agent (Claude Code / Codex) into a CRO (conversion-rate-optimization) audit agent: input = a single Shopify storefront URL, output = ONE structured audit report. Around it sits an **eval system** and a **self-improving eval loop** — and the loop is the headline graded signal ("a sharp self-improving eval on a thin harness beats a beautiful harness with static evals").

The working directory already contains three provided docs: `README.md` (the brief), `target_report.md` (the production-quality calibration bar for `gingerpeople.com`), and `build-plan.md` (the 8-phase plan I was handed). No code exists yet — this is greenfield.

Two test stores straddle the Shopify/not-Shopify boundary on purpose:
- **gingerpeople.com** — calibration target; `target_report.md` is the bar. NOT a clean Shopify store (`/cart` 404s, `/products.json` likely fails, retailer-routed, large catalog, strong content moat).
- **zenrojas.com** — generalization/unseen target. Clean transacting Shopify (`/products.json` works), small founder-led tea brand. The harness must produce a good audit here **without store-specific shortcuts**.

**Intended outcome:** a harness that runs end-to-end on both stores producing reports at the `target_report.md` bar, plus an eval that scores any report for any store and a loop that measurably improves the report-writer prompt on a **held-out** store without regressing the trained one — with a **comprehensive automated test gate after every phase**.

### Non-negotiable principles (hard rules baked into the design)
- **NEVER fabricate.** Any claim not tied to a captured artifact is dropped. Any unverifiable check degrades to an honest **Warn** ("not inspected"), never a fake **Pass**. A report that green-checks everything is worse than one that honestly warns.
- **Cite everything.** Every experiment cites a captured artifact path or a reachable URL. New/proposed surfaces cite an *existing* artifact as the "pattern to mirror."
- **Fingerprint, don't assume.** Probe platform + endpoint reachability before branching; don't assume Shopify conventions hold.
- **Fallback chains everywhere.** No single point of failure on an unknown store.
- **Determinism where possible.** Simplest mechanism that fully answers the question; no network hop behind a one-line HTTP probe or schema check.
- **Generalize, don't overfit.** Optimize against a held-out split.
- **Measured reliability.** The eval reports its own judge-vs-human agreement %, not an assertion of quality.
- **Test-gated.** No phase is "done" until its automated gate is green. Every bug found becomes a permanent test.

### Locked decisions (from clarifying Q&A)
1. **Eval/loop tooling = hand-rolled, runs clean.** Judge = direct Anthropic-API calls with explicit rubric prompts; optimizer = custom propose→evaluate→gate loop. DeepEval (G-Eval), DSPy+GEPA, promptfoo, Braintrust/Langfuse are named as the documented **scale path** only — not real dependencies.
2. **Loop mechanism = offline writer over cached artifacts.** Crawl each store ONCE, cache the artifact bundle to disk. The loop optimizes the report-writer prompt against the eval, regenerating reports from the cached bundle each iteration — no live re-crawl, deterministic and fast.
3. **Integration = thin MCP wrapper over an importable Python core.** All retry/crawl/check/scoring logic lives in importable `core/`; a thin FastMCP server wraps it for the agent. The eval imports `core/` directly (no network hop). The MCP-vs-scripts call is the explicit "reversible decision" for the Loom.
4. **All four runtime resources available:** Anthropic API key, PageSpeed Insights key, live Playwright crawl, Firecrawl API key. Nothing degrades to a stub for *capability* reasons — only for honest per-store verification failures.

### Repo-root decision (made, not asked)
Build the deliverable at the existing directory root. Preserve `target_report.md` in place (calibration references it). Move the two provided spec docs out of the deliverable's way:
- provided `README.md` (the brief) → `docs/BRIEF.md`
- `build-plan.md` → `docs/build-plan.md`

This frees `README.md` for the harness's own positioning doc. `git init` happens in Phase 0 (currently not a git repo).

---

## Architecture (three layers, kept separate)

```
Agent (Claude Code/Codex) ── reads ──▶ Layer 1: Skill (SKILL.md + references/)
        │ calls MCP tools
        ▼
Layer 2: thin FastMCP server (mcp/qosmic_audit_server/)  ──wraps──▶ Layer 3: core/ (importable)
        │                                                              │
        └──────────────── eval/ imports core/ directly ───────────────┘  (no network hop)
```

Reasoning + writing happen in the **agent**, driven by the Skill, calling MCP tools. The same `core/` logic is reused by the eval and the loop by direct import.

---

## Testing strategy (the spine of this rewrite)

Three test tiers, kept strictly separate so the gate after every phase is **deterministic, fast, free, and offline** — while still proving the live path works.

1. **Offline unit/integration tests (`pytest -m "not live and not llm"`)** — the CI gate. NO live network, NO paid APIs, NO browser. All external I/O is mocked:
   - **HTTP** mocked with `respx` (httpx transport) against **recorded response fixtures** (real homepage HTML, `/cart` responses, `robots.txt`, `products.json`, PSI JSON) captured once from the two stores and committed under `tests/fixtures/http/`.
   - **Playwright + Firecrawl** stubbed by a fake crawler that reads the recorded HTML and writes a manifest — so crawl logic is tested without a browser.
   - **Anthropic** replaced by a `FakeAnthropic` client returning canned, schema-valid JSON — so judge/writer/optimizer logic is tested deterministically.
   These run in <30s, gate every phase, and run in GitHub Actions on every push.

2. **Live smoke tests (`pytest -m live`)** — opt-in (`--run-live`), hit the real stores / PSI / Firecrawl / Playwright. Used at the HUMAN CHECKPOINTS to assert real-world facts (e.g. `/cart` is a 404 on gingerpeople, 200 on zenrojas) and to **record/refresh the fixtures** the offline tier replays. Not in CI (flaky, paid, rate-limited).

3. **LLM tests (`pytest -m llm`)** — opt-in, exercise the real Anthropic judge/writer on a tiny input to confirm prompt+parse round-trips. Separate from `live` because it costs tokens but not network-to-stores.

Cross-cutting conventions:
- **Golden fixtures** make the eval/loop fully offline: `tests/fixtures/golden_report.json` (a valid `AuditReport`), `tests/fixtures/bundles/{gingerpeople,zenrojas}/` (tiny cached artifact bundles). The real, larger bundles live in `eval/fixtures/bundles/` once Phase 2 records them.
- **Regression discipline:** every bug becomes a permanent case (unit regression test and/or a line in `eval/redteam/regression_corpus.jsonl`). The gate only ever grows.
- **Coverage floor:** `core/` and `eval/` keep ≥85% line coverage (`pytest --cov`, enforced in CI). Coverage is a guardrail, not the goal.
- **One command per gate.** Each phase gate is a single `make` target (thin wrappers over `pytest -m ...`), so "is the phase done?" has a yes/no answer.

---

## File-by-file plan

### Top-level / config

| File | What it does · how it's built · what it supports |
|---|---|
| `README.md` | Deliverable positioning doc: **"any storefront, Shopify-optimized."** Install, set keys, run the harness on a URL, run the eval, run the loop demo, **run the tests**. Built last (Phase 8). |
| `pyproject.toml` | Single dependency manifest (Python 3.11+). Runtime deps: `pydantic>=2`, `httpx`, `playwright`, `firecrawl-py`, `anthropic`, `mcp`/`fastmcp`, `jinja2`, `python-dotenv`. Dev/test deps: `pytest`, `pytest-cov`, `respx`, `ruff`. Console scripts: `qosmic-audit`, `qosmic-eval`, `qosmic-loop`. `[tool.pytest.ini_options]` registers markers `live`, `llm` and default `-m "not live and not llm"`. |
| `Makefile` | The single source of "how to run a gate." Targets: `make install`, `make test` (offline CI gate), `make test-live`, `make test-llm`, `make smoke` (live curl-block helper), `make eval`, `make loop`, `make cov`, `make lint`. Each phase gate below maps to one target. |
| `conftest.py` (root) | Adds the `--run-live` / `--run-llm` options, skips `live`/`llm` marked tests unless enabled, and exposes shared fixtures: `golden_report`, `broken_report` (factory that mutates one field), `cached_bundle`, `fake_anthropic`, `respx_http` (loads recorded fixtures). The backbone that keeps every gate deterministic. |
| `.env.example` | Documents the four keys: `ANTHROPIC_API_KEY`, `PSI_API_KEY`, `FIRECRAWL_API_KEY`. Loaded via `python-dotenv`. |
| `.gitignore` | Ignore `.env`, `__pycache__`, `.pytest_cache`, `htmlcov/`, `eval/loop/runs/*` (keep one sample), Playwright cache. |
| `.github/workflows/ci.yml` | Runs `make lint` + `make test` (offline tier only) on every push/PR. Green CI = the cumulative phase gates still hold. Names Braintrust/Langfuse as the managed scale path for hosted eval runs. |
| `CLAUDE.md` / `AGENTS.md` | Entry-point context files (Claude Code / Codex). Point the agent at `skills/storefront-audit/SKILL.md`, state the four hard rules, name the MCP tools. Built Phase 3. |
| `docs/BRIEF.md`, `docs/build-plan.md` | The provided spec docs (moved). Reference only. |
| `target_report.md` | **Unchanged, stays at root.** Calibration anchor / known-good. |

### Layer 3 — `core/` (pure, importable, reproducible)

| File | What it does · key functions · what it supports |
|---|---|
| `core/schema.py` | **The output contract.** `Pillar` enum; `Experiment` (the **11 fields**); `CompetitorRow`; `TechCheckRow` (`name`, `status: Pass\|Warn\|Fail`, `detail`); `AuditReport` (exec summary, exactly-10 experiments, competitors, ~15 tech checks). Validators: pillar-in-enum; `decision_rule` matches `^Ship if .+ without hurting .+$`; `expected_lift` parses as a range; `confidence` parses as %. `export_json_schema()`. |
| `core/render.py` | **Deterministic renderer.** `to_markdown(report)` / `to_html(report)` (Jinja2) producing the exact four-section layout matching `target_report.md`. Pure, no network. |
| `core/probes.py` | **HTTP probes, browser-like UA.** `check_ssl`, `check_https_redirect`, `fetch_robots`, `fetch_sitemap`, `probe_cart`, `probe_favicon`, `head_check`. Retries/backoff. Each returns a typed result + honest failure. |
| `core/psi.py` | **PageSpeed Insights v5 client.** `run_psi(url, strategy)` with retry/backoff; local Lighthouse fallback; honest Warn if both unavailable. |
| `core/checks.py` | **Assembles the ~15-row table.** `run_technical_checks(url)`. Every check degrades to honest Warn on failure; never fakes a Pass. |
| `core/eval_api.py` | **The single public eval entrypoint** — `score_report(report, bundle_dir) -> ScoreReport`. Imported by both the MCP tool AND the loop. Cheapest-first cascade (deterministic → judge). |

### Layer 2 — `mcp/qosmic_audit_server/` (thin FastMCP wrapper)

| File | Responsibility |
|---|---|
| `server.py` | FastMCP entrypoint; registers the tools. |
| `tools/fingerprint.py` | `fingerprint_store(url) -> StoreProfile` — platform signals AND endpoint reachability; picks the crawl branch. |
| `tools/catalog.py` | `fetch_catalog(url)` — waterfall: `/products.json` + `/collections.json` (paginate, cap 250/page) → sitemap → DOM. |
| `tools/crawl.py` | `crawl_storefront(url)` — representative surfaces; Playwright screenshots + Firecrawl content; artifact manifest with honest "not captured" entries + reached-URL list. |
| `tools/technical.py` | `run_technical_checks(url)` — thin wrapper over `core/checks.py`. |
| `tools/score.py` | `score_report(report_json, store_slug) -> dict` — thin wrapper over `core.eval_api.score_report`; loads the cached bundle. |
| `profile.py` | `StoreProfile` model + bundle path conventions. |

### Layer 1 — `skills/storefront-audit/` (the portable playbook)

| File | Responsibility |
|---|---|
| `SKILL.md` | Orchestration playbook: `fingerprint → crawl → checks` → pillar-sharded reasoning (≥1 grounded experiment/pillar) → supervisor prunes to a balanced 10 → **pre-write critic** → writer emits schema-valid JSON → render. Critic verifies every evidence path resolves AND the surface exists on THIS store; enforces two-part hypothesis + mandatory guardrail; rejects + loops. |
| `references/schema.md` | Human-readable spec of the 11 fields + 4 sections + enum. |
| `references/pillars.md` | Experiment archetypes that ADAPT to store type + catalog scale. **zenrojas must NOT get "fix retailer handoff" or "reorganize large catalog."** |
| `references/report-template.md` | Prose/tone template mirroring `target_report.md`. |

### Eval system — `eval/` + `core/eval_api.py` (the 60% + the headline)

| File | Responsibility |
|---|---|
| `eval/config.py` | `WEIGHTS` (determ 0.35 / groundedness 0.30 / specificity 0.20 / calibration 0.15), thresholds, `RUBRIC_VERSION`, bundle paths. Single source of truth. |
| `eval/score_model.py` | `ScoreReport`, `CheckResult` (`severity: hard\|soft`), `JudgeDimension` (`score, rationale, per_item, self_confidence`). Hard-gate failure → `combined_score=0`, judge never runs. |
| `eval/deterministic/checks.py` | The 7 functions + `run_deterministic()`. Hard gates: sections-present, exactly-10, all-11-fields (incl. guardrail regex + two-part hypothesis presence + lift/confidence parse), pillar-floor, citation-resolution, fabrication-detection. Soft: competitor-plausibility. |
| `eval/judge/rubrics.py` | 3 versioned rubric prompts: groundedness, specificity/actionability, calibration. |
| `eval/judge/judge.py` | `run_judge(report, bundle)` — 3 concurrent Anthropic calls (`temperature=0`, prompt-cached), each returns `JudgeDimension` incl. `self_confidence`. Reads artifact **text**, not screenshots. Runs only after the deterministic gate. |
| `eval/calibration/ablations.py` | `generate_ablations(good)` → 7 known-bad reports (drop-a-pillar, break-a-citation, fake-a-Pass, vague-hypothesis, drop-to-nine, strip-guardrail, overconfident-new-page). |
| `eval/calibration/labels.json` | **Human checkpoint:** hand labels for known-good + each ablation. |
| `eval/calibration/calibrate.py` | `compute_agreement(judge, labels)`; writes `calibration_state.json` `{agreement, escalation_threshold=agreement, pass_threshold, rubric_version, n_items}`. The decision-4 linkage. |
| `eval/redteam/cases/*.json` | 4 adversarial bundles+reports (malformed / empty / single-product / non-English). |
| `eval/redteam/regression_corpus.jsonl` | Append-only permanent failure cases. |
| `eval/loop/writer.py` | `generate(prompt, bundle) -> AuditReport` via Anthropic over the **cached bundle**. The optimized artifact is the writer prompt. |
| `eval/loop/cascade.py` | `evaluate_cascade(...)` — deterministic → judge → escalate (3-sample self-consistency) when confidence < threshold → human queue for the residual. |
| `eval/loop/optimizer.py` | `optimize(train, holdout, max_iters=4)` — propose→evaluate→**held-out gate** (land only if held-out improves AND trained not regressed). |
| `eval/loop/state.py` | `OptimizerState/OptimizerRun/IterationRecord` (incl. per-iter `human_queue_size`). |
| `eval/loop/run_loop.py` | CLI demo: baseline → per-iter accept/reject → final held-out-gain table → queue-shrink comparison. The `EVAL_LOOP.md` proof. |
| `eval/fixtures/bundles/{gingerpeople,zenrojas}/`, `eval/fixtures/reports/target_report.json` | Cached artifact bundles + parsed known-good. |

### Test tree (new — the comprehensive gate)

> Product-level pytest already lives **inside** `eval/` (it *is* the eval system). The `tests/` tree below is the **harness's own developer test suite** for `core/` and `mcp/`, plus cross-phase integration and the live/LLM smoke tiers.

| File / dir | Responsibility · tier |
|---|---|
| `tests/fixtures/http/` | Recorded real responses for both stores (homepage HTML, `/cart`, `robots.txt`, `sitemap.xml`, `products.json`, PSI JSON). Replayed by `respx`. Refreshed by `make smoke`. |
| `tests/fixtures/golden_report.json` | A hand-authored valid `AuditReport` — the renderer/eval golden input. |
| `tests/fixtures/bundles/...` | Tiny cached bundles for offline eval/loop tests. |
| `tests/unit/test_schema.py` | **Phase 0.** Valid report validates; each of the 11-field omissions, bad pillar, missing-guardrail decision-rule, malformed lift/confidence is **rejected**. JSON-schema export round-trips. *offline* |
| `tests/unit/test_render.py` | **Phase 0.** Renders all four sections; exactly-10 experiments rendered; markdown↔structure matches `target_report.md`'s headings; HTML well-formed. *offline* |
| `tests/unit/test_probes.py` | **Phase 1.** Each probe against recorded fixtures; **failure → honest Warn/typed error, never a fake Pass**; redirect/SSL/HEAD edge cases. *offline (respx)* |
| `tests/unit/test_psi.py` | **Phase 1.** PSI JSON parsed to rows; PSI error → Lighthouse fallback path; both unavailable → Warn. *offline* |
| `tests/unit/test_checks.py` | **Phase 1.** Always 15 rows; statuses ∈ {Pass,Warn,Fail}; an unreachable dependency yields Warn not Pass; `/cart` 404 fixture → Fail/Warn. *offline* |
| `tests/live/test_probes_live.py` | **Phase 1 checkpoint.** Real assertion: `/cart` is non-200 on gingerpeople, 200 on zenrojas; SSL valid on both. Also **records** the http fixtures. *live* |
| `tests/unit/test_fingerprint.py` | **Phase 2.** Shopify signals + endpoint reachability → correct branch (zenrojas JSON vs gingerpeople fallback) from fixtures. *offline* |
| `tests/unit/test_catalog.py` | **Phase 2.** Waterfall: products.json path; products.json-fails → sitemap → DOM; pagination cap honored. *offline* |
| `tests/integration/test_crawl_manifest.py` | **Phase 2.** Fake crawler → manifest lists reached URLs + honest "not captured" entries; bundle layout correct. *offline* |
| `tests/integration/test_mcp_tools.py` | **Phase 2.** Each MCP tool is registered, callable in-process, returns typed dict; no logic duplicated outside `core/`. *offline* |
| `tests/live/test_crawl_live.py` | **Phase 2 checkpoint.** Real crawl of both stores produces `eval/fixtures/bundles/<slug>/` with screenshots + content + manifest; branch assertion holds. *live* |
| `tests/integration/test_skeleton_outputs.py` | **Phase 3.** Each produced `sample_output/<slug>/report` validates against schema, has exactly-10, spans all 5 pillars, and **every evidence path resolves in that store's bundle**. *offline* |
| `tests/integration/test_eval_api.py` | **Phase 4.** `score_report` returns a well-formed `ScoreReport`; hard-gate failure short-circuits (judge not called); scores both sample outputs. *offline* |
| `eval/deterministic/test_structure.py` · `test_citations.py` · `test_fabrication.py` | **Phase 4.** The 7 checks as pytest on fixtures + sample outputs (incl. fabrication: report=Pass vs cached-probe=Warn → Fail). *offline* |
| `eval/judge/test_judge_smoke.py` | **Phase 5.** Judge returns valid JSON via `FakeAnthropic`; per-item lengths correct; runs only post-gate. *offline* |
| `eval/calibration/test_calibration.py` | **Phase 5.** Agreement ≥ floor (e.g. 0.80); **every ablation is penalized** in its targeted dimension/gate; `calibration_state.json` written with `escalation_threshold==agreement`. *offline (FakeAnthropic with rubric-faithful canned scores)* |
| `tests/llm/test_judge_live.py` | **Phase 5 (opt-in).** Real Anthropic judge scores the golden report ≥ a sane floor and an ablation lower. *llm* |
| `eval/redteam/test_redteam.py` | **Phase 6.** 4 adversarial inputs get expected verdicts (no traceback, honest gate fails, no invented surfaces, language-agnostic); every corpus case still passes. *offline* |
| `tests/integration/test_regression_gate.py` | **Phase 6.** Monkeypatch a deliberate regression (loosen the guardrail regex) → assert the suite goes **red** (proves the gate bites). *offline* |
| `eval/loop/test_optimizer_gate.py` | **Phase 7.** With `FakeAnthropic` scripted so a candidate improves held-out + holds trained → **ACCEPT**; a candidate that regresses held-out → **REJECT**. Stop criteria fire. *offline* |
| `tests/integration/test_loop_demo.py` | **Phase 7.** `run_loop` over fixture bundles writes a `run_*.json` with held-out Δ>0 and trained Δ≥−ε; queue size shrinks from low-agreement to high-agreement. *offline* |
| `tests/integration/test_score_report_mcp.py` | **Phase 7.** MCP `score_report` == direct `core.eval_api.score_report` for the same input (one impl, two adapters). *offline* |
| `tests/test_docs.py` | **Phase 8.** `EVAL_LOOP.md` & `WORKFLOWS.md` ≤ ~1 page (word bound); required sections present; both `sample_output/<slug>/` reports exist and validate; README has the run commands. *offline* |

---

## Build sequence — phase → **TEST GATE** → next phase

Walking skeleton (0–3) first, then harden (4–7), then ship (8). **A phase is "done" only when its gate is green.** After each green gate: commit, append to `AGENT_LOG.md` (framing each choice by the failure mode it handles).

### Phase 0 — Contracts + renderer
Build `core/schema.py`, `core/render.py`, `pyproject.toml`, `Makefile`, root `conftest.py`, `.env.example`, `.gitignore`, `git init`, move spec docs to `docs/`, author `tests/fixtures/golden_report.json`.
**▶ TEST GATE 0** — `make test` runs `tests/unit/test_schema.py` + `tests/unit/test_render.py`.
Pass when: valid fixture validates; **every** missing-field / bad-pillar / missing-guardrail / malformed-lift mutation is rejected; renderer emits all four sections and exactly-10 experiments; rendered markdown headings match `target_report.md`'s structure; JSON-schema export round-trips. **Do not start Phase 1 until green.**

### Phase 1 — Verifiable technical-check slice
Build `core/probes.py`, `core/psi.py`, `core/checks.py`.
**HUMAN CHECKPOINT:** run `make smoke` (and `make test-live`) — the live tier hits both stores, asserts the curl-block facts, and **records** `tests/fixtures/http/`.
**▶ TEST GATE 1** — `make test` runs `test_probes.py` + `test_psi.py` + `test_checks.py` (offline, replayed). Then `make test-live` runs `test_probes_live.py`.
Pass when (offline): 15 rows always; no failure path ever yields a fake Pass; `/cart` 404 fixture → Fail/Warn. Pass when (live): `/cart` non-200 on gingerpeople, 200 on zenrojas; SSL Pass on both. **Both green → Phase 2.**

### Phase 2 — MCP server (fingerprint / catalog / crawl / technical)
Build `mcp/qosmic_audit_server/*`. Record the real bundles into `eval/fixtures/bundles/`.
**▶ TEST GATE 2** — `make test` runs `test_fingerprint.py` + `test_catalog.py` + `test_crawl_manifest.py` + `test_mcp_tools.py`. Then `make test-live` runs `test_crawl_live.py`.
Pass when (offline): fingerprint picks zenrojas→JSON / gingerpeople→fallback from fixtures; catalog waterfall falls through products.json→sitemap→DOM; manifest is honest about "not captured"; each MCP tool callable and typed. Pass when (live): both stores yield a complete bundle and the branch assertion holds. **Both green → Phase 3.**

### Phase 3 — Skill + walking skeleton (Part-1 deliverable)
Build `skills/storefront-audit/*`, `CLAUDE.md`, `AGENTS.md`. Run the harness end-to-end on both stores → `sample_output/{gingerpeople,zenrojas}/`.
**HUMAN CHECKPOINT:** eyeball both live stores so archetypes match reality.
**▶ TEST GATE 3** — `make test` runs `tests/integration/test_skeleton_outputs.py` against the produced reports.
Pass when: both reports validate against schema; exactly-10; all 5 pillars present; **every evidence path resolves in that store's bundle**; zenrojas got no retailer-handoff/large-catalog archetype. **Green → walking skeleton complete; start Phase 4.**

### Phase 4 — Eval deterministic core
Build `eval/config.py`, `eval/score_model.py`, `eval/deterministic/*`, `core/eval_api.py`.
**▶ TEST GATE 4** — `make eval` runs `eval/deterministic/test_*.py` + `tests/integration/test_eval_api.py`.
Pass when: all 7 checks pass on `target_report.json` and the two sample outputs; a hand-broken report fails the right hard gate; fabrication check flags a Pass-vs-cached-Warn; `score_report` short-circuits before the judge on hard-gate failure. **Green → Phase 5.**

### Phase 5 — Judge + calibration (the linchpin)
Build `eval/judge/*`, `eval/calibration/*`.
**HUMAN CHECKPOINT:** write the CRO rubric + hand-label the calibration set (`labels.json`).
**▶ TEST GATE 5** — `make eval` runs `eval/judge/test_judge_smoke.py` + `eval/calibration/test_calibration.py`. Optionally `make test-llm` runs `tests/llm/test_judge_live.py`.
Pass when: judge returns valid JSON (FakeAnthropic); **every ablation penalized** in its targeted dimension; agreement ≥ floor; `calibration_state.json` written with `escalation_threshold == agreement`. (LLM tier, if run: real judge scores golden ≥ floor, ablation lower.) **Green → Phase 6.**

### Phase 6 — Adversarial + regression gating
Build `eval/redteam/*`.
**▶ TEST GATE 6** — `make eval` runs `eval/redteam/test_redteam.py` + `tests/integration/test_regression_gate.py`.
Pass when: each adversarial input gets its expected verdict and **never** crashes/fabricates; the deliberate regression (loosened guardrail regex) makes the suite go red as designed; the corpus replays clean. **Green → Phase 7.**

### Phase 7 — Self-improving loop (the headline)
Build `eval/loop/*` + the `score_report` MCP tool.
**▶ TEST GATE 7** — `make test` runs `eval/loop/test_optimizer_gate.py` + `tests/integration/test_loop_demo.py` + `tests/integration/test_score_report_mcp.py`. Then `make loop` runs the real demo.
Pass when (offline): the held-out gate accepts only on held-out↑ & trained-not-regressed and rejects the regressing candidate; `run_loop` writes a `run_*.json` proving held-out Δ>0 with trained Δ≥−ε; queue shrinks as agreement rises; MCP score == direct score. Pass when (`make loop`): the printed final table shows zenrojas (held-out) up, gingerpeople (trained) not down. **Green → Phase 8.**

### Phase 8 — Docs, outputs, ship
Build `README.md`, `AGENT_LOG.md`, `EVAL_LOOP.md`, `WORKFLOWS.md`; finalize both `sample_output/` sets.
**▶ TEST GATE 8 (full regression)** — `make lint && make cov` runs the **entire** offline suite with coverage; `make test-live` + `make test-llm` re-confirm the live/LLM paths once.
Pass when: full offline suite green at ≥85% coverage on `core/`+`eval/`; `tests/test_docs.py` green (docs within length, sample outputs validate); live + LLM tiers green on a final manual run. **HUMAN CHECKPOINT:** record the 5-min Loom (name one reversible decision — custom MCP server vs. skill-scripts; name one unmeasured dimension — e.g., business-realism of lift estimates / competitor reality), push the repo.

**Critical path:** Phase 0 → everything. 1 → 2 → 3 (skeleton). 4–6 → 7 (loop needs a working eval). **Linchpin:** the Phase-5 agreement number feeding the Phase-7 escalation threshold (`calibration_state.json`) — verified by Gate 5 (`escalation_threshold == agreement`) and exercised by Gate 7 (queue shrinks as agreement rises).

---

## Minimal-honest slices (where build-plan ambition exceeds budget)

Deliberate, documented scope cuts that still demonstrate the mechanism (each is itself test-gated):
1. **Optimizer:** 1 candidate/iter, ≤4 iters, 2 stores (not a GEPA population search). DSPy+GEPA = scale path.
2. **Escalation = 3-sample self-consistency**, not a second model. Larger-model escalation = upside.
3. **Calibration set = 1 known-good + 7 programmatic ablations (~9 items).** Report agreement % **with its n**.
4. **Fabrication re-probes from the cached bundle in CI**; live re-probe only in an opt-in nightly sweep.
5. **Competitor plausibility stays structural** (populated/distinct/non-self-referencing). Search-grounded verification = the Loom's "unmeasured dimension."
6. **Judge reads artifact text, not screenshots.** Vision-grounded judging = upside.

---

## How to run the gates (quick reference)

```
make install      # pip install -e .[dev]; playwright install chromium
make lint         # ruff
make test         # OFFLINE gate: pytest -m "not live and not llm"  (this is CI)
make test-live    # opt-in: pytest -m live      (real stores/PSI/Playwright/Firecrawl)
make test-llm     # opt-in: pytest -m llm        (real Anthropic judge/writer)
make smoke        # live curl-block helper; records tests/fixtures/http/
make eval         # score both sample outputs + run eval/* pytest
make loop         # python -m eval.loop.run_loop --train gingerpeople --holdout zenrojas
make cov          # offline suite + coverage report (≥85% core/+eval/)
```
Every phase gate above is one of these targets. Green gate = phase done = commit + log.
