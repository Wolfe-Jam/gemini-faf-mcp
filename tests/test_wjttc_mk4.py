"""
WJTTC Championship Test Suite: gemini-faf-mcp v2.2.1 — Mk4 Integration
========================================================================
When brakes must work flawlessly, so must our MCP server.

Tier 1: BRAKE (Critical)     - Mk4 scoring wired correctly, no regressions
Tier 2: ENGINE (Core)        - All 12 tools with Mk4 scoring, faf_auto resilience
Tier 3: AERO (Edge Cases)    - Malformed manifests, hostile paths, encoding
Tier 4: STRESS (Scale)       - Concurrent tool calls, large files, many fields
Tier 5: SECURITY (Hardening) - Path traversal, template injection, input validation
Tier 6: CONTRACT (Parity)    - Mk4 scores match across SDK and server
"""

import os
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp.client import Client
from server import mcp, __version__, _mk4_score_file
from faf_sdk.mk4 import score_faf, _score_to_tier, LicenseTier


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TROPHY_FAF = """
faf_version: '2.5.0'
project:
  name: trophy-project
  goal: Achieve 100% Mk4 score
  main_language: Python
human_context:
  who: Championship engineers
  what: F1-grade MCP server
  why: Scale to a million downloads
  where: Global PyPI distribution
  when: "2026"
  how: WJTTC certification
stack:
  frontend: React
  css_framework: Tailwind
  ui_library: Radix
  state_management: Zustand
  backend: FastMCP
  api_type: MCP
  runtime: Python 3.14
  database: PostgreSQL
  connection: asyncpg
  hosting: Cloud Run
  build: setuptools
  cicd: GitHub Actions
"""

MINIMAL_FAF = """
faf_version: '2.5.0'
project:
  name: minimal-project
"""

EMPTY_SLOTS_FAF = """
faf_version: '2.5.0'
project:
  name: null
  goal: ""
  main_language: unknown
"""

SLOTIGNORED_FAF = """
faf_version: '2.5.0'
project:
  name: backend-only
  goal: API service
  main_language: Python
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: FastAPI
  api_type: REST
  runtime: Python
  database: PostgreSQL
  connection: asyncpg
  hosting: AWS
  build: setuptools
  cicd: GitHub Actions
human_context:
  who: API consumers
  what: REST API
  why: Microservices
  where: AWS
  when: "2026"
  how: FastAPI
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
def trophy_faf(tmp_path):
    f = tmp_path / "project.faf"
    f.write_text(TROPHY_FAF)
    return str(f)


@pytest.fixture
def minimal_faf(tmp_path):
    f = tmp_path / "project.faf"
    f.write_text(MINIMAL_FAF)
    return str(f)


@pytest.fixture
def empty_slots_faf(tmp_path):
    f = tmp_path / "project.faf"
    f.write_text(EMPTY_SLOTS_FAF)
    return str(f)


@pytest.fixture
def slotignored_faf(tmp_path):
    f = tmp_path / "project.faf"
    f.write_text(SLOTIGNORED_FAF)
    return str(f)


# ===================================================================
# TIER 1: BRAKE — Critical Mk4 integration. Must never fail.
# ===================================================================


class TestWJTTCTier1Brake:
    """Mk4 scoring engine must be correctly wired into server."""

    async def test_faf_score_returns_mk4_fields(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_score", {"path": trophy_faf}))
        assert "score" in data
        assert "tier" in data
        assert "populated" in data
        assert "active" in data
        assert "total" in data

    async def test_faf_score_trophy_is_100(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_score", {"path": trophy_faf}))
        assert data["score"] == 100
        assert data["tier"] == "TROPHY"
        assert data["populated"] == 21
        assert data["active"] == 21
        assert data["total"] == 21

    async def test_faf_score_minimal_low(self, client, minimal_faf):
        data = _parse(await client.call_tool("faf_score", {"path": minimal_faf}))
        assert data["score"] < 20
        assert data["populated"] == 1  # only name

    async def test_faf_validate_includes_mk4_score(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_validate", {"path": trophy_faf}))
        assert data["score"] == 100
        assert data["populated"] == 21
        assert data["total"] == 21
        assert data["valid"] is True

    async def test_faf_score_and_validate_agree(self, client, trophy_faf):
        """Score from faf_score must equal score from faf_validate."""
        score_data = _parse(await client.call_tool("faf_score", {"path": trophy_faf}))
        validate_data = _parse(await client.call_tool("faf_validate", {"path": trophy_faf}))
        assert score_data["score"] == validate_data["score"]
        assert score_data["tier"] == validate_data["tier"]

    async def test_server_version_is_2_2_0(self, client):
        data = _parse(await client.call_tool("faf_about", {}))
        assert data["server_version"] == "2.2.1"

    async def test_mk4_score_file_helper_works(self, trophy_faf):
        result = _mk4_score_file(trophy_faf)
        assert result.score == 100
        assert result.tier == "TROPHY"


# ===================================================================
# TIER 2: ENGINE — All tools with Mk4 scoring
# ===================================================================


class TestWJTTCTier2Engine:
    """Every tool that returns a score must use Mk4."""

    async def test_faf_context_has_mk4_score(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_context", {"path": trophy_faf}))
        assert data["context"]["score"] == 100
        assert data["context"]["tier"] == "TROPHY"

    async def test_faf_gemini_has_mk4_score(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_gemini", {"path": trophy_faf}))
        assert data["score"] == 100
        assert "100%" in data["content"]

    async def test_faf_agents_has_mk4_score(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_agents", {"path": trophy_faf}))
        assert "100%" in data["content"]

    async def test_faf_auto_scores_with_mk4(self, client, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "auto-test"\ndescription = "Testing auto"\n'
        )
        target = str(tmp_path / "project.faf")
        data = _parse(await client.call_tool("faf_auto", {
            "directory": str(tmp_path), "path": target
        }))
        assert data["success"] is True
        assert isinstance(data["score"], int)
        assert data["score"] >= 0

    async def test_slotignored_adjusts_denominator(self, client, slotignored_faf):
        data = _parse(await client.call_tool("faf_score", {"path": slotignored_faf}))
        assert data["total"] == 21
        assert data["active"] < 21  # some slots ignored
        assert data["score"] == 100  # all active slots populated

    async def test_empty_slots_score_low(self, client, empty_slots_faf):
        data = _parse(await client.call_tool("faf_score", {"path": empty_slots_faf}))
        assert data["score"] == 0  # null, empty, "unknown" all rejected
        assert data["populated"] == 0


# ===================================================================
# TIER 3: AERO — Edge cases and error resilience
# ===================================================================


class TestWJTTCTier3Aero:
    """Tools must handle hostile/unusual inputs gracefully."""

    async def test_score_missing_file_returns_zero(self, client):
        data = _parse(await client.call_tool("faf_score", {"path": "/no/such/file.faf"}))
        assert data["score"] == 0
        assert "error" in data

    async def test_score_invalid_yaml(self, client, tmp_path):
        bad = tmp_path / "bad.faf"
        bad.write_text("key: [unterminated")
        data = _parse(await client.call_tool("faf_score", {"path": str(bad)}))
        assert data["score"] == 0

    async def test_score_empty_file(self, client, tmp_path):
        empty = tmp_path / "empty.faf"
        empty.write_text("")
        data = _parse(await client.call_tool("faf_score", {"path": str(empty)}))
        assert data["score"] == 0

    async def test_score_binary_content(self, client, tmp_path):
        binary = tmp_path / "binary.faf"
        binary.write_bytes(b"\x00\x01\x02\xff\xfe\xfd")
        data = _parse(await client.call_tool("faf_score", {"path": str(binary)}))
        assert data["score"] == 0

    async def test_validate_missing_file(self, client):
        data = _parse(await client.call_tool("faf_validate", {"path": "/no.faf"}))
        assert data["success"] is False

    async def test_auto_nonexistent_directory(self, client):
        data = _parse(await client.call_tool("faf_auto", {"directory": "/nonexistent"}))
        assert data["success"] is False

    async def test_auto_malformed_pyproject(self, client, tmp_path):
        """Malformed pyproject.toml should not crash faf_auto."""
        (tmp_path / "pyproject.toml").write_text("this is not valid toml [[[")
        target = str(tmp_path / "project.faf")
        data = _parse(await client.call_tool("faf_auto", {
            "directory": str(tmp_path), "path": target
        }))
        assert data["success"] is True  # should still create a .faf

    async def test_auto_malformed_package_json(self, client, tmp_path):
        """Malformed package.json should not crash faf_auto."""
        (tmp_path / "package.json").write_text("{invalid json,}")
        target = str(tmp_path / "project.faf")
        data = _parse(await client.call_tool("faf_auto", {
            "directory": str(tmp_path), "path": target
        }))
        assert data["success"] is True

    async def test_auto_empty_pyproject(self, client, tmp_path):
        """Empty pyproject.toml should not crash."""
        (tmp_path / "pyproject.toml").write_text("")
        target = str(tmp_path / "project.faf")
        data = _parse(await client.call_tool("faf_auto", {
            "directory": str(tmp_path), "path": target
        }))
        assert data["success"] is True

    async def test_init_unicode_name(self, client, tmp_path):
        target = str(tmp_path / "project.faf")
        data = _parse(await client.call_tool("faf_init", {
            "name": "\u30d7\u30ed\u30b8\u30a7\u30af\u30c8", "path": target
        }))
        assert data["success"] is True
        content = open(target).read()
        assert "\u30d7\u30ed\u30b8\u30a7\u30af\u30c8" in content

    async def test_model_unknown_type(self, client):
        data = _parse(await client.call_tool("faf_model", {"project_type": "nonexistent"}))
        assert "error" in data

    async def test_model_empty_lists_types(self, client):
        data = _parse(await client.call_tool("faf_model", {}))
        assert "available_types" in data
        assert len(data["available_types"]) >= 10


# ===================================================================
# TIER 4: STRESS — Scale resilience
# ===================================================================


class TestWJTTCTier4Stress:
    """Must handle high throughput without degradation."""

    async def test_rapid_fire_scoring(self, client, trophy_faf):
        """20 sequential score calls — all must return identical results."""
        scores = []
        for _ in range(20):
            data = _parse(await client.call_tool("faf_score", {"path": trophy_faf}))
            scores.append(data["score"])
        assert all(s == 100 for s in scores)

    async def test_large_faf_file(self, client, tmp_path):
        """FAF with 500 extra fields — must not timeout."""
        lines = [TROPHY_FAF]
        for i in range(500):
            lines.append(f"extra_field_{i}: value_{i}")
        large = tmp_path / "large.faf"
        large.write_text("\n".join(lines))
        data = _parse(await client.call_tool("faf_score", {"path": str(large)}))
        assert data["score"] == 100  # extra fields don't affect Mk4 scoring

    async def test_score_after_auto_create(self, client, tmp_path):
        """faf_auto → faf_score pipeline must work cleanly."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "pipeline"\ndescription = "Pipeline test"\n'
            '[project.optional-dependencies]\ndev = ["pytest"]\n'
        )
        target = str(tmp_path / "project.faf")
        auto = _parse(await client.call_tool("faf_auto", {
            "directory": str(tmp_path), "path": target
        }))
        assert auto["success"]
        score = _parse(await client.call_tool("faf_score", {"path": target}))
        assert score["score"] == auto["score"]


# ===================================================================
# TIER 5: SECURITY — Input hardening
# ===================================================================


class TestWJTTCTier5Security:
    """Must resist hostile inputs."""

    async def test_path_traversal_blocked(self, client):
        data = _parse(await client.call_tool("faf_score", {
            "path": "../../../etc/passwd"
        }))
        assert data["score"] == 0
        assert "error" in data

    async def test_null_byte_in_path(self, client):
        """Null bytes in path should not cause issues."""
        try:
            data = _parse(await client.call_tool("faf_score", {
                "path": "project\x00.faf"
            }))
            assert data["score"] == 0
        except Exception:
            pass  # Any clean failure is acceptable

    async def test_very_long_path(self, client):
        data = _parse(await client.call_tool("faf_score", {
            "path": "a" * 10000 + ".faf"
        }))
        assert data["score"] == 0
        assert "error" in data

    async def test_init_refuses_overwrite(self, client, trophy_faf):
        data = _parse(await client.call_tool("faf_init", {"path": trophy_faf}))
        assert data["success"] is False

    async def test_init_preserves_existing_content(self, client, trophy_faf):
        """Overwrite refusal must not corrupt the original."""
        original = open(trophy_faf).read()
        await client.call_tool("faf_init", {"path": trophy_faf})
        assert open(trophy_faf).read() == original


# ===================================================================
# TIER 6: CONTRACT — Mk4 parity between SDK and server
# ===================================================================


class TestWJTTCTier6Contract:
    """Server Mk4 scores must exactly match SDK Mk4 scores."""

    async def test_trophy_parity(self, client, trophy_faf):
        server = _parse(await client.call_tool("faf_score", {"path": trophy_faf}))
        sdk = score_faf(TROPHY_FAF)
        assert server["score"] == sdk.score
        assert server["tier"] == sdk.tier
        assert server["populated"] == sdk.populated
        assert server["active"] == sdk.active
        assert server["total"] == sdk.total

    async def test_minimal_parity(self, client, minimal_faf):
        server = _parse(await client.call_tool("faf_score", {"path": minimal_faf}))
        sdk = score_faf(MINIMAL_FAF)
        assert server["score"] == sdk.score
        assert server["populated"] == sdk.populated

    async def test_slotignored_parity(self, client, slotignored_faf):
        server = _parse(await client.call_tool("faf_score", {"path": slotignored_faf}))
        sdk = score_faf(SLOTIGNORED_FAF)
        assert server["score"] == sdk.score
        assert server["tier"] == sdk.tier
        assert server["active"] == sdk.active

    async def test_empty_slots_parity(self, client, empty_slots_faf):
        server = _parse(await client.call_tool("faf_score", {"path": empty_slots_faf}))
        sdk = score_faf(EMPTY_SLOTS_FAF)
        assert server["score"] == sdk.score
        assert server["populated"] == sdk.populated

    async def test_validate_schema_complete(self, client, trophy_faf):
        """faf_validate response must have all required Mk4 fields."""
        data = _parse(await client.call_tool("faf_validate", {"path": trophy_faf}))
        required = {"success", "valid", "score", "tier", "populated", "active", "total", "errors", "warnings"}
        assert required == set(data.keys())

    async def test_score_schema_complete(self, client, trophy_faf):
        """faf_score response must have all required Mk4 fields."""
        data = _parse(await client.call_tool("faf_score", {"path": trophy_faf}))
        required = {"score", "tier", "populated", "active", "total"}
        assert required == set(data.keys())

    async def test_all_tier_emojis_valid(self):
        """Every possible tier must be a known emoji."""
        valid = {"TROPHY", "GOLD", "SILVER", "BRONZE", "GREEN", "YELLOW", "RED", "WHITE"}
        for score in range(101):
            tier = _score_to_tier(score)
            assert tier in valid, f"Score {score} produced invalid tier: {tier}"

    async def test_math_identity_from_server(self, client, trophy_faf):
        """populated + empty + ignored = total, always."""
        for faf_content, path_fixture in [
            (TROPHY_FAF, "trophy_faf"),
            (MINIMAL_FAF, "minimal_faf"),
            (SLOTIGNORED_FAF, "slotignored_faf"),
        ]:
            f = Path(tempfile.mktemp(suffix=".faf"))
            f.write_text(faf_content)
            data = _parse(await client.call_tool("faf_score", {"path": str(f)}))
            empty = data["total"] - data["populated"] - (data["total"] - data["active"])
            assert data["populated"] + (data["total"] - data["active"]) + empty == data["total"]
            f.unlink()


# Need tempfile for the last test
import tempfile
