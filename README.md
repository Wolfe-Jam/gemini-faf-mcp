# gemini-faf-mcp 🧬

> **Unify your AI project context.** One file to rule them all. 
> Bridges `CLAUDE.md`, `GEMINI.md`, and `AGENTS.md` into a single, IANA-registered source of truth.

<!-- mcp-name: io.github.Wolfe-Jam/gemini-faf-mcp -->

[![PyPI](https://img.shields.io/pypi/v/gemini-faf-mcp?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/gemini-faf-mcp/)
[![Downloads](https://img.shields.io/pypi/dm/gemini-faf-mcp?style=for-the-badge&color=blue)](https://pypi.org/project/gemini-faf-mcp/)
[![Tests](https://img.shields.io/badge/Tests-183%20passing-brightgreen?style=for-the-badge)](https://github.com/Wolfe-Jam/gemini-faf-mcp)
[![IANA](https://img.shields.io/badge/IANA-registered-informational?style=for-the-badge)](https://www.iana.org/assignments/media-types/application/vnd.faf+yaml)

### Stop re-explaining your project to every new AI session.

Gemini, Claude, and OpenAI all have different ways of "learning" your project. FAF (Foundational AI-context Format) unifies them into one machine-readable `.faf` file. 

**Result:** Zero context drift. Zero-minute onboarding. 100% project alignment.

<a href="https://glama.ai/mcp/servers/Wolfe-Jam/gemini-faf-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/Wolfe-Jam/gemini-faf-mcp/badge" alt="gemini-faf-mcp MCP server" />
</a>

| Feature | `CLAUDE.md` | `GEMINI.md` | `AGENTS.md` | **`project.faf`** |
|---------|-------------|-------------|-------------|-------------------|
| **Format** | Markdown | Markdown | Markdown | **Structured YAML** |
| **Schema** | Custom | Custom | Custom | **IANA Standard** |
| **Scoring** | No | No | No | **Yes (0-100%)** |
| **Auto-Detect** | No | No | No | **Yes (153+ files)** |
| **Vendor Neutral**| No | No | No | **Yes** |

---

## 🚀 One-Minute Setup

### 1. Install

```bash
pip install gemini-faf-mcp
```

### 2. Auto-Detect & Initialize

Scan your existing project and create your DNA in one command:

```bash
# Detects Python (FastAPI/Django), JS/TS (React/Next.js), Rust (Axum), and Go (Gin)
faf auto
```

### 3. Add to Gemini CLI

```bash
gemini extensions install https://github.com/Wolfe-Jam/gemini-faf-mcp
```

---

## 💎 The "One-File" Advantage

A `.faf` file is structured YAML that captures your project DNA. Every AI agent reads it once and knows exactly what you're building.

```yaml
# project.faf — your project, machine-readable
faf_version: '2.5.0'
project:
  name: my-api
  goal: REST API for user management
  main_language: Python
stack:
  backend: FastAPI
  database: PostgreSQL
  testing: pytest
human_context:
  who: Backend developers
  what: User CRUD with auth
  why: Replace legacy PHP service
```

**Result:** Gemini reads this once and knows your project. No 20-minute onboarding. No wrong assumptions. Every session starts aligned.

---

## Auto-Detect Your Stack

`faf_auto` scans your project's manifest files and generates a `.faf` with accurate slot values. No manual entry needed.

```
> Auto-detect my project stack
```

```json
{
  "detected": {
    "main_language": "Python",
    "package_manager": "pip",
    "build_tool": "setuptools",
    "framework": "FastMCP",
    "api_type": "MCP",
    "database": "BigQuery"
  },
  "score": 100,
  "tier": "Trophy"
}
```

**What it scans:**

| File | Detects |
|------|---------|
| `pyproject.toml` | Python + build system + frameworks (FastAPI, Django, Flask, FastMCP) + databases |
| `package.json` | JavaScript/TypeScript + frameworks (React, Vue, Next.js, Express) |
| `Cargo.toml` | Rust + cargo + frameworks (Axum, Actix) |
| `go.mod` | Go + go modules + frameworks (Gin, Echo) |
| `requirements.txt` | Python (fallback) |
| `Gemfile` | Ruby |
| `composer.json` | PHP |

**Priority rule:** `pyproject.toml` / `Cargo.toml` / `go.mod` take priority over `package.json`. Only sets values that are actually detected — no hardcoded defaults.

---

## All 12 Tools

### Create & Detect

| Tool | What it does |
|------|-------------|
| `faf_init` | Create a starter `.faf` file with project name, goal, and language |
| `faf_auto` | Auto-detect stack from manifest files and generate/update `.faf` |
| `faf_discover` | Find `.faf` files in the project tree |

### Validate & Score

| Tool | What it does |
|------|-------------|
| `faf_validate` | Full validation — score, tier, errors, warnings |
| `faf_score` | Quick score check (0-100%) with tier name |

### Read & Transform

| Tool | What it does |
|------|-------------|
| `faf_read` | Parse a `.faf` file into structured data |
| `faf_stringify` | Convert parsed FAF data back to clean YAML |
| `faf_context` | Get Gemini-optimized context (project + stack + score) |

### Export & Interop

| Tool | What it does |
|------|-------------|
| `faf_gemini` | Export `GEMINI.md` with YAML frontmatter for Gemini CLI |
| `faf_agents` | Export `AGENTS.md` for OpenAI Codex, Cursor, and other AI tools |

### Reference

| Tool | What it does |
|------|-------------|
| `faf_about` | FAF format info — IANA registration, version, ecosystem |
| `faf_model` | Get a 100% Trophy-scored example `.faf` for any of 15 project types |

---

## Score and Tier System

Your `.faf` file is scored on completeness — how many slots are filled with real values.

| Score | Tier | Meaning |
|-------|------|---------|
| 100% | 🏆 Trophy | Perfect — AI has full autonomy |
| 99% | 🥇 Gold | Exceptional |
| 95% | 🥈 Silver | Top tier |
| 85% | 🥉 Bronze | Production ready — AI can work confidently |
| 70% | 🟢 Green | Solid foundation |
| 55% | 🟡 Yellow | Needs improvement |
| <55% | 🔴 Red | Major gaps — AI will guess |
| 0% | ⚪ White | Empty |

**Aim for Bronze (85%+).** That's where AI stops guessing and starts knowing.

---

## Using with Gemini CLI

```
> Create a .faf file for my Python FastAPI project
> Auto-detect my project and fill in the stack
> Score my .faf and show what's missing
> Export GEMINI.md for this project
> Show me a 100% example for an MCP server
> What is FAF and how does it work?
> Read my project.faf and summarize the stack
> Validate my .faf and fix the warnings
```

---

## Architecture

```
gemini-faf-mcp v2.1.0
├── server.py              → FastMCP MCP server (12 tools)
├── main.py                → Cloud Run REST API (GET/POST/PUT)
├── models.py              → 15 project type examples
└── src/gemini_faf_mcp/    → Python SDK (FAFClient, parser)
```

The MCP server delegates to `faf-python-sdk` for parsing, validation, and discovery. Stack detection in `faf_auto` is Python-native — no external CLI dependencies.

---

## Testing

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

183 tests passing across 9 WJTTC tiers (126 MCP server + 57 Cloud Function). Championship-grade test coverage — [WJTTC certified](https://github.com/Wolfe-Jam/WJTTC).

---

## FAF Ecosystem

One format, every AI platform.

| Package | Platform | Registry |
|---------|----------|----------|
| [claude-faf-mcp](https://npmjs.com/package/claude-faf-mcp) | Anthropic | npm + MCP #2759 |
| **gemini-faf-mcp** | **Google** | **PyPI** |
| [grok-faf-mcp](https://npmjs.com/package/grok-faf-mcp) | xAI | npm |
| [rust-faf-mcp](https://crates.io/crates/rust-faf-mcp) | Rust | crates.io |
| [faf-cli](https://npmjs.com/package/faf-cli) | Universal | npm |

---

## Python SDK

Use FAF directly in Python without MCP:

```python
from gemini_faf_mcp import FAFClient, parse_faf, validate_faf, find_faf_file

# Parse and validate locally
data = parse_faf("project.faf")
result = validate_faf(data)
print(f"Score: {result['score']}%, Tier: {result['tier']}")

# Find .faf files automatically
faf_path = find_faf_file(".")

# Or use the Cloud Run endpoint
client = FAFClient()
dna = client.get_project_dna()
```

---

## Cloud Run REST API

Live endpoint for badges, multi-agent context brokering, and voice-to-FAF mutations.

```
https://faf-source-of-truth-631316210911.us-east1.run.app
```

Supports agent-optimized responses (Gemini, Claude, Grok, Jules, Codex/Copilot/Cursor) via `X-FAF-Agent` header. Voice mutations via Gemini Live through PUT endpoint. Auto-deploys via Cloud Build on push to `main`.

---

## Links

- [FAF Specification](https://faf.one)
- [IANA Registration](https://www.iana.org/assignments/media-types/application/vnd.faf+yaml)
- [faf-python-sdk](https://pypi.org/project/faf-python-sdk/)
- [faf-cli](https://npmjs.com/package/faf-cli)
- [Changelog](./CHANGELOG.md)

## License

MIT

---

Built by [@wolfe_jam](https://x.com/wolfe_jam) | [wolfejam.dev](https://wolfejam.dev)