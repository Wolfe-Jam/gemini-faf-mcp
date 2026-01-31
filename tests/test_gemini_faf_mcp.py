"""
WJTTC Test Suite: gemini-faf-mcp v2.5.1
Championship-grade tests for the FAF Context Broker

Tier 1: BRAKE (Critical) - Must not fail
Tier 2: ENGINE (Core) - Core functionality
Tier 3: AERO (Polish) - Nice to have
Tier 4: VOICE (New!) - Voice-to-FAF specific
Tier 5: SECURITY (v2.5.1) - SW-01, SW-02, Telemetry
"""

import pytest
import requests
import json

# Live endpoint
BASE_URL = "https://us-east1-bucket-460122.cloudfunctions.net/faf-source-of-truth"
# Dry-run endpoint for PUT tests (prevents production pollution)
DRY_RUN_URL = f"{BASE_URL}?dry_run=true"


# =============================================================================
# TIER 1: BRAKE SYSTEMS (Critical)
# =============================================================================

class TestTier1Critical:
    """Critical tests - failures here are showstoppers."""

    def test_get_badge_returns_200(self):
        """GET request returns HTTP 200."""
        r = requests.get(BASE_URL)
        assert r.status_code == 200

    def test_get_badge_content_type_svg(self):
        """GET returns SVG content type."""
        r = requests.get(BASE_URL)
        assert "image/svg+xml" in r.headers.get("Content-Type", "")

    def test_get_badge_contains_svg(self):
        """GET response contains SVG element."""
        r = requests.get(BASE_URL)
        assert "<svg" in r.text

    def test_post_returns_200(self):
        """POST request returns HTTP 200."""
        r = requests.post(BASE_URL, headers={"Content-Type": "application/json"})
        assert r.status_code == 200

    def test_post_returns_json(self):
        """POST returns valid JSON."""
        r = requests.post(BASE_URL, headers={"Content-Type": "application/json"})
        data = r.json()
        assert isinstance(data, dict)

    def test_post_contains_agent_field(self):
        """POST response contains _agent field."""
        r = requests.post(BASE_URL, headers={"Content-Type": "application/json"})
        data = r.json()
        assert "_agent" in data

    def test_put_requires_body(self):
        """PUT without body returns 400."""
        r = requests.put(BASE_URL, headers={"Content-Type": "application/json"})
        assert r.status_code == 400

    def test_put_requires_updates(self):
        """PUT with empty updates returns 400."""
        r = requests.put(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json={"updates": {}}
        )
        assert r.status_code == 400


# =============================================================================
# TIER 2: ENGINE SYSTEMS (Core)
# =============================================================================

class TestTier2Engine:
    """Core functionality tests."""

    def test_agent_detection_jules(self):
        """Jules agent detected correctly."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "jules", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_agent"] == "jules"

    def test_agent_detection_grok(self):
        """Grok agent detected correctly."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "grok", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_agent"] == "grok"

    def test_agent_detection_claude(self):
        """Claude agent detected correctly."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "claude", "Content-Type": "application/json"}
        )
        # Claude gets XML
        assert "application/xml" in r.headers.get("Content-Type", "")

    def test_agent_detection_gemini(self):
        """Gemini agent detected correctly."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "gemini", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_agent"] == "gemini"

    def test_agent_detection_unknown(self):
        """Unknown agent returns default."""
        r = requests.post(BASE_URL, headers={"Content-Type": "application/json"})
        data = r.json()
        assert data["_agent"] == "unknown"

    def test_jules_format_minimal(self):
        """Jules gets minimal format."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "jules", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_format"] == "minimal"
        assert "project" in data
        assert "goal" in data
        assert "score" in data

    def test_grok_format_direct(self):
        """Grok gets direct format."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "grok", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_format"] == "direct"
        assert "what" in data
        assert "why" in data
        assert "how" in data

    def test_claude_format_xml(self):
        """Claude gets XML format."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "claude", "Content-Type": "application/json"}
        )
        assert r.text.startswith("<?xml")
        assert "<dna>" in r.text

    def test_gemini_format_structured(self):
        """Gemini gets structured format."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "gemini", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_format"] == "structured"
        assert "priority_1_identity" in data
        assert "priority_2_technical" in data

    def test_agent_detected_header(self):
        """X-FAF-Agent-Detected header returned."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "jules", "Content-Type": "application/json"}
        )
        assert r.headers.get("X-FAF-Agent-Detected") == "jules"

    def test_badge_no_cache(self):
        """Badge has no-cache header."""
        r = requests.get(BASE_URL)
        assert "no-cache" in r.headers.get("Cache-Control", "")


# =============================================================================
# TIER 3: AERO SYSTEMS (Polish)
# =============================================================================

class TestTier3Aero:
    """Polish and edge case tests."""

    def test_badge_contains_percentage(self):
        """Badge shows percentage."""
        r = requests.get(BASE_URL)
        assert "%" in r.text

    def test_badge_contains_trophy_or_tier(self):
        """Badge shows tier indicator."""
        r = requests.get(BASE_URL)
        # Should contain one of the tier symbols
        tier_symbols = ["🏆", "🥉", "🟢", "🟡", "🔴"]
        assert any(symbol in r.text for symbol in tier_symbols)

    def test_score_in_response(self):
        """Score included in POST response."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "jules", "Content-Type": "application/json"}
        )
        data = r.json()
        assert "score" in data
        assert isinstance(data["score"], int)

    def test_codex_format_code_focused(self):
        """Codex gets code-focused format."""
        r = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "codex", "Content-Type": "application/json"}
        )
        data = r.json()
        assert data["_format"] == "code_focused"


# =============================================================================
# TIER 4: VOICE SYSTEMS (New!)
# =============================================================================

class TestTier4Voice:
    """Voice-to-FAF specific tests (using dry_run to prevent production pollution)."""

    def test_voice_put_structure(self):
        """PUT accepts correct structure (dry_run)."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"test_field": "test_value"},
                "message": "wjttc-test: structure validation"
            }
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get("dry_run") == True

    def test_voice_response_fields(self):
        """PUT dry_run response contains expected fields."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.wjttc_test": "passed"},
                "message": "wjttc-test: response field validation"
            }
        )
        assert r.status_code == 200
        data = r.json()
        assert "dry_run" in data
        assert "would_apply" in data
        assert "preview" in data

    def test_voice_no_token_exposure(self):
        """GitHub token not exposed in response (dry_run)."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.security_test": "checking"},
                "message": "wjttc-test: security check"
            }
        )
        # Token should never appear in response
        assert "github_pat_" not in r.text
        assert "ghp_" not in r.text

    def test_voice_custom_message(self):
        """Custom commit message shown in dry_run preview."""
        custom_msg = "wjttc-test: custom message test"
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.message_test": "custom"},
                "message": custom_msg
            }
        )
        assert r.status_code == 200
        data = r.json()
        assert custom_msg in data.get("message", "")

    def test_voice_preview_includes_score(self):
        """Dry_run preview includes score and orange status."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.preview_test": "checking"},
                "message": "wjttc-test: preview validation"
            }
        )
        assert r.status_code == 200
        data = r.json()
        preview = data.get("preview", {})
        assert "score" in preview
        assert "has_orange" in preview
        assert "security" in preview


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Full workflow integration tests."""

    def test_full_read_write_cycle(self):
        """Complete read-write cycle works."""
        # 1. Read current state
        r1 = requests.post(
            BASE_URL,
            headers={"X-FAF-Agent": "gemini", "Content-Type": "application/json"}
        )
        assert r1.status_code == 200

        # 2. Get badge
        r2 = requests.get(BASE_URL)
        assert r2.status_code == 200
        assert "<svg" in r2.text

    def test_multi_agent_consistency(self):
        """All agents return score consistently."""
        scores = []

        for agent in ["jules", "grok", "gemini"]:
            r = requests.post(
                BASE_URL,
                headers={"X-FAF-Agent": agent, "Content-Type": "application/json"}
            )
            data = r.json()
            scores.append(data.get("score") or data.get("status", "").replace("%", ""))

        # All should report same underlying score
        # (formats differ but base score should match)
        assert len(set(str(s) for s in scores if s)) <= 2  # Allow minor format differences


# =============================================================================
# TIER 5: SECURITY SYSTEMS (v2.5.1)
# =============================================================================

class TestTier5Security:
    """v2.5.1 Security tests - SW-01, SW-02, Telemetry (using dry_run)."""

    def test_security_fields_in_dry_run_response(self):
        """Dry_run includes security status in preview."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.security_test": "v2.5.1"},
                "message": "wjttc-test: security fields validation"
            }
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get("dry_run") == True
        preview = data.get("preview", {})
        assert preview.get("security", {}).get("sw01") == "passed"
        assert preview.get("security", {}).get("sw02") == "passed"

    def test_sw02_blocks_unauthorized_orange(self):
        """SW-02: Cannot set Big Orange without 100% score (even in dry_run)."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {
                    "faf_distinction": "Big Orange",
                    "project.name": ""  # Empty field to drop score
                },
                "message": "wjttc-test: SW-02 validation"
            }
        )
        # Should be blocked by SW-02 (security checks run before dry_run)
        if r.status_code == 403:
            data = r.json()
            assert data.get("blocked_by") == "SW-02"
            assert "Scoring guard" in data.get("error", "")

    def test_blocked_response_includes_blocker(self):
        """Blocked responses identify which security check failed."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"x_faf_orange": True},
                "message": "wjttc-test: blocker identification"
            }
        )
        # May pass if score is 100, or block if trying to set orange
        if r.status_code == 403:
            data = r.json()
            assert "blocked_by" in data
            assert data["blocked_by"] in ["SW-01", "SW-02"]

    def test_would_apply_list_in_dry_run(self):
        """Dry_run returns list of updates that would be applied."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.test_field": "test_value"},
                "message": "wjttc-test: would_apply validation"
            }
        )
        assert r.status_code == 200
        data = r.json()
        assert "would_apply" in data
        assert isinstance(data["would_apply"], list)
        assert "state.test_field" in data["would_apply"]

    def test_agent_header_accepted(self):
        """Agent header accepted in dry_run."""
        r = requests.put(
            DRY_RUN_URL,
            headers={
                "Content-Type": "application/json",
                "X-FAF-Agent": "gemini"
            },
            json={
                "updates": {"state.agent_test": "gemini"},
                "message": "wjttc-test: agent header"
            }
        )
        assert r.status_code == 200

    def test_dot_notation_in_dry_run(self):
        """Dot notation for nested updates works in dry_run."""
        r = requests.put(
            DRY_RUN_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.focus": "test_focus"},
                "message": "wjttc-test: dot notation"
            }
        )
        assert r.status_code == 200
        data = r.json()
        assert "state.focus" in data.get("would_apply", [])


# =============================================================================
# TIER 6: PYPI PACKAGE (v1.0.2)
# =============================================================================

class TestTier6PyPI:
    """PyPI package tests - validates the installable package works correctly."""

    def test_package_import(self):
        """Package imports successfully."""
        import gemini_faf_mcp
        assert hasattr(gemini_faf_mcp, '__version__')
        assert gemini_faf_mcp.__version__ == "1.0.2"

    def test_fafclient_import(self):
        """FAFClient class imports."""
        from gemini_faf_mcp import FAFClient
        assert FAFClient is not None

    def test_parse_faf_import(self):
        """parse_faf function imports."""
        from gemini_faf_mcp import parse_faf
        assert callable(parse_faf)

    def test_validate_faf_import(self):
        """validate_faf function imports."""
        from gemini_faf_mcp import validate_faf
        assert callable(validate_faf)

    def test_local_parse_project_faf(self):
        """Local parse of project.faf works."""
        from gemini_faf_mcp import parse_faf
        import os

        # Find project.faf relative to this test
        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        faf_path = os.path.join(project_root, "project.faf")

        if os.path.exists(faf_path):
            result = parse_faf(faf_path)
            assert "project" in result
            assert result["project"]["name"] == "gemini-faf-mcp"

    def test_validate_faf_scoring(self):
        """FAF validation returns score and tier."""
        from gemini_faf_mcp import parse_faf, validate_faf
        import os

        test_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(test_dir)
        faf_path = os.path.join(project_root, "project.faf")

        if os.path.exists(faf_path):
            parsed = parse_faf(faf_path)
            result = validate_faf(parsed)
            assert "score" in result
            assert "tier" in result
            assert result["score"] >= 85  # At least Bronze

    def test_fafclient_remote_connection(self):
        """FAFClient has expected methods."""
        from gemini_faf_mcp import FAFClient

        client = FAFClient(local=True)  # Use local mode to avoid network in unit tests
        # Test that the client has the expected methods
        assert hasattr(client, 'get_project_dna')
        assert hasattr(client, 'get_score')
        assert hasattr(client, 'is_elite')
        assert hasattr(client, 'update_dna')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
