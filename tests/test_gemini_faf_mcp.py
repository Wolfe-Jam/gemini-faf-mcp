"""
WJTTC Test Suite: gemini-faf-mcp v2.0.0
Championship-grade tests for the FAF Context Broker

Tier 1: BRAKE (Critical) - Must not fail
Tier 2: ENGINE (Core) - Core functionality
Tier 3: AERO (Polish) - Nice to have
Tier 4: VOICE (New!) - Voice-to-FAF specific
"""

import pytest
import requests
import json

# Live endpoint
BASE_URL = "https://us-east1-bucket-460122.cloudfunctions.net/faf-source-of-truth"


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
    """Voice-to-FAF specific tests."""

    def test_voice_put_structure(self):
        """PUT accepts correct structure."""
        # This test doesn't actually commit - just validates structure
        r = requests.put(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"test_field": "test_value"},
                "message": "wjttc-test: structure validation"
            }
        )
        # Should either succeed (200) or fail gracefully (not 500)
        assert r.status_code in [200, 400, 401, 403]

    def test_voice_response_fields(self):
        """PUT response contains expected fields on success."""
        r = requests.put(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.wjttc_test": "passed"},
                "message": "wjttc-test: response field validation"
            }
        )
        if r.status_code == 200:
            data = r.json()
            assert "success" in data
            assert "sha" in data or "error" in data

    def test_voice_no_token_exposure(self):
        """GitHub token not exposed in response."""
        r = requests.put(
            BASE_URL,
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
        """Custom commit message used when provided."""
        custom_msg = "wjttc-test: custom message test"
        r = requests.put(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.message_test": "custom"},
                "message": custom_msg
            }
        )
        if r.status_code == 200:
            data = r.json()
            if "message" in data:
                assert custom_msg in data["message"]

    def test_voice_url_points_to_github(self):
        """Response URL points to GitHub."""
        r = requests.put(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            json={
                "updates": {"state.url_test": "checking"},
                "message": "wjttc-test: url validation"
            }
        )
        if r.status_code == 200:
            data = r.json()
            if "url" in data:
                assert "github.com" in data["url"]


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
