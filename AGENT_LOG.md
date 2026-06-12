# AGENT_LOG

This is the build log for the harness, plan before code, work in ordered phases with a checkpoint after each,
parallelize what's independent, keep fixes minimal, and write down every failure. I owned the architecture, the
cadence, and the checkpoints; the agent owned turning each phase spec into code and keeping it
consistent across files.

## Time per part

This was agent-driven under human steering — the agent did the authoring, I steered at the gates,
so the numbers below are wall-clock for a focused session, not four hours of hand-typing.

| Part | ~Time | What got built |
|------|-------|----------------|
| Part 1 — runtime harness (Phases 0–3) | ~1.5–2h | the contract + renderer, probes/PSI/checks, the MCP server, the skill, and both sample reports |
| Part 2 — eval + loop (Phases 4–7) | ~2–2.5h | the deterministic eval, the judge + calibration, the red-team suite, the self-improving loop |
| Docs + cleanup (Phase 8) | ~0.5h | README, EVAL_LOOP, WORKFLOWS, this log, the auto-audit + a calibration-to-the-bar pass, and a lean-repo pass |

## Plan before code

The whole thing started with `/plan`. The agent drafted a file-by-file implementation plan; I
reviewed and approved it before any code was written. The decisions that usually cause rework got
settled in the plan instead — hand-rolling the eval and loop rather than pulling in DeepEval/GEPA,
wrapping the tools in a thin MCP server, running the loop over a cached bundle deterministically.
Each of those cost one review cycle, not a mid-build refactor.

## Ordered phases with checkpoints

Eight phases, each with a single `make` target as its checkpoint, and I didn't let the agent move
on until the checkpoint was green and I'd signed off. Four of them had a live checkpoint I ran or
approved myself.

| Checkpoint | Criterion |
|---|---|
| P0 `make test` | the contract validates and rejects bad reports; renderer matches the target layout |
| P1 live HTTP checkpoint | `/cart` is 404 on gingerpeople, 200 on zenrojas; real HTTP fixtures recorded |
| P2 live crawl | both stores produce a full artifact bundle; branch assertion holds |
| P3 `make test` | both sample reports validate, span 5 pillars, every citation resolves |
| P4 `make eval` | the 7 deterministic checks pass on three known-goods; broken reports fail the right gate |
| P5 `calibrate --live` | real judge-vs-human agreement measured (0.90, n=10 on the v2 rubric; 0.875/n=8 at the original checkpoint) |
| P6 `make eval` | adversarial inputs never crash; a deliberate regression turns the gate red |
| P7 `make loop` | held-out store up, trained store not down, overfit candidate rejected |

## Prompts I fed the agent

- "Use `finalized-plan.md` as the plan for this project."
- "start phase 1" … "start phase 7" — one phase at a time, reviewing each green gate before the next.
- The live go/no-go calls at each checkpoint: "run it now" for the Phase 1 smoke, the Phase 2 full
  crawl, the Phase 5 real judge, and the Phase 7 live-writer test.
- "only keep what powers the core functionality" and "delete tests with the config fixes" — the cleanup.
- "how are we sure this follows the brief / the plans?" — which produced the audits in this log.

## Parallelize what's independent

Within a phase, independent files were written together rather than one at a time. The clearest
example is the final comment-cleanup pass: I split the tree by directory and ran it across four
subagents at once, then reviewed the combined diff in one place.

## Minimal fixes — and every failure written down

When a checkpoint diverged from spec, the rule was the same: name the root cause in one sentence,
make the smallest change that fixes it, and log it. No drive-by cleanup, no speculative guards. The
ones worth keeping:

- **Guardrail regex would have rejected the gold standard.** The target's own report uses "without
  compliance flags," not "without hurting" — so I anchored the rule on `without`. Became a permanent
  regression case.
- **The Markdown renderer was escaping `&` → `&amp;`.** Jinja's `select_autoescape` defaults
  `default_for_string=True`; split into a no-escape Markdown env and an escaped HTML env.
- **Recording real fixtures flipped two of my guesses.** gingerpeople actually emits JSON-LD;
  zenrojas's `/favicon.ico` is a 404 (Shopify defines it in-theme). Softened the favicon check from
  Fail to Warn and let the sitemap probe accept a `<sitemapindex>`.
- **The fake judge returned all-zero scores.** A greedy regex was swallowing the rubric block after
  the report JSON; switched to `raw_decode` so only the JSON object is parsed.
- **The live writer crashed the eval.** It wrote `"content/01-pdp.md: <explanation>"` into the
  evidence field, and the citation check did `(bundle / that).exists()` → `OSError: File name too
  long`. Fixed by taking the leading path token and guarding the call; added two regression tests.
- **Naming `mcp/` shadowed the installed MCP SDK.** Renamed the package to `qosmic_audit_server`.
- **`make lint` had never actually run** (ruff wasn't installed). Installed it, fixed nine
  pre-existing nits, and the gate is green now.

The point of logging these is the second occurrence: the PostgREST-style "filter values are data,
not SQL" mistake that shows up across projects is fixed instantly the next time from the prior entry.


## What I drove vs. what the agent drove

| I took the wheel | The agent drove |
|---|---|
| Requirements, architecture, the cadence (pause every phase) | Turning each phase spec into code |
| Checkpoint criteria and running every checkpoint | Writing independent files in parallel |
| Diagnosing failures and the root-cause hypothesis | Confirming the cause and writing the minimal fix |
| Design tradeoffs and scope cuts; all commits | Cross-file consistency (schema names, imports, paths) |

## Deviations and scope cuts (all deliberate)

- Hand-rolled judge/optimizer/red-team; DeepEval / promptfoo / DSPy-GEPA named as the scale path.
- `mcp/` → `qosmic_audit_server/` to avoid shadowing the SDK; Python 3.10 (the available interpreter).
- `make loop` uses a deterministic writer for a reproducible headline; the real Anthropic writer is wired.
- In the final cleanup I removed the `tests/` dev suite to keep the repo lean — the eval system's own
  tests still live under `eval/`. Honest trade: `core/` and the MCP server lost their unit coverage.
- Greedy optimizer, 3-sample escalation, and a ~9-item calibration set are the documented small cuts;
  each is a named upside, not a hidden gap.
