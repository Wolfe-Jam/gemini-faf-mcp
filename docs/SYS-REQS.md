# System Requirements: gemini-faf-mcp

**Version:** 1.0
**Date:** 2026-03-08
**Author:** wolfejam (via Claude)

---

## 1. Overview

### 1.1 Purpose
gemini-faf-mcp is a Gemini Extensions Gallery MCP server that gives Gemini CLI native access to FAF (Foundational AI-context Format) project DNA. It eliminates the "re-explain your project every session" tax by reading, validating, scoring, and exporting IANA-registered `.faf` files.

### 1.2 Scope

**IN scope:**
- MCP server with 10 FAF tools (read, validate, score, discover, init, stringify, context, gemini, agents, about)
- Gemini Extensions Gallery distribution (install via `gemini extensions install`)
- Self-bootstrapping runtime (`run.sh` creates venv on first launch)
- Guided onboarding commands (setup, score, export)
- GEMINI.md context file auto-loaded by Gemini CLI
- PyPI distribution for manual install

**OUT of scope:**
- Cloud Run REST API (`main.py`) — separate deployment, tested separately
- PyPI SDK (`src/gemini_faf_mcp/`) — separate package, tested separately
- Other MCP bridges (claude-faf-mcp, grok-faf-mcp, rust-faf-mcp)

### 1.3 Definitions

| Term | Meaning |
|------|---------|
| FAF | Foundational AI-context Format — IANA-registered YAML format for project DNA |
| MCP | Model Context Protocol — standard for AI tool integration |
| FastMCP | Python framework for building MCP servers |
| Tier | Score bracket (Trophy/Gold/Silver/Bronze/Green/Yellow/Red/White) |
| Conductor | Gemini CLI's command system — `.toml` files in `commands/` |
| project.faf | The single source of truth for project DNA |

---

## 2. Functional Requirements (FR)

### FR-001: MCP Server Bootstrap
**Priority:** MUST
**Description:** Server starts and registers all 10 tools via FastMCP when launched by Gemini CLI.
**Acceptance Criteria:**
- [ ] Server identifies as "gemini-faf-mcp"
- [ ] Server version matches `pyproject.toml`
- [ ] Exactly 10 tools registered, all prefixed `faf_`
- [ ] Every tool has a non-empty description (>10 chars)

### FR-002: Self-Bootstrapping Install
**Priority:** MUST
**Description:** `run.sh` creates a Python venv and installs dependencies on first run with zero user intervention.
**Acceptance Criteria:**
- [ ] Creates `.venv` if not present
- [ ] Installs fastmcp, faf-python-sdk, pyyaml into venv
- [ ] Runs `server.py` using the venv Python
- [ ] Subsequent runs skip install (venv already exists)
- [ ] `run.sh` exists at repo root

### FR-003: Read Project DNA
**Priority:** MUST
**Description:** `faf_read` parses a `.faf` file and returns the full structured data.
**Acceptance Criteria:**
- [ ] Returns `{success: true, path, data}` on valid file
- [ ] Returns `{success: false, error}` on missing file
- [ ] Returns `{success: false, error}` on invalid YAML
- [ ] Does not modify the source file

### FR-004: Validate Project DNA
**Priority:** MUST
**Description:** `faf_validate` checks a `.faf` file and returns score, tier, errors, and warnings.
**Acceptance Criteria:**
- [ ] Returns `{success, valid, score, tier, errors, warnings}`
- [ ] Score is an integer 0-100
- [ ] Tier matches score via tier calculation
- [ ] Errors and warnings are lists
- [ ] Does not modify the source file

### FR-005: Quick Score Check
**Priority:** MUST
**Description:** `faf_score` returns just the score and tier, faster than full validation.
**Acceptance Criteria:**
- [ ] Returns `{score, tier, valid}` on success
- [ ] Returns `{score: 0, tier: "White", error}` on failure
- [ ] Score matches `faf_validate` for the same file

### FR-006: Discover FAF Files
**Priority:** MUST
**Description:** `faf_discover` walks up the directory tree to find `project.faf`.
**Acceptance Criteria:**
- [ ] Returns `{found: true, path}` when found
- [ ] Returns `{found: false, searched_from}` when not found
- [ ] Searches from `start_dir` upward

### FR-007: Initialize FAF File
**Priority:** MUST
**Description:** `faf_init` creates a starter `.faf` file from provided project info.
**Acceptance Criteria:**
- [ ] Creates valid FAF YAML with name, goal, language
- [ ] Returns `{success: true, path, message}`
- [ ] Refuses to overwrite existing file (`{success: false, error}`)
- [ ] Created file is parseable by `faf_read`
- [ ] Created file passes `faf_validate`

### FR-008: Stringify FAF Data
**Priority:** SHOULD
**Description:** `faf_stringify` re-serializes parsed FAF data to clean YAML.
**Acceptance Criteria:**
- [ ] Returns `{success: true, yaml}` with YAML string
- [ ] Output contains project name and faf_version
- [ ] Does not modify the source file

### FR-009: Gemini-Optimized Context
**Priority:** SHOULD
**Description:** `faf_context` returns key sections an AI needs from a `.faf` file.
**Acceptance Criteria:**
- [ ] Returns project info, score, tier
- [ ] Includes human_context, stack, ai_instructions when present
- [ ] Handles minimal .faf (no stack, no human_context) without crashing
- [ ] Handles null fields without crashing

### FR-010: Export GEMINI.md
**Priority:** MUST
**Description:** `faf_gemini` generates Markdown with YAML frontmatter for Gemini CLI auto-loading.
**Acceptance Criteria:**
- [ ] Content starts with `---` YAML frontmatter
- [ ] Frontmatter includes faf_score, faf_tier
- [ ] Body includes project name and IANA reference
- [ ] Score >= 85 includes "full autonomy" guidance
- [ ] Returns `{success, content, score, tier}`

### FR-011: Export AGENTS.md
**Priority:** MUST
**Description:** `faf_agents` generates universal agent context compatible with OpenAI Codex, Cursor, etc.
**Acceptance Criteria:**
- [ ] Content includes `# AGENTS.md` header and `## Project` section
- [ ] Includes IANA reference
- [ ] Includes human_context and stack when present
- [ ] Minimal .faf still produces valid output
- [ ] Returns `{success, content}`

### FR-012: FAF About/Info
**Priority:** SHOULD
**Description:** `faf_about` returns static metadata about FAF format and ecosystem.
**Acceptance Criteria:**
- [ ] Returns name, media_type, iana_registered, spec, server version
- [ ] Ecosystem lists 5 platforms (claude, gemini, grok, cli, rust)
- [ ] Tier system lists all 8 tiers (Trophy through White)

### FR-013: Onboarding Wizard Command
**Priority:** MUST
**Description:** `/gemini-faf-mcp:setup` walks users through discovering, creating, scoring, and exporting project DNA.
**Acceptance Criteria:**
- [ ] `commands/gemini-faf-mcp/setup.toml` exists with `description` and `prompt`
- [ ] Prompt instructs Gemini to use FAF MCP tools (not built-in file tools)
- [ ] Covers: discover → create → validate → export flow
- [ ] Handles both "existing .faf" and "no .faf" paths

### FR-014: Score Command
**Priority:** SHOULD
**Description:** `/gemini-faf-mcp:score` provides quick score check with improvement suggestions.
**Acceptance Criteria:**
- [ ] `commands/gemini-faf-mcp/score.toml` exists with `description` and `prompt`
- [ ] Suggests `/gemini-faf-mcp:setup` if no .faf found
- [ ] Shows tier meaning and improvement suggestions below Bronze

### FR-015: Export Command
**Priority:** SHOULD
**Description:** `/gemini-faf-mcp:export` offers format choices and writes export files.
**Acceptance Criteria:**
- [ ] `commands/gemini-faf-mcp/export.toml` exists with `description` and `prompt`
- [ ] Offers GEMINI.md, AGENTS.md, or both
- [ ] Suggests `/gemini-faf-mcp:setup` if no .faf found

---

## 3. Non-Functional Requirements (NFR)

### NFR-001: Performance
**Target:** MCP tool calls complete in <2 seconds for typical `.faf` files
**Measurement:** pytest execution time per test (current: ~3s for 111 tests)

### NFR-002: Reliability
**Target:** Zero crashes on malformed input — all tools return structured error responses
**Measurement:** Tier 3 (Aero) test suite — all error paths return `{success: false, error}` or `{score: 0, tier: "White", error}`

### NFR-003: Correctness
**Target:** Tier calculation is mathematically correct at all boundary values
**Measurement:** Tier 4 (Scoring) test suite — 16 boundary tests, descending order validation

### NFR-004: Safety
**Target:** Read-only tools never modify source files. `faf_init` never overwrites existing files.
**Measurement:** Tier 6 (Safety) test suite — file hash comparison before/after tool calls

### NFR-005: API Consistency
**Target:** Every tool returns a predictable, documented schema
**Measurement:** Tier 7 (Contract) test suite — exact key set assertions per tool

### NFR-006: End-to-End Integrity
**Target:** Full pipeline (init → read → validate → score → stringify → context → gemini → agents) produces consistent results
**Measurement:** Tier 8 (Roundtrip) test suite — 9 pipeline tests including full championship lap

---

## 4. Constraints

### 4.1 Technical Constraints
- Python 3.10+ (FastMCP minimum)
- FastMCP >= 3.0.0
- faf-python-sdk >= 1.0.2
- pytest >= 7.0.0 with pytest-asyncio >= 0.21.0 for MCP server tests
- Gemini Extensions Gallery manifest format (`gemini-extension.json`)
- Conductor command format (`.toml` with `description` + `prompt`)

### 4.2 Development Environment
- Install dev dependencies: `pip install -e ".[dev]"`
- This installs: pytest, pytest-cov, pytest-asyncio
- Run MCP server tests: `python3 -m pytest tests/test_fastmcp_server.py -v`
- Run Cloud Run tests: `python3 -m pytest tests/test_gemini_faf_mcp.py -v` (requires network + `pip install -e .`)

### 4.3 Business Constraints
- MIT licensed (open source)
- PyPI distribution (Trusted Publisher via GitHub Actions)
- Must work as Gemini Extension (zero manual config after install)

---

## 5. Assumptions

- Gemini CLI supports Conductor `.toml` command discovery in `commands/<extension-name>/`
- `faf-python-sdk` handles all FAF parsing, validation, and discovery correctly
- Users have Python 3.10+ available on their system
- `run.sh` bootstrap pattern is supported by Gemini Extensions Gallery

---

## 6. Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| fastmcp >= 3.0.0 | Runtime | Available | MCP server framework |
| faf-python-sdk >= 1.0.2 | Runtime | Available | FAF parsing/validation |
| pyyaml >= 6.0 | Runtime | Available | YAML handling |
| pytest >= 7.0.0 | Dev | Available | Test runner |
| pytest-asyncio >= 0.21.0 | Dev | Available | Async test support for FastMCP Client |
| pytest-cov >= 4.0.0 | Dev | Available | Coverage reporting |
| Gemini CLI | External | Available | Host environment |
| Conductor (commands/) | External | Available | Slash command discovery |

---

## 7. Test Architecture

### Two Test Suites

| File | Tests | What It Covers | Requirements |
|------|-------|----------------|-------------|
| `test_fastmcp_server.py` | 111 | MCP server (10 tools, 9 tiers) | `pip install -e ".[dev]"` |
| `test_gemini_faf_mcp.py` | 57 | Cloud Run API + PyPI SDK | Network + `pip install -e .` |

### MCP Server Test Tiers (WJTTC)

| Tier | Name | Tests | What It Validates |
|------|------|-------|-------------------|
| 1 | Brake | 8 | Server boots, tools registered, MCP handshake |
| 2 | Engine | 17 | Each tool with valid input |
| 3 | Aero | 15 | Graceful failure on bad input |
| 4 | Scoring | 17 | Score-to-tier math, boundaries |
| 5 | Exports | 11 | GEMINI.md / AGENTS.md output quality |
| 6 | Safety | 8 | Overwrite protection, read-only guarantees |
| 7 | Contract | 16 | Response schema consistency |
| 8 | Roundtrip | 9 | End-to-end pipeline integration |
| 9 | Gallery | 10 | gemini-extension.json manifest validation |

### Running Tests

```bash
# First time setup
pip install -e ".[dev]"

# MCP server tests (primary — must always pass)
python3 -m pytest tests/test_fastmcp_server.py -v

# Cloud Run tests (requires network + installed package)
python3 -m pytest tests/test_gemini_faf_mcp.py -v

# Full suite
python3 -m pytest tests/ -v
```

---

## 8. Open Questions

- [ ] Should Conductor commands be tested programmatically (TOML parse + schema validation)?
- [ ] Should `run.sh` pin dependency versions for reproducibility?
- [ ] Do Cloud Run tests need a mock/fixture mode for offline CI?

---

*Generated with Wolfejam Workflow - Step 1: System Requirements*
