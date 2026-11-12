"""The extension starts the server with Python directly, in isolated mode.

`uvx gemini-faf-mcp` runs uv's console script, a `#!/bin/sh` launcher in uv's
cached environments. A POSIX shell resets PWD to the real cwd when it starts, so
under Antigravity (which starts a plugin's server in the plugin folder) the
server saw PWD = the plugin folder and `_start_in_workspace` could not find the
project: 3.2.1's fix did nothing on the default launch, and relative writes
landed in the plugin folder. Launching `python` directly keeps PWD.

`-I` (isolated) keeps the current folder off sys.path: plain `python -m server`
would run a project's own server.py instead of ours (checked: it did).
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_extension_launches_python_directly_and_isolated():
    faf = json.loads((REPO / "gemini-extension.json").read_text())["mcpServers"]["faf"]
    assert faf["command"] == "uvx"
    assert faf["args"] == ["--from", "gemini-faf-mcp", "python", "-I", "-m", "server"]


def test_server_module_runs_main_when_executed():
    # `python -m server` must start the server: the module ends in a __main__ guard.
    src = (REPO / "server.py").read_text()
    assert 'if __name__ == "__main__":\n    main()' in src
