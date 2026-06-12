# Qosmic CRO Audit Harness — agent context

This repo turns a coding agent into Qosmic's storefront CRO audit agent. Input: one Shopify
storefront URL. Output: one structured audit report at the bar of `target_report.md`.

## How to run an audit
Follow the playbook in **`skills/storefront-audit/SKILL.md`**. It orchestrates the
`qosmic-audit` MCP tools, then reasons per-pillar and writes a schema-valid report.

## MCP tools (server: `qosmic_audit_server/server.py`, run with `qosmic-audit`)
- `fingerprint_store(url)` — platform + endpoint reachability → catalog branch.
- `fetch_catalog(url)` — products via products.json → sitemap → DOM waterfall.
- `crawl_storefront(url)` — screenshots + content into a cached bundle + honest manifest.
- `run_technical_checks(url)` — the 15-row technical table.

All tool logic lives in importable `core/` and `qosmic_audit_server/`; the eval imports `core/`
directly (no network hop).

## The four hard rules (override everything else)
1. **Never fabricate** — every claim ties to a captured artifact; unverifiable → honest Warn, never a fake Pass.
2. **Cite everything** — each experiment cites a real bundle artifact path or reachable URL; new surfaces cite an existing artifact as the pattern.
3. **Fingerprint, don't assume** — probe before branching; Shopify conventions may not hold.
4. **Generalize, don't overfit** — adapt archetypes to platform + catalog scale; a small clean store gets no retailer-handoff / large-catalog archetype.

## Output contract
`core/schema.py` (`AuditReport`): 4 sections, exactly 10 experiments across all 5 pillars,
3-4 competitors, ~15 technical checks. Render with `core/render.py`.

## Tests / gates
`make test` (offline gate), `make eval`, `make loop`. One make target per gate; see `journal.md`
for build status.
