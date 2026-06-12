# EVAL_LOOP — how the eval becomes autonomous & self-learning

**The thesis:** the eval, not the writer, is the asset. A report writer is a prompt; the eval
is the thing that lets *any* writer (or model, or future agent) improve safely without a human
reading every output. So the loop optimizes the writer **against the eval**, on a **held-out
split**, and gates every change on generalization.

## What runs today (`make loop`)
1. **Cheapest-first cascade.** Deterministic gate (sections, exactly-10, all-fields, pillar-floor,
   citation-resolution, **fabrication-detection**, plus a soft **evidence-diversity** check —
   citations have to spread across distinct captured surfaces) → if a hard check fails, score 0 and
   the judge never runs. Only survivors reach the LLM judge (4 rubrics: groundedness, specificity,
   calibration, **surface-specificity** — is each experiment anchored to a real captured surface).
2. **Selective escalation.** A judged dimension whose self-confidence < the **escalation threshold**
   gets a 3-sample self-consistency pass; whatever stays uncertain (< `1 − agreement`) lands in a
   **human queue**. The threshold *is* the calibration agreement — the linchpin.
3. **Optimization with a held-out gate.** The loop edits the writer prompt and **lands a change only
   if the held-out store improves AND the trained store doesn't regress.** Demonstrated: held-out
   **+0.215**, trained held, an overfitting candidate **rejected**, human queue **2→0** (as the
   writer improves) and **4→2** (as agreement rises).

**Measured reliability, not asserted:** real judge-vs-human agreement is **0.90 (n=10)** — and the
one miss is honest (the judge flagged that our remapped calibration target is only moderately
grounded against a 3-surface bundle).

## Calibrating to the bar (the loop, run once by hand)
The two sample reports aren't hand-written — `python -m qosmic_audit_server.audit` regenerates them
end to end: crawl the live store → the writer drafts a report from the cached bundle → a critic loop
re-prompts on any deterministic failure until the gate is clean → render and overwrite. So the eval
isn't just grading the harness; it's *driving* what the harness produces.

That gave me a way to close the gap to `target_report.md` mechanically instead of by eye. Diffing an
auto-generated report against the target surfaced two soft weaknesses the gate didn't yet catch: the
writer leaned on one or two artifacts for most experiments, and a few experiments named a vague
sitewide change instead of a specific captured surface. So I encoded each weakness as an eval lever,
then taught the writer to clear it — the same propose→measure→gate motion the optimizer runs, done by
hand for one turn:

| Gap the target exposed | Lever added to the eval | Directive added to the writer | Measured climb |
|---|---|---|---|
| Citations bunched on a few artifacts | soft **evidence-diversity** check (distinct surfaces, max reuse ≤ 3) | "spread evidence across distinct captured surfaces" | distinct **5 → 7**, max-reuse **4 → 2**, gate now green |
| Experiments named vague sitewide changes | **surface-specificity** judge rubric (v2) | "anchor each experiment to a specific surface and name the missing module" | surface score **0.79 → 0.93** (= the target) |

Both directives are always-on guidance in the writer's base prompt (not optimizer-toggled levers), so
the offline loop's deterministic fixtures are untouched. The critic now also enforces evidence-diversity
deterministically, so the auto-audit lands both stores at **deterministic 1.00, combined ≈ 0.99, in one
attempt**. Growing the calibration set to **n=10** and re-anchoring it to the v2 rubrics re-measured real
agreement at **0.90**.

## How the human surface shrinks
| Human input today | Becomes self-sustaining by |
|---|---|
| Authoring the CRO rubric | Versioned rubrics; only re-touched when the model class changes |
| Hand-labeling the calibration set | Every human verdict in the queue → a new labeled example → recalibrate → threshold tightens → fewer escalations |
| Reviewing the residual queue | Queue size ∝ `(1 − agreement)`; as agreement climbs, the queue mechanically shrinks |
| Spotting regressions | Every production failure → an append-only regression case → a permanent gate |

The feedback is compounding: more labels → higher agreement → higher escalation threshold → smaller
human queue → humans only see the genuinely novel cases.

## 1–3 months out
- **Optimizer:** greedy forward-selection → a population search (GEPA/DSPy) over a prompt+tool space.
- **Escalation:** 3-sample self-consistency → a larger-model second opinion on the residual only.
- **Judge:** text-only → vision-grounded (read the screenshots, not just the captured text).
- **Groundedness:** structural competitor checks → search-grounded verification of competitor claims.
- **Fabrication:** cached re-probe → a nightly live re-probe sweep; drift opens regression cases.
- **Calibration:** ~9 items → a growing, production-sourced set; agreement reported continuously with its `n`.

## Where it stays human (on purpose)
Bar-setting (what "good" means) and the irreducible novel-case review. Everything else is designed
to converge toward the agreement number doing the gatekeeping — so adding stores or swapping models
costs recalibration, not a rewrite.
