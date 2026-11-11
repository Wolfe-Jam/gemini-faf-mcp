"""The server works in the user's project when Antigravity starts it in its plugin folder.

Antigravity CLI (agy 1.5.5) starts a plugin's MCP server with cwd = the plugin's
install folder and sets PLUGIN_ROOT to that folder. Before this fix every write to
the project was refused ("path escapes FAF_ALLOWED_ROOTS") and `faf_discover` found
the plugin's own project.faf. `_start_in_workspace` moves to the inherited PWD,
only when PLUGIN_ROOT is the cwd, and never to a folder broad enough to widen the
write boundary. The last test runs the real server over stdio the way agy does.
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import _start_in_workspace  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FAF = 'faf_version: "3.3"\nproject:\n  name: probe\n  goal: test the workspace\n'


def _layout(tmp_path):
    home = tmp_path / "home"
    plugin = home / ".gemini" / "config" / "plugins" / "gemini-faf-mcp"
    plugin.mkdir(parents=True)
    (plugin / "project.faf").write_text(FAF.replace("probe", "the-plugin-itself"))
    project = home / "work" / "my-project"
    project.mkdir(parents=True)
    return home, plugin, project


def _env(home, plugin, pwd):
    return {"HOME": str(home), "PLUGIN_ROOT": str(plugin), "PWD": str(pwd)}


def test_moves_from_the_plugin_folder_to_pwd(tmp_path, monkeypatch):
    home, plugin, project = _layout(tmp_path)
    monkeypatch.chdir(plugin)
    assert _start_in_workspace(env=_env(home, plugin, project)) == str(project.resolve())
    assert Path.cwd() == project.resolve()


def test_follows_a_symlinked_pwd_to_the_real_folder(tmp_path, monkeypatch):
    home, plugin, project = _layout(tmp_path)
    link = home / "link-to-project"
    link.symlink_to(project)
    monkeypatch.chdir(plugin)
    assert _start_in_workspace(env=_env(home, plugin, link)) == str(project.resolve())


@pytest.mark.parametrize(
    "case",
    [
        "no-plugin-root",  # Claude Code, Gemini CLI, uvx, a dev checkout
        "plugin-root-elsewhere",
        "no-pwd",
        "relative-pwd",
        "missing-pwd",
        "pwd-is-a-file",
        "pwd-is-cwd",
        "pwd-is-root",  # F1: would widen the write boundary to the whole disk
        "pwd-is-home",  # F1: the whole home folder
        "pwd-contains-plugin",  # ~/.gemini holds the plugin folder
        "pwd-inside-plugin",
    ],
)
def test_stays_put(tmp_path, monkeypatch, case):
    home, plugin, project = _layout(tmp_path)
    (plugin / "sub").mkdir()
    (home / "a-file").write_text("x")
    env = _env(home, plugin, project)
    if case == "no-plugin-root":
        del env["PLUGIN_ROOT"]
    elif case == "plugin-root-elsewhere":
        env["PLUGIN_ROOT"] = str(project)
    elif case == "no-pwd":
        del env["PWD"]
    else:
        env["PWD"] = {
            "relative-pwd": "work/my-project",
            "missing-pwd": str(home / "nowhere"),
            "pwd-is-a-file": str(home / "a-file"),
            "pwd-is-cwd": str(plugin),
            "pwd-is-root": "/",
            "pwd-is-home": str(home),
            "pwd-contains-plugin": str(home / ".gemini"),
            "pwd-inside-plugin": str(plugin / "sub"),
        }[case]
    monkeypatch.chdir(plugin)
    assert _start_in_workspace(env=env) is None
    assert Path.cwd() == plugin.resolve()


async def test_server_started_in_plugin_folder_works_in_the_project(tmp_path):
    """The real server over stdio, as agy starts it: cwd = plugin, PLUGIN_ROOT, PWD = project.

    The child gets a minimal environment (no PORT / MCP_TRANSPORT / FAF_ALLOWED_ROOTS
    from the caller) and its own TMPDIR, so the system temp folder that holds
    tmp_path is not a write root: on the old code the write is refused.
    """
    from fastmcp.client import Client
    from fastmcp.client.transports import StdioTransport

    home, plugin, project = _layout(tmp_path)
    (project / "project.faf").write_text(FAF)
    server_tmp = tmp_path / "server-tmp"
    server_tmp.mkdir()
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(home),
        "PYTHONPATH": str(REPO / "src"),
        "TMPDIR": str(server_tmp),
        "PLUGIN_ROOT": str(plugin),
        "PWD": str(project),
    }
    transport = StdioTransport(command=sys.executable, args=[str(REPO / "server.py")], env=env, cwd=str(plugin))
    async with Client(transport) as c:
        found = (await c.call_tool_mcp("faf_discover", {})).structured_content
        assert found["found"] is True
        assert Path(found["path"]).resolve() == (project / "project.faf").resolve()
        wrote = await c.call_tool_mcp("faf_agents", {"path": str(project / "project.faf")})
        assert wrote.is_error is False, wrote.structured_content
    assert (project / "AGENTS.md").is_file()
    assert not (plugin / "AGENTS.md").exists()
