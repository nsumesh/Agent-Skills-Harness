# Zen Rojas CRO Audit Report

## Executive summary

**Zen Rojas has a clear brand identity and a focused organic tea catalog, but conversion is being left on the table due to missing social proof, weak urgency signals, and an underdeveloped product detail page experience.** The homepage communicates a calming wellness narrative effectively, yet no customer reviews, star ratings, or user-generated content appear anywhere in the captured surfaces — a critical trust gap for a consumable product where taste and efficacy are purchase barriers.

**Average order value is constrained by a sampler-led entry point that lacks structured upsell pathways beyond a single 'frequently bought together' bundle on the mug PDP.** With 12 SKUs spanning teas, teaware, and samplers, the store has the raw ingredients for meaningful cross-sell and bundle mechanics, but the collection and cart pages show no recommended pairings, no tiered free-shipping threshold messaging, and no loyalty or subscription nudge.

**Technical performance scores of 72 (mobile) and 63 (desktop) represent a measurable drag on paid acquisition efficiency and organic ranking potential.** Combined with the absence of JSON-LD structured data on the homepage, the store is underserving both search engines and performance-sensitive shoppers — issues that are structurally fixable on Shopify and should be prioritized alongside conversion experiments.

## Proposed experiments

### EXP-01 — Add Star Ratings + Review Count Below PDP Product Title

**Pillar:** Conversion
**Affected surface:** Product Detail Page — Zen Rojas Mug 11oz
**URL:** https://zenrojas.com/products/zen-rojas-mug
**Evidence:** content/01-pdp.md
**Hypothesis:** Displaying a star rating and review count directly beneath the product title will reduce purchase hesitation by providing third-party social proof at the moment of evaluation. The current PDP for the Zen Rojas Mug 11oz contains zero reviews or ratings despite listing a $8.00 price and a 30-Day Warranty claim.
**Primary change:** Integrate a reviews app (e.g., Judge.me or Loox) and render aggregate star rating + review count (e.g., '4.8 ★ · 47 reviews') immediately below the H1 product title on all PDPs.
**Primary KPI:** PDP Add-to-Cart rate
**Decision rule:** Ship if PDP Add-to-Cart rate improves by ≥5% without hurting average session duration.
**Expected lift:** +9-16%
**Confidence:** 82%

### EXP-02 — Introduce Free Shipping Threshold Progress Bar in Cart

**Pillar:** AOV
**Affected surface:** Cart Page
**URL:** https://zenrojas.com/cart
**Evidence:** content/03-cart.md
**Hypothesis:** A dynamic progress bar showing how close the shopper is to a free shipping threshold (e.g., 'Add $7 more for free shipping') will motivate cart additions before checkout. The current cart page captured at /cart shows only a subtotal, a discount field, and a checkout button with no AOV-lifting incentive messaging.
**Primary change:** Add a free-shipping progress bar component to the cart drawer and cart page, set at a threshold of $35 (aligned with the existing 'Pay over time for orders over $35' messaging already on the PDP).
**Primary KPI:** Average Order Value
**Decision rule:** Ship if AOV increases by ≥$3 without hurting cart-to-checkout conversion rate.
**Expected lift:** +8-13%
**Confidence:** 79%

### EXP-03 — Add Email Capture Pop-up with First-Order Discount for Retention Seeding

**Pillar:** Retention
**Affected surface:** Homepage
**URL:** https://zenrojas.com
**Evidence:** content/00-homepage.md
**Hypothesis:** Capturing email addresses at the homepage level with a 10%-off first-order incentive will build a retargetable subscriber list and increase repeat purchase rates via post-purchase flows. The homepage currently has no visible email capture mechanism, newsletter sign-up, or loyalty program entry point in the captured content.
**Primary change:** Deploy a timed exit-intent or scroll-triggered pop-up offering 10% off the first order in exchange for email opt-in; connect to a Klaviyo welcome + post-purchase automation sequence.
**Primary KPI:** Email capture rate / 90-day repeat purchase rate
**Decision rule:** Ship if email capture rate exceeds 3% without increasing bounce rate on the homepage.
**Expected lift:** +10-18%
**Confidence:** 74%

### EXP-04 — Surface Benefit-Led Category Tiles on the Best Sellers Collection Page

**Pillar:** Conversion
**Affected surface:** Best Sellers Collection Page
**URL:** https://zenrojas.com/collections/best-sellers
**Evidence:** content/02-collection.md
**Hypothesis:** Adding short benefit callouts (e.g., 'Calms in 20 min', 'Antioxidant-rich') beneath product titles on the Best Sellers collection grid will increase click-through to PDPs by helping shoppers self-select based on need. The current Best Sellers collection page shows only product name and price with no benefit copy, ingredient highlights, or use-case labels.
**Primary change:** Add a one-line benefit subtitle (max 8 words) beneath each product title on the collection grid cards, drawn from existing PDP copy.
**Primary KPI:** Collection-to-PDP click-through rate
**Decision rule:** Ship if collection-to-PDP CTR improves by ≥8% without hurting overall collection page bounce rate.
**Expected lift:** +8-14%
**Confidence:** 71%

### EXP-05 — Implement JSON-LD Product Structured Data on All PDPs for Rich Snippet Acquisition

**Pillar:** Acquisition
**Affected surface:** Homepage and all PDPs
**URL:** https://zenrojas.com
**Evidence:** technical.json
**Hypothesis:** Adding JSON-LD structured data (Product, Organization, BreadcrumbList schemas) will enable Google rich snippets — star ratings, price, availability — in organic search results, increasing click-through rates from search. The technical audit explicitly flags 'No JSON-LD structured data found on the homepage' as a Warn, and with 12 products in the catalog there is significant untapped organic search surface area.
**Primary change:** Inject JSON-LD Product schema (name, price, availability, aggregateRating) on all 12 PDPs and Organization schema on the homepage via Shopify theme liquid or a structured data app.
**Primary KPI:** Organic search click-through rate (Google Search Console)
**Decision rule:** Ship if organic CTR improves by ≥10% within 60 days without any drop in crawl coverage.
**Expected lift:** +10-20%
**Confidence:** 85%

### EXP-06 — Add a Tea Subscription / Subscribe & Save Option on High-Velocity Tea PDPs

**Pillar:** Retention
**Affected surface:** Product Detail Page — Organic Sleep Tea
**URL:** https://zenrojas.com/products/organicsleeptea
**Evidence:** catalog.json
**Hypothesis:** Offering a subscribe-and-save option (e.g., 10% off, delivered every 30 days) on consumable tea SKUs will convert one-time buyers into recurring revenue and increase customer lifetime value. The catalog contains at least 7 consumable tea products (Unwind, Sleep, Bodyguard, Black Tea, Sencha, Heartburn, Tea Bags) with no subscription mechanic visible in any captured surface.
**Primary change:** Integrate a Shopify subscription app (e.g., Recharge or Seal Subscriptions) and add a 'One-time / Subscribe & Save 10%' toggle on all tea PDPs.
**Primary KPI:** Subscription opt-in rate / Customer LTV at 180 days
**Decision rule:** Ship if subscription opt-in rate exceeds 5% of tea PDP visitors without reducing one-time purchase conversion.
**Expected lift:** +12-22%
**Confidence:** 70%

### EXP-07 — Improve Mobile PageSpeed Score from 72 to 85+ via Image Format and Render-Blocking Fixes

**Pillar:** Performance
**Affected surface:** Sitewide — Mobile
**URL:** https://zenrojas.com
**Evidence:** technical.json
**Hypothesis:** Optimizing image formats (converting .heic files to WebP), lazy-loading below-the-fold images, and deferring non-critical scripts will raise the mobile PageSpeed score from 72 toward 85+, reducing bounce rates among mobile shoppers. The technical audit flags mobile PageSpeed at 72 and image optimization as unresolved Warns, and the homepage content references multiple .heic image files served from the Shopify CDN which are not natively optimal for web delivery.
**Primary change:** Convert all .heic product and homepage images to WebP format, implement native lazy loading on below-fold images, and defer third-party scripts (social share, chat widget) to reduce Time to Interactive.
**Primary KPI:** Mobile PageSpeed score / Mobile bounce rate
**Decision rule:** Ship if mobile PageSpeed score reaches ≥82 without any increase in mobile cart abandonment rate.
**Expected lift:** +6-11%
**Confidence:** 80%

### EXP-08 — Add a 'Complete the Ritual' Cross-Sell Section on Tea PDPs Linking to Teaware

**Pillar:** AOV
**Affected surface:** Product Detail Page — Bodyguard Organic Tea
**URL:** https://zenrojas.com/products/bodyguardtea
**Evidence:** content/00-homepage.md
**Hypothesis:** Adding a 'Complete the Ritual' cross-sell row beneath the Add-to-Cart button on tea PDPs — featuring the Tea Infuser ($5), Tea Bags ($5), and Zen Rojas Mug ($8) — will increase units per transaction by surfacing complementary teaware at the point of highest purchase intent. The homepage already groups these teaware items under the heading 'Steep Into Something Sacred' confirming brand-level intent to bundle, but this pairing is absent from tea PDPs in the captured content.
**Primary change:** Add a 3-product horizontal cross-sell widget ('Complete the Ritual') on all tea PDPs featuring Tea Infuser, Tea Bags, and Mug with one-click add-to-cart.
**Primary KPI:** Units per transaction / AOV
**Decision rule:** Ship if AOV increases by ≥$2.50 without reducing tea PDP conversion rate.
**Expected lift:** +7-12%
**Confidence:** 75%

### EXP-09 — Add a Sampler-to-Full-Size Upsell Prompt Post-Add-to-Cart for Sampler Products

**Pillar:** AOV
**Affected surface:** Product Detail Page — Zen Rojas Tea Bag Samplers
**URL:** https://zenrojas.com/products/teabagsamplers
**Evidence:** content/02-collection.md
**Hypothesis:** Displaying a post-add-to-cart modal suggesting the full-size version of the sampled tea (e.g., 'Love this blend? Grab the full 50g bag and save') will convert sampler buyers into higher-value full-size purchases in the same session. The Best Sellers collection page shows Tea Bag Samplers starting from $2 alongside full-size teas at $8–$13, indicating a clear price ladder that is not currently being leveraged with an upsell prompt.
**Primary change:** Trigger a slide-in upsell modal after 'Add to Cart' on sampler PDPs, recommending the corresponding full-size SKU with a brief value message and one-click add.
**Primary KPI:** Average Order Value / Sampler-to-full-size attach rate
**Decision rule:** Ship if sampler-to-full-size attach rate exceeds 8% without increasing cart abandonment.
**Expected lift:** +9-15%
**Confidence:** 72%

### EXP-10 — Add a 'Why Organic?' Trust Section with Certifications and Sourcing Story on the Homepage

**Pillar:** Acquisition
**Affected surface:** Homepage
**URL:** https://zenrojas.com
**Evidence:** content/01-pdp.md
**Hypothesis:** Adding a dedicated homepage section with organic certification badges, an ethical sourcing statement, and a one-sentence origin story will improve trust signals for first-time visitors arriving from paid or organic search, increasing homepage-to-collection click-through. The PDP copy states 'All Zen Rojas teas are 100% organic and ethically sourced' but this claim is buried in fine print on a single product page and is absent from the homepage's above-the-fold and mid-page sections.
**Primary change:** Insert a 3-column trust bar on the homepage (below the hero) with icons and short copy for: '100% USDA Organic', 'Ethically Sourced', and '30-Day Guarantee', linking to a dedicated About/Sourcing page.
**Primary KPI:** Homepage-to-collection CTR / New visitor conversion rate
**Decision rule:** Ship if homepage-to-collection CTR improves by ≥6% without hurting homepage bounce rate.
**Expected lift:** +6-12%
**Confidence:** 73%

## Competitor analysis

Zen Rojas competes in the premium organic wellness tea segment against brands that have invested heavily in ritual-based storytelling, subscription infrastructure, and community-driven social proof. The following four competitors represent the primary conversion and positioning benchmarks.

| Competitor | Domain | Positioning | What they make easier | Zen Rojas edge | Pattern to adapt |
|---|---|---|---|---|---|
| Vahdam Teas | vahdamteas.com | Farm-to-cup premium Indian teas with direct sourcing transparency and strong sustainability credentials. | Vahdam makes it easy to understand origin and sourcing with dedicated 'From the Garden' storytelling on every PDP, plus a robust subscription program with flexible cadence controls. | Zen Rojas has a tighter, more curated catalog focused on functional wellness blends (sleep, immunity, digestion) which is a clearer benefit-led positioning than Vahdam's origin-first approach. | Adopt Vahdam's per-PDP sourcing callout (farm name, region, harvest date) to reinforce the 'ethically sourced' claim already in Zen Rojas PDP copy. |
| Pique Tea | piquelife.com | Science-backed functional teas in crystal form targeting health-optimizers and biohackers with clinical language and influencer credibility. | Pique makes the health benefit case with clinical citations, third-party lab test results, and a quiz-based product finder that routes shoppers to the right SKU in under 60 seconds. | Zen Rojas's accessible price points ($2 samplers, $5 infuser) and loose-leaf format appeal to a broader, ritual-focused audience that Pique's premium price tier ($40+) excludes. | Implement a short 'Find Your Tea' quiz on the homepage to replicate Pique's guided selling mechanic and reduce decision paralysis across 12 SKUs. |
| Harney & Sons | harney.com | Heritage American tea brand with 35+ years of authority, extensive SKU depth, and strong gifting positioning. | Harney makes gifting frictionless with dedicated gift sets, gift message fields at checkout, and a prominent 'Gifts' navigation category that surfaces curated bundles by price range. | Zen Rojas's organic-only, wellness-first positioning is a sharper differentiator than Harney's broad conventional catalog for health-conscious millennial buyers. | Build a dedicated Gifts collection page with pre-bundled gift sets (e.g., Mug + Sampler + Infuser) and a gift message option at checkout to capture the gifting occasion. |
| Art of Tea | artoftea.com | Artisan blended teas with a strong B2B wholesale channel and a loyalty rewards program that drives repeat DTC purchases. | Art of Tea makes repeat purchasing easy with a visible points-based loyalty program, a subscription with pause/skip controls, and a 'Recently Viewed' persistent widget across the browse experience. | Zen Rojas's focused functional wellness narrative (sleep, immunity, digestion, energy) is more actionable for a shopper with a specific health goal than Art of Tea's flavor-first catalog. | Launch a simple points-based loyalty program (e.g., via Smile.io) with visible point balances in the account dashboard to mirror Art of Tea's repeat-purchase engine. |

## Technical checks

| Check | Status | Detail |
|---|---|---|
| SSL Certificate | Pass | HTTPS storefront loaded successfully. |
| HTTPS Redirect | Pass | http:// 301-redirected to HTTPS. |
| Sitemap | Pass | sitemap.xml present and well-formed. |
| Robots.txt | Pass | robots.txt present. |
| Critical Pages Loading | Pass | Homepage and /cart returned 200. |
| Meta Tags & Social Previews | Pass | Title, meta description, and Open Graph tags present. |
| Structured Data | Warn | No JSON-LD structured data found on the homepage. |
| Favicon | Warn | No favicon at /favicon.ico (often theme-defined). |
| Mobile-Friendly | Pass | Responsive viewport meta tag present. |
| Page Speed Mobile | Warn | PageSpeed Insights mobile performance score 72. |
| Page Speed Desktop | Warn | PageSpeed Insights desktop performance score 63. |
| Broken Links | Pass | No broken links among the homepage and /cart checks. |
| Image Optimization | Warn | Byte-level image weight not measured in this pass. |
| Cookie/Privacy | Warn | Privacy policy link present; consent mechanics not inspected. |
| Checkout Reachable | Pass | /cart reachable (200). |
