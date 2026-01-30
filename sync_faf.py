"""
FAF Bi-Sync: Keep GEMINI.md in sync with project.faf

Performs three critical roles:
1. Extracts current DNA from project.faf
2. Calculates current AI-Readiness score
3. Updates GEMINI.md dynamically using frontmatter
"""

import yaml
import frontmatter  # install via: pip install python-frontmatter
import os

FAF_FILE = 'project.faf'
GEMINI_FILE = 'GEMINI.md'


def calculate_faf_score(data):
    """Calculates completion score based on the 21-slot standard."""
    total_slots = 21
    filled_slots = sum(1 for key, value in data.items() if value and value != "TBD")
    return int((filled_slots / total_slots) * 100)


def sync():
    # 1. Load the latest Source of Truth DNA
    with open(FAF_FILE, 'r') as f:
        faf_dna = yaml.safe_load(f)

    score = calculate_faf_score(faf_dna)
    tier = "Bronze" if score >= 85 else "Incomplete"

    # 2. Load and Update GEMINI.md
    post = frontmatter.load(GEMINI_FILE)
    post.metadata['faf_score'] = f"{score}%"
    post.metadata['faf_tier'] = tier
    post.metadata['last_sync'] = faf_dna.get('generated', 'unknown')

    # 3. Write back with preserved structure
    with open(GEMINI_FILE, 'wb') as f:
        frontmatter.dump(post, f)

    print(f"✅ Bi-Sync Complete: Score {score}% ({tier})")


if __name__ == "__main__":
    sync()
