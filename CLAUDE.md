# CLAUDE.md — gemini-faf-mcp

## Project
- **Name:** gemini-faf-mcp
- **Version:** 2.1.1
- **Purpose:** MCP server + Cloud Run API for FAF (Foundational AI-context Format)
- **Stack:** Python 3.10+ / FastMCP / faf-python-sdk / Cloud Run
- **Tests:** 183/183 passing (126 MCP server + 57 Cloud Function)
- **Registry:** PyPI
- **Format:** IANA `application/vnd.faf+yaml`

## Architecture

```
gemini-faf-mcp v2.1.1
├── server.py              → FastMCP MCP server (12 tools)
├── main.py                → Cloud Run REST API (GET/POST/PUT)
├── src/gemini_faf_mcp/    → Python SDK (FAFClient, parser)
└── tests/
    ├── test_fastmcp_server.py  → 126 tests (WJTTC 9-tier)
    └── test_gemini_faf_mcp.py  → 57 tests (7 tiers + integration)
```

## MCP Tools (12)

| Tool | Source |
|------|--------|
| `faf_read` | `faf_sdk.parse_file()` |
| `faf_validate` | `faf_sdk.validate()` |
| `faf_score` | `faf_sdk.validate()` |
| `faf_discover` | `faf_sdk.find_faf_file()` |
| `faf_init` | Custom |
| `faf_auto` | Custom (stack detection) |
| `faf_stringify` | `faf_sdk.stringify()` |
| `faf_context` | Custom |
| `faf_gemini` | Custom |
| `faf_agents` | Custom |
| `faf_about` | Static |
| `faf_model` | `models.py` (15 project types) |

## Key Files

| File | Purpose |
|------|---------|
| `server.py` | FastMCP MCP server (entry point) |
| `main.py` | Cloud Run REST API |
| `pyproject.toml` | Package config, deps, version |
| `gemini-extension.json` | Gemini Extensions Gallery manifest |
| `GEMINI.md` | Gemini AI context |
| `project.faf` | Persistent project context |
| `src/gemini_faf_mcp/` | PyPI SDK (FAFClient, parser) |

## Commands

```bash
# MCP server
python server.py

# Tests
pip install -e ".[dev]"
python -m pytest tests/ -v

# Build
python -m build
twine check dist/*

# MCP Inspector
npx @modelcontextprotocol/inspector --command python3 server.py
```

## Ecosystem

| Package | Platform | Registry |
|---------|----------|----------|
| claude-faf-mcp | Anthropic | npm + MCP #2759 |
| **gemini-faf-mcp** | **Google** | **PyPI** |
| grok-faf-mcp | xAI | npm |
| rust-faf-mcp | Rust | crates.io |
| faf-cli | Universal | npm |

## Publish

Trusted Publisher (OIDC) — tag + GitHub Release triggers `pypi.yml` workflow. No tokens.

## Notes

- `faf-python-sdk` handles all parsing/validation — server.py delegates
- Cloud Run API stays for badges, multi-agent handshake, voice-to-FAF
- Version tests read from pyproject.toml dynamically
- Python 3.10+ (FastMCP minimum)
---

**STATUS: BI-SYNC ACTIVE - Synchronized with .faf context!**

*Last Sync: 2026-03-08T21:48:02.000Z*
*Sync Engine: F1-Inspired Software Engineering*
*🏎️⚡️_championship_sync*
