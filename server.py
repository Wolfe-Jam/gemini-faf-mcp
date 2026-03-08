"""
gemini-faf-mcp v2.0.1 — FastMCP Server

Native MCP server for FAF (Foundational AI-context Format).
Powered by faf-python-sdk. Built for Gemini Extensions Gallery.

Media Type: application/vnd.faf+yaml
Spec: https://faf.one
"""

from fastmcp import FastMCP
from faf_sdk import parse_file, parse, validate, find_faf_file, stringify
from faf_sdk.parser import FafParseError
import os
from pathlib import Path

__version__ = "2.0.1"

mcp = FastMCP(
    "gemini-faf-mcp",
    version=__version__,
    instructions="FAF — Universal AI context from IANA-registered .faf files",
)

# --- Tier calculation (mirrors CLAUDE.md tier system) ---

TIERS = [
    (100, "Trophy"),
    (99, "Gold"),
    (95, "Silver"),
    (85, "Bronze"),
    (70, "Green"),
    (55, "Yellow"),
    (0, "Red"),
]


def _get_tier(score: int) -> str:
    for threshold, name in TIERS:
        if score >= threshold:
            return name
    return "White"


# --- Tools ---


@mcp.tool()
def faf_read(path: str = "project.faf") -> dict:
    """Read project DNA from a .faf file. Returns the full parsed structure
    including project info, stack, preferences, and scoring data.
    Use this as the first step to understand any FAF-enabled project."""
    try:
        faf = parse_file(path)
        return {"success": True, "path": path, "data": faf.raw}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def faf_validate(path: str = "project.faf") -> dict:
    """Validate a .faf file and return score, tier, and issues.
    Returns errors (must fix) and warnings (should fix) with specific messages.
    Use after faf_init or when checking if a .faf file meets quality standards."""
    try:
        faf = parse_file(path)
        result = validate(faf)
        score = result.score
        return {
            "success": True,
            "valid": result.valid,
            "score": score,
            "tier": _get_tier(score),
            "errors": result.errors,
            "warnings": result.warnings,
        }
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def faf_score(path: str = "project.faf") -> dict:
    """Quick score check — returns score (0-100%) and tier.
    Faster than faf_validate when you only need the number and tier name.
    Use this for status checks; use faf_validate when you need error details."""
    try:
        faf = parse_file(path)
        result = validate(faf)
        score = result.score
        return {
            "score": score,
            "tier": _get_tier(score),
            "valid": result.valid,
        }
    except FileNotFoundError:
        return {"score": 0, "tier": "White", "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"score": 0, "tier": "White", "error": str(e)}


@mcp.tool()
def faf_discover(start_dir: str = ".") -> dict:
    """Find .faf files in the project tree by walking up from start_dir.
    Searches the current directory and parent directories for project.faf.
    Use this before faf_read to locate the file automatically."""
    result = find_faf_file(start_dir)
    if result:
        return {"found": True, "path": result}
    return {"found": False, "searched_from": os.path.abspath(start_dir)}


@mcp.tool()
def faf_init(
    name: str = "my-project",
    goal: str = "",
    language: str = "",
    path: str = "project.faf",
) -> dict:
    """Create a starter .faf file with project name, goal, and language.
    Generates a valid FAF YAML file with all required sections.
    Will not overwrite an existing file — use faf_discover first to check."""
    if os.path.exists(path):
        return {"success": False, "error": f"File already exists: {path}"}

    content = f"""faf_version: '2.5.0'
project:
  name: {name}
  goal: {goal or 'Describe your project goal'}
  main_language: {language or 'unknown'}
stack:
  frontend: null
  backend: null
  database: null
  testing: null
human_context:
  who: Developers
  what: {goal or 'What problem does this solve?'}
  why: Why does this project exist?
ai_instructions:
  priority: Read project.faf first
  usage: Code-first, minimal explanations
preferences:
  quality_bar: zero_errors
  commit_style: conventional
state:
  phase: development
  version: 0.1.0
  status: active
"""
    Path(path).write_text(content)
    return {"success": True, "path": os.path.abspath(path), "message": f"Created {path} — edit to match your project"}


@mcp.tool()
def faf_stringify(path: str = "project.faf") -> dict:
    """Convert parsed FAF data back to YAML string.
    Useful for displaying the raw .faf content or preparing it for editing.
    Reads the file, parses it, then re-serializes to clean YAML."""
    try:
        faf = parse_file(path)
        yaml_str = stringify(faf)
        return {"success": True, "yaml": yaml_str}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def faf_context(path: str = "project.faf") -> dict:
    """Get Gemini-optimized context from a .faf file.
    Returns the key sections an AI needs: project info, stack, instructions, and score.
    Use this to quickly understand a project without reading the full .faf structure."""
    try:
        faf = parse_file(path)
        data = faf.data
        result = validate(faf)

        context = {
            "project": {
                "name": data.project.name,
                "goal": data.project.goal,
                "language": data.project.main_language,
            },
            "score": result.score,
            "tier": _get_tier(result.score),
        }

        if data.instant_context:
            context["instant_context"] = {
                "what_building": data.instant_context.what_building,
                "tech_stack": data.instant_context.tech_stack,
                "key_files": data.instant_context.key_files,
                "commands": data.instant_context.commands,
            }

        if data.human_context:
            context["human_context"] = {
                "who": data.human_context.who,
                "what": data.human_context.what,
                "why": data.human_context.why,
            }

        if data.stack:
            context["stack"] = {
                "frontend": data.stack.frontend,
                "backend": data.stack.backend,
                "database": data.stack.database,
                "testing": data.stack.testing,
            }

        if data.ai_instructions:
            context["ai_instructions"] = {
                "priority": getattr(data.ai_instructions, "priority", None),
                "usage": getattr(data.ai_instructions, "usage", None),
            }

        return {"success": True, "context": context}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def faf_gemini(path: str = "project.faf") -> dict:
    """Export GEMINI.md content from a .faf file.
    Generates a Markdown file with YAML frontmatter optimized for Gemini CLI.
    The output should be written to GEMINI.md in the project root for auto-loading."""
    try:
        faf = parse_file(path)
        data = faf.data
        result = validate(faf)
        score = result.score
        tier = _get_tier(score)

        md = f"""---
faf_score: {score}%
faf_tier: {tier}
faf_version: {data.faf_version}
---

# Gemini Project DNA ({data.project.name})

## Project: {data.project.name}
- **Goal:** {data.project.goal or 'Not specified'}
- **Language:** {data.project.main_language or 'Not specified'}
- **Score:** {score}% ({tier})

## AI Instructions
- Read project.faf first for full context
- Score of {score}% means {'full autonomy' if score >= 85 else 'check with user on ambiguous decisions'}

## Source of Truth
The .faf file is the single source of truth for project DNA.
Media Type: application/vnd.faf+yaml (IANA registered)
"""
        return {"success": True, "content": md, "score": score, "tier": tier}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def faf_agents(path: str = "project.faf") -> dict:
    """Export AGENTS.md content from a .faf file.
    Generates a universal agent context file compatible with OpenAI Codex, Cursor, and other AI tools.
    Write the output to AGENTS.md in the project root."""
    try:
        faf = parse_file(path)
        data = faf.data
        result = validate(faf)

        md = f"""# AGENTS.md — {data.project.name}

## Project
- **Name:** {data.project.name}
- **Goal:** {data.project.goal or 'Not specified'}
- **Language:** {data.project.main_language or 'Not specified'}
- **FAF Score:** {result.score}%

## Instructions for AI Agents
- This project uses FAF (Foundational AI-context Format)
- Read project.faf for complete project DNA
- Media Type: application/vnd.faf+yaml (IANA registered)
"""

        if data.human_context:
            md += f"""
## Context
- **Who:** {data.human_context.who or 'Not specified'}
- **What:** {data.human_context.what or 'Not specified'}
- **Why:** {data.human_context.why or 'Not specified'}
"""

        if data.stack:
            md += f"""
## Stack
- **Frontend:** {data.stack.frontend or 'N/A'}
- **Backend:** {data.stack.backend or 'N/A'}
- **Database:** {data.stack.database or 'N/A'}
- **Testing:** {data.stack.testing or 'N/A'}
"""
        return {"success": True, "content": md}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def faf_about() -> dict:
    """FAF format info — IANA registration, version, ecosystem.
    Returns metadata about the FAF format, server version, and available MCP bridges.
    Use this when users ask what FAF is or how it connects to other AI platforms."""
    return {
        "name": "FAF (Foundational AI-context Format)",
        "media_type": "application/vnd.faf+yaml",
        "iana_registered": True,
        "spec": "https://faf.one",
        "server": "gemini-faf-mcp",
        "server_version": __version__,
        "sdk": "faf-python-sdk",
        "tools": 10,
        "ecosystem": {
            "claude": "claude-faf-mcp (npm)",
            "gemini": "gemini-faf-mcp (PyPI)",
            "grok": "grok-faf-mcp (npm)",
            "cli": "faf-cli (npm)",
            "rust": "rust-faf-mcp (crates.io)",
        },
        "tier_system": {
            "100%": "Trophy",
            "99%": "Gold",
            "95%": "Silver",
            "85%": "Bronze",
            "70%": "Green",
            "55%": "Yellow",
            "<55%": "Red",
            "0%": "White",
        },
    }


if __name__ == "__main__":
    mcp.run()
