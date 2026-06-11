<!-- faf: gemini-faf-mcp | Python | mcp-server | FAF MCP server for Google Gemini — persistent project context via PyPI -->
<!-- faf: doc=changelog | latest=v2.4.3 | canonical=project.faf | family=FAF -->

# Changelog

All notable changes to gemini-faf-mcp are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [2.4.3] - 2026-06-11

**`faf_agents` and `faf_gemini` now enhance your files.** The same solid, structured `.faf` data is prefixed to the top of AGENTS.md / GEMINI.md for rapid AI consumption upfront — and your Markdown stays in the instruction lane.

### Changed

- **Non-destructive export.** `faf_agents` and `faf_gemini` now write AGENTS.md / GEMINI.md by injecting a structured `.faf` block and preserving everything you've written below. Re-runs update the block in place (idempotent); existing faf-generated files upgrade cleanly in one pass.

## [2.4.2] - 2026-06-11 — The Confinement Edition

**Security release.** Caller-supplied `path` arguments are now confined: read tools open only `.faf` / `.fafm` context files, and `faf_init` writes only inside the project root (override with `FAF_ALLOWED_ROOTS`). Closes a path-traversal / arbitrary local-file read — and an arbitrary file write via `faf_init`.

### Security
- **Path confinement on every `path` argument (CWE-22 / CWE-73 / CWE-200).** `faf_read`, `faf_validate`, `faf_score`, `faf_stringify`, `faf_context`, `faf_gemini`, and `faf_agents` previously passed a caller path straight into `Path(path).read_text()` with no confinement, and `faf_init` into `Path(path).write_text()` — so an absolute path or `../` traversal could read any file the server uid could read (e.g. `/etc/passwd`, `/proc/self/environ`, `~/.ssh/id_rsa`) or write outside the project. New `safe_path.py` confines reads to `.faf`/`.fafm` files and writes to the project root (cwd + system temp; override via `FAF_ALLOWED_ROOTS`), canonicalizes through symlinks (closing the symlink bypass), and rejects traversal/absolute escapes. Reported via coordinated disclosure; full credit in the security advisory.

### Tests
- Added `tests/test_security_path_confinement.py` — reproduces the disclosed vectors (incl. symlink bypass and arbitrary write) as a permanent regression.
- Fixed a stale Gallery manifest test (`test_manifest_uses_uvx`) to track the intentional `run.sh` → `uvx` migration (2f6d7d8).

## [2.4.1] - 2026-06-07

### Docs
- README badges cleaned up (refreshes the README rendered on PyPI — no code changes): removed the duplicate FAF trophy badge (kept the 🏆 100%) and the rate-limited PyPI downloads badge; added both IANA media types (`vnd.faf+yaml`, `vnd.fafm+yaml`) and both Zenodo paper DOIs (Context #18251362, Memory #20348942). docs/index.html mirror bumped + Chameleon Edition social-card thumbnail added. Still The Chameleon Edition.

## [2.4.0] - 2026-06-07 — The Chameleon Edition

**One command, both modes.** gemini-faf-mcp now auto-selects its transport: **stdio** locally, **Streamable HTTP** on Cloud Run. Same binary, 12 tools, zero config — and a clean stdio handshake for every MCP client. One binary that's a local MCP server and a hosted one, decided by its environment.

### Added
- **Unified dual-transport entry point.** One command — `gemini-faf-mcp` (or `uvx gemini-faf-mcp`) — auto-selects its transport: **stdio** locally (the CLI / MCP-client path) and **Streamable HTTP** on Cloud Run (when `PORT` is set, or `MCP_TRANSPORT=http`). Same binary, same 12 tools, zero config. The console script and `python server.py` now share one `main()` entry, so both paths behave identically.

### Fixed
- **stdio handshake compatibility with standard MCP SDK clients.** The console entry now passes `transport="stdio"` explicitly instead of relying on FastMCP's default (entry point `server:mcp.run` → `server:main`). A strict MCP SDK stdio client that previously hung mid-handshake against the implicit-default entry now connects cleanly (initialize + tools/list + tools/call). Also future-proofs against any change to FastMCP's default transport — `uvx` users can never be silently flipped off stdio.

## [2.3.0] - 2026-06-07

### Added
- **Streamable HTTP transport for Cloud Run.** When `PORT` is set (or `MCP_TRANSPORT=http`), `server.py` now serves modern **Streamable HTTP** — stateless + JSON (`FASTMCP_STATELESS_HTTP` / `FASTMCP_JSON_RESPONSE`), no SSE, no session handshake. The mcpaas.live RC edge fronts this as a tool executor, forwarding `tools/list` + `tools/call` as plain JSON-RPC POSTs. The same dual-transport pattern every FAF MCP can adopt.
- Dockerfile updated for the Cloud Run / Streamable-HTTP path (`MCP_TRANSPORT=http`, stateless+JSON env, `EXPOSE 8080`).
- FAF Trophy badge + `v#` repo badge in README/docs (ecosystem badge rollout).

### Changed
- **Off deprecated SSE onto the current transport.** `uvx gemini-faf-mcp` / `pip install` stay **stdio — unchanged**; only the hosted path moves. Zero regression for CLI users (the hard gate).
- FastMCP floor raised to `>=3.4.0`; dev-dep `mypy` to `>=1.20.2`.

### Verified
- stdio regression: 221/221 tests green under fastmcp 3.4.0.
- HTTP local + Docker container + **staging Cloud Run (Linux)**: all 12 tools execute over Streamable HTTP.

## [2.2.5] - 2026-05-12

### Fixed
- **Version-string sync across three source locations.** Prior 2.2.x line had `__version__ = "2.2.1"` hardcoded in `server.py` while `pyproject.toml` advanced independently — installed users would see "version 2.2.2" in PyPI but a running server banner reading "2.2.1." Now all three locations (pyproject.toml, src/gemini_faf_mcp/client.py, server.py) bump together.
- `tests/test_wjttc_mk4.py` no longer hardcodes the version assertion — it reads `__version__` from `client.py` so the version-drift bug class fails the test suite at build time instead of materializing post-publish.

### Changed
- Publish pipeline: TestPyPI staging is now mandatory via OIDC Trusted Publisher. `git push origin v*` fires `.github/workflows/testpypi.yml` → uploads to test.pypi.org. Production publish via `gh release create` → `.github/workflows/pypi.yml`. No tokens used in either stage.

### Notes
- 2.2.3 + 2.2.4 are burned on TestPyPI (test artifacts from the staging-gate setup arc on 2026-05-11). They never shipped to production PyPI. 2.2.5 is the first production release after the discipline rebuild.
- Structural cleanup — moving `server.py`, `models.py`, `main.py` from repo root into `src/gemini_faf_mcp/` to stop polluting downstream users' global site-packages — deferred to v2.3.0.

## [2.2.2] - 2026-05-07

### Changed
- **Glory Wall URL** in module docstring: `faf-landing.vercel.app/glory.html` → `faf.one/glory`. The Glory Wall has been rehomed to the canonical brand domain (Cloudflare-hosted SvelteKit at faf.one). Cards on the new home are now clickable to each project's GitHub. The old Vercel-hosted `faf-landing` slot is being retired.

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
