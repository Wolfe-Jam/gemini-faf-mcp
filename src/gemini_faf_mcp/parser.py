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


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys, as faf-cli and the kernel do."""

    def construct_mapping(self, node, deep=False):  # type: ignore[no-untyped-def]
        if isinstance(node, yaml.MappingNode):
            seen: set[Any] = set()
            for key_node, _ in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":
                    continue
                key = self.construct_object(key_node, deep=True)
                try:
                    duplicate = key in seen
                except TypeError:
                    continue
                if duplicate:
                    raise yaml.constructor.ConstructorError(
                        None, None, f"duplicate key {key!r}", key_node.start_mark
                    )
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


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
        data = yaml.load(content, Loader=_UniqueKeyLoader)  # noqa: S506 (a SafeLoader subclass)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in FAF file: {e}") from e

    return data or {}


def _plain(value: Any, _seen: frozenset[int] = frozenset()) -> Any:
    """Turn any mapping, sequence or str subclass into plain YAML types; anything else becomes its str()."""
    if value is None or isinstance(value, (bool, int, float)) and type(value) in (bool, int, float):
        return value
    if isinstance(value, str):
        return str(value)
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        if id(value) in _seen:
            raise ValueError("the data refers to itself")
        seen = _seen | {id(value)}
        if isinstance(value, Mapping):
            return {str(k) if not isinstance(k, (str, int, float, bool)) or k is None else k: _plain(v, seen) for k, v in value.items()}
        return [_plain(v, seen) for v in value]
    return str(value)


def validate_faf(data: dict[str, Any]) -> dict[str, Any]:
    """
    Score a parsed .faf with the always-33 kernel and list the empty slots.

    One engine, one number: the score and tier are faf-python-sdk's
    ``score_faf``, the same as ``faf_score``, faf-cli and mcpaas.live. All
    33 slots count unless the file marks them ``slotignored``.

    ``data`` is already parsed, so YAML merge keys (``<<``) have already been
    applied. For the exact score of a file's text, use ``faf_score``.

    Args:
        data: Parsed FAF data

    Returns:
        ``score`` (0-100); ``tier`` (the kernel's: TROPHY, GOLD, SILVER,
        BRONZE, GREEN, YELLOW, RED, WHITE); ``populated`` / ``active`` /
        ``total`` slots; ``filled_slots`` / ``total_slots`` (populated /
        active, kept for existing callers; ``total_slots`` is 0 when every
        slot is slotignored); ``issues`` (each empty active slot, or why the
        data couldn't be scored); ``warnings`` (e.g. no ``faf_version``);
        ``valid`` (scored, with no issues).
    """
    warnings: list[str] = []
    if not isinstance(data, Mapping):
        return {
            "valid": False, "score": 0, "tier": "WHITE",
            "populated": 0, "active": 33, "total": 33,
            "filled_slots": 0, "total_slots": 33,
            "issues": [f"Could not score: expected a mapping, got {type(data).__name__}"],
            "warnings": warnings,
        }
    if "faf_version" not in data:
        warnings.append("Missing: faf_version")

    try:
        result = score_faf(yaml.safe_dump(_plain(data), sort_keys=False, allow_unicode=True))
    except Exception as e:  # noqa: BLE001 — reported as an issue, never a silent 0
        return {
            "valid": False, "score": 0, "tier": "WHITE",
            "populated": 0, "active": 33, "total": 33,
            "filled_slots": 0, "total_slots": 33,
            "issues": [f"Could not score: {e}"],
            "warnings": warnings,
        }

    issues = [
        f"Missing or placeholder: {slot}"
        for slot, state in result.slots
        if state.name == "EMPTY"
    ]

    return {
        "valid": not issues,
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
