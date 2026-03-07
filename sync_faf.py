"""
FAF Bi-Sync: Keep GEMINI.md in sync with project.faf

Performs three critical roles:
1. Extracts current DNA from project.faf
2. Reads the AI-Readiness score from scores.faf_score
3. Updates GEMINI.md dynamically using frontmatter
"""

import yaml
import frontmatter  # install via: pip install python-frontmatter
import sys
import os

FAF_FILE = 'project.faf'
GEMINI_FILE = 'GEMINI.md'


def _get_tier(score):
    """Get FAF tier based on score (mirrors parser._get_tier)."""
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


def get_faf_score(data):
    """Read FAF score from scores.faf_score in project.faf."""
    scores = data.get('scores', {})
    if isinstance(scores, dict) and 'faf_score' in scores:
        return int(scores['faf_score'])

    # Fallback: count filled fields against spec slots
    total_slots = 21
    filled = sum(1 for k, v in data.items() if v and v != "TBD")
    return min(int((filled / total_slots) * 100), 100)


def sync():
    # 1. Load the latest Source of Truth DNA
    if not os.path.exists(FAF_FILE):
        print(f"ERROR: {FAF_FILE} not found")
        sys.exit(1)

    try:
        with open(FAF_FILE, 'r') as f:
            faf_dna = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse {FAF_FILE}: {e}")
        sys.exit(1)

    if not faf_dna or not isinstance(faf_dna, dict):
        print(f"ERROR: {FAF_FILE} is empty or not a valid YAML mapping")
        sys.exit(1)

    score = get_faf_score(faf_dna)
    tier = _get_tier(score)

    # 2. Load and Update GEMINI.md
    if not os.path.exists(GEMINI_FILE):
        print(f"ERROR: {GEMINI_FILE} not found")
        sys.exit(1)

    try:
        post = frontmatter.load(GEMINI_FILE)
    except Exception as e:
        print(f"ERROR: Failed to parse {GEMINI_FILE}: {e}")
        sys.exit(1)

    post.metadata['faf_score'] = f"{score}%"
    post.metadata['faf_tier'] = tier
    post.metadata['last_sync'] = faf_dna.get('generated', 'unknown')

    # 3. Write back with preserved structure
    with open(GEMINI_FILE, 'wb') as f:
        frontmatter.dump(post, f)

    print(f"Bi-Sync Complete: Score {score}% ({tier})")


if __name__ == "__main__":
    sync()
