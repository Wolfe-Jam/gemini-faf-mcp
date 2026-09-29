"""The hosted function (main.py, Cloud Function faf-source-of-truth) scores
with the always-33 kernel via faf-python-sdk — the same number as every FAF
app — and never trusts a score written inside the file."""
from pathlib import Path

import yaml
from faf_sdk import score_faf

import main

ROOT = Path(__file__).resolve().parent.parent

BASE21 = {
    "project": {"name": "p", "goal": "g", "main_language": "Python"},
    "human_context": {k: "x" for k in ("who", "what", "why", "where", "when", "how")},
    "stack": {k: "x" for k in ("frontend", "css_framework", "ui_library", "state_management",
                               "backend", "api_type", "runtime", "database", "connection",
                               "hosting", "build", "cicd")},
}
MARKERS = {
    "stack": {k: "slotignored" for k in ("monorepo_tool", "package_manager", "workspaces",
                                         "admin", "cache", "search", "storage")},
    "monorepo": {k: "slotignored" for k in ("packages_count", "build_orchestrator",
                                            "versioning_strategy", "shared_configs", "remote_cache")},
}


def test_21_filled_without_markers_is_64_and_with_markers_is_100():
    assert main.calculate_score(BASE21) == 64
    marked = {**BASE21, "stack": {**BASE21["stack"], **MARKERS["stack"]}, "monorepo": MARKERS["monorepo"]}
    assert main.calculate_score(marked) == 100


def test_a_score_written_in_the_file_is_not_trusted():
    claims = {"project": {"name": "p"}, "scores": {"faf_score": 100}}
    assert main.calculate_score(claims) == score_faf(yaml.safe_dump(claims)).score
    assert main.calculate_score(claims) < 100


def test_matches_the_sdk_on_this_repo_project_faf():
    text = (ROOT / "project.faf").read_text()
    assert main.calculate_score(yaml.safe_load(text)) == score_faf(text).score == 100


def test_not_a_mapping_scores_zero():
    assert main.calculate_score(None) == 0
    assert main.calculate_score(["a"]) == 0
