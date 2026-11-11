"""The server works in the user's project when a host starts it in its plugin folder.

Antigravity CLI (agy 1.5.5) starts a plugin's MCP server with cwd = the plugin's
install folder. Before this fix every write to the project was refused ("path
escapes FAF_ALLOWED_ROOTS") and `faf_discover` found the plugin's own project.faf.
`_start_in_workspace` moves to the inherited PWD, only when the cwd is our own
plugin folder. The last test runs the real server over stdio the way agy does.
"""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import _start_in_workspace  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FAF = 'faf_version: "3.3"\nproject:\n  name: probe\n  goal: test the workspace\n'


def _plugin(tmp_path, name="gemini-faf-mcp"):
    plugin = tmp_path / "plugins" / "gemini-faf-mcp"
    plugin.mkdir(parents=True)
    (plugin / "gemini-extension.json").write_text(json.dumps({"name": name, "version": "3.2.0"}))
    (plugin / "project.faf").write_text(FAF.replace("probe", "the-plugin-itself"))
    project = tmp_path / "work" / "my-project"
    project.mkdir(parents=True)
    return plugin, project


def test_moves_from_our_plugin_folder_to_pwd(tmp_path, monkeypatch):
    plugin, project = _plugin(tmp_path)
    monkeypatch.chdir(plugin)
    assert _start_in_workspace(env={"PWD": str(project)}) == str(project.resolve())
    assert Path.cwd() == project.resolve()


def test_moves_when_only_plugin_json_names_us(tmp_path, monkeypatch):
    plugin, project = _plugin(tmp_path)
    (plugin / "gemini-extension.json").unlink()
    (plugin / "plugin.json").write_text(json.dumps({"name": "gemini-faf-mcp"}))
    monkeypatch.chdir(plugin)
    assert _start_in_workspace(env={"PWD": str(project)}) == str(project.resolve())


@pytest.mark.parametrize(
    "case",
    ["no-manifest", "other-extension", "no-pwd", "relative-pwd", "missing-pwd", "pwd-is-cwd", "bad-json"],
)
def test_leaves_everything_else_alone(tmp_path, monkeypatch, case):
    plugin, project = _plugin(tmp_path, name="other-extension" if case == "other-extension" else "gemini-faf-mcp")
    if case == "no-manifest":
        (plugin / "gemini-extension.json").unlink()
    if case == "bad-json":
        (plugin / "gemini-extension.json").write_text("{not json")
    env = {
        "no-pwd": {},
        "relative-pwd": {"PWD": "work/my-project"},
        "missing-pwd": {"PWD": str(tmp_path / "nowhere")},
        "pwd-is-cwd": {"PWD": str(plugin)},
    }.get(case, {"PWD": str(project)})
    monkeypatch.chdir(plugin)
    assert _start_in_workspace(env=env) is None
    assert Path.cwd() == plugin.resolve()


async def test_server_started_in_plugin_folder_works_in_the_project(tmp_path):
    """Run the real server over stdio with cwd = a plugin folder and PWD = the project."""
    from fastmcp.client import Client
    from fastmcp.client.transports import StdioTransport

    plugin, project = _plugin(tmp_path)
    (project / "project.faf").write_text(FAF)
    env = dict(os.environ, PWD=str(project), PYTHONPATH=str(REPO / "src"))
    transport = StdioTransport(command=sys.executable, args=[str(REPO / "server.py")], env=env, cwd=str(plugin))
    async with Client(transport) as c:
        found = (await c.call_tool_mcp("faf_discover", {})).structured_content
        assert found["found"] is True
        assert Path(found["path"]).resolve() == (project / "project.faf").resolve()
        wrote = await c.call_tool_mcp("faf_agents", {"path": "project.faf"})
        assert wrote.is_error is False, wrote.structured_content
    assert (project / "AGENTS.md").is_file()
    assert not (plugin / "AGENTS.md").exists()
