"""
WJTTC: --version / --help answer and exit; they never start the server.

Before 3.1.1, both flags were ignored: the server started, printed the FastMCP
banner on stderr and waited on stdin, with no version on stdout.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def _run(*args: str) -> subprocess.CompletedProcess:
    # stdin closed and a time limit: if a flag ever starts the server again,
    # the test fails instead of waiting for a client.
    return subprocess.run(
        [sys.executable, str(ROOT / "server.py"), *args],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.parametrize("flag", ["--version", "-V"])
def test_version_prints_name_and_version(flag):
    r = _run(flag)
    assert r.returncode == 0
    assert r.stdout.strip() == f"gemini-faf-mcp {server.__version__}"


@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_prints_usage_and_a_client_config(flag):
    r = _run(flag)
    assert r.returncode == 0
    assert "Usage:" in r.stdout
    assert "--version" in r.stdout
    assert '"command": "uvx"' in r.stdout


def test_other_arguments_still_serve():
    # Unknown arguments fall through to the server, so client configs that
    # pass extra args keep working.
    assert server._handle_flags(["gemini-faf-mcp"]) is None
    assert server._handle_flags(["gemini-faf-mcp", "--stdio"]) is None


def test_version_matches_pyproject():
    import tomllib

    with open(ROOT / "pyproject.toml", "rb") as f:
        assert tomllib.load(f)["project"]["version"] == server.__version__
