"""
FAF Parser - Local .faf file parsing

Validates and parses .faf files according to the v2.5.2 specification.
Format: application/vnd.faf+yaml (IANA registered)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def parse_faf(path: str = "project.faf") -> Dict[str, Any]:
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

    with open(faf_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in FAF file: {e}")

    return data or {}


def validate_faf(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate FAF structure against v2.5.2 specification.

    Args:
        data: Parsed FAF data

    Returns:
        Validation result with score and issues

    Required sections (v2.5.2):
        - faf_version
        - project (name, goal, main_language)
        - human_context (who, what, why, where, when, how)
    """
    issues = []
    score = 0
    total_slots = 0

    # Check faf_version
    total_slots += 1
    if "faf_version" in data:
        score += 1
    else:
        issues.append("Missing: faf_version")

    # Check project section
    project = data.get("project", {})
    project_fields = ["name", "goal", "main_language"]
    for field in project_fields:
        total_slots += 1
        if project.get(field):
            score += 1
        else:
            issues.append(f"Missing: project.{field}")

    # Check human_context section
    human_context = data.get("human_context", {})
    context_fields = ["who", "what", "why", "where", "when", "how"]
    for field in context_fields:
        total_slots += 1
        value = human_context.get(field)
        # Check for non-empty, non-placeholder values
        if value and value not in ["None", "Unknown", "TBD", ""]:
            score += 1
        else:
            issues.append(f"Missing or placeholder: human_context.{field}")

    # Calculate percentage
    percentage = round((score / total_slots) * 100) if total_slots > 0 else 0

    # Determine tier
    tier = _get_tier(percentage)

    return {
        "valid": len(issues) == 0,
        "score": percentage,
        "tier": tier,
        "filled_slots": score,
        "total_slots": total_slots,
        "issues": issues
    }


def _get_tier(score: int) -> str:
    """Get FAF tier based on score."""
    if score == 100:
        return "Trophy"
    elif score >= 99:
        return "Gold"
    elif score >= 95:
        return "Silver"
    elif score >= 85:
        return "Bronze"
    elif score >= 70:
        return "Green"
    elif score >= 55:
        return "Yellow"
    else:
        return "Red"


def find_faf_file(directory: str = ".") -> Optional[str]:
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
