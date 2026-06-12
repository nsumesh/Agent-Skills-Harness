# Pillar archetypes — adapt to platform AND catalog scale

Use these as starting points, not templates. **The right archetype depends on what the
captured artifacts actually show.** Before applying one, confirm the problem exists on THIS
store. The anti-patterns below are the generalization test.

## Conversion
- Clarify an ambiguous primary CTA / hero (when the homepage entry is one vague button).
- Add a buying module / sticky add-to-cart (when the PDP buries or omits the buy action).
- Surface social proof above the fold (when reviews exist but sit below the fold — or are absent).
- Recover a broken purchase surface (when a critical page like `/cart` 404s).

## AOV
- Bundle complementary SKUs into a kit (when related items are sold only separately).
- Sampler/trial entry (when a category has many variants and no low-risk first purchase).
- Threshold nudge in cart (when free-shipping / financing thresholds are hidden until checkout).

## Retention
- Subscribe-and-save on consumables (when only one-time purchase is offered).
- Post-purchase reorder reminder (when there's no replenishment prompt for a consumable).
- Routine/bundle a recurring use-case (when content implies repeat use, e.g. a daily regimen).

## Acquisition
- Need/goal-led landing page or quiz (when intent disperses across category pages).
- Condition/use-case page (when a high-intent use case has no dedicated destination).
- Structured-data / SEO fix (when JSON-LD or rich-result markup is missing).

## Performance
- Image/asset weight + LCP fix (when PSI is low and the hero ships heavy media).
- Render-blocking / third-party script trim (when a heavy platform tanks mobile speed).

## Anti-patterns (DO NOT mis-apply)
- **Retailer handoff / "Where to buy" / store locator** — ONLY for retailer-routed brands
  that don't transact directly (e.g. gingerpeople, whose `/cart` 404s and which links out to
  Amazon). A clean transacting Shopify store (working `/cart`, `/products.json`) must NOT get this.
- **"Reorganize the large catalog" / need-first catalog restructure** — ONLY when the catalog
  is genuinely large (dozens+ of SKUs). A ~12-product store does not have a catalog-overload
  problem; proposing one is overfitting to the calibration store.
- Never propose a surface the store can't support, and never cite an artifact that wasn't captured.
