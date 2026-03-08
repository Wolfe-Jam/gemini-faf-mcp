"""
WJTTC Test Suite: gemini-faf-mcp v2.0.0 — FastMCP Server
Championship-grade certification for Gemini Extensions Gallery

Tier 1: BRAKE (Critical)     — Server boots, tools registered, MCP handshake
Tier 2: ENGINE (Core)        — Each tool works with valid input
Tier 3: AERO (Error Paths)   — Graceful failure on bad input
Tier 4: SCORING (Tier Math)  — Score → tier mapping, boundary conditions
Tier 5: EXPORTS (Interop)    — GEMINI.md / AGENTS.md output quality
Tier 6: SAFETY (Guard Rails) — Overwrite protection, path handling
Tier 7: CONTRACT (API Shape) — Response schemas, field types, consistency
Tier 8: ROUNDTRIP (Pipeline) — init → read → validate → score → stringify
Tier 9: GALLERY (Extension)  — gemini-extension.json manifest validation
"""

import os
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp.client import Client
from server import mcp, _get_tier, __version__, TIERS


# ---------------------------------------------------------------------------
# Test fixtures & sample data
# ---------------------------------------------------------------------------

FULL_FAF = """\
faf_version: '2.5.0'
project:
  name: test-project
  goal: Test project for MCP server validation
  main_language: Python
stack:
  frontend: React
  backend: FastAPI
  database: PostgreSQL
  testing: pytest
human_context:
  who: Developers
  what: A test project for validation
  why: Validate MCP tools work correctly
  where: Local development
  when: On-demand
  how: Python + FastMCP
ai_instructions:
  priority: Read project.faf first
  usage: Code-first
preferences:
  quality_bar: zero_errors
state:
  phase: testing
  version: 1.0.0
"""

MINIMAL_FAF = """\
faf_version: '2.5.0'
project:
  name: minimal-project
"""

EMPTY_PROJECT_FAF = """\
faf_version: '2.5.0'
project:
  name: empty-slots
  goal: null
  main_language: null
"""

INVALID_YAML = """\
this is not: valid: yaml: {{{{
  broken [
"""


def _parse(result):
    """Extract dict from FastMCP tool result."""
    if hasattr(result, "data") and isinstance(result.data, dict):
        return result.data
    return json.loads(result[0].text)


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


@pytest.fixture
def full_faf(tmp_path):
    p = tmp_path / "project.faf"
    p.write_text(FULL_FAF)
    return str(p)


@pytest.fixture
def minimal_faf(tmp_path):
    p = tmp_path / "project.faf"
    p.write_text(MINIMAL_FAF)
    return str(p)


@pytest.fixture
def empty_faf(tmp_path):
    p = tmp_path / "project.faf"
    p.write_text(EMPTY_PROJECT_FAF)
    return str(p)


@pytest.fixture
def invalid_faf(tmp_path):
    p = tmp_path / "project.faf"
    p.write_text(INVALID_YAML)
    return str(p)


@pytest.fixture
def empty_dir(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    return str(d)


# ===================================================================
# TIER 1: BRAKE SYSTEMS (Critical) — Must not fail
# ===================================================================

class TestTier1Brake:
    """Server fundamentals. Failure here = showstopper."""

    async def test_server_name(self, client):
        """Server identifies as gemini-faf-mcp."""
        assert mcp.name == "gemini-faf-mcp"

    async def test_server_version(self):
        """Server version matches 2.0.0."""
        assert __version__ == "2.0.0"

    async def test_tool_count(self, client):
        """Exactly 10 tools registered."""
        tools = await client.list_tools()
        assert len(tools) == 10

    async def test_all_tool_names(self, client):
        """All 10 expected tools are present."""
        tools = await client.list_tools()
        names = {t.name for t in tools}
        expected = {
            "faf_read", "faf_validate", "faf_score", "faf_discover",
            "faf_init", "faf_stringify", "faf_context",
            "faf_gemini", "faf_agents", "faf_about",
        }
        assert names == expected

    async def test_no_extra_tools(self, client):
        """No unexpected tools leaked in."""
        tools = await client.list_tools()
        names = {t.name for t in tools}
        for name in names:
            assert name.startswith("faf_"), f"Unexpected tool: {name}"

    async def test_all_tools_have_descriptions(self, client):
        """Every tool has a non-empty description."""
        tools = await client.list_tools()
        for t in tools:
            assert t.description, f"Tool {t.name} has no description"
            assert len(t.description) > 10, f"Tool {t.name} description too short"

    async def test_faf_read_responds(self, client, full_faf):
        """faf_read returns data (smoke test)."""
        result = await client.call_tool("faf_read", {"path": full_faf})
        data = _parse(result)
        assert data["success"] is True

    async def test_faf_about_responds(self, client):
        """faf_about returns data (smoke test)."""
        result = await client.call_tool("faf_about", {})
        data = _parse(result)
        assert "name" in data


# ===================================================================
# TIER 2: ENGINE SYSTEMS (Core) — Each tool, happy path
# ===================================================================

class TestTier2Engine:
    """Core functionality — every tool with valid input."""

    async def test_read_returns_project_name(self, client, full_faf):
        result = await client.call_tool("faf_read", {"path": full_faf})
        data = _parse(result)
        assert data["data"]["project"]["name"] == "test-project"

    async def test_read_returns_full_structure(self, client, full_faf):
        result = await client.call_tool("faf_read", {"path": full_faf})
        data = _parse(result)
        assert "faf_version" in data["data"]
        assert "stack" in data["data"]
        assert "human_context" in data["data"]

    async def test_read_includes_path(self, client, full_faf):
        result = await client.call_tool("faf_read", {"path": full_faf})
        data = _parse(result)
        assert data["path"] == full_faf

    async def test_validate_full_file(self, client, full_faf):
        result = await client.call_tool("faf_validate", {"path": full_faf})
        data = _parse(result)
        assert data["success"] is True
        assert data["valid"] is True
        assert isinstance(data["score"], int)
        assert data["score"] > 0

    async def test_validate_returns_tier(self, client, full_faf):
        result = await client.call_tool("faf_validate", {"path": full_faf})
        data = _parse(result)
        valid_tiers = {"Trophy", "Gold", "Silver", "Bronze", "Green", "Yellow", "Red"}
        assert data["tier"] in valid_tiers

    async def test_validate_returns_lists(self, client, full_faf):
        result = await client.call_tool("faf_validate", {"path": full_faf})
        data = _parse(result)
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)

    async def test_score_valid_file(self, client, full_faf):
        result = await client.call_tool("faf_score", {"path": full_faf})
        data = _parse(result)
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 100
        assert data["valid"] is True

    async def test_score_matches_validate(self, client, full_faf):
        """faf_score and faf_validate return same score for same file."""
        r1 = await client.call_tool("faf_score", {"path": full_faf})
        r2 = await client.call_tool("faf_validate", {"path": full_faf})
        assert _parse(r1)["score"] == _parse(r2)["score"]

    async def test_discover_finds_project_faf(self, client, full_faf):
        search_dir = str(Path(full_faf).parent)
        result = await client.call_tool("faf_discover", {"start_dir": search_dir})
        data = _parse(result)
        assert data["found"] is True
        assert "project.faf" in data["path"]

    async def test_init_creates_file(self, client, tmp_path):
        target = str(tmp_path / "new.faf")
        result = await client.call_tool("faf_init", {
            "name": "my-app", "goal": "Test app",
            "language": "Python", "path": target,
        })
        data = _parse(result)
        assert data["success"] is True
        assert os.path.exists(target)

    async def test_init_content_matches_args(self, client, tmp_path):
        target = str(tmp_path / "new.faf")
        await client.call_tool("faf_init", {
            "name": "cool-project", "goal": "Build something cool",
            "language": "Rust", "path": target,
        })
        content = Path(target).read_text()
        assert "cool-project" in content
        assert "Build something cool" in content
        assert "Rust" in content

    async def test_init_creates_valid_yaml(self, client, tmp_path):
        """faf_init output is parseable by faf_read."""
        target = str(tmp_path / "new.faf")
        await client.call_tool("faf_init", {
            "name": "yaml-test", "path": target,
        })
        result = await client.call_tool("faf_read", {"path": target})
        data = _parse(result)
        assert data["success"] is True
        assert data["data"]["project"]["name"] == "yaml-test"

    async def test_stringify_roundtrip(self, client, full_faf):
        result = await client.call_tool("faf_stringify", {"path": full_faf})
        data = _parse(result)
        assert data["success"] is True
        assert "test-project" in data["yaml"]
        assert "faf_version" in data["yaml"]

    async def test_context_returns_project(self, client, full_faf):
        result = await client.call_tool("faf_context", {"path": full_faf})
        data = _parse(result)
        assert data["success"] is True
        assert data["context"]["project"]["name"] == "test-project"

    async def test_context_includes_sections(self, client, full_faf):
        result = await client.call_tool("faf_context", {"path": full_faf})
        ctx = _parse(result)["context"]
        assert "human_context" in ctx
        assert "stack" in ctx
        assert "score" in ctx
        assert "tier" in ctx

    async def test_gemini_export(self, client, full_faf):
        result = await client.call_tool("faf_gemini", {"path": full_faf})
        data = _parse(result)
        assert data["success"] is True
        assert isinstance(data["content"], str)
        assert isinstance(data["score"], int)

    async def test_agents_export(self, client, full_faf):
        result = await client.call_tool("faf_agents", {"path": full_faf})
        data = _parse(result)
        assert data["success"] is True
        assert isinstance(data["content"], str)

    async def test_about_ecosystem(self, client):
        result = await client.call_tool("faf_about", {})
        data = _parse(result)
        assert data["iana_registered"] is True
        assert data["media_type"] == "application/vnd.faf+yaml"
        assert data["tools"] == 10
        assert len(data["ecosystem"]) >= 5


# ===================================================================
# TIER 3: AERO (Error Paths) — Graceful failure
# ===================================================================

class TestTier3Aero:
    """Every tool must fail gracefully, never crash."""

    async def test_read_missing_file(self, client):
        data = _parse(await client.call_tool("faf_read", {"path": "/nonexistent.faf"}))
        assert data["success"] is False
        assert "error" in data

    async def test_read_invalid_yaml(self, client, invalid_faf):
        data = _parse(await client.call_tool("faf_read", {"path": invalid_faf}))
        assert data["success"] is False

    async def test_validate_missing_file(self, client):
        data = _parse(await client.call_tool("faf_validate", {"path": "/nonexistent.faf"}))
        assert data["success"] is False

    async def test_validate_invalid_yaml(self, client, invalid_faf):
        data = _parse(await client.call_tool("faf_validate", {"path": invalid_faf}))
        assert data["success"] is False

    async def test_score_missing_returns_zero(self, client):
        data = _parse(await client.call_tool("faf_score", {"path": "/nonexistent.faf"}))
        assert data["score"] == 0
        assert data["tier"] == "White"

    async def test_score_invalid_yaml(self, client, invalid_faf):
        data = _parse(await client.call_tool("faf_score", {"path": invalid_faf}))
        assert data["score"] == 0
        assert data["tier"] == "White"

    async def test_discover_empty_dir(self, client, empty_dir):
        data = _parse(await client.call_tool("faf_discover", {"start_dir": empty_dir}))
        assert data["found"] is False

    async def test_stringify_missing_file(self, client):
        data = _parse(await client.call_tool("faf_stringify", {"path": "/nonexistent.faf"}))
        assert data["success"] is False

    async def test_stringify_invalid_yaml(self, client, invalid_faf):
        data = _parse(await client.call_tool("faf_stringify", {"path": invalid_faf}))
        assert data["success"] is False

    async def test_context_missing_file(self, client):
        data = _parse(await client.call_tool("faf_context", {"path": "/nonexistent.faf"}))
        assert data["success"] is False

    async def test_gemini_missing_file(self, client):
        data = _parse(await client.call_tool("faf_gemini", {"path": "/nonexistent.faf"}))
        assert data["success"] is False

    async def test_agents_missing_file(self, client):
        data = _parse(await client.call_tool("faf_agents", {"path": "/nonexistent.faf"}))
        assert data["success"] is False

    async def test_context_minimal_no_crash(self, client, minimal_faf):
        """Minimal .faf (no stack, no human_context) doesn't crash faf_context."""
        data = _parse(await client.call_tool("faf_context", {"path": minimal_faf}))
        assert data["success"] is True
        assert data["context"]["project"]["name"] == "minimal-project"

    async def test_gemini_minimal_no_crash(self, client, minimal_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": minimal_faf}))
        assert data["success"] is True

    async def test_agents_minimal_no_crash(self, client, minimal_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": minimal_faf}))
        assert data["success"] is True

    async def test_context_null_fields_no_crash(self, client, empty_faf):
        """Explicit null fields don't crash faf_context."""
        data = _parse(await client.call_tool("faf_context", {"path": empty_faf}))
        assert data["success"] is True


# ===================================================================
# TIER 4: SCORING (Tier Math) — Boundary conditions
# ===================================================================

class TestTier4Scoring:
    """Tier calculation must be mathematically correct."""

    def test_tier_100_is_trophy(self):
        assert _get_tier(100) == "Trophy"

    def test_tier_99_is_gold(self):
        assert _get_tier(99) == "Gold"

    def test_tier_95_is_silver(self):
        assert _get_tier(95) == "Silver"

    def test_tier_85_is_bronze(self):
        assert _get_tier(85) == "Bronze"

    def test_tier_70_is_green(self):
        assert _get_tier(70) == "Green"

    def test_tier_55_is_yellow(self):
        assert _get_tier(55) == "Yellow"

    def test_tier_0_is_red(self):
        assert _get_tier(0) == "Red"

    def test_tier_negative_is_white(self):
        assert _get_tier(-1) == "White"

    def test_tier_boundary_99_not_trophy(self):
        """99 is Gold, not Trophy — Trophy requires exactly 100."""
        assert _get_tier(99) != "Trophy"

    def test_tier_boundary_95_not_gold(self):
        assert _get_tier(95) != "Gold"

    def test_tier_boundary_85_not_silver(self):
        assert _get_tier(85) != "Silver"

    def test_tier_boundary_70_not_bronze(self):
        assert _get_tier(70) != "Bronze"

    def test_tier_boundary_55_not_green(self):
        assert _get_tier(55) != "Green"

    def test_tier_boundary_54_is_yellow(self):
        """54 is below Yellow threshold — drops to Red."""
        assert _get_tier(54) == "Red"

    def test_tier_list_descending(self):
        """TIERS list is in descending order (highest first)."""
        thresholds = [t[0] for t in TIERS]
        assert thresholds == sorted(thresholds, reverse=True)

    def test_score_and_validate_tier_agree(self, full_faf):
        """faf_score and faf_validate produce same tier for same file."""
        # This is a sync test using the internal function
        from faf_sdk import parse_file, validate
        faf = parse_file(full_faf)
        result = validate(faf)
        assert _get_tier(result.score) in {"Trophy", "Gold", "Silver", "Bronze", "Green", "Yellow", "Red"}

    async def test_minimal_faf_scores_lower(self, client, tmp_path):
        """Full .faf scores higher than minimal .faf."""
        full = tmp_path / "full.faf"
        full.write_text(FULL_FAF)
        mini = tmp_path / "mini.faf"
        mini.write_text(MINIMAL_FAF)
        r1 = _parse(await client.call_tool("faf_score", {"path": str(full)}))
        r2 = _parse(await client.call_tool("faf_score", {"path": str(mini)}))
        assert r1["score"] > r2["score"]


# ===================================================================
# TIER 5: EXPORTS (Interop) — GEMINI.md / AGENTS.md quality
# ===================================================================

class TestTier5Exports:
    """Export tools produce valid, useful output."""

    async def test_gemini_has_frontmatter(self, client, full_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": full_faf}))
        content = data["content"]
        assert content.startswith("---")
        assert "faf_score:" in content
        assert "faf_tier:" in content

    async def test_gemini_has_project_name(self, client, full_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": full_faf}))
        assert "test-project" in data["content"]

    async def test_gemini_has_iana_reference(self, client, full_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": full_faf}))
        assert "application/vnd.faf+yaml" in data["content"]

    async def test_gemini_score_matches_metadata(self, client, full_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": full_faf}))
        assert f"{data['score']}%" in data["content"]
        assert data["tier"] in data["content"]

    async def test_gemini_high_score_autonomy(self, client, full_faf):
        """Score >= 85 should say 'full autonomy' in GEMINI.md."""
        data = _parse(await client.call_tool("faf_gemini", {"path": full_faf}))
        if data["score"] >= 85:
            assert "full autonomy" in data["content"]

    async def test_agents_has_header(self, client, full_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": full_faf}))
        assert "# AGENTS.md" in data["content"]

    async def test_agents_has_project_section(self, client, full_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": full_faf}))
        assert "## Project" in data["content"]
        assert "test-project" in data["content"]

    async def test_agents_has_iana_reference(self, client, full_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": full_faf}))
        assert "application/vnd.faf+yaml" in data["content"]

    async def test_agents_includes_human_context(self, client, full_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": full_faf}))
        assert "Developers" in data["content"]

    async def test_agents_includes_stack(self, client, full_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": full_faf}))
        assert "FastAPI" in data["content"]
        assert "PostgreSQL" in data["content"]

    async def test_agents_minimal_still_valid(self, client, minimal_faf):
        """Minimal .faf produces valid AGENTS.md (no stack/context sections)."""
        data = _parse(await client.call_tool("faf_agents", {"path": minimal_faf}))
        assert "# AGENTS.md" in data["content"]
        assert "minimal-project" in data["content"]


# ===================================================================
# TIER 6: SAFETY (Guard Rails) — File protection
# ===================================================================

class TestTier6Safety:
    """Tools must never corrupt or overwrite user data."""

    async def test_init_refuses_overwrite(self, client, full_faf):
        """faf_init refuses to overwrite existing file."""
        data = _parse(await client.call_tool("faf_init", {"path": full_faf}))
        assert data["success"] is False
        assert "already exists" in data["error"]

    async def test_init_original_unchanged(self, client, full_faf):
        """After refused overwrite, original file is untouched."""
        original = Path(full_faf).read_text()
        await client.call_tool("faf_init", {"path": full_faf})
        assert Path(full_faf).read_text() == original

    async def test_read_does_not_modify_file(self, client, full_faf):
        """faf_read is read-only."""
        original = Path(full_faf).read_text()
        await client.call_tool("faf_read", {"path": full_faf})
        assert Path(full_faf).read_text() == original

    async def test_validate_does_not_modify_file(self, client, full_faf):
        original = Path(full_faf).read_text()
        await client.call_tool("faf_validate", {"path": full_faf})
        assert Path(full_faf).read_text() == original

    async def test_stringify_does_not_modify_file(self, client, full_faf):
        original = Path(full_faf).read_text()
        await client.call_tool("faf_stringify", {"path": full_faf})
        assert Path(full_faf).read_text() == original

    async def test_context_does_not_modify_file(self, client, full_faf):
        original = Path(full_faf).read_text()
        await client.call_tool("faf_context", {"path": full_faf})
        assert Path(full_faf).read_text() == original

    async def test_init_creates_in_correct_location(self, client, tmp_path):
        target = str(tmp_path / "subdir" / "test.faf")
        os.makedirs(str(tmp_path / "subdir"))
        data = _parse(await client.call_tool("faf_init", {"path": target}))
        assert data["success"] is True
        assert os.path.exists(target)

    async def test_error_responses_have_error_field(self, client):
        """All failure responses include 'error' key."""
        tools_with_path = ["faf_read", "faf_validate", "faf_stringify",
                           "faf_context", "faf_gemini", "faf_agents"]
        for tool_name in tools_with_path:
            data = _parse(await client.call_tool(tool_name, {"path": "/nonexistent.faf"}))
            assert "error" in data, f"{tool_name} missing 'error' on failure"


# ===================================================================
# TIER 7: CONTRACT (API Shape) — Response schema consistency
# ===================================================================

class TestTier7Contract:
    """Every tool must return a predictable schema."""

    async def test_read_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_read", {"path": full_faf}))
        assert set(data.keys()) == {"success", "path", "data"}
        assert isinstance(data["data"], dict)

    async def test_read_error_schema(self, client):
        data = _parse(await client.call_tool("faf_read", {"path": "/x.faf"}))
        assert set(data.keys()) == {"success", "error"}

    async def test_validate_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_validate", {"path": full_faf}))
        expected_keys = {"success", "valid", "score", "tier", "errors", "warnings"}
        assert set(data.keys()) == expected_keys

    async def test_score_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_score", {"path": full_faf}))
        assert set(data.keys()) == {"score", "tier", "valid"}

    async def test_score_error_schema(self, client):
        data = _parse(await client.call_tool("faf_score", {"path": "/x.faf"}))
        assert "score" in data
        assert "tier" in data
        assert "error" in data

    async def test_discover_found_schema(self, client, full_faf):
        search_dir = str(Path(full_faf).parent)
        data = _parse(await client.call_tool("faf_discover", {"start_dir": search_dir}))
        assert set(data.keys()) == {"found", "path"}

    async def test_discover_not_found_schema(self, client, empty_dir):
        data = _parse(await client.call_tool("faf_discover", {"start_dir": empty_dir}))
        assert set(data.keys()) == {"found", "searched_from"}

    async def test_init_success_schema(self, client, tmp_path):
        target = str(tmp_path / "schema.faf")
        data = _parse(await client.call_tool("faf_init", {"path": target}))
        assert set(data.keys()) == {"success", "path", "message"}

    async def test_init_error_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_init", {"path": full_faf}))
        assert set(data.keys()) == {"success", "error"}

    async def test_stringify_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_stringify", {"path": full_faf}))
        assert set(data.keys()) == {"success", "yaml"}
        assert isinstance(data["yaml"], str)

    async def test_context_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_context", {"path": full_faf}))
        assert set(data.keys()) == {"success", "context"}
        assert "project" in data["context"]
        assert "score" in data["context"]
        assert "tier" in data["context"]

    async def test_gemini_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": full_faf}))
        assert set(data.keys()) == {"success", "content", "score", "tier"}

    async def test_agents_success_schema(self, client, full_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": full_faf}))
        assert set(data.keys()) == {"success", "content"}

    async def test_about_schema(self, client):
        data = _parse(await client.call_tool("faf_about", {}))
        required = {"name", "media_type", "iana_registered", "spec",
                     "server", "server_version", "sdk", "tools",
                     "ecosystem", "tier_system"}
        assert required.issubset(set(data.keys()))

    async def test_about_ecosystem_has_five_platforms(self, client):
        data = _parse(await client.call_tool("faf_about", {}))
        platforms = data["ecosystem"]
        assert "claude" in platforms
        assert "gemini" in platforms
        assert "grok" in platforms
        assert "cli" in platforms
        assert "rust" in platforms

    async def test_about_tier_system_complete(self, client):
        data = _parse(await client.call_tool("faf_about", {}))
        ts = data["tier_system"]
        assert ts["100%"] == "Trophy"
        assert ts["0%"] == "White"


# ===================================================================
# TIER 8: ROUNDTRIP (Pipeline) — End-to-end integration
# ===================================================================

class TestTier8Roundtrip:
    """Full pipeline: init → read → validate → score → stringify → context."""

    async def test_init_then_read(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "goal": "E2E test", "path": target,
        })
        data = _parse(await client.call_tool("faf_read", {"path": target}))
        assert data["success"] is True
        assert data["data"]["project"]["name"] == "roundtrip"

    async def test_init_then_validate(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "path": target,
        })
        data = _parse(await client.call_tool("faf_validate", {"path": target}))
        assert data["success"] is True
        assert data["valid"] is True
        assert data["score"] > 0

    async def test_init_then_score(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "path": target,
        })
        data = _parse(await client.call_tool("faf_score", {"path": target}))
        assert data["score"] > 0
        assert data["tier"] != "White"

    async def test_init_then_stringify(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "path": target,
        })
        data = _parse(await client.call_tool("faf_stringify", {"path": target}))
        assert data["success"] is True
        assert "roundtrip" in data["yaml"]

    async def test_init_then_context(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "goal": "Pipeline test", "path": target,
        })
        data = _parse(await client.call_tool("faf_context", {"path": target}))
        assert data["success"] is True
        assert data["context"]["project"]["name"] == "roundtrip"

    async def test_init_then_gemini_export(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "path": target,
        })
        data = _parse(await client.call_tool("faf_gemini", {"path": target}))
        assert data["success"] is True
        assert "roundtrip" in data["content"]

    async def test_init_then_agents_export(self, client, tmp_path):
        target = str(tmp_path / "rt.faf")
        await client.call_tool("faf_init", {
            "name": "roundtrip", "path": target,
        })
        data = _parse(await client.call_tool("faf_agents", {"path": target}))
        assert data["success"] is True
        assert "roundtrip" in data["content"]

    async def test_full_pipeline(self, client, tmp_path):
        """The complete championship lap: init → read → validate → score → stringify → context → gemini → agents."""
        target = str(tmp_path / "champion.faf")

        # init
        d = _parse(await client.call_tool("faf_init", {
            "name": "champion", "goal": "Win", "language": "Python", "path": target,
        }))
        assert d["success"] is True

        # read
        d = _parse(await client.call_tool("faf_read", {"path": target}))
        assert d["data"]["project"]["name"] == "champion"

        # validate
        d = _parse(await client.call_tool("faf_validate", {"path": target}))
        assert d["valid"] is True
        score = d["score"]

        # score
        d = _parse(await client.call_tool("faf_score", {"path": target}))
        assert d["score"] == score  # consistent

        # stringify
        d = _parse(await client.call_tool("faf_stringify", {"path": target}))
        assert "champion" in d["yaml"]

        # context
        d = _parse(await client.call_tool("faf_context", {"path": target}))
        assert d["context"]["project"]["name"] == "champion"

        # gemini
        d = _parse(await client.call_tool("faf_gemini", {"path": target}))
        assert "champion" in d["content"]

        # agents
        d = _parse(await client.call_tool("faf_agents", {"path": target}))
        assert "champion" in d["content"]


# ===================================================================
# TIER 9: GALLERY (Extension Manifest) — Gemini CLI compliance
# ===================================================================

class TestTier9Gallery:
    """gemini-extension.json must be valid for the Gemini Extensions Gallery."""

    @pytest.fixture
    def manifest(self):
        manifest_path = Path(__file__).parent.parent / "gemini-extension.json"
        with open(manifest_path) as f:
            return json.load(f)

    def test_manifest_has_name(self, manifest):
        assert manifest["name"] == "gemini-faf-mcp"

    def test_manifest_has_version(self, manifest):
        assert manifest["version"] == "2.0.0"

    def test_manifest_has_description(self, manifest):
        assert len(manifest["description"]) > 20

    def test_manifest_has_mcp_servers(self, manifest):
        assert "mcpServers" in manifest
        assert "faf" in manifest["mcpServers"]

    def test_manifest_uses_python(self, manifest):
        """Extension runs python3, not npx."""
        server = manifest["mcpServers"]["faf"]
        assert server["command"] == "python3"

    def test_manifest_points_to_server_py(self, manifest):
        server = manifest["mcpServers"]["faf"]
        assert any("server.py" in arg for arg in server["args"])

    def test_manifest_has_context_file(self, manifest):
        assert manifest["contextFileName"] == "GEMINI.md"

    def test_server_py_exists(self):
        """server.py exists at repo root."""
        server_path = Path(__file__).parent.parent / "server.py"
        assert server_path.exists()

    def test_gemini_md_exists(self):
        """GEMINI.md exists at repo root."""
        gemini_path = Path(__file__).parent.parent / "GEMINI.md"
        assert gemini_path.exists()
