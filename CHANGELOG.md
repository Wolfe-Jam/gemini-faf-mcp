# Changelog

All notable changes to gemini-faf-mcp are documented here.

## [2.0.0] - 2026-03-08

### Added
- **FastMCP MCP server** (`server.py`) — 10 tools powered by faf-python-sdk
  - `faf_read`, `faf_validate`, `faf_score`, `faf_discover`, `faf_init`
  - `faf_stringify`, `faf_context`, `faf_gemini`, `faf_agents`, `faf_about`
- **faf-python-sdk** integration for parsing, validation, and discovery
- **WJTTC 9-tier test suite** for MCP server (111 tests across Brake, Engine, Aero, Scoring, Exports, Safety, Contract, Roundtrip, Gallery)
- Console entry point: `gemini-faf-mcp` command
- `gemini-extension.json` updated for native Python MCP server

### Changed
- Python requirement: `>=3.12` → `>=3.10` (FastMCP minimum)
- Test count: 57 → 168 (111 MCP server + 57 Cloud Function)
- README restructured for clarity (MCP server first, REST API second)

### Dependencies
- Added: `fastmcp>=3.0.0`, `faf-python-sdk>=1.0.2`

## [1.1.0] - 2026-03-07

### Fixed
- `sync_faf.py` score calculation — now reads `scores.faf_score` from project.faf instead of counting top-level keys
- `sync_faf.py` tier function — proper Trophy/Gold/Silver/Bronze/Green/Yellow/Red tiers (was only "Bronze" or "Incomplete")
- GEMINI.md frontmatter corrected from 42% Incomplete to 100% Trophy

### Added
- **Input validation** on PUT endpoint: max 50 updates, 100 char keys, 10K char values (returns 400 on violation)
- **YAML round-trip validation** before GitHub commit — prevents malformed data from being committed
- **`X-FAF-Version`** response header on all endpoints (GET, POST, PUT)
- `find_faf_file` exported in package `__all__` — discovers .faf files in any directory
- Error handling in `sync_faf.py` — clear error messages and `exit(1)` on failure
- 14 new Tier 7 unit tests (input validation, YAML round-trip, find_faf_file, validate_faf edges, version consistency)

### Changed
- Test count: 43 → 57 (7 tiers + integration)

## [1.0.2] - 2026-01-31

### Added
- PyPI package with Trusted Publisher (OIDC) — no tokens needed
- `FAFClient` class with remote and local modes
- `parse_faf` and `validate_faf` functions for local .faf parsing
- MCP Registry name for ownership validation
- FAQ and CONTRIBUTING docs
- AI Agent Instructions header in README

### Changed
- Test count: 36 → 43 (added Tier 6 PyPI tests)

## [1.0.1] - 2026-01-31

### Added
- Dry-run mode (`?dry_run=true`) for testing without production pollution
- Dependabot for security-only updates

## [1.0.0] - 2026-01-30

### Added
- v2.5.1 Security Hardening: SW-01 (Temporal Integrity), SW-02 (Scoring Guard)
- BigQuery telemetry for mutation logging
- WJTTC test suite (36 tests across 5 tiers)
- Gemini Live function declarations for Voice-to-FAF

## [0.9.0] - 2026-01-29

### Added
- Voice-to-FAF: update project DNA via Gemini Live voice commands
- Multi-Agent Handshake: Context Broker for AI dialects (Claude/Gemini/Grok/Jules/Codex)
- Live SVG badge engine (GET endpoint)
- Distinction Model (100% Trophy + Big Orange)
- Bi-sync: GEMINI.md ↔ project.faf (script, GitHub Action, Cloud Build step)
- OpenAPI manifest for Vertex AI Extension
- Initial Cloud Function deployment

[2.0.0]: https://github.com/Wolfe-Jam/gemini-faf-mcp/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/Wolfe-Jam/gemini-faf-mcp/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/Wolfe-Jam/gemini-faf-mcp/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/Wolfe-Jam/gemini-faf-mcp/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Wolfe-Jam/gemini-faf-mcp/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/Wolfe-Jam/gemini-faf-mcp/releases/tag/v0.9.0
