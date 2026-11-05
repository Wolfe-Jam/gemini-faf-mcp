"""inject.py — non-destructive faf-block injection.

Python port of faf-cli's injector (src/interop/inject.ts), the one faf-cli,
faf-mcp, claude-faf-mcp and grok-faf-mcp use. The rules:

  - no file                 -> create it containing just the block
  - a whole-line marker pair -> replace ONLY the text between them
  - anything else           -> PREFIX the block; everything already there stays

faf replaces only text it can prove it wrote: what sits between its own marker
lines. A file with no marker pair is never reclaimed, whatever it starts with
(a `<!-- faf:` first line, a START with no END). Markers count only as whole
lines at column 0, outside fenced code — never as substrings.

A file that is not UTF-8, a link that leads out of the project, a dangling link
and anything inside `.git` are refused (InjectRefused) and nothing is written.
The write is atomic and keeps the file's permissions.
"""
import os
import stat
import tempfile
from pathlib import Path

FAF_START = "<!-- faf:start -->"
FAF_END = "<!-- faf:end -->"

# What a legacy faf stamp looks like. Only used to explain, never to reclaim.
FAF_METASTAMP = "<!-- faf:"

LEGACY_NOTE = (
    "faf's block is now on top; the old faf text below it is left as you had it — "
    "delete it by hand if you no longer want it."
)


class InjectRefused(Exception):
    """faf would not write this file; it is left exactly as it was."""


def _lines_with_ends(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def _strip_end(line: str) -> str:
    return line.rstrip("\r\n")


def _fence_open(bare: str) -> tuple[str, int] | None:
    """A CommonMark fence opener: up to 3 spaces, then 3+ backticks or tildes.
    A backtick fence's info string may not contain a backtick."""
    indent = len(bare) - len(bare.lstrip(" "))
    if indent > 3:
        return None
    rest = bare[indent:]
    for ch in ("`", "~"):
        n = len(rest) - len(rest.lstrip(ch))
        if n >= 3:
            if ch == "`" and "`" in rest[n:]:
                return None
            return (ch, n)
    return None


def _fence_closes(bare: str, fence: tuple[str, int]) -> bool:
    """A closing fence: up to 3 spaces, the same character at least as many
    times as the opener, then only whitespace (no info string)."""
    ch, n = fence
    indent = len(bare) - len(bare.lstrip(" "))
    if indent > 3:
        return False
    rest = bare[indent:]
    run = len(rest) - len(rest.lstrip(ch))
    return run >= n and rest[run:].strip() == ""


def _marker_lines(text: str):
    """Yield (offset, bom, bare) for every line outside fenced code."""
    offset = 0
    fence: tuple[str, int] | None = None
    for i, line in enumerate(_lines_with_ends(text)):
        bare = _strip_end(line)
        bom = 0
        if i == 0 and bare.startswith("\ufeff"):
            bom = 1
            bare = bare[1:]
        if fence is not None:
            if _fence_closes(bare, fence):
                fence = None
        else:
            opened = _fence_open(bare)
            if opened is not None:
                fence = opened
            else:
                yield offset, bom, bare
        offset += len(line)


def _find_block(text: str, start: str, end: str) -> tuple[int, int] | None:
    """faf's marked range: the last whole-line START before the first whole-line
    END after it, both outside fenced code. Returns the char range covering both
    marker lines (the END line's terminator excluded), or None.

    A leading BOM on line 1 stays outside the range."""
    start_at: int | None = None
    for offset, bom, bare in _marker_lines(text):
        if bare == start:
            start_at = offset + bom
        elif bare == end and start_at is not None:
            return (start_at, offset + bom + len(bare))
    return None


def _has_unpaired_marker(text: str, start: str, end: str) -> bool:
    return any(bare in (start, end) for _, _, bare in _marker_lines(text))


def legacy_stamp_note(label: str, existing: str | None, start: str = FAF_START, end: str = FAF_END) -> str | None:
    """Why the block will go on top instead of replacing: the file starts with a
    faf-looking stamp, or carries a marker line with no pair. None otherwise."""
    if existing is None or _find_block(existing, start, end) is not None:
        return None
    if existing.lstrip("﻿").lstrip().startswith(FAF_METASTAMP) or _has_unpaired_marker(existing, start, end):
        return f"{label}: {LEGACY_NOTE}"
    return None


def _resolve_target(p: Path, root: Path) -> Path:
    """The real file to write, inside the project, or InjectRefused."""
    root_real = root.resolve()
    if p.is_symlink():
        if not p.exists():
            raise InjectRefused(f"{p.name} is a link to nothing — refused.")
        real = p.resolve()
    else:
        real = p.parent.resolve() / p.name
    try:
        rel = real.relative_to(root_real)
    except ValueError:
        raise InjectRefused(f"{p.name} leads outside the project — refused.") from None
    if ".git" in rel.parts:
        raise InjectRefused(f"{p.name} is inside .git/ — refused.")
    if real.exists() and not real.is_file():
        raise InjectRefused(f"{p.name} is not a file — refused.")
    return real


def _read_utf8(real: Path, label: str) -> str | None:
    try:
        raw = real.read_bytes()
    except FileNotFoundError:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise InjectRefused(f"{label} is not UTF-8 — faf left it unchanged.") from None


def _atomic_write(real: Path, text: str) -> None:
    """Temp file in the same folder, fsync, rename. Keeps an existing file's
    permissions; a new file gets the usual 0666 minus the umask. The rename
    gives the path a new inode, so other hard links keep the old text."""
    if real.exists():
        mode = stat.S_IMODE(real.stat().st_mode)
        # Mode bits, not os.access: root can write anything, and faf still
        # leaves a file someone marked read-only alone.
        if not mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
            raise InjectRefused(f"{real.name} is read-only — faf left it unchanged.")
    else:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    try:
        fd, tmp = tempfile.mkstemp(prefix=".faf-tmp-", dir=str(real.parent))
    except OSError as e:
        raise InjectRefused(f"{real.name}: can't write in its folder ({e.strerror}) — nothing changed.") from None
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, real)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def inject_faf_block(
    path,
    block: str,
    start: str = FAF_START,
    end: str = FAF_END,
    root=None,
) -> str | None:
    """Write a faf-managed block into a file without touching anything else.

    Returns a note for the user when the block went on top instead of replacing
    (the file carried a faf-looking stamp or an unpaired marker), else None.
    Raises InjectRefused when the file is not safe to write; nothing is written.
    """
    p = Path(path)
    project = Path(root) if root is not None else p.parent
    real = _resolve_target(p, project)
    label = p.name
    body = block.strip()
    if any(_strip_end(line) in (start, end) for line in _lines_with_ends(body)):
        raise InjectRefused(f"{label}: the generated block contains a faf marker line — nothing written.")

    existing = _read_utf8(real, label)
    # Match the file's line endings, so a CRLF file stays CRLF.
    nl = "\r\n" if existing and existing.count("\r\n") > existing.count("\n") / 2 else "\n"
    wrapped = nl.join([start, *body.splitlines(), end])
    if existing is None:
        _atomic_write(real, wrapped + nl)
        return None

    note = legacy_stamp_note(label, existing, start, end)
    found = _find_block(existing, start, end)
    if found is not None:
        s, e = found
        _atomic_write(real, existing[:s] + wrapped + existing[e:])
        return None

    # No block faf can prove it wrote: put the block on top, keep everything.
    bom = "﻿" if existing.startswith("﻿") else ""
    rest = existing[len(bom):]
    _atomic_write(real, bom + wrapped + nl + nl + rest)
    return note
