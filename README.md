<!-- faf: gemini-faf-mcp | Python | mcp-server | FAF MCP server for Google Gemini — persistent project context via PyPI -->
<!-- faf: doc=readme | canonical=project.faf | score=100 | family=FAF -->

# gemini-faf-mcp — The Interop Edition

**Persistent Project Context for Google Gemini. Define once. Sync everywhere.**

**FAF defines. MD instructs. AI codes.**

⭐ **A star helps other devs discover gemini-faf-mcp** — despite the downloads, ~3 of 4 devs check stars first.

Stop re-explaining your project to every new Gemini session. Every Gemini conversation starts cold — you re-state your stack, your goals, your conventions every single time. `.faf` is one structured file that captures all of it. This package is the MCP server that lets Gemini read it.

<!-- mcp-name: one.faf/gemini-faf-mcp -->

[![PyPI](https://img.shields.io/pypi/v/gemini-faf-mcp?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/gemini-faf-mcp/)
[![FAF Trophy 100%](https://img.shields.io/badge/FAF-%F0%9F%8F%86%20100%25-000000?labelColor=FF6B35)](https://faf.one)
[![Tests](https://img.shields.io/badge/Tests-245%20passing-brightgreen?style=for-the-badge)](https://github.com/Wolfe-Jam/gemini-faf-mcp)
[![IANA: vnd.faf+yaml](https://img.shields.io/badge/IANA-vnd.faf%2Byaml-00D4D4?style=for-the-badge)](https://www.iana.org/assignments/media-types/application/vnd.faf+yaml)
[![IANA: vnd.fafm+yaml](https://img.shields.io/badge/IANA-vnd.fafm%2Byaml-00D4D4?style=for-the-badge)](https://www.iana.org/assignments/media-types/application/vnd.fafm+yaml)
[![DOI: Context paper](https://img.shields.io/badge/DOI-Context%20paper-FF6B35?style=for-the-badge)](https://doi.org/10.5281/zenodo.18251362)
[![DOI: Memory paper](https://img.shields.io/badge/DOI-Memory%20paper-FF6B35?style=for-the-badge)](https://doi.org/10.5281/zenodo.20348942)
[![DOI: Agents paper](https://img.shields.io/badge/DOI-Agents%20paper-FF6B35?style=for-the-badge)](https://doi.org/10.5281/zenodo.21951641)

### Before and after

```
Without FAF                           With FAF (.faf at 85%+ Bronze)
─────────────────────────             ─────────────────────────
You: "I'm using FastAPI with...       You: "Add a /users/me endpoint"
      PostgreSQL, pytest, and..."     Gemini: [generates correct code,
Gemini: "Got it. What's the              uses your auth pattern,
        codebase like?"                  matches your test style]
You: "It's a REST API for..."
[5 minutes of re-explaining]
Gemini: [now ready to help]
```

`.faf` is read once at session start. Every tool call lands on a Gemini that already knows your project.

### What's New in v2.7.0 — The Interop Edition

**`faf_agents` and `faf_gemini` now author family-standard AGENTS.md / GEMINI.md, and a new `faf_migrate` brings a .faf up to the current format.**

`faf_agents` was a 4-field stub that padded sections with "N/A" and shipped who/why marketing. It now authors a full BETTER-shaped doc through `faf-python-sdk`'s `generate_agents_md` — setup (install→build→dev ordered) · tests · where things live · conventions · three-tier guardrails · definition of done · when stuck · security · commit & PR · stack. No Human Context section — that belongs in the README / `.faf` DNA, not agent ops. `faf_gemini` now follows Gemini CLI's own hierarchical, `@file`-importable convention. Both are in parity with faf-cli's `faf export`. New `faf_migrate` bumps a `.faf` to the current format version (`dry_run` to preview). **13 tools.** Also: `fastmcp >=4.0.0`, Python 3.11+, and a `ci.yml` running the 245-test suite on every push.

> **v2.6.0 — The Agent Card Edition** added a real `agent.fafa` passport (authored from live tool introspection), an MCP Server Card (SEP-2127), and an AI Catalog entry. **v2.5.1** one.faf namespace migration. **v2.5.0 — The Dart Edition** detects Dart/Flutter from `pubspec.yaml`. **v2.4.3** made `faf_agents` / `faf_gemini` non-destructive. **v2.4.2 — The Confinement Edition** confined every caller `path` argument. **v2.4.0 — The Chameleon Edition** auto-selects its transport: stdio locally, Streamable HTTP on Cloud Run.

---

## One-Minute Setup

### 1. Install

```bash
uvx gemini-faf-mcp          # zero-install run via uvx (fetched from PyPI)
# or: pip3 install gemini-faf-mcp
```

### 2. Add to Gemini CLI

```bash
gemini extensions install https://github.com/Wolfe-Jam/gemini-faf-mcp
```

### 3. Author your project context

In your Gemini CLI:

```
> /faf:setup
```

You should see: `Created project.faf — Score: 85% (BRONZE)`. From this point, every Gemini session in this project reads it automatically.

> **Tip:** A score of 85% (BRONZE) is the minimum where Gemini stops guessing. Run `/faf:score` to see what's missing and how to push to 100% (TROPHY).

---

## The "One-File" Advantage

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

> **FAF defines. MD instructs. AI codes.**

### What about my `GEMINI.md`?

You don't replace it. `.faf` **authors** it. Run `faf_gemini` and you get a fresh `GEMINI.md` with the structured project data baked in as YAML frontmatter — the same `GEMINI.md` Gemini CLI already reads, but authored from a single source of truth instead of hand-maintained.

```bash
> /faf:export
# Generates GEMINI.md from project.faf
```

`.faf` is the source. `GEMINI.md` is one of its outputs. Same logic for `AGENTS.md` (OpenAI Codex), `.cursorrules`, `CLAUDE.md`, and others — write once, render everywhere.

---

## Auto-Detect Your Stack

`faf_auto` scans your project's manifest files and authors a `.faf` with accurate slot values. No manual entry needed.

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
  "tier": "TROPHY"
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
| `faf_auto` | Auto-detect stack from manifest files and author/update `.faf` |
| `faf_discover` | Find `.faf` files in the project tree |

### Validate & Score

| Tool | What it does |
|------|-------------|
| `faf_validate` | Full Mk4 validation — score, tier, slot counts, errors, warnings |
| `faf_score` | Quick Mk4 score — score, tier, populated/active/total slot counts |

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
| 100% | TROPHY | AI has full context for your project |
| 99% | GOLD | Exceptional |
| 95% | SILVER | Top tier |
| 85% | BRONZE | Minimum recommended — AI can build from here |
| 70% | GREEN | Solid foundation |
| 55% | YELLOW | Needs improvement |
| <55% | RED | Major gaps — AI will guess |
| 0% | WHITE | Empty |

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
gemini-faf-mcp v2.7.0
├── server.py              → FastMCP MCP server (13 tools, dual-transport, Mk4 scoring)
├── safe_path.py           → path confinement for caller-supplied `path` args
├── inject.py              → non-destructive faf-managed-block injection
├── main.py                → Cloud Run REST API (GET/POST/PUT)
├── models.py              → 15 project type examples
└── src/gemini_faf_mcp/    → Python SDK (FAFClient, parser)
```

The MCP server delegates to `faf-python-sdk` for parsing, validation, and Mk4 scoring. Stack detection in `faf_auto` is Python-native — no external CLI dependencies.

---

## Testing

```bash
pip3 install -e ".[dev]"
python -m pytest tests/ -v
```

233 tests passing across 9 WJTTC tiers (137 MCP server + 55 Cloud Function + 41 Mk4 WJTTC championship). Championship-grade test coverage — [WJTTC certified](https://github.com/Wolfe-Jam/WJTTC).

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

If `gemini-faf-mcp` has been useful, consider starring the repo — it helps others find it.

---

## Links

- [FAF Specification](https://faf.one)
- [IANA Registration](https://www.iana.org/assignments/media-types/application/vnd.faf+yaml)
- [faf-python-sdk](https://pypi.org/project/faf-python-sdk/)
- [faf-cli](https://npmjs.com/package/faf-cli)
- [Changelog](./CHANGELOG.md)

## Citation

If you use `gemini-faf-mcp` or the `.faf` / `.fafm` / `.fafa` formats in research or production, please cite the format papers:

> Wolfe, J. (2025). *Format-Driven AI Context Architecture: The .faf Standard for Persistent Project Understanding*. Zenodo. https://doi.org/10.5281/zenodo.18251362

> Wolfe, J. (2026). *Permanent Memory and Instant Recall: The .fafm Standard for Multi-Profile AI Agent Memory*. Zenodo. https://doi.org/10.5281/zenodo.20348942

> Wolfe, J. (2026). *Why Agents Need a Passport: .fafa — Portable Identity for the Agentic Era*. Zenodo. https://doi.org/10.5281/zenodo.21951641

### BibTeX

```bibtex
@article{wolfe2025faf,
  title     = {Format-Driven AI Context Architecture: The .faf Standard for Persistent Project Understanding},
  author    = {Wolfe, James},
  year      = {2025},
  month     = {nov},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.18251362},
  url       = {https://doi.org/10.5281/zenodo.18251362}
}

@article{wolfe2026fafm,
  title     = {Permanent Memory and Instant Recall: The .fafm Standard for Multi-Profile AI Agent Memory},
  author    = {Wolfe, James},
  year      = {2026},
  month     = {may},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.20348942},
  url       = {https://doi.org/10.5281/zenodo.20348942}
}

@article{wolfe2026fafa,
  title     = {Why Agents Need a Passport: .fafa — Portable Identity for the Agentic Era},
  author    = {Wolfe, James},
  year      = {2026},
  month     = {aug},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21951641},
  url       = {https://doi.org/10.5281/zenodo.21951641}
}
```

## License

MIT

---

Built by [@wolfe_jam](https://x.com/wolfe_jam) | [wolfejam.dev](https://wolfejam.dev)

---

### Get the CLI

> **faf-cli** — The original AI-Context CLI. A must-have for every builder.

```bash
npx faf-cli auto
```

**Anthropic MCP [#2759](https://github.com/modelcontextprotocol/servers/pull/2759)** · **IANA Registered:** `application/vnd.faf+yaml` · [faf.one](https://faf.one) · [npm](https://www.npmjs.com/package/faf-cli)
