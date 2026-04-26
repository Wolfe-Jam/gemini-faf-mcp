# Changelog

All notable changes to gemini-faf-mcp are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [2.2.1] - 2026-04-26

### Changed
- Package description aligned with the canonical "Persistent project context for Google Gemini" framing on PyPI catalog, GitHub repo metadata, `gemini-extension.json` (Gemini Extensions Gallery), and `server.json` (MCP Registry).
- `server.json` version corrected from 2.1.2 to 2.2.1 to track the published PyPI version going forward.

### Added
- `[dev]` extras now include `mypy>=1.10`, `types-PyYAML`, and `types-requests` so type checking runs clean out-of-the-box (zero stub-missing warnings).

### Notes
No runtime code changes. Patch release to surface the description alignment in the PyPI catalog (the catalog only updates on a new publish) and tighten dev tooling.

## [2.2.0] - 2026-03-29

### Added
- **Mk4 Championship Scoring Engine** — all 12 tools now use the same 21-slot scoring algorithm as Rust and TypeScript FAF engines
- `faf_score` and `faf_validate` return slot-level detail: `populated`, `active`, `total`
- 41 new WJTTC championship tests (parity, stress, security, contracts)
- Requires `faf-python-sdk>=1.1.0` for Mk4 engine

### Removed
- `sync_faf.py` — dead bi-sync script (superseded by `faf bi-sync` in faf-cli)
- `.github/workflows/faf-sync.yml` — its GitHub Action
- `cloudbuild.yaml` Step 2 — sync step removed
- `TIERS` list and `_get_tier()` helper — tier now comes from Mk4Result

### Changed
- Tier names normalized to uppercase (`TROPHY`, `GOLD`, `SILVER`, `BRONZE`, `GREEN`, `YELLOW`, `RED`) — returned as plain strings from `faf_score` and `faf_validate`
- `faf_score` error responses return `RED` for unscorable inputs
- 221 total tests (was 183)

---

## [2.1.1] - 2026-03-08

### Fixed
- **Packaging bug:** `models.py` was missing from PyPI distribution — `gemini-faf-mcp` entry point would fail with `ModuleNotFoundError: No module named 'models'`

---

## [2.1.0] - 2026-03-08

### Added
- **Tool #12: `faf_auto`** — Auto-detect project stack and generate/update .faf files
  - Scans pyproject.toml, package.json, Cargo.toml, go.mod, requirements.txt, Gemfile, composer.json
  - Detects language, framework, database, API type, build tools from actual dependencies
  - Creates new .faf if none exists, fills empty slots in existing ones
  - Priority rule: pyproject.toml/Cargo.toml/go.mod > package.json (matches faf-cli v5.0.2)
  - No hardcoded defaults — null slot is better than a wrong slot
- **`_detect_stack()` helper** — Python-native stack detection (no shelling out to faf-cli)
- **15 faf_auto tests** across Tier 2 (Engine), Tier 3 (Aero), Tier 7 (Contract), Tier 8 (Roundtrip)

### Tests
- 183/183 passing (126 MCP server + 57 Cloud Run)

---

## [2.0.1] - 2026-03-08

### Added
- **Tool #11: `faf_model`** — 100% Trophy-scored example .faf files for 15 project types
  - mcp-server, web-app, saas, cli-tool, api-service, mobile-app, chrome-extension
  - python-ml, rust-crate, library, monorepo, android-app, iot-device, desktop-app, game
  - Call without arguments to list types, with type to get complete example
- **Model library** (`models.py`) — comprehensive reference for AI to target 100% scores
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
