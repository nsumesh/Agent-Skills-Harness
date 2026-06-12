# Ginger People audit — strong proof, leaking buy path and mobile speed

## Executive summary

**Ginger People has the demand and the proof; the buy path is leaking it.** The storefront leads with strong proof — "World's #1 selling ginger candy," "10x more ginger," a pregnancy testimonial — over a 44-product catalog spanning candy, juice, and gingerade. But `/cart` returns a branded 404, and the homepage mixes internal "SHOP NOW" links with a raw Amazon handoff, so high-intent sessions hit dead ends and inconsistent buy paths.

**A large, use-case-rich catalog is presented as a flat list.** The 44 SKUs map cleanly to missions — nausea and travel, cooking, candy, drinks — but the products area asks shoppers to decode product names instead of shopping their job-to-be-done, and consumables like ginger juice and gingerade sell one-time only despite being natural repeat purchases.

**Mobile speed is the silent tax on all of it.** PageSpeed mobile scored 23 on a heavy homepage, throttling every session before the proof can do its work. The first test should be structural: fix the `/cart` dead end and unify the buying handoff, then organize the catalog by need and recover mobile performance.

## Proposed experiments

### exp-gp-conv-cart — Make the empty cart useful

**Pillar:** Conversion
**Affected surface:** /cart URL
**URL:** https://gingerpeople.com/cart
**Evidence:** screenshots/02-cart.png
**Hypothesis:** High-intent returning sessions are recovered by replacing the /cart 404 with a purchase-recovery page. The captured /cart returns a branded 404, and for a retailer-routed brand /cart is a common destination for returning users, old links, browser memory, and tracking tools — a dead end there silently loses demand.
**Primary change:** Replace the /cart 404 with a branded recovery page offering "Continue shopping," "Shop online retailers," "Find a store," and support links.
**Primary KPI:** /cart exit rate
**Decision rule:** Ship if /cart exit rate drops without hurting site-wide conversion.
**Expected lift:** +10–20%
**Confidence:** 84%

### exp-gp-conv-buybox — Unify the buying handoff

**Pillar:** Conversion
**Affected surface:** Homepage heroes and product hubs
**URL:** https://gingerpeople.com/gin-gins/
**Evidence:** content/00-homepage.md
**Hypothesis:** Outbound-purchase clarity improves CVR by giving every hero and product hub one consistent "Buy online / Find near me" module. The captured homepage routes one "SHOP NOW" to a raw Amazon URL and others to internal hubs, so the purchase action is ambiguous and inconsistent across the page.
**Primary change:** Add a consistent buying box (retailer logos + "Buy online" + "Find near me") to the hero and each product hub, replacing the ad-hoc mix of internal and Amazon links.
**Primary KPI:** Outbound retailer click-through rate
**Decision rule:** Ship if outbound retailer click-through improves without hurting homepage bounce rate.
**Expected lift:** +12–20%
**Confidence:** 78%

### exp-gp-conv-needfirst — Make the Products page need-first

**Pillar:** Conversion
**Affected surface:** Products grid
**URL:** https://gingerpeople.com/products/
**Evidence:** catalog.json
**Hypothesis:** CVR improves by presenting the catalog by shopper mission instead of a flat product list. The captured catalog spans 44 SKUs with distinct use cases (nausea/travel, cooking, candy, drinks), but the products area asks shoppers to decode product names rather than shop their job-to-be-done.
**Primary change:** Restructure /products/ into need-first blocks ("For nausea + travel," "For cooking," "For candy lovers," "For drinks") each with a use-case header and a "find your match" CTA.
**Primary KPI:** Products-page click-through to PDP
**Decision rule:** Ship if products-page click-through improves without hurting PDP-to-purchase conversion.
**Expected lift:** +8–14%
**Confidence:** 76%

### exp-gp-aov-sampler — Build a GIN GINS flavor sampler

**Pillar:** AOV
**Affected surface:** GIN GINS category + new sampler PDP
**URL:** https://gingerpeople.com/gin-gins/
**Evidence:** catalog.json
**Hypothesis:** AOV rises when first-time candy shoppers can buy a multi-flavor trial instead of committing to one flavor. The captured catalog lists 6+ GIN GINS flavors (mandarin, lemon, spicy apple, peanut, spicy turmeric, super strength) with no sampler entry point.
**Primary change:** Launch a "GIN GINS Flavor Tour" sampler bundling the core flavors, promoted on the GIN GINS category.
**Primary KPI:** AOV among first-time candy shoppers
**Decision rule:** Ship if first-time AOV rises by ≥$4 without hurting overall candy conversion.
**Expected lift:** +7–12%
**Confidence:** 72%

### exp-gp-aov-rescuekit — Sell a travel nausea kit

**Pillar:** AOV
**Affected surface:** Ginger Rescue PDPs + new kit
**URL:** https://gingerpeople.com/ginger-rescue-lozenges/
**Evidence:** content/00-homepage.md
**Hypothesis:** AOV rises by bundling the nausea-relief formats into one travel-ready kit. The captured homepage positions Ginger Rescue for "nausea, motion sickness & indigestion" — one of the highest-intent use cases — but sells the formats separately with no kit.
**Primary change:** Launch a "Travel Stomach Rescue Kit" (lozenges + chewables) positioned for motion sickness, morning sickness, and travel, promoted on Ginger Rescue PDPs.
**Primary KPI:** AOV among Ginger Rescue visitors
**Decision rule:** Ship if AOV rises by ≥$3 without hurting Ginger Rescue conversion.
**Expected lift:** +8–14%
**Confidence:** 70%

### exp-gp-ret-routine — Package a daily ginger + turmeric routine

**Pillar:** Retention
**Affected surface:** Turmeric Gingerade PDP + routine hub
**URL:** https://gingerpeople.com/products/ginger-soother-turmeric-gingerade/
**Evidence:** content/00-homepage.md
**Hypothesis:** Repeat purchase rate improves by turning a daily wellness habit into a named routine shoppers can reorder. The captured homepage promotes a ginger + turmeric gift set and Turmeric Gingerade but offers no reorderable daily routine.
**Primary change:** Create a "Daily Ginger + Turmeric Routine" bundle (gingerade + turmeric formats) with a subscribe option, placed on the gingerade PDPs and a routine hub.
**Primary KPI:** 30-day repeat purchase rate
**Decision rule:** Ship if 30-day repeat purchase rate improves without hurting first-order AOV.
**Expected lift:** +6–12%
**Confidence:** 68%

### exp-gp-ret-subscribe — Add subscribe-and-save to consumable juices

**Pillar:** Retention
**Affected surface:** Ginger juice / gingerade PDPs
**URL:** https://gingerpeople.com/products/organic-ginger-juice/
**Evidence:** catalog.json
**Hypothesis:** Reorder rate improves by offering subscribe-and-save on consumables. The captured catalog includes ginger juice and gingerade — regular repeat purchases — sold one-time only, so loyal customers must reorder manually each time.
**Primary change:** Add a "Subscribe & save" option to consumable juice and gingerade PDPs with an editable cadence.
**Primary KPI:** 90-day repeat purchase rate
**Decision rule:** Ship if 90-day repeat purchase rate improves without hurting first-order conversion.
**Expected lift:** +5–10%
**Confidence:** 68%

### exp-gp-acq-pregnancy — Create a pregnancy nausea page

**Pillar:** Acquisition
**Affected surface:** New page at /morning-sickness-ginger/
**URL:** https://gingerpeople.com/morning-sickness-ginger/ (new)
**Evidence:** content/00-homepage.md
**Hypothesis:** Landing-page CVR improves by matching high-anxiety morning-sickness visitors to testimonials and product choices in one compliant destination. The captured homepage carries a strong pregnancy testimonial ("I'm pregnant... 34 weeks... settled my tummy"), but morning-sickness intent has no dedicated page to land on.
**Primary change:** Create /morning-sickness-ginger/ using existing testimonials and Ginger Rescue / GIN GINS recommendations, with "ask your clinician" language and ingredient transparency.
**Primary KPI:** Landing-page conversion rate
**Decision rule:** Ship if landing-page CVR exceeds existing health pages without compliance flags.
**Expected lift:** +10–16%
**Confidence:** 70%

### exp-gp-acq-quiz — Help shoppers find their ginger

**Pillar:** Acquisition
**Affected surface:** New page at /find-your-ginger/
**URL:** https://gingerpeople.com/find-your-ginger/ (new)
**Evidence:** screenshots/00-homepage.png
**Hypothesis:** Landing-page CVR improves by routing health-intent and snack-intent visitors to the right product family via a short quiz. The captured homepage uses need language (nausea, motion sickness, digestion) but drops shoppers straight into product hubs with no guided path.
**Primary change:** Create /find-your-ginger/ with prompts for nausea, travel, cooking, daily wellness, and candy, each returning a recommendation and a "buy online / find near me" choice.
**Primary KPI:** Landing-page conversion rate
**Decision rule:** Ship if landing-page CVR improves without hurting site-wide conversion rate.
**Expected lift:** +12–18%
**Confidence:** 70%

### exp-gp-perf-mobile — Recover mobile page speed

**Pillar:** Performance
**Affected surface:** Homepage and sitewide imagery/scripts
**URL:** https://gingerpeople.com/
**Evidence:** technical.json
**Hypothesis:** Bounce drops as mobile largest-contentful-paint improves. PageSpeed mobile scored 23 on a heavy WordPress homepage with large hero images and many third-party scripts, so most sessions are throttled before the proof can land.
**Primary change:** Compress and serve responsive images, lazy-load below-fold media, defer non-critical scripts, and trim unused plugins.
**Primary KPI:** Mobile page-speed score / LCP
**Decision rule:** Ship if mobile page speed improves without hurting conversion.
**Expected lift:** +8–15%
**Confidence:** 80%

## Competitor analysis

Competitors make the shopping job easier through use-case clarity, symptom-led navigation, retailer handoffs, and flavor-led merchandising. Ginger People's edge is deeper ginger specialization, proof, reviews, recipes, health education, and broader formats.

| Competitor | Domain | Positioning | What they make easier | Ginger People edge | Pattern to adapt |
|---|---|---|---|---|---|
| Dramamine | dramamine.com | OTC motion sickness relief | Immediate use-case clarity for nausea and travel. | Natural ginger formats and candy/snack permission. | Dedicated nausea/travel pages with product-choice modules. |
| Tummydrops | tummydrops.com | Ginger/peppermint drops for nausea and digestive comfort | Symptom-specific shopping. | Broader catalog, recipes, and mainstream candy formats. | Symptom-led navigation and format comparisons. |
| Reed's | drinkreeds.com | Ginger beverages and ginger candy | Beverage-led discovery and retail familiarity. | Deeper ginger specialization and health education. | Stronger retailer handoff per product family. |
| Chimes Gourmet | chimesgourmet.com | Ginger chews and candy variety | Simple flavor-led candy shopping. | Stronger functional use cases, reviews, recipes, and family story. | Flavor sampler and heat/flavor comparison. |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Pass | HTTPS storefront loaded successfully. |
| HTTPS Redirect | Pass | http:// 301-redirected to HTTPS. |
| Sitemap | Pass | sitemap.xml present and well-formed. |
| Robots.txt | Pass | robots.txt present. |
| Critical Pages Loading | Warn | Homepage loaded; /cart returned HTTP 404. |
| Meta Tags & Social Previews | Pass | Title, meta description, and Open Graph tags present. |
| Structured Data | Pass | JSON-LD structured data found on the homepage. |
| Favicon | Pass | Favicon served. |
| Mobile-Friendly | Pass | Responsive viewport meta tag present. |
| Page Speed Mobile | Warn | PageSpeed Insights mobile performance score 23. |
| Page Speed Desktop | Warn | PageSpeed Insights desktop performance score 46. |
| Broken Links | Fail | Broken link found: /cart returned HTTP 404. |
| Image Optimization | Warn | Byte-level image weight not measured in this pass. |
| Cookie/Privacy | Warn | Privacy policy link present; consent mechanics not inspected. |
| Checkout Reachable | Fail | Checkout edge not reachable: /cart returned HTTP 404. |
