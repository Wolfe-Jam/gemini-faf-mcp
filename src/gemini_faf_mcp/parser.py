"""
FAF Parser - Local .faf file parsing

Parses .faf files and scores them with the always-33 kernel (faf-python-sdk's
``score_faf``): the same number as faf-cli, the MCP servers and mcpaas.live.
Format: application/vnd.faf+yaml (IANA registered)
"""

from pathlib import Path
from typing import Any

import yaml
from faf_sdk import score_faf


def parse_faf(path: str = "project.faf") -> dict[str, Any]:
    """
    Parse a .faf file and return its contents.

    Args:
        path: Path to the .faf file

    Returns:
        Parsed YAML content as dictionary

    Raises:
        FileNotFoundError: If .faf file doesn't exist
        ValueError: If .faf file is invalid YAML
    """
    faf_path = Path(path)

    if not faf_path.exists():
        raise FileNotFoundError(f"FAF file not found: {path}")

    with open(faf_path, encoding="utf-8") as f:
        content = f.read()

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in FAF file: {e}") from e

    return data or {}


def validate_faf(data: dict[str, Any]) -> dict[str, Any]:
    """
    Score a parsed .faf with the always-33 kernel and list what's missing.

    One engine, one number: the score is faf-python-sdk's ``score_faf``, the
    same as faf-cli, ``faf_score`` and mcpaas.live. All 33 slots count unless
    the file marks them ``slotignored``.

    Args:
        data: Parsed FAF data

    Returns:
        ``score`` (0-100), ``tier`` (Trophy, Gold, Silver, Bronze, Green,
        Yellow, Red or White), ``populated`` / ``active`` / ``total`` slots
        (``filled_slots`` / ``total_slots`` are the same populated / active
        counts, kept for existing callers), ``issues`` (missing basics) and
        ``valid`` (no issues).
    """
    issues = []

    if "faf_version" not in data:
        issues.append("Missing: faf_version")

    project = data.get("project") or {}
    for field in ("name", "goal", "main_language"):
        if not (isinstance(project, dict) and project.get(field)):
            issues.append(f"Missing: project.{field}")

    human_context = data.get("human_context") or {}
    for field in ("who", "what", "why", "where", "when", "how"):
        value = human_context.get(field) if isinstance(human_context, dict) else None
        if not value or value in ("None", "Unknown", "TBD"):
            issues.append(f"Missing or placeholder: human_context.{field}")

    try:
        result = score_faf(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
        score, tier = result.score, result.tier.title()
        populated, active, total = result.populated, result.active, result.total
    except Exception:
        score, tier, populated, active, total = 0, "White", 0, 33, 33

    return {
        "valid": len(issues) == 0,
        "score": score,
        "tier": tier,
        "populated": populated,
        "active": active,
        "total": total,
        "filled_slots": populated,
        "total_slots": active,
        "issues": issues,
    }


def find_faf_file(directory: str = ".") -> str | None:
    """
    Find .faf file in directory.

    Searches for: project.faf, .faf, *.faf

    Args:
        directory: Directory to search

    Returns:
        Path to .faf file or None if not found
    """
    dir_path = Path(directory)

    # Priority order
    candidates = [
        dir_path / "project.faf",
        dir_path / ".faf",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    # Fallback: any .faf file
    faf_files = list(dir_path.glob("*.faf"))
    if faf_files:
        return str(faf_files[0])

    return None
