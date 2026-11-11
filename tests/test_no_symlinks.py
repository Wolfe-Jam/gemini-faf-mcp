"""The repo tracks no symlinks.

Gemini CLI installs the whole repo as the extension, and rewrote a committed
link (`.gemini/project.faf -> ../project.faf`) to point at a temporary folder it
then deleted. `agy plugin import gemini` then stopped on the dangling link, so
the extension could not move to Antigravity. A plain file or nothing at all is
safe; a link is not.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_no_tracked_symlinks():
    if not (ROOT / ".git").exists() or shutil.which("git") is None:
        pytest.skip("needs a git checkout (an sdist or tarball has no .git)")
    out = subprocess.run(
        ["git", "ls-files", "-s"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    links = [line.split("\t", 1)[1] for line in out.splitlines() if line.startswith("120000 ")]
    assert links == [], f"tracked symlinks ship in the extension and break agy plugin import: {links}"
