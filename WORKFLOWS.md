# WORKFLOWS — how I work with coding agents

Not about this take-home — my general practice. The throughline: **the human owns every
architectural decision and root-cause hypothesis; the agent owns parallel execution and cross-file
consistency.** Plan before touching code, parallelize everything that can be parallelized, keep
fixes minimal, and document every failure.

## Tool stack
- **Claude Code** as the primary driver, via its `/plan` feature (plan first, approve, then execute).
  **Codex** for an independent second opinion on tricky diffs.
- **Custom skills + thin MCP servers** as the unit of reuse — capability behind a stable tool
  interface (this repo is one: a FastMCP server over an importable core).
- A running **`debug-decisions.md`** per project: every failure logged with root cause, fix, and a
  prevention rule.
- A running **`journal.md`** per project : every phase is marked, describing what has been completed and
what gate has been passed.

## Plan before code
Every feature starts with `/plan`. The agent drafts an implementation plan; I review and approve
before a line is written. Design decisions get resolved in the plan which costs
one review cycle instead of a post-implementation refactor.

## Ordered batches + checkpoints
I break the work into ordered batches with explicit dependency ordering and checkpoint criteria
defined upfront (schema applied, server boots, pipeline returns results, eval passes the golden
queries, end-to-end flow works). The agent does not move to the next batch until I've confirmed the
current checkpoint passed.

## Parallelize independent files
Within a batch, independent files are written in a single agent turn — five agent modules or
four frontend components in one message, not five round-trips.

## The debug loop
When a checkpoint shows wrong behavior, I run it, observe, and suggest the likely cause. The agent
reads those files, confirms or refines the hypothesis, and states the root cause in one sentence
— then writes the minimal fix: no adjacent cleanup, no speculative guards I re-run. Every fix
is logged, which builds a pattern library: the second time a bug category shows up (e.g. "PostgREST
filter values are data, not SQL"), the fix is immediate from the prior entry.

## What I drive vs. what the agent drives
| I take the wheel | The agent drives |
|---|---|
| Requirements, architecture, system boundaries | Translating batch specs into code |
| Breaking the problem into batches + checkpoint criteria | Writing independent files in parallel |
| Running checkpoints, diagnosing failures, forcing pivots | Confirming the root cause + the minimal fix |
| Design tradeoffs; the human gates | Cross-file consistency (schema names, imports, state access) |

## Principles
- **Plan before touching code** — cheap to redirect a plan, expensive to redirect a half-built feature.
- **Minimal fixes** — no speculative guards, no drive-by refactors; one change per root cause.
- **Document every failure** — the gate only ever grows.
- **Human gates in the product mirror human gates in the process** — I confirm before anything
  important or irreversible; the agent proposes, I land.
