"""
safe_path.py — confinement for caller-supplied `path` arguments.

Python twin of the grok-faf-mcp helper (src/utils/safe-path.ts). FAF MCP tools
take a `path` argument and read/write a `.faf` context file from it; historically
that path reached `Path(path).read_text()` / `.write_text()` with no confinement,
so an absolute path or `../` traversal could read any file the server uid can
read (and `faf_init` could write any file). CWE-22 / CWE-73 / CWE-200.

Two layers:
  1. Context-file allow-list (ALWAYS ON for reads) — a resolved *file* must be a
     `.faf` / `.fafm` context file. Blocks /etc/passwd, ~/.ssh/id_rsa,
     ~/.aws/credentials, .env, etc. regardless of directory.
  2. Root confinement — reads: opt-in via FAF_ALLOWED_ROOTS. General file ops
     (faf_init write): always confined to cwd + system temp (override with
     FAF_ALLOWED_ROOTS), so a write can't escape the project (e.g. ~/.bashrc).

Paths are canonicalized through symlinks (closing the symlink bypass) and
tolerant of a not-yet-existing write target.
"""

import os
import tempfile
from pathlib import Path


class PathConfinementError(Exception):
    """Raised when a caller-supplied path escapes the allowed boundary."""


def is_faf_context_file(p: Path) -> bool:
    name = p.name.lower()
    return name == ".faf" or name.endswith(".faf") or name.endswith(".fafm")


def _canonical(p: Path) -> Path:
    """Symlink-canonical absolute path, tolerant of a not-yet-existing target:
    resolves the nearest EXISTING ancestor through symlinks, then re-appends the
    missing tail (so a new file under /tmp matches a /private/tmp root on macOS)."""
    p = p.expanduser()
    base = p if p.is_absolute() else (Path.cwd() / p)
    cur = base
    tail: list = []
    while True:
        try:
            real = cur.resolve(strict=True)
            for seg in reversed(tail):
                real = real / seg
            return real
        except (FileNotFoundError, RuntimeError, OSError):
            if cur.parent == cur:
                return base
            tail.append(cur.name)
            cur = cur.parent


def allowed_roots() -> list:
    """Opt-in roots from FAF_ALLOWED_ROOTS (OS-delimited). Empty when unset."""
    env = os.environ.get("FAF_ALLOWED_ROOTS")
    if env and env.strip():
        return [_canonical(Path(r)) for r in env.split(os.pathsep) if r.strip()]
    return []


def file_op_roots() -> list:
    """Roots for write/general file ops: FAF_ALLOWED_ROOTS, else cwd + temp."""
    roots = allowed_roots()
    if roots:
        return roots
    out = [Path.cwd().resolve(), Path(tempfile.gettempdir()).resolve()]
    if os.name != "nt":
        out.append(_canonical(Path("/tmp")))
    return out


def _within(child: Path, root: Path) -> bool:
    if child == root:
        return True
    try:
        child.relative_to(root)
        return True
    except ValueError:
        return False


def confine_path(input_path, require_faf: bool = True, roots=None) -> Path:
    """Resolve and confine a caller path. Returns the safe absolute Path or
    raises PathConfinementError. Does not perform the read/write itself."""
    if not isinstance(input_path, str) or input_path == "":
        raise PathConfinementError("path must be a non-empty string")
    if "\x00" in input_path:
        raise PathConfinementError("path contains a null byte")

    resolved = _canonical(Path(input_path))
    rootset = [_canonical(r) for r in (roots if roots is not None else allowed_roots())]

    if rootset and not any(_within(resolved, r) for r in rootset):
        raise PathConfinementError(f'path escapes FAF_ALLOWED_ROOTS: "{input_path}"')

    if require_faf and resolved.is_file() and not is_faf_context_file(resolved):
        raise PathConfinementError(
            f'refusing to read a non-context file via `path`: "{input_path}". '
            "Only .faf / .fafm files are allowed."
        )

    return resolved


def confine_file_op(input_path) -> Path:
    """Confine a general file read/write path (any file type) to file_op_roots()."""
    return confine_path(input_path, require_faf=False, roots=file_op_roots())
