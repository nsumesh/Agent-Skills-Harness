# Qosmic CRO Audit Harness

A runtime harness that turns a coding agent (Claude Code, Codex, or anything similar) into a
storefront CRO auditor, plus the eval system that grades its reports and a loop that improves the
writer over time. Built for any Shopify store, calibrated against `target_report.md`.

## What it does

You give it one storefront URL. It gives you one structured audit report:

- an executive summary (2–3 paragraphs, biggest leak first),
- exactly 10 proposed experiments spanning all five pillars (Conversion, AOV, Retention, Acquisition, Performance),
- a competitor table (3–4 competitors), and
- a ~15-row technical-checks table.

Every claim is tied to a captured artifact. Anything we couldn't verify is an honest `Warn`, never
a fake `Pass`.

## How it's put together

Three layers, kept separate so each can be reused on its own.

```
Agent ── reads ──▶  Layer 1   skills/storefront-audit/  (the playbook)
  │ calls tools
  ▼
            Layer 2   qosmic_audit_server/   (thin FastMCP server)
  │ wraps
  ▼
            Layer 3   core/                  (importable: contract, renderer, probes, checks, eval)
                          ▲
            eval/ ────────┘  imports core/ directly, no network hop
```

- **The agent does the thinking and writing.** That's what makes this a harness and not an app — the
  same playbook runs under Claude Code, Codex, or the next agent.
- **The tools are capabilities behind a stable interface** — crawling, fingerprinting, checks,
  scoring. All the retry and fallback logic lives in here.
- **`core/` holds the contract** (`schema.py`) and the renderer, so a report literally can't be
  malformed. The eval and the loop import it directly.

(The server package is named `qosmic_audit_server` rather than `mcp` so it can't shadow the
installed MCP SDK.)

## Getting started

```bash
make install                 # installs deps + the Playwright browser
cp .env.example .env         # then add ANTHROPIC_API_KEY, PSI_API_KEY, FIRECRAWL_API_KEY
make test                    # offline gate — deterministic, no network
```

## Running an audit

Open the repo in your coding agent and ask it to audit a URL following
`skills/storefront-audit/SKILL.md`. The skill walks the agent through the three phases — crawl,
reason, write — using these tools:

| Tool | What it returns |
|------|-----------------|
| `fingerprint_store(url)` | platform + endpoint reachability, and which catalog branch to take |
| `fetch_catalog(url)` | products, via a `products.json` → sitemap → DOM waterfall |
| `crawl_storefront(url)` | screenshots + page content captured into a cached bundle |
| `run_technical_checks(url)` | the 15-row technical table |
| `score_report(report, slug)` | the eval, exposed as a tool so the agent can self-check |

The output lands in `sample_output/<slug>/report.md` (also `.html` and `.json`). To capture the
artifact bundles up front, run `python -m qosmic_audit_server.record_bundles`.

The harness can also drive the whole thing itself: `python -m qosmic_audit_server.audit` crawls each
store live, has the writer draft a report from the cached bundle, runs a critic loop that re-prompts
on any deterministic failure until the gate is clean, and overwrites `sample_output/`. That's how the
two sample reports in this repo are produced — they're an output of the harness, not hand-written.

## The eval and the loop

The eval scores any report for any store, cheapest checks first:

1. **Deterministic gate** — sections present, exactly 10 experiments, all fields, all five pillars,
   every citation resolves, and no fabricated passes, plus a soft **evidence-diversity** check that
   citations spread across distinct surfaces. Fail any hard check and the score is 0; the judge never runs.
2. **LLM judge** — four rubrics (groundedness, specificity, calibration, surface-specificity) over
   the captured text.
3. **Escalation** — low-confidence judgements get a self-consistency pass; whatever's still
   uncertain goes to a human queue that shrinks as the system gets more trustworthy.

The judge is calibrated against a known-good report plus nine deliberate ablations. Measured
judge-vs-human agreement is **0.90 (n=10)** — reported with its sample size, not asserted. That
number is written to `eval/calibration/calibration_state.json` and used as the loop's escalation
threshold.

The loop (`make loop`) then optimizes the **writer prompt** against the eval on a held-out split:
it only keeps a change if the held-out store improves and the trained store doesn't regress. The
demo lands two generalizing improvements, rejects an overfitting one, and shrinks the human queue.

For the full autonomy argument, see `EVAL_LOOP.md`.

## What's in the repo

```
core/                 the output contract, renderer, probes, PSI, checks, eval API
qosmic_audit_server/  the FastMCP server + tools
skills/               the portable audit playbook (SKILL.md + references/)
eval/                 deterministic / judge / calibration / redteam / loop + recorded bundles
sample_output/        the two finished audits
target_report.md      the calibration anchor — the quality bar
```

| Command | What it runs |
|---------|--------------|
| `make test` | the offline test gate |
| `make eval` | the eval suite |
| `make loop` | the self-improving loop demo |
| `make lint` | ruff |

## Sample outputs

`sample_output/` has two finished audits: **gingerpeople** (the calibration store — a
retailer-routed WordPress site whose `/cart` 404s) and **zenrojas** (the held-out store — a clean
Shopify shop the harness wasn't calibrated against). zenrojas gets store-appropriate experiments
with none of gingerpeople's retailer-handoff or large-catalog archetypes, which is the
generalization test.

## Notes

- Needs Python 3.10+. Keys load from `.env` via `python-dotenv`; `.env` is gitignored, so blank the
  keys before zipping or sharing.
- `make loop` uses a deterministic stand-in writer so the headline is reproducible. The real
  Anthropic writer is wired up in `eval/loop/writer.py` (drop `--fake-writer` to use it).
- A few deliberate scope cuts — a greedy optimizer rather than a population search, 3-sample
  escalation rather than a second model, a 10-item calibration set — are written up in `AGENT_LOG.md`
  and `EVAL_LOOP.md`.

## More docs

- `EVAL_LOOP.md` — how the eval becomes autonomous and self-learning.
- `WORKFLOWS.md` — how I  work with coding agents.
- `AGENT_LOG.md` — the build log, decisions, and where the agent drove vs. where I did.
