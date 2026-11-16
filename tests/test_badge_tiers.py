"""The hosted badge uses faf-cli's tier ladder (src/core/tiers.ts), not the retired emoji ladder."""

import sys
from pathlib import Path

# main.py (the hosted Cloud Function) isn't a packaged module: import it from the repo root,
# whatever order pytest collects the test files in.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main  # noqa: E402

RETIRED = ["🏆", "🥇", "🥈", "🥉", "🟢", "🟡", "🔴", "🤍"]


def test_badge_tiers_match_faf_cli():
    cases = {100: "✪", 99: "★", 95: "◆", 85: "◇", 70: "●", 55: "●", 54: "○", 1: "○", 0: "♡"}
    for score, symbol in cases.items():
        assert main.badge_tier(score)[0] == symbol, score


def test_badge_never_uses_the_retired_emoji():
    for score in (0, 1, 54, 55, 70, 85, 95, 99, 100):
        svg = main.generate_badge(score, False)
        assert not any(e in svg for e in RETIRED), score


def test_orange_is_a_declared_flag_not_a_score():
    assert "🍊" not in main.generate_badge(100, False)
    assert "🍊" in main.generate_badge(42, True)
