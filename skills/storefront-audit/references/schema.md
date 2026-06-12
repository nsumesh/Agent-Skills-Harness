# Output contract (human-readable)

The deliverable is one `AuditReport` (see `core/schema.py` for the enforced version). Four
sections, in this order. The renderer (`core/render.py`) produces the exact Markdown layout.

## Sections
1. **Title** — one headline framing the single biggest constraint (H1).
2. **Executive summary** — 2-3 prose paragraphs, each led by a **bold claim**, biggest leak first.
3. **Proposed experiments** — **exactly 10**, each `### <exp_id> — <title>`.
4. **Competitor analysis** — a 3-4 row table.
5. **Technical checks** — a ~15 row table (`Check | Status | Detail`), Pass/Warn/Fail.

## Experiment fields (all required, all non-empty)
`exp_id` and `title` render in the heading; the rest render as bold-labelled lines:

| Field | Rule |
|---|---|
| `pillar` | One of: Conversion, AOV, Retention, Acquisition, Performance |
| `affected_surface` | The UI region/page. A new page is marked "(new)". |
| `url` | The live URL (mark new pages "(new)"). |
| `evidence` | A real artifact path in this store's bundle, or a reachable URL. New surfaces cite an existing artifact as the pattern to mirror. |
| `hypothesis` | **Two parts**: predicted metric mechanism + grounded current-state observation. A full sentence. |
| `primary_change` | The concrete change being tested. |
| `primary_kpi` | The single metric the test moves. |
| `decision_rule` | Must read `Ship if <KPI> ... without <guardrail>` — the guardrail clause is mandatory. |
| `expected_lift` | A percent range, e.g. `+8–14%`. |
| `confidence` | A percent, e.g. `78%`. Tracks speculativeness: structural fixes high, new content lower. |

## The 10 experiments must
- span **all 5 pillars** (≥1 each; even spread not required),
- lead with the biggest revenue leak,
- each cite a resolvable artifact.

## Technical checks (the 15)
SSL Certificate · HTTPS Redirect · Sitemap · Robots.txt · Critical Pages Loading ·
Meta Tags & Social Previews · Structured Data · Favicon · Mobile-Friendly · Page Speed Mobile ·
Page Speed Desktop · Broken Links · Image Optimization · Cookie/Privacy · Checkout Reachable.
Status ∈ {Pass, Warn, Fail}; one-line detail; honest Warn when not inspected.
