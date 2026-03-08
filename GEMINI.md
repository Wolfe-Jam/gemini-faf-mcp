---
faf_score: 100%
faf_tier: Trophy
faf_version: 2.5.2
last_sync: 2026-03-08 07:34:52.974000+00:00
server_version: 2.0.1
---

# Gemini Project DNA — gemini-faf-mcp

FAF (Foundational AI-context Format) is an IANA-registered format (`application/vnd.faf+yaml`) that gives AI tools instant project context. One `project.faf` file eliminates re-explaining your project every session. This extension brings FAF to Gemini CLI.

## Quick Start

```
/gemini-faf-mcp:setup
```

The setup wizard will discover or create your `.faf` file, score it, and export context files. Done in under a minute.

## Commands

| Command | What It Does |
|---------|-------------|
| `/gemini-faf-mcp:setup` | Guided wizard — discover, create, score, and export project DNA |
| `/gemini-faf-mcp:score` | Quick score check with tier and improvement suggestions |
| `/gemini-faf-mcp:export` | Export to GEMINI.md, AGENTS.md, or both |

## MCP Tools

Use these tools to work with FAF project DNA. Prefer these over built-in file tools when working with `.faf` files.

| Tool | What It Does |
|------|-------------|
| `faf_read` | Read and parse a .faf file into structured project DNA |
| `faf_validate` | Validate a .faf file — returns score, tier, errors, warnings |
| `faf_score` | Quick score (0-100%) and tier lookup |
| `faf_discover` | Find .faf files by walking up the project tree |
| `faf_init` | Create a new .faf file from project info |
| `faf_stringify` | Convert parsed FAF data back to YAML |
| `faf_context` | Get Gemini-optimized context summary from .faf |
| `faf_gemini` | Generate GEMINI.md content from .faf |
| `faf_agents` | Generate AGENTS.md content from .faf |
| `faf_about` | FAF format info, IANA registration, ecosystem |

## Score & Tier System

Scores tell AI tools how much autonomy they can take:

| Score | Tier | Meaning |
|-------|------|---------|
| 100% | Trophy | Perfect DNA — full AI autonomy |
| 99% | Gold | Exceptional — nearly complete |
| 95% | Silver | Top tier — very strong context |
| 85% | Bronze | Production ready — AI works confidently |
| 70% | Green | Solid foundation — some gaps |
| 55% | Yellow | Needs improvement — AI will ask questions |
| <55% | Red | Major gaps — limited effectiveness |
| 0% | White | Empty — no useful context |

**Target: Bronze (85%) or higher** for effective AI assistance.

## How It Works

```
project.faf (source of truth)
       |
       v
  faf_gemini / faf_agents (export tools)
       |
       v
  GEMINI.md / AGENTS.md (AI reads these automatically)
```

1. `project.faf` holds your project DNA in YAML
2. Export tools generate context files for specific AI platforms
3. GEMINI.md is auto-loaded by this extension every session
4. AI gets instant context — no re-explaining needed

## Usage with Gemini CLI

```bash
# Install
gemini extensions install gemini-faf-mcp

# Run the setup wizard
/gemini-faf-mcp:setup

# Or use tools directly
> Read my project DNA
> Score my .faf file
> Export GEMINI.md from my project.faf
```

## Ecosystem

| Package | Platform | Registry |
|---------|----------|----------|
| claude-faf-mcp | Anthropic | npm + MCP #2759 |
| **gemini-faf-mcp** | **Google** | **PyPI** |
| grok-faf-mcp | xAI | npm |
| rust-faf-mcp | Rust | crates.io |
| faf-cli | Universal | npm |

## Source of Truth

The `project.faf` file is the single source of truth. GEMINI.md and AGENTS.md are generated exports — always regenerate from `.faf` when the project changes.

- **Format:** YAML
- **Media Type:** `application/vnd.faf+yaml` (IANA registered)
- **Spec:** https://faf.one
