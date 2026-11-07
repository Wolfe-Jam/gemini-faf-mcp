"""A tool that answers ``success: false`` sets MCP's ``isError``.

Before 3.1.3 every gemini-faf-mcp failure (a missing file, a refused write, a
path outside the project) came back as an ordinary result whose dict said
``success: false``; a client that reads ``isError`` saw success. The
``_FailureIsError`` middleware sets the flag and leaves the dict as it was.
Each case goes through a real MCP client against the server in memory.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp.client import Client  # noqa: E402

from server import faf_read, mcp  # noqa: E402

FAF = 'faf_version: "3.3"\nproject:\n  name: probe\n  goal: test isError\n'


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "project.faf").write_text(FAF)
    return tmp_path


async def _call(tool, args):
    async with Client(transport=mcp) as c:
        return await c.call_tool_mcp(tool, args)


async def test_a_result_is_not_an_error(project):
    r = await _call("faf_score", {"path": str(project / "project.faf")})
    assert r.isError is False


async def test_missing_file_is_an_error_with_the_same_dict(project):
    path = str(project / "missing.faf")
    r = await _call("faf_read", {"path": path})
    assert r.isError is True
    expected = faf_read(path)  # the function itself still returns the dict
    assert expected["success"] is False
    assert r.structured_content == expected
    assert json.loads(r.content[0].text) == expected


async def test_refused_write_is_an_error(project):
    bad = b"# Caf\xe9\n"
    (project / "GEMINI.md").write_bytes(bad)
    r = await _call("faf_gemini", {"path": str(project / "project.faf")})
    assert r.isError is True
    assert r.structured_content["success"] is False
    assert "not UTF-8" in r.structured_content["error"]
    assert (project / "GEMINI.md").read_bytes() == bad


async def test_path_outside_the_project_is_an_error(project):
    r = await _call("faf_read", {"path": "/etc/hosts"})
    assert r.isError is True
    assert r.structured_content["success"] is False
