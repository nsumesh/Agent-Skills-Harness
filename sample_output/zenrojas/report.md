# Zen Rojas audit — a clear wellness story the product pages don't close

## Executive summary

**Zen Rojas has a sharp wellness story; the product pages don't close it.** The storefront merchandises teas by moment — Sleep & Relaxation, Immune Support, Daily Energy, Digestion — and the Unwind PDP sells a detailed, ingredient-led story at $12. But the captured product page carries no star rating, no review count, and a "Sold Out" variant with no notify-me path, so a first-time buyer of a wellness tea gets benefits but no peer proof and a dead end on stockouts.

**The catalog is small and consumable — built for repeat revenue it isn't capturing.** With ~12 SKUs and ~15 cups per bag, tea here is a monthly consumable, yet PDPs offer only one-time purchase and there is no reorder prompt or subscribe option. The brewing essentials (infuser $5, mug $8, tea bags $5) are merchandised separately with no guided pairing, leaving both repeat revenue and basket size on the table.

**Mobile speed and discovery are the cheapest early wins.** PageSpeed mobile scored 49 against an image-heavy homepage, and the strong moment framing is buried beneath a slideshow and a single vague "Discover Your Ritual" CTA. The first test should be structural: add proof to the PDP and promote the moment cards, then layer in subscriptions and a speed fix.

## Proposed experiments

### exp-zr-conv-reviews — Add a review module to product pages

**Pillar:** Conversion
**Affected surface:** Product detail page (pattern applies to all PDPs)
**URL:** https://zenrojas.com/products/unwind
**Evidence:** screenshots/01-pdp.png
**Hypothesis:** CVR improves by placing ratings and reviews next to the price so first-time wellness-tea buyers have peer proof at the decision point. The captured Unwind PDP sells a detailed ingredient story at $12 but shows no star rating, no review count, and no testimonial anywhere on the page.
**Primary change:** Add a review module (aggregate stars + count + 2-3 reviews) directly under the product title, seeded from existing customer feedback, with a verified-buyer badge.
**Primary KPI:** PDP add-to-cart rate
**Decision rule:** Ship if PDP add-to-cart rate improves without hurting PDP bounce rate.
**Expected lift:** +6–12%
**Confidence:** 76%

### exp-zr-conv-moments — Lead the homepage with moment cards

**Pillar:** Conversion
**Affected surface:** Homepage hero
**URL:** https://zenrojas.com/
**Evidence:** screenshots/00-homepage.png
**Hypothesis:** CVR improves by promoting the existing Sleep / Immune / Energy / Digestion sections above the fold instead of a single vague "Discover Your Ritual" CTA. The captured homepage opens with a slideshow and one broad CTA, pushing the high-intent need cards far down the page.
**Primary change:** Replace the hero CTA with four tappable moment cards (Sleep, Immune, Energy, Digestion), each linking to the matching product or collection.
**Primary KPI:** Homepage click-through to product/collection
**Decision rule:** Ship if homepage click-through improves without hurting downstream conversion rate.
**Expected lift:** +5–10%
**Confidence:** 72%

### exp-zr-conv-waitlist — Capture demand on sold-out variants

**Pillar:** Conversion
**Affected surface:** PDP variant selector
**URL:** https://zenrojas.com/products/unwind
**Evidence:** content/01-pdp.md
**Hypothesis:** Recovered demand improves conversion by turning a stockout into an email capture instead of a dead end. The captured Unwind PDP shows a "Sold Out" variant with no back-in-stock or notify-me option, so high-intent shoppers who hit it simply leave.
**Primary change:** Add a "Notify me when back in stock" email capture on sold-out variants, with an automated back-in-stock email.
**Primary KPI:** Recovered-demand conversion (notify sign-up to purchase)
**Decision rule:** Ship if recovered-demand conversion improves without hurting in-stock add-to-cart rate.
**Expected lift:** +3–7%
**Confidence:** 70%

### exp-zr-aov-ritualkit — Bundle a ritual starter kit

**Pillar:** AOV
**Affected surface:** Teas collection + Sleep PDP cross-sell
**URL:** https://zenrojas.com/collections/teas
**Evidence:** content/00-homepage.md
**Hypothesis:** AOV rises by pairing a best-selling tea with the brewing essentials a new buyer needs. The captured homepage merchandises a Tea Infuser ($5), Mug ($8), and Tea Bags ($5) as standalone low-price SKUs with no guided pairing, so first-time buyers leave with tea and no easy way to brew it.
**Primary change:** Create a "Sleep Ritual Kit" (Organic Sleep Tea + infuser + mug) at a modest bundle discount, merchandised on the teas collection and the Sleep PDP.
**Primary KPI:** AOV among first-time buyers
**Decision rule:** Ship if first-time AOV rises by ≥$5 without hurting collection conversion.
**Expected lift:** +7–13%
**Confidence:** 70%

### exp-zr-aov-threshold — Surface the $35 threshold in the cart

**Pillar:** AOV
**Affected surface:** Cart drawer
**URL:** https://zenrojas.com/cart
**Evidence:** content/01-pdp.md
**Hypothesis:** AOV rises by showing shoppers how close they are to the $35 financing/shipping threshold with a one-tap add. The captured PDP advertises "Pay over time for orders over $35.00," but that threshold is invisible in the cart, so shoppers just under it get no nudge to add one more item.
**Primary change:** Add a cart progress bar toward the $35 threshold with a one-tap suggested add-on (tea bag samplers from $2 or the $5 infuser).
**Primary KPI:** AOV
**Decision rule:** Ship if AOV rises without hurting cart-to-checkout rate.
**Expected lift:** +4–9%
**Confidence:** 71%

### exp-zr-ret-subscribe — Offer subscribe-and-save on consumable teas

**Pillar:** Retention
**Affected surface:** Product detail page
**URL:** https://zenrojas.com/products/unwind
**Evidence:** content/01-pdp.md
**Hypothesis:** Repeat purchase rate improves by letting daily tea drinkers auto-replenish their staple. The captured Unwind PDP advertises ~15 cups (30g) per bag — a few weeks of daily use — but offers only one-time purchase, so loyal customers must remember to reorder.
**Primary change:** Add a "Subscribe & save 10%" toggle on consumable tea PDPs with an editable delivery cadence.
**Primary KPI:** 90-day repeat purchase rate
**Decision rule:** Ship if 90-day repeat purchase rate improves without hurting first-order conversion.
**Expected lift:** +6–11%
**Confidence:** 70%

### exp-zr-ret-reorder — Send a timed reorder reminder

**Pillar:** Retention
**Affected surface:** Lifecycle email (new)
**URL:** https://zenrojas.com/products/unwind
**Evidence:** content/01-pdp.md
**Hypothesis:** Reorder rate improves by emailing a one-tap reorder timed to when a bag runs out. With ~15 cups per bag (captured on the Unwind PDP) and no replenishment prompt today, repeat demand depends entirely on the customer remembering the brand.
**Primary change:** Trigger a reorder-reminder email ~21 days post-purchase with a pre-filled cart of the items previously bought.
**Primary KPI:** 30-day reorder rate
**Decision rule:** Ship if 30-day reorder rate improves without hurting email unsubscribe rate.
**Expected lift:** +5–10%
**Confidence:** 68%

### exp-zr-acq-schema — Add product structured data

**Pillar:** Acquisition
**Affected surface:** Homepage and PDP document head
**URL:** https://zenrojas.com/
**Evidence:** technical.json
**Hypothesis:** Organic acquisition improves by adding Product, Organization, and AggregateRating JSON-LD so listings qualify for rich results. The technical scan found no JSON-LD structured data on the homepage, so the store forfeits star ratings and price snippets in search.
**Primary change:** Add Product/Organization JSON-LD to PDPs and the homepage, including review aggregate once the review module ships.
**Primary KPI:** Organic search click-through rate
**Decision rule:** Ship if organic CTR improves without hurting page load time.
**Expected lift:** +4–8%
**Confidence:** 68%

### exp-zr-acq-quiz — Build a 'find your tea' wellness quiz

**Pillar:** Acquisition
**Affected surface:** New page at /pages/find-your-tea/
**URL:** https://zenrojas.com/pages/find-your-tea/ (new)
**Evidence:** screenshots/00-homepage.png
**Hypothesis:** Landing-page CVR improves by routing wellness-intent visitors to the matched tea before they self-navigate a 12-SKU range. The captured homepage already frames teas by moment (sleep, energy, digestion, immunity) but leaves shoppers to find the right one on their own.
**Primary change:** Add a four-question wellness quiz that returns a recommended tea, the benefit rationale, and an add-to-cart; link it from the primary nav and homepage.
**Primary KPI:** Quiz landing-page conversion rate
**Decision rule:** Ship if quiz landing-page CVR improves without hurting site-wide conversion.
**Expected lift:** +8–14%
**Confidence:** 66%

### exp-zr-perf-mobile — Cut mobile image weight

**Pillar:** Performance
**Affected surface:** Homepage and PDP imagery
**URL:** https://zenrojas.com/
**Evidence:** screenshots/00-homepage.png
**Hypothesis:** Bounce drops as mobile largest-contentful-paint improves. PageSpeed mobile scored 49 and the captured homepage ships multiple full-size CDN images (including .heic source files) above the fold, delaying first render on phones.
**Primary change:** Serve responsive compressed WebP for hero and tile imagery, lazy-load below-fold media, and defer non-critical scripts.
**Primary KPI:** Mobile LCP
**Decision rule:** Ship if mobile LCP improves without hurting homepage click-through.
**Expected lift:** +8–15%
**Confidence:** 78%

## Competitor analysis

Competitors win the wellness-tea shopper through benefit-led navigation, symptom-specific discovery, and subscriptions. Zen Rojas's edge is a small, curated organic loose-leaf range, a founder-led story, and a direct customer relationship.

| Competitor | Domain | Positioning | What they make easier | Zen Rojas edge | Pattern to adapt |
|---|---|---|---|---|---|
| Pukka Herbs | pukkaherbs.com | Organic herbal wellness tea | Benefit-led browsing (sleep, digestion, energy) across a broad range. | Smaller curated range with a founder story and a direct relationship. | Clear benefit/intention filters and ritual bundles. |
| Traditional Medicinals | traditionalmedicinals.com | Functional wellness teas by symptom | Symptom-specific shopping with strong trust cues. | Premium loose-leaf positioning and a modern, calmer brand. | Symptom-led navigation plus subscription for repeat use. |
| Yogi Tea | yogiproducts.com | Intention-based functional tea | Intention-led discovery and variety packs. | Organic loose-leaf focus and a smaller, curated catalog. | Variety / sampler packs as a low-risk trial entry. |
| Rishi Tea | rishi-tea.com | Organic loose-leaf and botanicals | Brewing education and origin storytelling. | Wellness-moment merchandising at an approachable price. | Brew guides plus subscription for loose-leaf staples. |

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
| Page Speed Mobile | Warn | PageSpeed Insights mobile performance score 49. |
| Page Speed Desktop | Warn | PageSpeed Insights desktop performance score 79. |
| Broken Links | Pass | No broken links among the homepage and /cart checks. |
| Image Optimization | Warn | Byte-level image weight not measured in this pass. |
| Cookie/Privacy | Warn | Privacy policy link present; consent mechanics not inspected. |
| Checkout Reachable | Pass | /cart reachable (200). |
