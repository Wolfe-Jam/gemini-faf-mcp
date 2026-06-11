"""TRUST SEAL — "enhance, never replace" (source write-guard).

faf must NEVER raw-overwrite a context file. Context writes go through
inject_faf_block (non-destructive). This guard fails the build if any
`.write_text(...)` targets a context file directly — so the file-wipe bug
physically cannot be reintroduced. A write is allowed only if it routes through
inject_faf_block OR carries an explicit `trust-seal-ok:` exemption.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = re.compile(
    r"\.write_text\s*\([^)]*\b(AGENTS\.md|GEMINI\.md|CLAUDE\.md|\.cursorrules)\b"
)


def _py_files():
    for f in ROOT.glob("*.py"):
        if f.name != "inject.py":
            yield f
    src = ROOT / "src"
    if src.exists():
        for f in src.rglob("*.py"):
            if f.name != "inject.py":
                yield f


def test_no_raw_context_file_write():
    violations = []
    for f in _py_files():
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if CONTEXT.search(line) and "trust-seal-ok" not in line:
                violations.append(f"{f.relative_to(ROOT)}:{i}  {line.strip()}")
    assert not violations, (
        "TRUST SEAL BROKEN — raw context-file write detected. Route it through "
        "inject_faf_block (enhance, never replace):\n  " + "\n  ".join(violations)
    )


def test_export_tools_use_the_injector():
    """faf_agents / faf_gemini must enhance, not overwrite — they go through inject_faf_block."""
    server = (ROOT / "server.py").read_text()
    assert "from inject import inject_faf_block" in server
    assert server.count("inject_faf_block(") >= 2  # faf_agents + faf_gemini
