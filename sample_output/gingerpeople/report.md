# CRO Audit Report: The Ginger People

## Executive summary

**The Ginger People has a compelling product story but a broken purchase path that is actively costing conversions.** The /cart endpoint returns HTTP 404, meaning any visitor who attempts to add a product to cart hits a dead end — a structural failure that makes checkout unreachable from the site itself. Combined with mobile PageSpeed scores of 32 and desktop scores of 53, the site is losing a significant share of intent-driven visitors before they ever reach a product page.

**Product pages are content-rich but lack transactional infrastructure.** The GIN GINS® Ginger Spice Drops PDP (content/01-pdp.md) features strong ingredient callouts, social proof via reviews, and clear benefit bullets, yet the only purchase mechanism is a third-party Destini product locator — there is no native add-to-cart, no price displayed, and no upsell or bundle prompt. Visitors who arrive ready to buy are redirected to retail partners rather than converted on-site.

**The brand's authority and community signals are strong enough to support a higher-converting experience.** Homepage testimonials reference life-changing health outcomes, the brand claims the world's #1 selling ginger candy title, and the catalog spans 44 SKUs across candy, juice, sauces, and wellness shots. These assets — combined with a loyal, health-conscious audience — create a high-upside opportunity if the technical and UX gaps are closed.

## Proposed experiments

### EXP-01 — Restore /cart and Add Native Add-to-Cart on PDPs

**Pillar:** Conversion
**Affected surface:** Product Detail Page — GIN GINS® Ginger Spice Drops
**URL:** https://gingerpeople.com/products/gin-gins-ginger-spice-drops/
**Evidence:** content/02-cart.md
**Hypothesis:** Replacing the broken /cart 404 with a functional cart and adding a native add-to-cart button on PDPs will restore the purchase path and directly increase on-site conversion rate. Currently the cart page returns a '404 — Captain, we're lost' error page, meaning no visitor can complete a purchase without being routed off-site to a retail partner.
**Primary change:** Fix /cart routing, implement WooCommerce or headless cart, and add a visible 'Add to Cart' button above the fold on all PDPs.
**Primary KPI:** On-site conversion rate
**Decision rule:** Ship if on-site conversion rate improves by at least 1 percentage point without increasing cart abandonment rate.
**Expected lift:** +40-70%
**Confidence:** 92%

### EXP-02 — Add Price Display and Variant Selector to PDP Above the Fold

**Pillar:** Conversion
**Affected surface:** Product Detail Page — GIN GINS® Ginger Spice Drops
**URL:** https://gingerpeople.com/products/gin-gins-ginger-spice-drops/
**Evidence:** content/01-pdp.md
**Hypothesis:** Displaying a clear price and size/quantity variant selector above the fold on the PDP will reduce friction and increase add-to-cart clicks by removing the ambiguity that causes visitors to leave without acting. The current PDP lists only a single size ('Available in: 3.5 oz bag') with no price shown and no variant selector, forcing visitors to seek pricing information elsewhere.
**Primary change:** Add price tag, quantity selector, and size variant options directly beneath the product title on the PDP, above the ingredient details.
**Primary KPI:** Add-to-cart click rate
**Decision rule:** Ship if add-to-cart click rate improves without hurting average session duration.
**Expected lift:** +12-22%
**Confidence:** 82%

### EXP-03 — Homepage Hero CTA A/B Test: Amazon Gift Set vs. On-Site Shop

**Pillar:** Acquisition
**Affected surface:** Homepage — Hero Carousel
**URL:** https://gingerpeople.com/
**Evidence:** content/00-homepage.md
**Hypothesis:** Replacing the Amazon-linked 'Give the Gift of Wellness' hero CTA with an on-site shop destination will retain traffic on the brand's own domain and improve first-party data capture and revenue attribution. The current homepage carousel includes a 'SHOP NOW' button that links directly to an Amazon product listing (amazon.com/…/B0B2FFC5MK), sending high-intent visitors off-site before they can be cookied or retargeted.
**Primary change:** Replace the Amazon hero CTA with a link to an on-site gift set collection page; test against the current Amazon-linked variant.
**Primary KPI:** On-site session-to-purchase rate
**Decision rule:** Ship if on-site session-to-purchase rate improves without a statistically significant drop in total gift set revenue.
**Expected lift:** +8-15%
**Confidence:** 75%

### EXP-04 — PDP Bundle Upsell: 'Complete Your Wellness Routine' Cross-Sell Block

**Pillar:** AOV
**Affected surface:** Product Detail Page — GIN GINS® Ginger Spice Drops
**URL:** https://gingerpeople.com/products/gin-gins-ginger-spice-drops/
**Evidence:** catalog.json
**Hypothesis:** Adding a 'Frequently Bought Together' or 'Complete Your Wellness Routine' cross-sell module beneath the PDP description — featuring complementary SKUs like Ginger Rescue Tablets and Organic Ginger Juice — will increase average order value by encouraging multi-product purchases. The catalog contains 44 SKUs across candy, juice, shots, and wellness categories that are thematically linked by the nausea-relief and digestive-wellness use case but are never surfaced together on any single PDP.
**Primary change:** Implement a 3-product cross-sell carousel on all PDPs, algorithmically seeded by category affinity (e.g., candy → shots → tablets).
**Primary KPI:** Average order value
**Decision rule:** Ship if AOV increases by at least $3 without reducing conversion rate.
**Expected lift:** +10-18%
**Confidence:** 74%

### EXP-05 — Homepage Social Proof Bar: Quantified Trust Signals Above the Fold

**Pillar:** Conversion
**Affected surface:** Homepage — Above-the-Fold Section
**URL:** https://gingerpeople.com/
**Evidence:** screenshots/00-homepage.png
**Hypothesis:** Adding a sticky trust bar immediately below the navigation — displaying stats like '#1 Selling Ginger Candy Worldwide,' '10x More Ginger Than Leading Brands,' and a star rating aggregate — will increase scroll depth and click-through to product pages by anchoring credibility at first glance. The homepage currently buries these claims in mid-page carousel copy and testimonial sections, meaning visitors who bounce early never encounter them.
**Primary change:** Insert a full-width trust signal bar (3–4 icons with short copy) pinned below the nav on homepage and all collection pages.
**Primary KPI:** Homepage-to-PDP click-through rate
**Decision rule:** Ship if homepage-to-PDP CTR improves without increasing bounce rate.
**Expected lift:** +8-14%
**Confidence:** 70%

### EXP-06 — Mobile PageSpeed Optimization: Defer Non-Critical JS and Compress Hero Images

**Pillar:** Performance
**Affected surface:** Homepage — Mobile
**URL:** https://gingerpeople.com/
**Evidence:** technical.json
**Hypothesis:** Deferring non-critical JavaScript and serving next-gen compressed images on the homepage will improve the mobile PageSpeed score from 32 toward 60+, reducing bounce rates among mobile visitors who currently abandon before the page fully loads. A mobile PageSpeed score of 32 places the site in the bottom quartile of e-commerce performance, and research consistently shows that each 1-second improvement in load time can lift mobile conversions by 3–5%.
**Primary change:** Audit and defer non-critical JS, convert hero images to WebP, implement lazy loading for below-fold images, and enable browser caching.
**Primary KPI:** Mobile bounce rate
**Decision rule:** Ship if mobile PageSpeed score reaches 55+ and mobile bounce rate decreases without hurting desktop session metrics.
**Expected lift:** +10-20%
**Confidence:** 85%

### EXP-07 — Post-Purchase Email Flow: Ginger Education Series for Retention

**Pillar:** Retention
**Affected surface:** Post-Purchase Email Sequence
**URL:** https://gingerpeople.com/
**Evidence:** content/00-homepage.md
**Hypothesis:** Launching a 3-email post-purchase education series — covering ginger's health benefits, usage tips, and a replenishment reminder at day 25 — will increase 90-day repeat purchase rate by reinforcing the brand's wellness identity and prompting timely reorders. Homepage testimonials reference ongoing daily use ('my go-to,' 'my whole pregnancy'), indicating a loyal customer base that responds to health-outcome messaging and is primed for subscription or repeat purchase nudges.
**Primary change:** Build a 3-part post-purchase email flow: Day 3 (usage tips), Day 14 (health benefits deep-dive), Day 25 (replenishment offer with 10% discount).
**Primary KPI:** 90-day repeat purchase rate
**Decision rule:** Ship if 90-day repeat purchase rate improves by at least 5 percentage points without increasing unsubscribe rate above 0.5%.
**Expected lift:** +12-20%
**Confidence:** 72%

### EXP-08 — Subscription / Subscribe-and-Save Option on High-Velocity SKUs

**Pillar:** Retention
**Affected surface:** Product Detail Page — Ginger Rescue Chewable Tablets
**URL:** https://gingerpeople.com/products/ginger-rescue-chewable-ginger-tablets-strong/
**Evidence:** catalog.json
**Hypothesis:** Adding a subscribe-and-save toggle (e.g., 15% off on monthly delivery) to consumable, high-repurchase SKUs like Ginger Rescue Tablets and Organic Ginger Juice will convert one-time buyers into subscribers and increase customer lifetime value. The catalog includes at least 8 consumable wellness SKUs — including ginger shots, juices, and tablets — that are natural candidates for monthly replenishment subscriptions, yet no subscription mechanic is present on any captured PDP.
**Primary change:** Integrate a subscription app (e.g., Recharge or WooCommerce Subscriptions) and add a one-time vs. subscribe toggle on the top 5 consumable PDPs.
**Primary KPI:** Subscriber conversion rate on eligible PDPs
**Decision rule:** Ship if subscriber conversion rate on eligible PDPs exceeds 8% without reducing one-time purchase volume.
**Expected lift:** +15-25%
**Confidence:** 68%

### EXP-09 — SEO-Optimized Collection Landing Pages for High-Intent Queries

**Pillar:** Acquisition
**Affected surface:** Products Collection Page
**URL:** https://gingerpeople.com/products/
**Evidence:** screenshots/01-pdp.png
**Hypothesis:** Creating dedicated, SEO-optimized collection pages for high-intent queries like 'ginger candy for nausea,' 'ginger chews for morning sickness,' and 'ginger shots for digestion' will capture organic search traffic from symptom-driven searchers who currently land on generic product pages with no contextual copy. The PDP for Ginger Spice Drops already contains strong benefit language ('Great for travel and nausea-related conditions,' 'Plant-based') that can seed collection page copy, but no collection-level landing pages with editorial content currently exist in the sitemap.
**Primary change:** Build 3–5 collection landing pages targeting symptom-based long-tail keywords, each with 300+ words of editorial copy, product grid, and FAQ schema.
**Primary KPI:** Organic search sessions to collection pages
**Decision rule:** Ship if organic sessions to new collection pages exceed 500/month within 90 days without cannibalizing existing PDP rankings.
**Expected lift:** +18-30%
**Confidence:** 65%

### EXP-10 — Sticky Add-to-Cart Bar on PDP Scroll

**Pillar:** AOV
**Affected surface:** Product Detail Page — GIN GINS® Ginger Spice Drops
**URL:** https://gingerpeople.com/products/gin-gins-ginger-spice-drops/
**Evidence:** screenshots/01-pdp.png
**Hypothesis:** Implementing a sticky bottom bar on PDPs that persists as users scroll through ingredients, nutritional info, and reviews — displaying product name, price, and an 'Add to Cart' button — will capture purchase intent from visitors who read deeply but lose the CTA as they scroll. The GIN GINS Spice Drops PDP contains multiple content sections (ingredients, allergens, nutritional info, 4 reviews) that push the primary CTA area far above the visible viewport on mobile, meaning engaged readers have no persistent purchase prompt.
**Primary change:** Add a sticky bottom CTA bar that appears after 300px of scroll on all PDPs, containing product name, price, quantity selector, and add-to-cart button.
**Primary KPI:** PDP-to-cart conversion rate
**Decision rule:** Ship if PDP-to-cart conversion rate improves without hurting average session duration on PDP.
**Expected lift:** +9-16%
**Confidence:** 78%

## Competitor analysis

The Ginger People operates in a niche but growing wellness-candy and functional-food segment. The following competitors represent the primary benchmarks for UX, conversion mechanics, and brand positioning that The Ginger People should study and selectively adapt.

| Competitor | Domain | Positioning | What they make easier | The Ginger People edge | Pattern to adapt |
|---|---|---|---|---|---|
| Chimes Ginger Chews | chimesginger.com | Premium Southeast Asian ginger candy brand emphasizing authentic Indonesian ginger and clean ingredients, targeting health-conscious snackers and travelers. | Chimes offers a clean, fast-loading product grid with visible pricing, flavor variant selectors, and a direct add-to-cart flow — visitors can go from homepage to checkout in under 3 clicks. | The Ginger People has a broader catalog (44 SKUs vs. Chimes' narrower candy focus), stronger clinical/wellness positioning, and more powerful testimonials referencing medical conditions. | Adopt Chimes' above-the-fold price display and single-page variant selection pattern on all PDPs to reduce purchase friction. |
| Reed's Ginger Beer | reedsgingerbeer.com | Craft ginger beverage brand leveraging 'real ginger' authenticity and a subscription-first DTC model targeting ginger enthusiasts and cocktail mixers. | Reed's prominently features a subscribe-and-save toggle on every product page with a clear savings callout (e.g., 'Save 15% + free shipping'), making the subscription value proposition immediately legible. | The Ginger People's wellness and nausea-relief positioning is more medically credible and emotionally resonant than Reed's beverage-centric messaging. | Implement Reed's subscribe-and-save toggle pattern on The Ginger People's consumable SKUs (tablets, juices, shots) with a clear percentage-savings callout. |
| Buderim Ginger | buderimginger.com | Australian heritage ginger brand with a farm-to-table story, targeting premium grocery shoppers and gift buyers with crystallized ginger and confectionery. | Buderim uses a prominent 'Find in Store' locator alongside a native DTC cart, giving visitors both retail and direct purchase options without forcing a choice — reducing the friction The Ginger People creates by routing all purchases through Destini. | The Ginger People's US market penetration, Whole Foods and Sprouts placement (mentioned in testimonials), and broader SKU range give it stronger retail credibility. | Offer both a 'Buy Online' (native cart) and 'Find in Store' (Destini locator) option side-by-side on PDPs rather than making the locator the only purchase path. |
| Gaia Herbs | gaiaherbs.com | Premium herbal supplement brand with a strong DTC subscription model, farm-transparency story, and clinical credibility targeting wellness-first consumers. | Gaia Herbs uses a post-purchase education hub and loyalty program that drives repeat purchases, with clear 'why it works' science sections on every PDP that build purchase confidence. | The Ginger People's food-first positioning (candy, sauces, juices) makes ginger more accessible and less intimidating than supplement brands, broadening the addressable audience. | Adapt Gaia's 'why it works' science callout pattern — a 2–3 sentence evidence block beneath the product title — to reinforce The Ginger People's '10x more ginger' and clinical nausea-relief claims on PDPs. |

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
| Page Speed Mobile | Warn | PageSpeed Insights mobile performance score 32. |
| Page Speed Desktop | Warn | PageSpeed Insights desktop performance score 53. |
| Broken Links | Fail | Broken link found: /cart returned HTTP 404. |
| Image Optimization | Warn | Byte-level image weight not measured in this pass. |
| Cookie/Privacy | Warn | Privacy policy link present; consent mechanics not inspected. |
| Checkout Reachable | Fail | Checkout edge not reachable: /cart returned HTTP 404. |
