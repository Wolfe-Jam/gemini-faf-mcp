"""
gemini-faf-mcp v2.8.0 — FastMCP Server

Native MCP server for FAF (Foundational AI-context Format).
Powered by faf-python-sdk with Mk4 Championship Scoring Engine.
Built for Gemini Extensions Gallery.

Media Type: application/vnd.faf+yaml
Spec: https://faf.one
"""

import functools
import os
from pathlib import Path

from faf_sdk import (
    author_agents_md,
    author_gemini_md,
    detect_dart_project,
    find_faf_file,
    parse_file,
    score_faf,
    stringify,
    validate,
)
from faf_sdk.parser import FafParseError
from fastmcp import FastMCP

from inject import inject_faf_block
from interrogate import interrogate_repo
from models import get_model, list_models
from safe_path import PathConfinementError, confine_file_op, confine_path

__version__ = "2.8.0"

# The .faf FORMAT version this server writes (distinct from __version__, the
# server's own release). Matches faf-cli's FAF_VERSION / faf-python-sdk.
FAF_FORMAT_VERSION = "3.0"

# Stack framework buckets — which detected framework lands in which .faf slot.
# Includes Dart/Flutter (Flutter = frontend/UI; Dart servers = backend) so the
# SDK's Dart detection (faf_sdk.detect_dart_project) flows into the generated .faf.
FRONTEND_FRAMEWORKS = ("React", "Vue", "Svelte", "Next.js", "Flutter")
BACKEND_FRAMEWORKS = (
    "FastAPI", "Flask", "Django", "Express", "FastMCP", "Axum", "Actix", "Gin", "Echo",
    "Serverpod", "Dart Frog", "Shelf", "Conduit", "Angel3", "Alfred",
)


def _confined(fn):
    """Wrap a tool so a path-confinement violation returns a clean error dict
    instead of leaking a file or raising (CWE-22/73/200)."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except PathConfinementError as e:
            return {"success": False, "error": f"Security error: {e}"}
    return wrapper


def _parse_faf(path: str):
    """Confine a caller path to a .faf/.fafm context file, then parse it."""
    return parse_file(str(confine_path(path)))

mcp = FastMCP(
    "gemini-faf-mcp",
    version=__version__,
    instructions="FAF — Universal AI context from IANA-registered .faf files",
)

# --- Mk4 scoring helper ---


def _mk4_score_file(path: str):
    """Read a .faf file and return Mk4Result. Path is confined to a .faf/.fafm
    context file (raises PathConfinementError otherwise)."""
    safe = confine_path(path)
    content = Path(safe).read_text()
    return score_faf(content)


# --- Tools ---


@mcp.tool()
@_confined
def faf_read(path: str = "project.faf") -> dict:
    """Read project DNA from a .faf file. Returns the full parsed structure
    including project info, stack, preferences, and scoring data.
    Use this as the first step to understand any FAF-enabled project."""
    try:
        faf = _parse_faf(path)
        return {"success": True, "path": path, "data": faf.raw}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_confined
def faf_validate(path: str = "project.faf") -> dict:
    """Validate a .faf file and return score, tier, and issues.
    Returns errors (must fix) and warnings (should fix) with specific messages.
    Use after faf_init or when checking if a .faf file meets quality standards."""
    try:
        faf = _parse_faf(path)
        result = validate(faf)
        mk4 = _mk4_score_file(path)
        return {
            "success": True,
            "valid": result.valid,
            "score": mk4.score,
            "tier": mk4.tier,
            "populated": mk4.populated,
            "active": mk4.active,
            "total": mk4.total,
            "errors": result.errors,
            "warnings": result.warnings,
        }
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_confined
def faf_score(path: str = "project.faf") -> dict:
    """Quick Mk4 score check — returns score (0-100%), tier, and slot counts.
    Uses the Mk4 Championship 21-slot scoring engine for universal parity.
    Use this for status checks; use faf_validate when you need error details."""
    try:
        mk4 = _mk4_score_file(path)
        return {
            "score": mk4.score,
            "tier": mk4.tier,
            "populated": mk4.populated,
            "active": mk4.active,
            "total": mk4.total,
        }
    except FileNotFoundError:
        return {"score": 0, "tier": "WHITE", "error": f"File not found: {path}"}
    except Exception as e:
        return {"score": 0, "tier": "WHITE", "error": str(e)}


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
@_confined
def faf_init(
    name: str = "my-project",
    goal: str = "",
    language: str = "",
    path: str = "project.faf",
) -> dict:
    """Create a starter .faf file with project name, goal, and language.
    Writes a valid FAF YAML file with all required sections.
    Will not overwrite an existing file — use faf_discover first to check.
    The path is confined to the project root (cwd / FAF_ALLOWED_ROOTS)."""
    # Confine the write target — no arbitrary file write outside the project
    # (e.g. overwriting ~/.bashrc). CWE-22.
    safe = confine_file_op(path)
    if safe.exists():
        return {"success": False, "error": f"File already exists: {path}"}

    content = f"""faf_version: "{FAF_FORMAT_VERSION}"
project:
  name: {name}
  goal: {goal or 'Describe your project goal'}
  main_language: {language or 'unknown'}
commands:
  install: ""
  build: ""
  test: ""
key_files: []
stack:
  frontend: slotignored
  backend: slotignored
  database: slotignored
  runtime: slotignored
  testing: slotignored
human_context:
  who: Developers
  what: {goal or 'What problem does this solve?'}
  why: Why does this project exist?
ai_instructions:
  working_style:
    quality_bar: zero_errors
    testing: required
  warnings: []
preferences:
  commit_style: conventional
state:
  phase: development
  version: 0.1.0
  status: active
"""
    safe.write_text(content)
    return {"success": True, "path": str(safe), "message": f"Created {path} — edit to match your project"}


@mcp.tool()
@_confined
def faf_stringify(path: str = "project.faf") -> dict:
    """Convert parsed FAF data back to YAML string.
    Useful for displaying the raw .faf content or preparing it for editing.
    Reads the file, parses it, then re-serializes to clean YAML."""
    try:
        faf = _parse_faf(path)
        yaml_str = stringify(faf)
        return {"success": True, "yaml": yaml_str}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_confined
def faf_context(path: str = "project.faf") -> dict:
    """Get Gemini-optimized context from a .faf file.
    Returns the key sections an AI needs: project info, stack, instructions, and score.
    Use this to quickly understand a project without reading the full .faf structure."""
    try:
        faf = _parse_faf(path)
        data = faf.data
        mk4 = _mk4_score_file(path)

        context = {
            "project": {
                "name": data.project.name,
                "goal": data.project.goal,
                "language": data.project.main_language,
            },
            "score": mk4.score,
            "tier": mk4.tier,
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
@_confined
def faf_gemini(path: str = "project.faf") -> dict:
    """Export and write GEMINI.md from a .faf file (non-destructive).
    Authors GEMINI.md in Gemini CLI's own convention (hierarchical,
    @file-importable — setup · verify · key files · stack · confirm-first
    actions) via faf-python-sdk's authoring tool, in parity with faf-cli's
    `faf export --gemini`. Injects it as a faf-managed block, preserving any
    hand content. Re-running updates the block in place."""
    try:
        faf = _parse_faf(path)
        mk4 = _mk4_score_file(path)
        md = author_gemini_md(faf.data.raw)
        target = confine_file_op(str(Path(path).parent / "GEMINI.md"))
        inject_faf_block(target, md)
        return {
            "success": True,
            "path": str(target),
            "content": md,
            "score": mk4.score,
            "tier": mk4.tier,
            "message": "GEMINI.md updated — faf block injected, existing content preserved",
        }
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_confined
def faf_agents(path: str = "project.faf") -> dict:
    """Export and write AGENTS.md from a .faf file (non-destructive).
    Authors a BETTER-shaped AGENTS.md (setup · tests · layout · conventions ·
    three-tier guardrails · definition of done · security · commit) via
    faf-python-sdk's authoring tool — in parity with faf-cli's `faf export --agents`.
    Injects it into AGENTS.md as a faf-managed block, preserving any hand
    content. Re-running updates the block in place — it never overwrites your file."""
    try:
        faf = _parse_faf(path)
        md = author_agents_md(faf.data.raw)
        target = confine_file_op(str(Path(path).parent / "AGENTS.md"))
        inject_faf_block(target, md)
        return {
            "success": True,
            "path": str(target),
            "content": md,
            "message": "AGENTS.md updated — faf block injected, existing content preserved",
        }
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except FafParseError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
@_confined
def faf_migrate(path: str = "project.faf", dry_run: bool = False) -> dict:
    """Migrate a .faf file to the current format version (3.0).
    Bumps `faf_version`, ensures the section roots exist (`project`, `stack`,
    `human_context`, `monorepo`), and re-serializes. Legacy slot names
    (`frontend`/`database`/…) still score via the registry's aliases — this
    only touches the version and structure, never your values. Parity with
    faf-cli's `faf migrate`. Pass dry_run=true to preview."""
    try:
        faf = _parse_faf(path)
        data = dict(faf.data.raw)
        old = str(data.get("faf_version") or "unknown")

        if old == FAF_FORMAT_VERSION:
            return {"success": True, "changed": False,
                    "message": f"Already at faf_version {FAF_FORMAT_VERSION}"}

        data["faf_version"] = FAF_FORMAT_VERSION
        for root in ("project", "stack", "human_context", "monorepo"):
            data.setdefault(root, {})

        if dry_run:
            return {"success": True, "changed": True, "dry_run": True,
                    "message": f"Would migrate {path}: faf_version {old} -> {FAF_FORMAT_VERSION}"}

        safe = confine_file_op(path)
        safe.write_text(stringify(data))
        return {"success": True, "changed": True,
                "old_version": old, "new_version": FAF_FORMAT_VERSION,
                "path": str(safe),
                "message": f"Migrated {path}: faf_version {old} -> {FAF_FORMAT_VERSION}"}
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
    has_pubspec = (dir_path / "pubspec.yaml").is_file()

    # Priority: pyproject.toml / Cargo.toml / go.mod / pubspec.yaml > package.json
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

    elif has_pubspec:
        # Dart/Flutter — DELEGATE to the SDK detector (the shared Truth, A+B hybrid).
        # NEVER fork pubspec parsing here: faf_sdk.detect_dart_project is the one brain
        # (faf-cli src/detect/dart.ts <-> faf_sdk/detect.py, byte-identical spec, parity-tested).
        detected["main_language"] = "Dart"
        detected["package_manager"] = "pub"
        dart = detect_dart_project(str(dir_path))
        if dart:
            if dart.framework:
                detected["framework"] = dart.framework
            if dart.testing:
                detected["testing"] = dart.testing
            if dart.app_type == "mcp":
                detected["api_type"] = "MCP"
            elif dart.app_type == "backend":
                detected["api_type"] = "REST"

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

    # --- Metadata Extraction (Name, Version, Goal) ---
    try:
        if has_pyproject:
            import tomllib
            data = tomllib.loads((dir_path / "pyproject.toml").read_text())
            if "project" in data:
                detected["name"] = data["project"].get("name")
                detected["version"] = data["project"].get("version")
                detected["goal"] = data["project"].get("description")
        elif has_package_json:
            import json as _json
            data = _json.loads((dir_path / "package.json").read_text())
            detected["name"] = data.get("name")
            detected["version"] = data.get("version")
            detected["goal"] = data.get("description")
        elif has_cargo:
            content = (dir_path / "Cargo.toml").read_text()
            import re
            name_match = re.search(r'^name\s*=\s*"(.*)"', content, re.MULTILINE)
            version_match = re.search(r'^version\s*=\s*"(.*)"', content, re.MULTILINE)
            if name_match:
                detected["name"] = name_match.group(1)
            if version_match:
                detected["version"] = version_match.group(1)
        elif has_pubspec:
            import re
            content = (dir_path / "pubspec.yaml").read_text()
            name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            version_match = re.search(r'^version:\s*(.+)$', content, re.MULTILINE)
            desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
            if name_match:
                detected["name"] = name_match.group(1).strip()
            if version_match:
                detected["version"] = version_match.group(1).strip().strip('"\'')
            if desc_match:
                desc = desc_match.group(1).strip()
                if desc not in (">", "|", ">-", "|-"):  # skip folded/literal block headers
                    detected["goal"] = desc
    except Exception:
        pass

    # CI/CD — a file fact, same class as docker-compose.
    if (dir_path / ".github" / "workflows").is_dir():
        detected["cicd"] = "GitHub Actions"
    elif (dir_path / ".gitlab-ci.yml").is_file():
        detected["cicd"] = "GitLab CI"
    elif (dir_path / ".circleci").is_dir():
        detected["cicd"] = "CircleCI"

    return detected


@mcp.tool()
@_confined
def faf_auto(directory: str = ".", path: str = "project.faf") -> dict:
    """Auto-detect project stack and author/update a .faf file.
    Scans package.json, pyproject.toml, Cargo.toml, go.mod, and other manifest
    files for language, framework, database, API type, and build tools — then
    grounds the result in the repo's own files: docker-compose service images
    (Postgres, Redis, Elasticsearch...) map onto stack slots, and Makefile /
    justfile targets map onto test / build / lint commands. Facts from files,
    no hardcoded defaults. Creates a new .faf if none exists, or fills empty
    slots in an existing one."""
    try:
        dir_path = Path(directory).resolve()
        if not dir_path.is_dir():
            return {"success": False, "error": f"Directory not found: {directory}"}

        detected = _detect_stack(directory)

        # Full-Facts grounding: docker-compose services + Makefile targets are
        # ground truth the root-manifest scan never sees (in parity with
        # faf-cli 7.10). A running Postgres/Redis service IS the database/cache —
        # it wins over a dependency guess (an ORM in requirements ≠ the DB).
        # `hosting` / `runtime` only fill empties (Cloud Run beats "Docker Compose").
        ground = interrogate_repo(directory)
        for slot in ("database", "cache", "search", "storage"):
            if ground["stack"].get(slot):
                detected[slot] = ground["stack"][slot]
        for slot in ("runtime", "hosting"):
            if ground["stack"].get(slot) and not detected.get(slot):
                detected[slot] = ground["stack"][slot]
        commands: dict[str, str] = dict(ground["commands"])

        # Resolve path relative to directory
        faf_path = Path(path)
        if not faf_path.is_absolute():
            faf_path = dir_path / faf_path
        faf_path = faf_path.resolve()

        created = not faf_path.exists()

        def _yv(v: str) -> str:
            """Quote a detected value for YAML unless it is the bare sentinel."""
            return v if v == "slotignored" else '"' + v.replace('"', '\\"') + '"'

        if created:
            # Author a new .faf from detection + Full-Facts grounding.
            name = detected.get("name") or dir_path.name or "my-project"
            lang = detected.get("main_language", "unknown")
            goal = detected.get("goal") or "Describe your project goal"
            version = detected.get("version") or "0.1.0"
            fw = detected.get("framework")
            _stack = {
                "frontend": fw if fw in FRONTEND_FRAMEWORKS else "slotignored",
                "css_framework": "slotignored",
                "ui_library": "slotignored",
                "state_management": "slotignored",
                "backend": fw if fw in BACKEND_FRAMEWORKS else "slotignored",
                "api_type": detected.get("api_type", "slotignored"),
                "runtime": detected.get("runtime", "slotignored"),
                "database": detected.get("database", "slotignored"),
                "cache": detected.get("cache", "slotignored"),
                "search": detected.get("search", "slotignored"),
                "storage": detected.get("storage", "slotignored"),
                "connection": "slotignored",
                "hosting": detected.get("hosting", "slotignored"),
                "build": detected.get("build_tool", "slotignored"),
                "cicd": detected.get("cicd", "slotignored"),
                "testing": detected.get("testing", "slotignored"),
            }
            stack_lines = "\n".join(f"  {k}: {_yv(v)}" for k, v in _stack.items())
            cmd_lines = (
                "\n".join(f"  {k}: {_yv(v)}" for k, v in commands.items())
                if commands else '  test: ""\n  build: ""'
            )
            content = f"""faf_version: "{FAF_FORMAT_VERSION}"
project:
  name: {_yv(name)}
  goal: {_yv(goal)}
  main_language: {_yv(lang)}
stack:
{stack_lines}
commands:
{cmd_lines}
key_files: []
human_context:
  who: Developers
  what: {_yv(goal)}
  why: Why does this project exist?
ai_instructions:
  working_style:
    quality_bar: zero_errors
    testing: required
  warnings: []
preferences:
  commit_style: conventional
state:
  phase: development
  version: {_yv(version)}
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
            
            # Fill metadata if missing
            for field, key in [("name", "name"), ("goal", "goal"), ("version", "version")]:
                val = detected.get(key)
                if val and f"{field}: null" in updated:
                    updated = updated.replace(f"{field}: null", f"{field}: {val}")
                if val and field == "goal" and "Describe your project goal" in updated:
                    updated = updated.replace("Describe your project goal", val)

            # Fill null stack fields — includes the Full-Facts slots
            # (database / cache / search / storage / runtime / hosting) grounded
            # from docker-compose above.
            _stack_fill = [
                ("frontend", "framework"), ("backend", "framework"),
                ("database", "database"), ("cache", "cache"), ("search", "search"),
                ("storage", "storage"), ("runtime", "runtime"), ("hosting", "hosting"),
                ("testing", "testing"),
            ]
            for field, key in _stack_fill:
                val = detected.get(key)
                if val and f"  {field}: null" in updated:
                    if field == "frontend" and val not in FRONTEND_FRAMEWORKS:
                        continue
                    if field == "backend" and val not in BACKEND_FRAMEWORKS:
                        continue
                    updated = updated.replace(f"  {field}: null", f'  {field}: {_yv(val)}')

            # Fill empty command slots from Makefile / justfile targets
            for cmd, val in commands.items():
                for empty in (f'  {cmd}: ""', f"  {cmd}: null"):
                    if empty in updated:
                        updated = updated.replace(empty, f'  {cmd}: {_yv(val)}')
                        break

            if updated != existing:
                faf_path.write_text(updated)

        # Score with Mk4 engine
        try:
            mk4 = _mk4_score_file(str(faf_path))
            score = mk4.score
            tier = mk4.tier
        except Exception:
            score = 0
            tier = "RED"

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
                "cache": detected.get("cache"),
                "search": detected.get("search"),
                "hosting": detected.get("hosting"),
                "commands": commands or None,
            },
            "score": score,
            "tier": tier,
            "message": " ".join(msg_parts),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main() -> None:
    """Single entry for both the console script (`gemini-faf-mcp`, via
    pyproject [project.scripts]) and `python server.py`.

    Transports are passed EXPLICITLY — never rely on FastMCP's default. The
    console script previously pointed at `server:mcp.run`, which left the
    transport to FastMCP's default; a future FastMCP changing that default
    would silently flip `uvx gemini-faf-mcp` users off stdio and break every
    MCP client. Being explicit makes the contract bulletproof.

    Default = stdio (the `uvx`/CLI path). When PORT is set (Cloud Run) or
    MCP_TRANSPORT=http, serve modern Streamable HTTP instead — same tools,
    just a hosted transport.
    """
    _port = os.environ.get("PORT")
    _raw = os.environ.get("MCP_TRANSPORT", "http" if _port else "stdio")
    if _raw == "stdio":
        mcp.run(transport="stdio")
    elif _raw in ("http", "sse", "streamable-http"):
        from typing import Literal, cast

        _t = cast(Literal["http", "sse", "streamable-http"], _raw)
        mcp.run(transport=_t, host="0.0.0.0", port=int(_port or 8080))
    else:
        # Unknown MCP_TRANSPORT → safe hosted default
        mcp.run(transport="http", host="0.0.0.0", port=int(_port or 8080))


if __name__ == "__main__":
    main()
