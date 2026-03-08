---
faf_score: 100%
faf_tier: Trophy
faf_version: 2.5.2
server_version: 2.0.0
last_sync: '2026-03-08'
---

# Gemini Project DNA — gemini-faf-mcp v2.0.0

FAF MCP server for Gemini. 10 tools powered by faf-python-sdk. IANA-registered format (`application/vnd.faf+yaml`).

## MCP Tools

| Tool | What It Does |
|------|-------------|
| `faf_read` | Read & parse project.faf into structured DNA |
| `faf_validate` | Validate .faf — score, tier, errors, warnings |
| `faf_score` | Quick score check (0-100%) + tier |
| `faf_discover` | Find .faf files in the project tree |
| `faf_init` | Create a starter .faf file |
| `faf_stringify` | Convert FAF data back to YAML |
| `faf_context` | Get Gemini-optimized context from .faf |
| `faf_gemini` | Export GEMINI.md from .faf |
| `faf_agents` | Export AGENTS.md from .faf |
| `faf_about` | FAF format info, IANA registration, version |

## Usage with Gemini CLI

```bash
# Install from gallery
gemini extensions install gemini-faf-mcp

# Or manual
pip install gemini-faf-mcp
python server.py
```

Then in Gemini CLI:
```
> Read my project DNA
> What's the FAF score for this project?
> Create a starter .faf file for my project
> Export a GEMINI.md from the .faf
```

## Score & Tier System

| Score | Tier |
|-------|------|
| 100% | Trophy |
| 99% | Gold |
| 95% | Silver |
| 85% | Bronze |
| 70% | Green |
| 55% | Yellow |
| <55% | Red |
| 0% | White |

## Architecture

```
gemini-faf-mcp v2.0.0
├── server.py          → FastMCP MCP server (10 tools)
├── main.py            → Cloud Run REST API (GET/POST/PUT)
└── src/gemini_faf_mcp → PyPI SDK (FAFClient, parser)
```

The MCP server uses `faf-python-sdk` for parsing, validation, and discovery. The Cloud Run API provides live badges, multi-agent handshake, and voice-to-FAF mutations.

## Source of Truth

The `project.faf` file is the single source of truth for project DNA.

- **Format:** YAML (IANA: `application/vnd.faf+yaml`)
- **Spec:** https://faf.one
- **Tools:** `faf_read` to parse, `faf_validate` to check, `faf_score` for quick status

## Ecosystem

| Package | Platform | Registry |
|---------|----------|----------|
| claude-faf-mcp | Anthropic | npm + MCP #2759 |
| **gemini-faf-mcp** | **Google** | **PyPI** |
| grok-faf-mcp | xAI | npm |
| rust-faf-mcp | Rust | crates.io |
| faf-cli | Universal | npm |

---

*Media Type: application/vnd.faf+yaml*
