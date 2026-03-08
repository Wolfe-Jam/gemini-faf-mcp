# Changelog

All notable changes to gemini-faf-mcp are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [2.0.1] - 2026-03-08

### Added
- **Gemini CLI commands** — slash commands via `.toml` files in `commands/gemini-faf-mcp/`
  - `/gemini-faf-mcp:setup` — one-shot project DNA setup (faf_init → faf_score)
  - `/gemini-faf-mcp:score` — quick score check with improvement suggestions
  - `/gemini-faf-mcp:export` — export to GEMINI.md, AGENTS.md, or both
- **Setup guide** (`docs/SETUP.md`) — install, first run, troubleshooting
- **System requirements** (`docs/SYS-REQS.md`) — 15 FRs, 6 NFRs, test architecture

### Fixed
- `faf_discover` now rejects directories — only matches actual `.faf` files
- Cloud Run POST 500 — `datetime` objects from YAML now serialize via `FafJSONEncoder`
- Tier 9 gallery tests updated for `run.sh` manifest (was checking for `python3` command)

### Changed
- All 10 tool docstrings expanded (1 → 3 lines) for better Gemini tool selection
- `GEMINI.md` rewritten with quick start, commands table, tier system, how-it-works flow
- `gemini-extension.json` description now action-oriented
- `project.faf` human_context updated with full 6Ws
- Setup command simplified from wizard (~200 lines) to one-shot faf_init (~20 lines)

### Tests
- 168/168 passing (111 MCP server + 57 Cloud Run)
- Cloud Run deployed and verified

---

_Prior versions (v0.9.0 → v2.0.0) delivered the FastMCP server, Cloud Run API, PyPI package, WJTTC test suite, and faf-python-sdk integration. History starts fresh from here._
