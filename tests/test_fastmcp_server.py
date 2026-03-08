"""
gemini-faf-mcp v2.0.0 — FastMCP Server Tests

Tests all 10 MCP tools using FastMCP's test client pattern.
Separate from WJTTC suite (which tests the Cloud Function).
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

# Add repo root to path so we can import server.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp.client import Client
from server import mcp

# --- Sample .faf content for testing ---

VALID_FAF = """faf_version: '2.5.0'
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
  what: A test project
  why: Validate MCP tools work correctly
ai_instructions:
  priority: Read project.faf first
  usage: Code-first
preferences:
  quality_bar: zero_errors
state:
  phase: testing
  version: 1.0.0
"""

MINIMAL_FAF = """faf_version: '2.5.0'
project:
  name: minimal-project
"""


# --- Fixtures ---


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


@pytest.fixture
def faf_file(tmp_path):
    """Create a temporary .faf file for testing."""
    faf_path = tmp_path / "project.faf"
    faf_path.write_text(VALID_FAF)
    return str(faf_path)


@pytest.fixture
def minimal_faf_file(tmp_path):
    """Create a minimal .faf file."""
    faf_path = tmp_path / "project.faf"
    faf_path.write_text(MINIMAL_FAF)
    return str(faf_path)


# --- Tool Tests ---


class TestFafRead:
    async def test_read_valid_file(self, client, faf_file):
        result = await client.call_tool("faf_read", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert data["data"]["project"]["name"] == "test-project"

    async def test_read_missing_file(self, client):
        result = await client.call_tool("faf_read", {"path": "/nonexistent/project.faf"})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is False
        assert "not found" in data["error"].lower()


class TestFafValidate:
    async def test_validate_full_file(self, client, faf_file):
        result = await client.call_tool("faf_validate", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert data["valid"] is True
        assert isinstance(data["score"], int)
        assert data["score"] > 0
        assert data["tier"] in ["Trophy", "Gold", "Silver", "Bronze", "Green", "Yellow", "Red"]

    async def test_validate_minimal_file(self, client, minimal_faf_file):
        result = await client.call_tool("faf_validate", {"path": minimal_faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert isinstance(data["score"], int)

    async def test_validate_missing_file(self, client):
        result = await client.call_tool("faf_validate", {"path": "/nonexistent.faf"})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is False


class TestFafScore:
    async def test_score_valid(self, client, faf_file):
        result = await client.call_tool("faf_score", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert isinstance(data["score"], int)
        assert data["score"] > 0
        assert data["tier"] in ["Trophy", "Gold", "Silver", "Bronze", "Green", "Yellow", "Red"]
        assert data["valid"] is True

    async def test_score_missing(self, client):
        result = await client.call_tool("faf_score", {"path": "/nonexistent.faf"})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["score"] == 0
        assert data["tier"] == "White"


class TestFafDiscover:
    async def test_discover_finds_file(self, client, faf_file):
        search_dir = str(Path(faf_file).parent)
        result = await client.call_tool("faf_discover", {"start_dir": search_dir})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["found"] is True
        assert "project.faf" in data["path"]

    async def test_discover_no_file(self, client, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = await client.call_tool("faf_discover", {"start_dir": str(empty_dir)})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["found"] is False


class TestFafInit:
    async def test_init_creates_file(self, client, tmp_path):
        target = str(tmp_path / "new_project.faf")
        result = await client.call_tool(
            "faf_init",
            {"name": "my-app", "goal": "Test app", "language": "Python", "path": target},
        )
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert os.path.exists(target)
        content = Path(target).read_text()
        assert "my-app" in content
        assert "Python" in content

    async def test_init_refuses_overwrite(self, client, faf_file):
        result = await client.call_tool("faf_init", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is False
        assert "already exists" in data["error"]


class TestFafStringify:
    async def test_stringify_roundtrip(self, client, faf_file):
        result = await client.call_tool("faf_stringify", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert "test-project" in data["yaml"]
        assert "faf_version" in data["yaml"]

    async def test_stringify_missing(self, client):
        result = await client.call_tool("faf_stringify", {"path": "/nonexistent.faf"})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is False


class TestFafContext:
    async def test_context_full(self, client, faf_file):
        result = await client.call_tool("faf_context", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        ctx = data["context"]
        assert ctx["project"]["name"] == "test-project"
        assert ctx["project"]["language"] == "Python"
        assert isinstance(ctx["score"], int)
        assert ctx["tier"] in ["Trophy", "Gold", "Silver", "Bronze", "Green", "Yellow", "Red"]
        assert "human_context" in ctx
        assert ctx["human_context"]["who"] == "Developers"
        assert "stack" in ctx
        assert ctx["stack"]["backend"] == "FastAPI"

    async def test_context_minimal(self, client, minimal_faf_file):
        result = await client.call_tool("faf_context", {"path": minimal_faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert data["context"]["project"]["name"] == "minimal-project"


class TestFafGemini:
    async def test_gemini_export(self, client, faf_file):
        result = await client.call_tool("faf_gemini", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert "test-project" in data["content"]
        assert "faf_score" in data["content"]
        assert isinstance(data["score"], int)
        assert data["tier"] in ["Trophy", "Gold", "Silver", "Bronze", "Green", "Yellow", "Red"]


class TestFafAgents:
    async def test_agents_export(self, client, faf_file):
        result = await client.call_tool("faf_agents", {"path": faf_file})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["success"] is True
        assert "test-project" in data["content"]
        assert "AGENTS.md" in data["content"]
        assert "Developers" in data["content"]
        assert "FastAPI" in data["content"]


class TestFafAbout:
    async def test_about_returns_info(self, client):
        result = await client.call_tool("faf_about", {})
        data = result.data if hasattr(result, "data") else json.loads(result[0].text)
        assert data["name"] == "FAF (Foundational AI-context Format)"
        assert data["media_type"] == "application/vnd.faf+yaml"
        assert data["iana_registered"] is True
        assert data["server"] == "gemini-faf-mcp"
        assert data["server_version"] == "2.0.0"
        assert data["tools"] == 10
        assert "gemini" in data["ecosystem"]


class TestToolListing:
    async def test_lists_all_tools(self, client):
        tools = await client.list_tools()
        tool_names = {t.name for t in tools}
        expected = {
            "faf_read",
            "faf_validate",
            "faf_score",
            "faf_discover",
            "faf_init",
            "faf_stringify",
            "faf_context",
            "faf_gemini",
            "faf_agents",
            "faf_about",
        }
        assert tool_names == expected
        assert len(tools) == 10
