"""
FAF Parser - Local .faf file parsing

Parses .faf files and scores them with the always-33 kernel (faf-python-sdk's
``score_faf``): the same number as faf-cli, the MCP servers and mcpaas.live.
Format: application/vnd.faf+yaml (IANA registered)
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from faf_sdk import score_faf
from faf_sdk import validate as _validate_structure


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


_PLACEHOLDERS = {"", "null", "none", "unknown", "tbd", "todo", "n/a", "not applicable"}


def _plain(value: Any, _seen: frozenset[int] = frozenset()) -> Any:
    """Plain YAML types for scoring. Mappings, sequences and str subclasses become
    dict / list / str; other values become their str(), and an empty one stays empty."""
    if value is None or type(value) in (bool, int, float):
        return value
    if isinstance(value, str):
        return str.__str__(value)  # the text itself, not a subclass's __str__ (str Enums)
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        if id(value) in _seen:
            raise ValueError("the data refers to itself")
        seen = _seen | {id(value)}
        if isinstance(value, Mapping):
            return {(str.__str__(k) if isinstance(k, str) else k): _plain(v, seen) for k, v in value.items()}
        return [_plain(v, seen) for v in value]
    try:
        empty = not value
    except Exception:  # noqa: BLE001 — a value with no truth value is not empty
        empty = False
    return "" if empty else str(value)


def _looks_filled(data: Any, slot: str) -> bool:
    """True when the slot path holds a non-placeholder text or number in the plain data."""
    node = data
    for part in slot.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    if isinstance(node, bool) or node is None:
        return False
    if isinstance(node, (int, float)):
        return True
    return isinstance(node, str) and node.strip().lower() not in _PLACEHOLDERS | {"slotignored"}


def validate_faf(data: dict[str, Any]) -> dict[str, Any]:
    """
    Score a parsed .faf with the always-33 kernel and list the empty slots.

    One engine, one number: the score and tier are faf-python-sdk's
    ``score_faf``, the same as ``faf_score`` and faf-cli for ordinary files.
    ``valid`` means what it means in ``faf_validate``: the structure is valid.

    ``data`` is already parsed by PyYAML, so YAML merge keys (``<<``) are
    applied and duplicate keys are already collapsed. For the exact score of
    a file's text, use ``faf_score``.

    Args:
        data: Parsed FAF data

    Returns:
        ``valid`` (structure valid, as ``faf_validate``); ``score`` (0-100);
        ``tier`` (the kernel's: TROPHY, GOLD, SILVER, BRONZE, GREEN, YELLOW,
        RED, WHITE); ``populated`` / ``active`` / ``total``;
        ``filled_slots`` / ``total_slots`` (populated / active, kept for
        existing callers; ``total_slots`` is 0 when every slot is
        slotignored); ``issues`` (structure errors, why the data couldn't be
        scored, then each empty active slot); ``warnings`` (as ``faf_validate``).
    """
    def unscored(reason: str, warnings: list[str]) -> dict[str, Any]:
        return {
            "valid": False, "score": 0, "tier": "WHITE",
            "populated": 0, "active": 33, "total": 33,
            "filled_slots": 0, "total_slots": 33,
            "issues": [f"Could not score: {reason}"],
            "warnings": warnings,
        }

    if not isinstance(data, Mapping):
        return unscored(f"expected a mapping, got {type(data).__name__}", [])

    try:
        plain = _plain(data)
        result = score_faf(yaml.safe_dump(plain, sort_keys=False, allow_unicode=True))
    except Exception as e:  # noqa: BLE001 — reported as an issue, never a silent 0
        return unscored(str(e), [])

    structure = _validate_structure(plain)
    warnings = list(structure.warnings)

    if result.populated == 0 and any(_looks_filled(plain, slot) for slot, _ in result.slots):
        return unscored("the kernel could not read the data", warnings)

    issues = list(structure.errors) + [
        f"Missing or placeholder: {slot}"
        for slot, state in result.slots
        if state.name == "EMPTY"
    ]

    return {
        "valid": structure.valid,
        "score": result.score,
        "tier": result.tier,
        "populated": result.populated,
        "active": result.active,
        "total": result.total,
        "filled_slots": result.populated,
        "total_slots": result.active,
        "issues": issues,
        "warnings": warnings,
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
