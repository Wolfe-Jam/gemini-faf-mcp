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
from models import get_model, list_models
import os
from pathlib import Path

__version__ = "2.1.2"

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
    if result and Path(result).is_file():
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
        "tools": 12,
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


@mcp.tool()
def faf_model(project_type: str = "") -> dict:
    """Get a 100% Trophy-scored example .faf file for a specific project type.
    Returns a complete, realistic project.faf that fills all 21 scored slots.
    Use this as a reference when building or improving a .faf file — shows exactly what 100% looks like.
    Call without arguments to list all 15 available project types."""
    if not project_type:
        return {
            "available_types": list_models(),
            "usage": "Call faf_model with a project_type to get the full example .faf",
        }

    model = get_model(project_type)
    if not model:
        return {
            "error": f"Unknown project type: {project_type}",
            "available_types": list_models(),
        }

    return {
        "type": project_type,
        "description": model["description"],
        "covers": model["covers"],
        "faf": model["faf"],
        "note": "This is a 100% Trophy-scored example. Use it as a reference for structure and completeness.",
    }


# --- Stack detection helper ---


def _detect_stack(directory: str) -> dict:
    """Scan directory for manifest files and detect project stack.
    Only sets values that are actually detected — never hardcodes defaults."""
    detected = {}
    dir_path = Path(directory).resolve()

    # Check which manifest files exist
    has_pyproject = (dir_path / "pyproject.toml").is_file()
    has_package_json = (dir_path / "package.json").is_file()
    has_cargo = (dir_path / "Cargo.toml").is_file()
    has_go_mod = (dir_path / "go.mod").is_file()
    has_requirements = (dir_path / "requirements.txt").is_file()
    has_gemfile = (dir_path / "Gemfile").is_file()
    has_composer = (dir_path / "composer.json").is_file()
    has_tsconfig = (dir_path / "tsconfig.json").is_file()

    # Priority: pyproject.toml / Cargo.toml / go.mod > package.json
    if has_pyproject:
        detected["main_language"] = "Python"
        try:
            content = (dir_path / "pyproject.toml").read_text()
            # Detect build system
            if "setuptools" in content:
                detected["build_tool"] = "setuptools"
            elif "hatchling" in content or "hatch" in content:
                detected["build_tool"] = "hatch"
            elif "flit" in content:
                detected["build_tool"] = "flit"
            elif "pdm" in content:
                detected["build_tool"] = "pdm"
            elif "poetry" in content:
                detected["build_tool"] = "poetry"
            detected["package_manager"] = "pip"

            # Detect frameworks from dependencies
            content_lower = content.lower()
            if "fastmcp" in content_lower:
                detected["framework"] = "FastMCP"
                detected["api_type"] = "MCP"
            elif "fastapi" in content_lower:
                detected["framework"] = "FastAPI"
                detected["api_type"] = "REST"
            elif "flask" in content_lower:
                detected["framework"] = "Flask"
                detected["api_type"] = "REST"
            elif "django" in content_lower:
                detected["framework"] = "Django"
                detected["api_type"] = "REST"

            # Detect databases
            if "bigquery" in content_lower or "google-cloud-bigquery" in content_lower:
                detected["database"] = "BigQuery"
            elif "psycopg" in content_lower or "asyncpg" in content_lower or "postgresql" in content_lower:
                detected["database"] = "PostgreSQL"
            elif "pymongo" in content_lower or "motor" in content_lower:
                detected["database"] = "MongoDB"
            elif "redis" in content_lower:
                detected["database"] = "Redis"
            elif "sqlalchemy" in content_lower:
                detected["database"] = "SQLAlchemy"

            # Detect testing
            if "pytest" in content_lower:
                detected["testing"] = "pytest"
        except Exception:
            pass

    elif has_cargo:
        detected["main_language"] = "Rust"
        detected["package_manager"] = "cargo"
        try:
            content = (dir_path / "Cargo.toml").read_text()
            content_lower = content.lower()
            if "tokio" in content_lower:
                detected["framework"] = "Tokio"
            if "axum" in content_lower:
                detected["framework"] = "Axum"
                detected["api_type"] = "REST"
            elif "actix" in content_lower:
                detected["framework"] = "Actix"
                detected["api_type"] = "REST"
        except Exception:
            pass

    elif has_go_mod:
        detected["main_language"] = "Go"
        detected["package_manager"] = "go modules"
        try:
            content = (dir_path / "go.mod").read_text()
            if "gin-gonic" in content:
                detected["framework"] = "Gin"
                detected["api_type"] = "REST"
            elif "echo" in content:
                detected["framework"] = "Echo"
                detected["api_type"] = "REST"
        except Exception:
            pass

    elif has_package_json:
        detected["main_language"] = "TypeScript" if has_tsconfig else "JavaScript"
        detected["package_manager"] = "npm"
        try:
            import json as _json
            pkg = _json.loads((dir_path / "package.json").read_text())
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))
            dep_keys = " ".join(all_deps.keys()).lower()

            if "next" in all_deps:
                detected["framework"] = "Next.js"
            elif "react" in all_deps:
                detected["framework"] = "React"
            elif "vue" in all_deps:
                detected["framework"] = "Vue"
            elif "svelte" in all_deps or "@sveltejs/kit" in all_deps:
                detected["framework"] = "Svelte"
            elif "express" in all_deps:
                detected["framework"] = "Express"
                detected["api_type"] = "REST"

            if "jest" in dep_keys:
                detected["testing"] = "Jest"
            elif "vitest" in dep_keys:
                detected["testing"] = "Vitest"
            elif "mocha" in dep_keys:
                detected["testing"] = "Mocha"

            if "yarn.lock" in [f.name for f in dir_path.iterdir() if f.is_file()]:
                detected["package_manager"] = "yarn"
            elif "pnpm-lock.yaml" in [f.name for f in dir_path.iterdir() if f.is_file()]:
                detected["package_manager"] = "pnpm"
        except Exception:
            pass

    elif has_requirements:
        detected["main_language"] = "Python"
        detected["package_manager"] = "pip"

    elif has_gemfile:
        detected["main_language"] = "Ruby"
        detected["package_manager"] = "bundler"

    elif has_composer:
        detected["main_language"] = "PHP"
        detected["package_manager"] = "composer"

    # TypeScript upgrade if tsconfig exists alongside non-TS detection
    if has_tsconfig and detected.get("main_language") == "JavaScript":
        detected["main_language"] = "TypeScript"

    return detected


@mcp.tool()
def faf_auto(directory: str = ".", path: str = "project.faf") -> dict:
    """Auto-detect project stack and generate/update a .faf file.
    Scans for package.json, pyproject.toml, Cargo.toml, go.mod, and other
    manifest files. Extracts language, framework, database, API type, and
    build tools from actual dependencies — no hardcoded defaults.
    Creates a new .faf if none exists, or fills empty slots in an existing one."""
    try:
        dir_path = Path(directory).resolve()
        if not dir_path.is_dir():
            return {"success": False, "error": f"Directory not found: {directory}"}

        detected = _detect_stack(directory)

        # Resolve path relative to directory
        faf_path = Path(path)
        if not faf_path.is_absolute():
            faf_path = dir_path / faf_path
        faf_path = faf_path.resolve()

        created = not faf_path.exists()

        if created:
            # Generate new .faf from detections
            name = dir_path.name or "my-project"
            lang = detected.get("main_language", "unknown")
            content = f"""faf_version: '2.5.0'
project:
  name: {name}
  goal: Describe your project goal
  main_language: {lang}
stack:
  frontend: {detected.get('framework') if detected.get('framework') in ('React', 'Vue', 'Svelte', 'Next.js') else 'null'}
  backend: {detected.get('framework') if detected.get('framework') in ('FastAPI', 'Flask', 'Django', 'Express', 'FastMCP', 'Axum', 'Actix', 'Gin', 'Echo') else 'null'}
  database: {detected.get('database', 'null')}
  testing: {detected.get('testing', 'null')}
human_context:
  who: Developers
  what: What problem does this solve?
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
            faf_path.parent.mkdir(parents=True, exist_ok=True)
            faf_path.write_text(content)
        else:
            # Update existing: fill only empty/null slots
            existing = faf_path.read_text()
            updated = existing
            # Fill null main_language
            if detected.get("main_language") and ("main_language: null" in updated or "main_language: unknown" in updated):
                updated = updated.replace("main_language: null", f"main_language: {detected['main_language']}")
                updated = updated.replace("main_language: unknown", f"main_language: {detected['main_language']}")
            # Fill null stack fields
            for field, key in [("frontend", "framework"), ("backend", "framework"), ("database", "database"), ("testing", "testing")]:
                val = detected.get(key)
                if val and f"  {field}: null" in updated:
                    # Only set frontend for frontend frameworks, backend for backend frameworks
                    if field == "frontend" and val not in ("React", "Vue", "Svelte", "Next.js"):
                        continue
                    if field == "backend" and val not in ("FastAPI", "Flask", "Django", "Express", "FastMCP", "Axum", "Actix", "Gin", "Echo"):
                        continue
                    updated = updated.replace(f"  {field}: null", f"  {field}: {val}")
            if updated != existing:
                faf_path.write_text(updated)

        # Validate and score
        try:
            faf = parse_file(str(faf_path))
            result = validate(faf)
            score = result.score
            tier = _get_tier(score)
        except Exception:
            score = 0
            tier = "White"

        lang = detected.get("main_language", "unknown")
        fw = detected.get("framework")
        action = "Created" if created else "Updated"
        msg_parts = [f"Detected {lang}"]
        if fw:
            msg_parts[0] += f"/{fw}"
        msg_parts.append(f"{action} {faf_path.name} at {score}%.")

        return {
            "success": True,
            "path": str(faf_path),
            "created": created,
            "detected": {
                "main_language": detected.get("main_language"),
                "package_manager": detected.get("package_manager"),
                "build_tool": detected.get("build_tool"),
                "framework": detected.get("framework"),
                "api_type": detected.get("api_type"),
                "database": detected.get("database"),
            },
            "score": score,
            "tier": tier,
            "message": " ".join(msg_parts),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
