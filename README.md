# gemini-faf-mcp

<!-- mcp-name: io.github.Wolfe-Jam/gemini-faf-mcp -->

[![PyPI](https://img.shields.io/pypi/v/gemini-faf-mcp?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/gemini-faf-mcp/)
[![Tests](https://img.shields.io/badge/Tests-168%20passing-brightgreen?style=for-the-badge)](https://github.com/Wolfe-Jam/gemini-faf-mcp)
[![MCP Tools](https://img.shields.io/badge/MCP_Tools-10-blue?style=for-the-badge)](https://github.com/Wolfe-Jam/gemini-faf-mcp)

MCP server for [FAF](https://faf.one) (Foundational AI-context Format) — the IANA-registered standard for AI project context (`application/vnd.faf+yaml`). 10 tools powered by [faf-python-sdk](https://pypi.org/project/faf-python-sdk/).

## Install

```bash
# Gemini CLI
gemini extensions install https://github.com/Wolfe-Jam/gemini-faf-mcp

# Or from PyPI
pip install gemini-faf-mcp
python server.py
```

## Tools

| Tool | Description |
|------|-------------|
| `faf_read` | Read and parse a .faf file into structured data |
| `faf_validate` | Validate a .faf file — returns score, tier, errors, warnings |
| `faf_score` | Quick score check (0-100%) with tier |
| `faf_discover` | Find .faf files in the project tree |
| `faf_init` | Create a starter .faf file for a project |
| `faf_stringify` | Convert FAF data back to YAML |
| `faf_context` | Get Gemini-optimized context from a .faf file |
| `faf_gemini` | Export GEMINI.md from a .faf file |
| `faf_agents` | Export AGENTS.md from a .faf file |
| `faf_about` | FAF format info, IANA registration, version |

## Usage with Gemini CLI

```
> Read my project DNA
> What's the FAF score for this project?
> Create a starter .faf file
> Export a GEMINI.md
```

## Testing

```bash
# Run all tests (168 passing — 111 MCP server + 57 Cloud Function)
pip install -e ".[dev]"
python -m pytest tests/ -v

# MCP Inspector
npx @modelcontextprotocol/inspector --command python3 server.py
```

## Score and Tier System

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
├── server.py              → FastMCP MCP server (10 tools)
├── main.py                → Cloud Run REST API (GET/POST/PUT)
└── src/gemini_faf_mcp/    → Python SDK (FAFClient, parser)
```

The MCP server uses `faf-python-sdk` for parsing, validation, and discovery. The Cloud Run API provides live badges, multi-agent context brokering, and voice-to-FAF mutations.

---

## Python SDK

The package also includes a Python SDK for direct use without MCP.

```python
from gemini_faf_mcp import FAFClient, parse_faf, validate_faf, find_faf_file

# Local: Parse .faf files directly
data = parse_faf("project.faf")
result = validate_faf(data)
print(f"Score: {result['score']}%, Tier: {result['tier']}")

# Discovery: Find .faf files automatically
faf_path = find_faf_file(".")

# Remote: Call the Cloud Run endpoint
client = FAFClient()
dna = client.get_project_dna()
```

---

## Cloud Run REST API

The package includes a Cloud Run REST API that powers live badges, multi-agent handshake, and voice-to-FAF mutations.

**Endpoint:**
```
https://faf-source-of-truth-631316210911.us-east1.run.app
```

### Read Project DNA

```bash
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "Content-Type: application/json" \
  -d '{"path": "project.faf"}'
```

### Multi-Agent Context Broker

The endpoint returns format-optimized responses based on which AI is calling:

```bash
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "X-FAF-Agent: gemini" \
  -H "Content-Type: application/json"
```

| Agent | Format |
|-------|--------|
| Claude | XML |
| Gemini | Structured JSON |
| Grok | Direct JSON |
| Jules | Minimal JSON |
| Codex/Copilot/Cursor | Code-focused JSON |

### Voice-to-FAF (Gemini Live)

Update project context by voice through Gemini Live:

```bash
curl -X PUT https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "state.focus": "IETF Draft Submission",
      "state.phase": "review"
    },
    "message": "Update focus to IETF"
  }'
```

### Security

- Input validation: max 50 updates, 100-char keys, 10K-char values
- YAML round-trip validation before commit
- Temporal integrity checks (rejects stale mutations)
- All mutations logged to BigQuery

### Deployment

Auto-deploys via Cloud Build on push to `main`. See `cloudbuild.yaml`.

---

## FAF Ecosystem

| Package | Platform | Registry |
|---------|----------|----------|
| [claude-faf-mcp](https://npmjs.com/package/claude-faf-mcp) | Anthropic | npm + MCP #2759 |
| **gemini-faf-mcp** | **Google** | **PyPI** |
| [grok-faf-mcp](https://npmjs.com/package/grok-faf-mcp) | xAI | npm |
| [rust-faf-mcp](https://crates.io/crates/rust-faf-mcp) | Rust | crates.io |
| [faf-cli](https://npmjs.com/package/faf-cli) | Universal | npm |

## Links

- [FAF Specification](https://faf.one)
- [IANA Registration](https://www.iana.org/assignments/media-types/application/vnd.faf+yaml)
- [faf-python-sdk](https://pypi.org/project/faf-python-sdk/)
- [faf-cli](https://npmjs.com/package/faf-cli)

## License

MIT

---

Built by [@wolfe_jam](https://x.com/wolfe_jam) | wolfejam.dev
