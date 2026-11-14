<!-- faf: gemini-faf-mcp | Python | mcp | FAF MCP server for Google Gemini — persistent project context via PyPI -->
<!-- faf: doc=changelog | latest=v3.2.1 | canonical=project.faf | family=FAF -->

# Changelog

All notable changes to gemini-faf-mcp are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [Unreleased]

### Fixed
- **3.2.1's project fix now works on the plugin's default launch.** The plugin started the server with `uvx gemini-faf-mcp`, and that command goes through uv's `#!/bin/sh` launcher. The shell resets `PWD` to the folder it starts in (the plugin folder), so the server could not see where `agy` was run: `faf_discover` found the plugin's own `project.faf`, and a relative write went into the plugin folder. The plugin now starts Python directly (`uvx --from "gemini-faf-mcp>=3.2.1" python -I -X utf8 -m server`), which keeps `PWD`. `-I` keeps the current folder off Python's import path, so a project's own `server.py` is never run in place of ours. `-X utf8` reads and writes files as UTF-8 on every platform (`-I` ignores `PYTHONUTF8`). `>=3.2.1` stops an older `uv tool install` copy, without the project fix, from being used. Other MCP clients are unchanged.

## [3.2.1] - 2026-11-11 — The Straight Answers Edition

**3.2.1 lifts gemini-faf-mcp into Antigravity CLI: it installs as a plugin and works in your project.**

Antigravity CLI (`agy`) is Google's successor to Gemini CLI. Install: `agy plugin install https://github.com/Wolfe-Jam/gemini-faf-mcp`, then run `/setup` in your project.

345 tests pass, 0 fail.

### Fixed
- **Works in your project under Antigravity CLI.** `agy` starts a plugin's MCP server in the plugin's own folder (`~/.gemini/config/plugins/gemini-faf-mcp`), so every write to your project was refused ("path escapes FAF_ALLOWED_ROOTS") and `faf_discover` found the plugin's own `project.faf`. At startup (local stdio only), when `PLUGIN_ROOT` (which Antigravity sets for every plugin MCP server) is the current folder and `PWD` is another existing folder, the server works there: the folder `agy` was run in. It never moves to `/`, your home folder, a folder that contains the plugin folder, or a folder inside it; then it stays put and writes stay refused. Nothing changes for Claude Code, Gemini CLI, `uvx` by hand, a dev checkout or the hosted server (none set `PLUGIN_ROOT`). Not fixed on Windows, where `PWD` is usually unset. (`agy`'s plugin config fills in no workspace variable, and agy 1.5.5 can't answer an MCP roots round trip.) Checked under the real `agy` 1.5.5: `faf_discover` finds the project's file, `faf_init` writes into the project, and a non-UTF-8 GEMINI.md is refused by its own rule.
- **The extension converts to an Antigravity plugin.** The repo carried `.gemini/project.faf`, a link to `../project.faf` used only while working on this repo. Gemini CLI's install rewrote it to point at a temporary folder that it then deleted, so `agy plugin import gemini` stopped with `stat …/.gemini/project.faf: no such file or directory`. The `.gemini/` folder is gone (the link and a stale `context.yaml`; nothing used them), and a test fails if the repo tracks a symlink again.

### Changed
- **Antigravity CLI first** in the README, `docs/SETUP.md` and the project page: install with `agy plugin install https://github.com/Wolfe-Jam/gemini-faf-mcp`; a note for anyone moving from Gemini CLI (and the fix for the import error above); the Gemini CLI line kept for work accounts. The skills are named `setup`, `score` and `export` in Antigravity (`/faf:…` in Gemini CLI). `docs/SETUP.md` needs Python 3.11+, not 3.10. `gemini-faf-mcp --help`, the extension description and the skill prompts no longer send people to Gemini CLI only.
- **`project.faf` describes the Antigravity era** (who, where, how, current focus), and `when` is now the stage and since when (`Stable since Jan 2026; moving to Antigravity CLI`) instead of a usage line. Still ✪ 100%; CLAUDE.md re-synced.

## [3.2.0] - 2026-11-08 — The Straight Answers Edition

**Every gemini-faf-mcp failure now reaches your client as an error: MCP's isError is set, the reason text is unchanged, and /faf:setup checks before it creates.**

**Heads up:** Python scripts that call these tools through FastMCP's `Client.call_tool` now get a `ToolError` on a failure unless they pass `raise_on_error=False`. MCP clients that read `isError` now take their error path, with the same text.

320 tests pass, 0 fail.

### Fixed
- **A tool that answers `success: false` now sets MCP's `isError`.** A missing file, invalid YAML, a refused write, a path outside the project: each used to come back as an ordinary result, so a client that reads `isError` saw success. The dict is unchanged (same content and structured content), and calling the tool functions directly is unchanged. It covers both failure shapes: `{"success": false, ...}` (22 returns) and `{"error": ...}` with no `success` (`faf_score`'s missing file and path outside the project, `faf_model`'s unknown type). One middleware, `_FailureIsError` in `server.py`.
- **`faf_score` on a file the kernel can't read says so.** Syntax errors, duplicate keys and more than one document used to score 0, White, with no error; now they return `error: "Invalid YAML: …"` (and `isError`). The check uses the kernel's own YAML loader, the one the score uses (faf-cli parity), so a file faf-cli scores is never called invalid (a YAML tag is fine). An empty file, or YAML that isn't a mapping, still scores 0, White, as a result, as the kernel scores it; `faf_read` and `faf_validate` reject a non-mapping.

### Changed
- **Who sees the difference:** an MCP client that reads `isError` now takes its error path for these calls (the text is the same). A Python caller of FastMCP's `Client.call_tool` now gets a `ToolError` for them unless it passes `raise_on_error=False`. A success is unchanged, byte for byte.
- **`faf_discover` also returns `searched_from` when it finds a file** (it already did when it found none), so a caller can tell this directory's `project.faf` from a parent's.
- **`/faf:setup` checks before it creates.** It runs `faf_discover` first and scores an existing `project.faf` in this directory; `faf_init` runs only when there is none. Before, it always called `faf_init` and read "file already exists" as the normal path, which is now an error result.

## [3.1.2] - 2026-11-05

**faf_gemini and faf_agents keep your hand-written GEMINI.md and AGENTS.md, and tell you what they couldn't write.**

308 tests pass, 0 fail.

### Fixed
- **GEMINI.md and AGENTS.md are written by faf-cli's rules** ([#45](https://github.com/Wolfe-Jam/gemini-faf-mcp/pull/45)), the same ones faf-cli, faf-mcp, claude-faf-mcp and grok-faf-mcp follow. faf replaces only the block between its own marker lines; a file whose first line looks like a faf stamp is never reclaimed, and a START with no END cuts nothing.
- **Markers count only as whole lines outside code** (CommonMark fences), never as text in prose or an example.
- **Refused, nothing written:** a file that isn't UTF-8 text (incl. UTF-16 without a BOM), a dangling link, a link out of the project or into `.git/`, a link to a differently named file (except between AI context files), a read-only file. `faf_gemini` / `faf_agents` reply `success: false` with the reason; they used to say "existing content preserved" either way.
- **Atomic writes** that keep permissions, a CRLF file's line endings and a leading BOM; new files follow your umask.
- **`/faf:export`** no longer tells the model to write GEMINI.md / AGENTS.md itself (which would replace the whole file); the tools write them.

## [3.1.1] - 2026-10-16

**`gemini-faf-mcp --version` and `--help` answer and exit. Before, both started the server.**

281 tests pass, 0 fail.

### Fixed
- `--version` / `-V` prints `gemini-faf-mcp 3.1.1` and exits 0; `--help` / `-h` prints usage and a client config and exits 0. Both used to start the server, print the FastMCP banner and wait for a client, with no version on stdout. Any other argument still starts the server, so client configs don't change. New `tests/test_cli_flags.py` runs each flag with stdin closed and a time limit.

### Changed
- `pyproject.toml` lists a `Repository` URL, so PyPI shows where the source lives.

## [3.1.0] - 2026-10-05 — The New Era Edition

**Glass-box tools: every Gemini tool now says what it does — reads, writes or rewrites — so your client knows when to ask first. In Gemini CLI and Google Antigravity.**

275 tests pass, 0 fail.

### Added
- **Its own card, refreshed.** `agent.fafa` is written with faf-cli 8.2's `faf card init` (3.1.0, all 13 tools, the hosted MCP endpoint), and the MCP Server Card (`server-card`) is rebuilt from it with `faf cards --target mcp`: 3.1.0, the hosted remote, FAF's context. Both were at 2.8.0 with 12 tools.
- **README: Google Antigravity**, with the local (`uvx`) and hosted (`serverUrl`) configs.
- **Tool annotations on all 13 tools**, checked against each tool's code: read-only `faf_read`, `faf_validate`, `faf_score`, `faf_discover`, `faf_stringify`, `faf_context`, `faf_about`, `faf_model`; non-destructive writers `faf_init` (refuses to overwrite), `faf_auto` (fills empty slots only), `faf_gemini` and `faf_agents` (update faf's own block, keep the rest); destructive `faf_migrate`. None is open-world. New `TestToolAnnotations` tests.

### Changed
- Every mention of the slash commands uses their real names, `/faf:setup`, `/faf:score` and `/faf:export` (Gemini CLI names `commands/faf/setup.toml` as `/faf:setup`): in `/faf:score` and `/faf:export` themselves, `docs/SETUP.md`, `docs/SYS-REQS.md` and `project.faf`. They said `/gemini-faf-mcp:setup` and `/gemini-faf-mcp:score`.
- README: the setup step shows the real flow (starter file → fill it from your repo → `/faf:score`) instead of a fixed score; header tagline is "FAF defines. AGENTS.md instructs. AI codes."
- Removed `.well-known/ai-catalog.json`: its entry pointed to `faf.one/.well-known/fafa`, which is FAFA's passport, not Gemini's. A catalog entry returns when Gemini's passport has its own served address.

### Fixed
- `faf_migrate` re-serializes the whole file, so YAML comments and formatting are lost; its description now says so, and it is annotated as destructive. A test checks a comment does not survive, so the label stays earned.
- `faf_about` reported `"tools": 12`; the server has 13. The test now compares it with the live `tools/list` count instead of a fixed number.
- **The hosted function scores always-33.** `faf-source-of-truth` (Cloud Function, `main.py`) had its own scorer: it trusted a `scores.faf_score` written inside the file, or else counted top-level keys over 21. `calculate_score` now uses `faf_sdk.score_faf`, the same kernel-exact score as every FAF app, and never trusts a score the file claims for itself. Not in the PyPI package (`main.py` is hosted-only); deployed by the Cloud Build trigger on merge.

## [3.0.0] - 2026-09-28 — The Always33 Edition

One engine, one number: gemini-faf-mcp scores with the always-33 engine, exactly like faf-kernel — the same score faf-cli 8, claude-faf-mcp 7, faf-mcp 4 and grok-faf-mcp 2 give.

### Changed (breaking — scores move)
- **`faf-python-sdk>=2.0.0`** — the SDK's `score_faf` now returns exactly what
  faf-kernel returns. Every tool that reports a score (`faf_score`,
  `faf_validate`, `faf_context`, `faf_gemini`, `faf_agents`, `faf_auto`) scores
  against 33 slots: the 12 enterprise slots count unless marked `slotignored`.
  `total` is 33. A file with 21 slots filled and no markers scores 64% (21/33);
  the same file plus the 12 markers scores 100% (21/21).
- The 15 `faf_model` reference templates carry the 12 enterprise slots —
  `slotignored` where they do not apply; the `monorepo` template fills
  `packages_count`, `build_orchestrator`, `shared_configs`, `remote_cache`. Every
  template is still 100% Trophy (checked against faf-kernel and
  `faf-cli@8.0.0 check --strict`).
- `faf_auto` writes all 12 enterprise slots when it creates a `project.faf`
  (`slotignored` unless detection fills them, e.g. `package_manager`), so a fresh
  file scores what it did under 2.x instead of dropping: a FastAPI + psycopg2
  project scores 77 (10/13), not 45.
- CI checks `project.faf` with `faf-cli@8.0.0` (was 7.10.1).
- `gemini-extension.json`, `server.json`, `project.faf`, `AGENTS.md` version → 3.0.0.

### Upgrading
- Files without the 12 enterprise markers score lower. `faf auto` (faf-cli)
  writes the 12 markers.

## [2.8.2] - 2026-09-11 — The Full-Facts Edition

**Privacy patch — `FAFClient`'s start-up ping is now opt-in (`FAF_TELEMETRY=1`).**

### Changed
- `FAFClient`'s start-up ping is now opt-in: it sends only when `FAF_TELEMETRY=1`. It used to send by default, and the opt-out wasn't documented. `FAF_TELEMETRY_OFF` still turns it off. The MCP server never used `FAFClient`.
- `gemini-extension.json`, `server.json`, `project.faf`, `AGENTS.md` version → 2.8.2.

**13 tools · 265 tests.**

## [2.8.1] - 2026-09-08 — The Full-Facts Edition

Dependency patch — no behavior change.

### Changed
- `faf-python-sdk` floor `>=1.4.0`. The SDK renamed its interop functions: the
  public names are now `author_agents_md` / `author_gemini_md` (`generate_*`
  still works there as a deprecated alias, removed in the SDK's 2.0). `faf_agents`
  and `faf_gemini` call the new names. **Authored AGENTS.md / GEMINI.md output is
  byte-identical** — a naming change in the dependency, not a behavior change.
- `gemini-extension.json`, `server.json`, `project.faf`, `AGENTS.md` version → 2.8.1.

**13 tools · 262 tests.**

## [2.8.0] - 2026-09-07 — The Full-Facts Edition

**`faf_auto` now grounds its detection in the repo's own files, and every `faf_model` reference template scores 100% Trophy.**

### Added

- **Full-Facts grounding for `faf_auto`** (`interrogate.py`, in parity with faf-cli 7.10). After the root-manifest scan, `faf_auto` reads:
  - **docker-compose service images** — `postgres` / `redis` / `elasticsearch` / `minio` / `clickhouse` / `qdrant` / … map onto the `database` / `cache` / `search` / `storage` slots. A running Postgres service **is** the database — it wins over a dependency guess (an ORM in `requirements.txt` is not the DB).
  - **Makefile / justfile targets** — `test` / `build` / `check-all` map onto the `commands` block. The root file wins; a nested `backend/Makefile` is found and prefixed with `cd backend &&`.
  - **`.github/workflows/`** → `cicd: GitHub Actions` (also GitLab CI, CircleCI).
  A polyglot repo that reported `library` / `JavaScript` now reports its real Postgres + Redis + FastAPI stack.
- The `faf_auto` template now writes the full 12-slot stack plus a `commands` block and `key_files`.

### Fixed

- **Every `faf_model` reference template now scores 100% Trophy.** The 15 examples were scoring 48–57% (RED / YELLOW) — they filled only 4 stack slots and used `null` instead of `slotignored`. All 15 rewritten to the full 21-slot schema with realistic values; a test locks each at Trophy.

### Changed

- 245 → 262 tests (15 for `interrogate`, 2 for `faf_model` parity).

## [2.7.1] - 2026-09-07 — The Interop Edition

Docs / copy patch — no behavior change.

### Fixed
- README claimed **12 tools** and **233 tests** in the body sections (`## All 12 Tools`, Testing) — the v2.7.0 Doc Gate updated the front door but not the tables. Corrected to **13 tools** (added the `faf_migrate` row) and **245 tests**.
- README's "What about my `GEMINI.md`?" section and `commands/faf/export.toml` still described **YAML frontmatter** output — v2.7.0 dropped that. Rewritten for the hierarchical, `@file`-importable format `faf_gemini` now writes.
- Example `.faf` in the README used `faf_version: '2.5.0'`; updated to `"3.0"`.
- `AGENTS.md` / `GEMINI.md` re-authored against faf-python-sdk 1.3.1 (was stale at v2.7.0 with the old frontmatter-style GEMINI.md).
- "generate" removed from external copy — README prose, the `faf_init` / `faf_auto` / `faf_gemini` / `faf_agents` tool descriptions, and `/faf:export`. FAF authors and delivers facts. The `generate_agents_md` / `generate_gemini_md` function identifiers are unchanged.

### Changed
- `faf-python-sdk` floor `>=1.3.1` (the interop copy patch; no API change).
- `gemini-extension.json`, `server-card`, `agent.fafa` version → 2.7.1.

## [2.7.0] - 2026-09-06 — The Interop Edition

**`faf_agents` and `faf_gemini` now author family-standard AGENTS.md / GEMINI.md, and a new `faf_migrate` brings a .faf up to the current format.**

### Changed
- **`faf_agents`** — was a 4-field stub (`## Project`, `## Context`, `## Stack` with "N/A" everywhere, and it *included* who/why marketing). Now authors a full BETTER-shaped doc via `faf-python-sdk`'s `generate_agents_md` — `## Setup & build` (install→build→dev ordered) · `## Run the tests` · `## Where things live` · `## Conventions` (human-interaction prefs filtered) · three-tier `## Guardrails` · `## Definition of Done` · `## When stuck` · `## Security & secrets` · `## Commit & PR` · `## Stack`. **No Human Context section** — who/why belongs in the README / .faf DNA, not agent ops. In parity with faf-cli's `faf export --agents`.
- **`faf_gemini`** — now follows Gemini CLI's own convention via `generate_gemini_md` (hierarchical, `@file`-importable — setup / verify / key files / stack / confirm-first). Dropped the YAML frontmatter and the embedded score/IANA prose (that data is in the tool *result*, not the file).
- **`faf-python-sdk>=1.3.0`** — the interop authoring tools live in the SDK now, so every Python FAF tool shares one implementation.
- **fastmcp `>=4.0.0`** (was `>=3.4.7`).
- **Python 3.10 dropped** — `requires-python >=3.11` (the test suite `import tomllib` unconditionally; 3.10 EOL).
- `faf_init` / `faf_auto` templates emit `faf_version: "3.0"` and `slotignored` (was `'2.5.0'` + `null`).

### Added
- **`faf_migrate`** — bump a .faf to the current format version, ensure the section roots, re-serialize. Legacy slot names still score via the registry's aliases. `dry_run` to preview. Parity with faf-cli's `faf migrate`.
- **`.github/workflows/ci.yml`** — `ruff` + `mypy` + `pytest` on Python 3.11–3.13 + `faf-cli check project.faf --strict`, on every push/PR. The 245-test suite previously ran only locally.

### Fixed
- `[tool.mypy]` overrides that sat after `[tool.ruff]` were silently dropped — consolidated. `python_version "3.10"`.

## [2.6.0] - 2026-08-20 — The Agent Card Edition

**A real agent.fafa passport, MCP Server Card, and AI Catalog entry — gemini-faf-mcp joins the wider agent-discovery ecosystem.**

- **`agent.fafa`** — a real FAF Agent Card, authored from live introspection of `server.py`'s actual 12 tools (name + docstring, not guessed or copied from another server's tool list).
- **MCP Server Card** (SEP-2127) — `faf cards --target mcp`, carries the FAF context block by construction.
- **AI Catalog entry** — `.well-known/ai-catalog.json`, `faf cards --target catalog`. Fresh spec (ratified Nov 2025) — early adoption.
- **GEMINI.md** — regenerated with a genuinely richer template (Setup & build, Test & verify, Where things live, a universal "Before changing things" safety default) instead of the old thin project/goal/language-only output.
- **`fastmcp` floor** — `>=3.4.0` → `>=3.4.7` (7 patch releases since June).
- **`project.faf` data hygiene** — was 5 months stale. Added `project.version` and `project.title` (both previously missing, causing generated cards to silently fall back to `0.1.0`/no title); corrected a separately-stale `state.version` (2.2.0, real: 2.6.0); refreshed the `generated` timestamp.
- **`.gitignore`** — no longer hides `.faf-dna` (a real birth-certificate lineage file, dated 2026-03-12, invisible to git until now) or `.well-known/` — both now tracked.
- **Removed** a stale, never-tracked, factually-wrong hand-rolled `.well-known/mcp/server-card.json` (wrong version, a fabricated tool name) — superseded by the real generated card above.

**Not in this release:** A2A support. `faf cards --target a2a` correctly refuses to fabricate an endpoint gemini-faf-mcp doesn't serve — real A2A support is planned as its own future release, not bundled into this one's story.

Trophy 100%, 17/17 slots, throughout.

## [2.5.1] - 2026-07-04

**one.faf namespace migration — gemini joins the fleet on `one.faf/gemini-faf-mcp`.**

- **Namespace:** `io.github.Wolfe-Jam/gemini-faf-mcp` → `one.faf/gemini-faf-mcp` — server.json `name` + emitter `_meta` (publisher-provided, carrying the `one.faf/context` FAF/IANA receipt), and the PyPI README `mcp-name:` ownership marker. The MCP-registry entry now publishes via **DNS auth** (faf.one) instead of GitHub-OIDC.
- **Fixes:** `main.py` version drift corrected (2.0.1 → 2.5.1, back in lockstep with the rest); `docs/index.html` version-badge fallback refreshed.
- **CI:** `actions/checkout` → v7 across workflows; stranded branches consolidated into `main`.
- No tool or behaviour changes — pure identity + housekeeping.

## [2.5.0] - 2026-06-16 — The Dart Edition

**gemini-faf-mcp now understands Dart and Flutter projects.**

Detects Dart/Flutter from a `pubspec.yaml` — Flutter app vs package · Dart MCP / backend / CLI / library — by composing faf-python-sdk's detector, the shared engine, not a fork. Zero-Config, 12 exact tools.

### Added
- **Dart/Flutter detection in `faf_auto`.** Pointed at a Dart or Flutter project, `faf_auto` fills the stack from `pubspec.yaml` — `main_language: Dart`, plus Flutter (frontend) / Dart backend (Serverpod, Dart Frog, Shelf, …) / Dart MCP (`api_type: MCP`) / CLI / library — instead of leaving the language slot unset.

### Changed
- **Composed, not forked.** The pubspec brain is `faf_sdk.detect_dart_project` (the single source, mirrored from faf-cli), reached via `faf-python-sdk>=1.2.0`. gemini delegates detection; it carries no Dart parser of its own.

## [2.4.3] - 2026-06-11

**`faf_agents` and `faf_gemini` now enhance your files.** The same solid, structured `.faf` data is prefixed to the top of AGENTS.md / GEMINI.md for rapid AI consumption upfront — and your Markdown stays in the instruction lane.

### Changed

- **Non-destructive export.** `faf_agents` and `faf_gemini` now write AGENTS.md / GEMINI.md by injecting a structured `.faf` block and preserving everything you've written below. Re-runs update the block in place (idempotent); existing faf-authored files upgrade cleanly in one pass.

## [2.4.2] - 2026-06-11 — The Confinement Edition

**Security release.** Caller-supplied `path` arguments are now confined: read tools open only `.faf` / `.fafm` context files, and `faf_init` writes only inside the project root (override with `FAF_ALLOWED_ROOTS`). Closes a path-traversal / arbitrary local-file read — and an arbitrary file write via `faf_init`.

### Security
- **Path confinement on every `path` argument (CWE-22 / CWE-73 / CWE-200).** `faf_read`, `faf_validate`, `faf_score`, `faf_stringify`, `faf_context`, `faf_gemini`, and `faf_agents` previously passed a caller path straight into `Path(path).read_text()` with no confinement, and `faf_init` into `Path(path).write_text()` — so an absolute path or `../` traversal could read any file the server uid could read (e.g. `/etc/passwd`, `/proc/self/environ`, `~/.ssh/id_rsa`) or write outside the project. New `safe_path.py` confines reads to `.faf`/`.fafm` files and writes to the project root (cwd + system temp; override via `FAF_ALLOWED_ROOTS`), canonicalizes through symlinks (closing the symlink bypass), and rejects traversal/absolute escapes. Applied proactively as a defense-in-depth hardening.

### Tests
- Added `tests/test_security_path_confinement.py` — reproduces the path-traversal vectors (incl. symlink bypass and arbitrary write) as a permanent regression.
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
- **Tool #12: `faf_auto`** — Auto-detect project stack and author/update .faf files
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
