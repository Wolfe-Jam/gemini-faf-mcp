"""/setup creates project.faf with faf_auto, and faf_auto says what it really wrote.

Found while capturing examples for the docs (2026-11-16): the documented first run was
/setup (faf_init) then "fill it in from your repo" (faf_auto). faf_init marks every stack
slot slotignored, and faf_auto fills empty slots only, so on a FastAPI project it reported
"Detected Python/FastAPI. Updated project.faf at 21%." while writing nothing. faf_auto on
its own, on the same project, writes FastAPI, REST, pip and pytest and scores 75%.
"""

import json
from pathlib import Path

import pytest
from fastmcp.client import Client

from server import mcp

REPO = Path(__file__).resolve().parent.parent

FASTAPI_PYPROJECT = (
    '[project]\nname = "weather-api"\nversion = "0.1.0"\n'
    'description = "A small weather API"\n'
    'dependencies = ["fastapi>=0.115", "uvicorn>=0.30"]\n'
    '[project.optional-dependencies]\ndev = ["pytest>=8"]\n'
)


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


def _data(result):
    if isinstance(getattr(result, "data", None), dict):
        return result.data
    return json.loads(result.content[0].text)


async def test_init_then_auto_says_what_it_did_not_write(client, tmp_path):
    (tmp_path / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    faf = tmp_path / "project.faf"
    await client.call_tool("faf_init", {"name": "weather-api", "goal": "Weather", "language": "Python", "path": str(faf)})
    before = faf.read_text()

    d = _data(await client.call_tool("faf_auto", {"directory": str(tmp_path), "path": str(faf)}))

    assert faf.read_text() == before
    assert d["written"] == []
    assert d["not_written"]["backend"] == {"detected": "FastAPI", "current": "slotignored"}
    assert "unchanged" in d["message"]
    assert "Updated" not in d["message"]
    assert "backend is slotignored, detected FastAPI" in d["message"]


async def test_auto_lists_the_slots_it_fills(client, tmp_path):
    (tmp_path / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    faf = tmp_path / "project.faf"
    faf.write_text('faf_version: "3.0"\nproject:\n  name: weather-api\n  goal: null\n  main_language: null\n')

    d = _data(await client.call_tool("faf_auto", {"directory": str(tmp_path), "path": str(faf)}))

    assert "main_language" in d["written"]
    assert "main_language: Python" in faf.read_text()
    assert d["message"].startswith("Detected Python/FastAPI Updated project.faf at")
    assert "wrote main_language" in d["message"]


async def test_auto_alone_creates_the_stack(client, tmp_path):
    (tmp_path / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    faf = tmp_path / "project.faf"

    d = _data(await client.call_tool("faf_auto", {"directory": str(tmp_path), "path": str(faf)}))

    assert d["created"] is True
    assert d["written"] == [] and d["not_written"] == {}
    content = faf.read_text()
    assert 'backend: "FastAPI"' in content
    assert 'testing: "pytest"' in content
    assert d["score"] > 21  # the init-then-auto path scored 21 on this project


def test_setup_creates_with_faf_auto_not_faf_init():
    prompt = (REPO / "commands" / "faf" / "setup.toml").read_text()
    assert "run `faf_auto` with `directory` set to `.` and `path` set to `project.faf`" in prompt
    assert "faf_init" not in prompt
