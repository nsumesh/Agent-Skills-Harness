# Qosmic CRO Audit Harness — agent context (Codex / other agents)

Same harness, same rules as `CLAUDE.md`. Input: one Shopify storefront URL → one structured
CRO audit report at the bar of `target_report.md`.

## Run an audit
Follow `skills/storefront-audit/SKILL.md`: drive the `qosmic-audit` MCP tools
(`fingerprint_store`, `fetch_catalog`, `crawl_storefront`, `run_technical_checks`), reason one
or more experiments per pillar, run the pre-write critic, then emit a schema-valid
`AuditReport` (`core/schema.py`) and render with `core/render.py`.

## Four hard rules (override everything)
1. Never fabricate — claims tie to captured artifacts; unverifiable → honest Warn.
2. Cite everything — real bundle artifact path or reachable URL per experiment.
3. Fingerprint, don't assume — probe before branching.
4. Generalize, don't overfit — adapt archetypes to platform + catalog scale (no
   retailer-handoff / large-catalog archetype on a small clean store).

## Layout
- `core/` — importable contract, renderer, probes, checks, eval API.
- `qosmic_audit_server/` — thin FastMCP server over `core/` (named off `mcp` to avoid shadowing the SDK).
- `eval/` — deterministic + judge + calibration + redteam + self-improving loop.
- `skills/storefront-audit/` — the portable playbook.
Gates: `make test` (offline), `make eval`, `make loop`.
