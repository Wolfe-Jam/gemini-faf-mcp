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


async def test_init_then_auto_fills_the_stack(client, tmp_path):
    """faf_init leaves the stack empty (not slotignored), so faf_auto can fill it."""
    (tmp_path / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    faf = tmp_path / "project.faf"
    await client.call_tool("faf_init", {"name": "weather-api", "goal": "Weather", "path": str(faf)})

    d = _data(await client.call_tool("faf_auto", {"directory": str(tmp_path), "path": str(faf)}))

    content = faf.read_text()
    assert "main_language: Python" in content  # init left it empty; auto filled it
    assert 'backend: "FastAPI"' in content
    assert 'testing: "pytest"' in content
    assert "backend" in d["written"] and "testing" in d["written"]
    assert d["message"].startswith("Detected Python/FastAPI Updated project.faf at")


async def test_auto_says_what_it_did_not_write(client, tmp_path):
    """A slot the user set to slotignored stays as it is, and the result says so."""
    (tmp_path / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    faf = tmp_path / "project.faf"
    faf.write_text('faf_version: "3.0"\nproject:\n  name: weather-api\n  main_language: Python\nstack:\n  backend: slotignored\n  testing: slotignored\n')
    before = faf.read_text()

    d = _data(await client.call_tool("faf_auto", {"directory": str(tmp_path), "path": str(faf)}))

    assert faf.read_text() == before
    assert d["written"] == []
    assert d["not_written"]["backend"] == {"detected": "FastAPI", "current": "slotignored"}
    assert "unchanged" in d["message"] and "Updated" not in d["message"]
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
    assert d["suggested"] == {"goal": "A small weather API"}
    content = faf.read_text()
    assert 'backend: "FastAPI"' in content
    assert 'testing: "pytest"' in content
    assert d["score"] > 21  # the init-then-auto path scored 21 on this project


def test_setup_creates_with_faf_auto_not_faf_init():
    prompt = (REPO / "commands" / "faf" / "setup.toml").read_text()
    assert "run `faf_auto` with `directory` set to `.` and `path` set to `project.faf`" in prompt
    assert "faf_init" not in prompt


async def test_human_slots_are_never_invented(client, tmp_path):
    """Human Slots (faf-cli 8.10 parity): no placeholder or default in the goal or six W's."""
    (tmp_path / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    init_faf = tmp_path / "init.faf"
    auto_dir = tmp_path / "auto"
    auto_dir.mkdir()
    (auto_dir / "pyproject.toml").write_text(FASTAPI_PYPROJECT)
    await client.call_tool("faf_init", {"name": "weather-api", "path": str(init_faf)})
    d = _data(await client.call_tool("faf_auto", {"directory": str(auto_dir), "path": "project.faf"}))
    for content in (init_faf.read_text(), (auto_dir / "project.faf").read_text()):
        for junk in ("Why does this project exist?", "What problem does this solve?", "Describe your project goal", "who: Developers"):
            assert junk not in content
        for w in ("who", "what", "why", "where", "when", "how"):
            assert f'  {w}: ""' in content
    # the description from pyproject.toml is offered, not written
    assert "A small weather API" not in (auto_dir / "project.faf").read_text()
    assert d["suggested"]["goal"] == "A small weather API"
    assert "Suggested goal (confirm before adding): A small weather API" in d["message"]


async def test_init_keeps_a_goal_the_user_gave(client, tmp_path):
    faf = tmp_path / "project.faf"
    await client.call_tool("faf_init", {"name": "w", "goal": "Weather: by city", "path": str(faf)})
    assert '  goal: "Weather: by city"' in faf.read_text()  # quoted: a colon can't break the YAML
