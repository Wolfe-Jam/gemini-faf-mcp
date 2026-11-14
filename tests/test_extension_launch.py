"""The extension starts the server with Python directly, in isolated mode.

`uvx gemini-faf-mcp` runs uv's console script, a `#!/bin/sh` launcher in uv's
cached environments. A POSIX shell resets PWD to the real cwd when it starts, so
under Antigravity (which starts a plugin's server in the plugin folder) the
server saw PWD = the plugin folder and `_start_in_workspace` could not find the
project: 3.2.1's fix did nothing on the default launch, and relative writes
landed in the plugin folder. Launching `python` directly keeps PWD.

`-I` (isolated) keeps the current folder off sys.path: plain `python -m server`
would run a project's own server.py instead of ours (checked: it did).
`-I` also ignores PYTHONUTF8, so `-X utf8` turns UTF-8 mode on explicitly
(file reads and writes on Windows would otherwise use the legacy code page).
`>=3.2.1`: an older `uv tool install` copy would otherwise win, and versions
before 3.2.1 have no `_start_in_workspace`.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARGS = json.loads((REPO / "gemini-extension.json").read_text())["mcpServers"]["faf"]["args"]


def test_extension_launches_python_directly_and_isolated():
    faf = json.loads((REPO / "gemini-extension.json").read_text())["mcpServers"]["faf"]
    assert faf["command"] == "uvx"
    assert ARGS == ["--from", "gemini-faf-mcp>=3.2.1", "python", "-I", "-X", "utf8", "-m", "server"]


def test_launch_ignores_a_server_py_in_the_project(tmp_path):
    """Run the manifest's python arguments from a folder holding a decoy server.py.

    The decoy exits 7. Our server must answer `--version` instead, in UTF-8 mode.
    """
    (tmp_path / "server.py").write_text("import sys\nprint('DECOY')\nsys.exit(7)\n")
    python_args = ARGS[ARGS.index("python") + 1 :]
    out = subprocess.run(
        [sys.executable, *python_args, "--version"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    assert "DECOY" not in out.stdout
    assert out.stdout.startswith("gemini-faf-mcp ")
    flags = subprocess.run(
        [sys.executable, *python_args[: python_args.index("-m")], "-c",
         "import sys; print(sys.flags.isolated, sys.flags.utf8_mode)"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert flags.stdout.split() == ["1", "1"]
