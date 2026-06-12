# Prose & tone template (mirror target_report.md)

The report should read like a sharp operator who actually looked at the store, not a checklist.

## Title (H1)
One line that names the single biggest constraint, not the brand.
> e.g. "Ginger People audit — the store is back; the buy path is now the constraint"

## Executive summary (2-3 paragraphs)
- Each paragraph **opens with a bold claim** (`**...**`).
- Lead with the biggest revenue leak, grounded in concrete evidence (numbers, proof quotes,
  product names, PSI scores, a 404). Then the compounding/secondary issues. Then the
  forward-looking framing ("The first test should be structural: ...").
- Dense and opinionated — no bullet lists, no hedging.

## Experiments
- `### <exp_id> — <title>` then the bold-labelled fields.
- **Hypothesis is two parts in one sentence**: the predicted mechanism ("CVR improves by …")
  + the grounded current-state observation ("…the captured PDP shows no review module").
- **Decision rule** always: `Ship if <KPI> improves without hurting <guardrail>.`
- **Confidence** tracks risk: structural fixes (a 404, a missing module) 78-85%; brand-new
  pages/content 66-72%.
- Keep each experiment tight — a few sentences per field, concrete, no filler.

## Competitor analysis
- 3-4 real, niche-relevant competitors. Terse, data-dense cells:
  `Competitor | Domain | Positioning | What they make easier | <Store> edge | Pattern to adapt`.

## Technical checks
- The 15-row table straight from `run_technical_checks`. Keep the honest Warns — a report that
  green-checks everything is worse than one that warns truthfully.

## Voice
Specific over generic. Cite the artifact inline where it helps. Name the mechanism, not the
feature. Roughly 2,500-3,500 words total.
