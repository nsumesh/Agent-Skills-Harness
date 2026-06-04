1. Mission
Build a runtime harness that turns any coding agent into the Qosmic CRO audit
agent (Shopify storefront URL in → one structured audit report out), plus the
eval system that scores those reports and a self-improving eval loop.
Grading reality, in priority order:

The eval loop is the headline. A sharp, self-improving eval on a thin
harness beats a beautiful harness with static evals. Spend depth here.
Generalization is tested. The harness will be pointed at stores it has
never seen. No store-specific shortcuts.
Delegation is read. AGENT_LOG.md and WORKFLOWS.md show how the human
uses coding agents.

Optimize every decision for robustness (works in all cases) over ease of
building.

2. Non-negotiable principles (treat as hard rules)

NEVER fabricate. Any claim that cannot be tied to a captured artifact
(screenshot path or reachable URL) is dropped. Any check that cannot be
verified degrades to an honest Warn ("not inspected"), never a fake Pass.
A report that green-checks everything is worse than one that honestly warns.
Cite everything. Every experiment cites a specific captured artifact.
Proposed/new surfaces cite an existing artifact as the "pattern to mirror."
Fingerprint, don't assume. Probe the platform and endpoints before
branching. Do not assume Shopify conventions hold.
Fallback chains everywhere. No single point of failure on an unknown store.
Determinism where possible. Use the simplest mechanism that fully answers
the question. Do not put a one-line HTTP probe or a schema check behind a
network hop.
Generalize, don't overfit. Never tune the harness so the calibration store
scores well at the expense of unseen stores. Optimize against a held-out split.
Measured reliability. The eval must report its own judge-vs-human agreement
number, not assert quality.


3. Architecture (three layers — keep them separate)

Layer 1 — Skill (skills/storefront-audit/SKILL.md + CLAUDE.md/AGENTS.md):
the portable playbook and orchestration. This is what makes the deliverable a
harness (runs under Claude Code, Codex, etc.), not an app.
Layer 2 — Custom MCP server (mcp/qosmic_audit_server/): encapsulated
external capabilities (fingerprint, crawl waterfall, catalog fetch, technical
checks, score_report). All retry/fallback logic lives inside here, hidden
behind a stable tool interface. Reused by both the harness and the eval loop.
Layer 3 — Local deterministic functions (core/, eval/deterministic/):
schema validation, HTTP probes, the eval's deterministic core, the renderer.
Pure, reproducible, no network hop where avoidable.

Reasoning and writing happen in the agent (driven by the Skill), calling MCP
tools.

4. Tech stack (single language to keep the runtime surface small)

Python 3.11+
pydantic (schema/contract + validation)
pytest (deterministic eval as tests)
MCP server: official Python MCP SDK / FastMCP
Crawl: httpx (JSON endpoints, probes, PSI), playwright (python, embedded —
do NOT compose a separate Node Playwright MCP; one fewer runtime), Firecrawl
Python SDK for content-page extraction
Technical checks: Google PageSpeed Insights API v5 (free; 25k/day with a key)

local Lighthouse fallback


Judge: deepeval (G-Eval rubrics)
Adversarial: promptfoo
Loop: dspy + GEPA optimizer
Regression gating: CI logic now; name Braintrust/Langfuse as the scale path


5. Test target intel (already verified — do not re-research)
zenrojas.com — GENERALIZATION target (unseen reference held by Qosmic).

Clean, transacting Shopify store (shopify checkout token, /cdn/shop/,
"Powered by Shopify"; myshopify handle zen-rojas).
Routes: /products/<handle>, /collections/{teas,teaware,gift-cards},
/pages/{aboutus,faqs,...}, /blogs/weekly-blog, /cart, /search.
/products.json and /collections.json WILL work. Has cart + checkout
(Apple Pay/Shop Pay/PayPal), email capture, Ambassador Program, "free shipping
on $50+".
Small founder-led tea brand (~teas, teaware, gift cards; ~$8–13). Veteran-owned,
heavy social (IG/TikTok). Thin content footprint.
Expected experiment families: tea subscription/auto-replenish (Retention),
sampler bundle + $50-threshold nudge (AOV), import founder/veteran story +
social proof onto PDPs (Conversion/Acquisition), teaware cross-sell (AOV),
Ambassador Program leverage (Acquisition).

gingerpeople.com — CALIBRATION target. target_report.md is the bar.

NOT a clean Shopify store: retailer-routed (FAQ sends buyers to a store
locator), /cart returns a branded 404, custom WordPress-ish URL slugs
(/the-ginger-people-products/), separate eu. and wholesale. subdomains.
/products.json likely FAILS — this is exactly why the crawl waterfall is
mandatory. Probe it; branch on the result.
Large, broad catalog (candy, juices, lozenges, bulk), strong content moat
(GLP-1, recipes, health education).

Implication baked into the design: the two targets straddle the
Shopify/not-Shopify boundary, so no single crawl method covers both. The
fingerprint→waterfall is required, and the harness must adapt experiment
archetypes to store type and catalog scale.
Position the harness in the README as "any storefront, Shopify-optimized."

6. Report contract (the exact output)
One file (.md and/or .html) with EXACTLY four sections:

Executive summary — 2–3 paragraphs of prose. Prioritized diagnosis (the
single biggest leak first), not a problem list. Bold the lead claim of each
paragraph.
10 experiments — exactly 10, spanning ALL 5 pillars (≥1 each; even spread
not required). Each experiment has all 11 fields:
title, exp_id, pillar, affected_surface, url, evidence,
hypothesis (two parts: predicted metric mechanism + grounded current-state
observation), primary_change, primary_kpi, decision_rule (always
"Ship if <KPI> improves without hurting <guardrail>" — guardrail mandatory),
expected_lift (a range), confidence (%). Confidence must track
speculativeness (structural fixes high; new content lower).
Competitor analysis — table vs. 3–4 real, niche-relevant competitors:
positioning, what they make easier, the store's edge, pattern to adapt.
Technical checks — ~15 rows, each Pass/Warn/Fail + one-line detail:
SSL, HTTPS redirect, sitemap, robots.txt, critical pages loading, meta tags &
social previews, structured data, favicon, mobile-friendly, page speed mobile,
page speed desktop, broken links, image optimization, cookie/privacy,
checkout reachable.

Pillars enum: Conversion | AOV | Retention | Acquisition | Performance.

7. Repo layout
qosmic-audit/
  CLAUDE.md  AGENTS.md
  skills/storefront-audit/
    SKILL.md
    references/  schema.md  pillars.md  report-template.md
  mcp/qosmic_audit_server/        # FastMCP server
  core/  schema.py  render.py  probes.py  checks.py
  eval/
    deterministic/  judge/  calibration/  redteam/  loop/
  sample_output/{gingerpeople,zenrojas}/
  README.md  AGENT_LOG.md  EVAL_LOOP.md  WORKFLOWS.md

8. Working agreement

Build the walking skeleton (Phases 0–3) first: a rough but complete report
end-to-end on BOTH stores. Then harden eval + loop (Phases 4–7). Ship (Phase 8).
Do not perfect any single stage before the skeleton runs end-to-end.
After each phase: run against BOTH stores, commit, append to AGENT_LOG.md.
Frame every choice in AGENT_LOG.md by the failure mode it handles.
Stop at every HUMAN CHECKPOINT and ask.


PHASE 0 — Contracts + renderer (unblocks everything)
Create: core/schema.py, core/render.py
Do:

Pydantic Experiment (11 fields, pillar enum) and AuditReport (4 sections);
export JSON Schema.
AuditReport → .md and → .html renderer (pure, deterministic).
Robustness: validation rejects any experiment missing a field or with an
invalid pillar.
DONE WHEN: a hand-written fixture AuditReport validates and renders to a
file matching target_report.md's structure.

PHASE 1 — Verifiable slice (technical checks)
Create: core/probes.py, core/checks.py
Do:

HTTP probes (browser-like UA): SSL, HTTPS redirect, robots, sitemap, /cart,
favicon, broken-link HEAD checks.
PSI API call with retry/backoff; local Lighthouse fallback; assemble 15-row table.
Robustness: every check degrades to honest Warn on failure; never fake a Pass.
HUMAN CHECKPOINT: human runs the curl block on both stores first; assert
against those hand-verified values.
DONE WHEN: 15-row table produced for both stores; /cart is Fail/Warn on
gingerpeople and Pass on zenrojas.

PHASE 2 — MCP server: fingerprint + crawl waterfall + catalog
Create: mcp/qosmic_audit_server/ with tools:

fingerprint_store(url) -> StoreProfile — probe platform signals AND endpoint
reachability (don't trust meta tags alone).
fetch_catalog(url) — /products.json + /collections.json (paginate, cap
250/page) → sitemap fallback → DOM fallback.
crawl_storefront(url) — pick representative surfaces (homepage, top PDPs, a
collection, cart, FAQ/blog/where-to-buy); capture screenshots (embedded
Playwright) + cleaned content (Firecrawl); emit an artifact manifest with
honest "not captured" entries.
run_technical_checks(url) — wraps Phase 1.
Robustness: retries/backoff + full fallback chain inside the server; embed
Playwright (no separate Node MCP); browser UA to avoid bot-blocks.
DONE WHEN: both stores return StoreProfile + catalog + artifact manifest;
zenrojas takes the JSON branch, gingerpeople takes a fallback branch.

PHASE 3 — Skill: council + critic + writer (walking skeleton complete)
Create: skills/storefront-audit/SKILL.md, CLAUDE.md, AGENTS.md,
references/{schema.md,pillars.md,report-template.md}
Do:

Orchestrate: fingerprint → crawl → checks (MCP), then pillar-sharded
reasoning (≥1 grounded experiment per pillar) → supervisor prunes/dedups
to a balanced 10 → pre-write critic.
Critic must: verify every evidence path resolves to a captured artifact AND the
cited surface exists on THIS store; enforce two-part hypothesis + guardrail in
decision rule; reject + loop on failure.
Writer emits schema-validated JSON → render (Phase 0).
references/pillars.md: experiment archetypes that ADAPT to catalog scale (see
§5; zenrojas must NOT get "fix retailer handoff" or "reorganize large catalog").
HUMAN CHECKPOINT: human eyeballs both live stores so archetypes match reality.
DONE WHEN: end-to-end run yields complete reports in
sample_output/{gingerpeople,zenrojas}/. This is the Part 1 deliverable.

PHASE 4 — Eval deterministic core (the 60%)
Create: eval/deterministic/ (pytest)
Do: section presence; exactly-10 experiments; all fields; 5-pillar floor;
citation resolution (every evidence path resolves); fabrication detection
(re-run probes/PSI independently, flag any technical-check claim that disagrees);
competitor plausibility (light).
Robustness: zero LLM, reproducible, generalizes to any store.
DONE WHEN: scores both sample outputs into a structured score object; runs in CI.
PHASE 5 — Judge layer + calibration (credibility core)
Create: eval/judge/, eval/calibration/
Do:

DeepEval G-Eval rubrics: groundedness (evidence supports hypothesis),
specificity/actionability, confidence calibration.
Calibration set: known-good = target_report.md; hand-made ablations (drop a
pillar, break a citation, fake a Pass, vague hypothesis) = known-bad.
Measure and report judge-vs-label agreement %.
Robustness: runs only AFTER the deterministic gate (cheapest-first). The
agreement % is the eval's stated reliability and feeds Phase 7's threshold.
HUMAN CHECKPOINT: human writes the CRO quality rubric and hand-labels the
calibration set — irreducible bar-setting.
DONE WHEN: judge correlates with labels at a stated agreement %; every
ablation is penalized as expected.

PHASE 6 — Adversarial + regression gating
Create: eval/redteam/
Do: promptfoo configs feeding malformed/empty/single-product/non-English
reports; confirm eval + harness hold. Start a regression corpus — every failure
becomes a permanent case. CI gate blocks regressions (name Braintrust/Langfuse as
scale path).
DONE WHEN: red-team suite runs; a deliberately-regressed change is blocked.
PHASE 7 — Self-improving loop, working slice (the headline)
Create: eval/loop/
Do:

Cascaded selective evaluation: cheap judge first → escalate when confidence
< threshold (computed from Phase 5 calibration set) → route low-confidence to a
"human queue."
GEPA/DSPy slice: take eval feedback (score + explanation), revise one
harness skill prompt, evaluate on a HELD-OUT store split (train one store,
validate on the other), gate on eval gains.
Meta-eval: periodic check that the judge still discriminates known-good vs
known-bad.
Expose score_report as an MCP tool so the harness can self-evaluate mid-run.
Robustness: the train/val split is the anti-overfit guard; gating means
self-improvement cannot regress.
DONE WHEN: a GEPA pass measurably improves the HELD-OUT store's score without
regressing the trained one; the human queue shrinks as calibration grows. This
is the EVAL_LOOP.md proof.

PHASE 8 — Docs, outputs, Loom, ship
Do:

README (positioning: "any storefront, Shopify-optimized").
AGENT_LOG.md — choices framed by failure mode handled; honest time.
EVAL_LOOP.md (≤1 page) — autonomy argument + the Phase 7 slice; 1–3 month
picture; how it improves itself; where humans enter and how that surface shrinks.
WORKFLOWS.md (≤1 page) — the human's general agent-delegation practice.
Finalize both sample_output/ sets.
HUMAN CHECKPOINT: human records the 5-min Loom (walk harness + loop; name one
reversible decision — custom MCP server vs. skill-scripts; name one unmeasured
dimension that matters — e.g., business-realism of lift estimates), pushes the
public repo, replies to the thread.


Critical path
Phase 0 (schema) → everything. Phase 1 → 2 → 3 (walking skeleton).
Phases 4–6 → Phase 7 (loop needs a working eval). The linchpin is the Phase 5
calibration number feeding the Phase 7 threshold — that linkage turns
"self-improving eval" from a claim into a demonstrated mechanism. Do not let
Phase 5 stay shallow.

Based of this plan, resolve any ambiguities with detailed, specific questions. The final plan should consist of a file by file plan explaning what each file does, its exact function, how it would be built and what it supports. 