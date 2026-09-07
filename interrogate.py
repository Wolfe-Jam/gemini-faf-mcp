"""
Repo interrogation — the services and targets a repo declares ARE its stack.

Python port of faf-cli's `src/interrogate/compose.ts` + `build-files.ts`
(the "Full-Facts" grounding, faf-cli 7.10), kept in parity. A polyglot or
platform repo declares Postgres, Redis, ClickHouse in `docker-compose.yml`
and drives test/build/lint through a `Makefile` — neither of which the
root-manifest detectors in `_detect_stack` look at. Facts from files, never
prose or guesses.

`faf_auto` runs these after manifest detection and fills EMPTY slots only —
file-facts win over presence-only guesses, hand-written values win over both.
"""

from __future__ import annotations

import re
from pathlib import Path

_IGNORE_DIRS = {
    "node_modules", ".git", "dist", "build", "vendor", "target",
    "e2e", "tests", "test", "docs", "scripts", ".venv", "__pycache__",
}

# compose service image (before ':' tag, after last '/') -> (slot, label)
_IMAGE_MAP: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"^postgres|postgis|pgvector"), "database", "PostgreSQL"),
    (re.compile(r"^mysql"), "database", "MySQL"),
    (re.compile(r"^mariadb"), "database", "MariaDB"),
    (re.compile(r"^mongo"), "database", "MongoDB"),
    (re.compile(r"clickhouse"), "database", "ClickHouse"),
    (re.compile(r"^cockroach"), "database", "CockroachDB"),
    (re.compile(r"^redis|^valkey"), "cache", "Redis"),
    (re.compile(r"^memcached"), "cache", "Memcached"),
    (re.compile(r"elasticsearch"), "search", "Elasticsearch"),
    (re.compile(r"opensearch"), "search", "OpenSearch"),
    (re.compile(r"meilisearch"), "search", "Meilisearch"),
    (re.compile(r"typesense"), "search", "Typesense"),
    (re.compile(r"qdrant"), "search", "Qdrant (vector)"),
    (re.compile(r"weaviate"), "search", "Weaviate (vector)"),
    (re.compile(r"^minio"), "storage", "MinIO (S3-compatible)"),
    (re.compile(r"localstack"), "storage", "LocalStack (AWS)"),
    (re.compile(r"rabbitmq"), "runtime", "RabbitMQ"),
    (re.compile(r"kafka"), "runtime", "Kafka"),
    (re.compile(r"nats"), "runtime", "NATS"),
    (re.compile(r"temporalio/|temporal-server|temporal:"), "runtime", "Temporal"),
]

_COMPOSE_RE = re.compile(r"^(docker-)?compose.*\.ya?ml$", re.IGNORECASE)
_IMAGE_LINE_RE = re.compile(r"""^\s*image:\s*["']?([^\s"'#]+)""", re.MULTILINE)


def _find_compose_files(directory: Path) -> list[Path]:
    """Every compose file at root + one directory deep."""
    out: list[Path] = []

    def scan(d: Path, depth: int) -> None:
        try:
            entries = list(d.iterdir())
        except OSError:
            return
        for e in entries:
            if e.is_file() and _COMPOSE_RE.match(e.name):
                out.append(e)
            elif (
                e.is_dir()
                and depth > 0
                and not e.name.startswith(".")
                and e.name not in _IGNORE_DIRS
            ):
                scan(e, depth - 1)

    scan(directory, 1)
    return out


def interrogate_compose(directory: str | Path) -> dict[str, str]:
    """Map docker-compose service images onto stack slots.

    Returns a dict of {slot: label} for any of database / cache / search /
    storage / runtime that a recognised image was found for, plus
    `hosting: "Docker Compose"` when any compose file exists.
    """
    root = Path(directory)
    files = _find_compose_files(root)
    if not files:
        return {}

    found: dict[str, list[str]] = {
        "database": [], "cache": [], "search": [], "storage": [], "runtime": [],
    }
    for file in files:
        try:
            body = file.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in _IMAGE_LINE_RE.finditer(body):
            ref = m.group(1).lower()
            no_tag = re.sub(r":[^/]*$", "", ref)
            name = no_tag.split("/")[-1] or ref
            for pat, slot, label in _IMAGE_MAP:
                if (pat.search(name) or pat.search(no_tag)) and label not in found[slot]:
                    found[slot].append(label)

    stack: dict[str, str] = {}
    for slot in ("database", "cache", "search", "storage"):
        if found[slot]:
            stack[slot] = " · ".join(found[slot])
    if found["runtime"]:
        stack["runtime"] = f"Docker Compose ({' · '.join(found['runtime'])})"
    stack["hosting"] = "Docker Compose"
    return stack


# --- build files (Makefile / justfile / Taskfile) --------------------------

_BUILD_FILES: list[tuple[str, str, re.Pattern[str]]] = [
    # (filename, runner, target-name regex over the file body)
    ("Makefile", "make", re.compile(r"^([a-zA-Z][\w-]*)\s*:(?!=)", re.MULTILINE)),
    ("justfile", "just", re.compile(r"^([a-zA-Z][\w-]*)\s*(?:\([^)]*\))?\s*:", re.MULTILINE)),
]

_CMD_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "test": [re.compile(p, re.I) for p in (r"^test$", r"^tests$", r"test-all", r"^test-unit", r"^test")],
    "build": [re.compile(p, re.I) for p in (r"^build$", r"^compile$", r"^build")],
    "lint": [re.compile(p, re.I) for p in (r"^check-all$", r"^check$", r"^lint$", r"^lint", r"^fmt$", r"^format$")],
}


def _pick(targets: list[str], patterns: list[re.Pattern[str]]) -> str | None:
    for p in patterns:
        for t in targets:
            if p.search(t):
                return t
    return None


def _build_file_dirs(directory: Path) -> list[Path]:
    """Root, then each depth-1 subdir (nested `backend/Makefile` is found)."""
    dirs = [directory]
    try:
        for e in directory.iterdir():
            if e.is_dir() and not e.name.startswith(".") and e.name not in _IGNORE_DIRS:
                dirs.append(e)
    except OSError:
        pass
    return dirs


def _looks_primary(d: Path) -> int:
    s = 0
    if (d / "manage.py").exists() or (d / "pyproject.toml").exists() or (d / "Gemfile").exists():
        s += 3
    if d.name in ("backend", "api", "server", "core", "app"):
        s += 2
    return s


def _taskfile_targets(body: str) -> list[str]:
    i = body.find("tasks:")
    if i == -1:
        return []
    return re.findall(r"^\s{2}([a-zA-Z][\w-]*):", body[i:], re.MULTILINE)


def interrogate_build_files(directory: str | Path) -> dict[str, str]:
    """Read Makefile / justfile / Taskfile targets and map the obvious ones
    onto `test` / `build` / `lint` commands. Prefers the root file, then the
    dir that looks like the primary app."""
    root = Path(directory)
    candidates: list[tuple[int, dict[str, str]]] = []

    for scan_dir in _build_file_dirs(root):
        is_root = scan_dir == root
        prefix = "" if is_root else f"cd {scan_dir.name} && "
        specs = list(_BUILD_FILES)
        if (scan_dir / "Taskfile.yml").exists():
            specs = specs + [("Taskfile.yml", "task", None)]  # type: ignore[list-item]
        for fname, runner, target_re in specs:
            path = scan_dir / fname
            if not path.exists():
                continue
            try:
                body = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if fname == "Taskfile.yml":
                targets = _taskfile_targets(body)
            else:
                assert target_re is not None
                targets = target_re.findall(body)
            if not targets:
                continue

            commands: dict[str, str] = {}
            for slot, pats in _CMD_PATTERNS.items():
                hit = _pick(targets, pats)
                if hit:
                    commands[slot] = f"{prefix}{runner} {hit}"
            if not commands:
                continue
            score = len(commands) + (10 if is_root else _looks_primary(scan_dir))
            candidates.append((score, commands))

    if not candidates:
        return {}
    candidates.sort(key=lambda c: c[0], reverse=True)
    return candidates[0][1]


def interrogate_repo(directory: str | Path) -> dict[str, dict[str, str]]:
    """Run every interrogator, return `{"stack": {...}, "commands": {...}}`.
    Both may be empty. Callers fill empty slots only."""
    return {
        "stack": interrogate_compose(directory),
        "commands": interrogate_build_files(directory),
    }
