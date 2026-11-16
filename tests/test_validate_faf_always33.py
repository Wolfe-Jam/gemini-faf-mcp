"""validate_faf gives the always-33 number (faf-python-sdk score_faf), the same as faf-cli and faf_score.

It used to count its own 10 slots "against v2.5.2", a second scorer with a different number.
"""

import yaml
from faf_sdk import score_faf

from gemini_faf_mcp import validate_faf

SAMPLE = {
    "faf_version": "3.0",
    "project": {"name": "weather-api", "goal": "Weather by city", "main_language": "Python"},
    "stack": {"backend": "FastAPI", "api_type": "REST", "testing": "pytest", "frontend": "slotignored"},
    "human_context": {"who": "Developers building travel apps"},
}


def test_same_number_as_the_kernel():
    kernel = score_faf(yaml.safe_dump(SAMPLE, sort_keys=False))
    r = validate_faf(SAMPLE)
    assert r["score"] == kernel.score
    assert (r["populated"], r["active"], r["total"]) == (kernel.populated, kernel.active, 33)
    assert r["tier"] == kernel.tier.title()


def test_counts_33_slots_not_10():
    r = validate_faf(SAMPLE)
    assert r["total"] == 33
    assert r["total_slots"] == r["active"]  # kept for existing callers: the score's denominator
    assert r["active"] != 10


def test_issues_still_list_the_missing_basics():
    r = validate_faf(SAMPLE)
    assert "Missing or placeholder: human_context.why" in r["issues"]
    assert r["valid"] is False


def test_bad_input_scores_zero_white():
    r = validate_faf({"project": "not-a-mapping"})
    assert r["score"] == 0 or r["tier"] in ("White", "Red")
    assert "Missing: project.name" in r["issues"]
