"""inject.py — non-destructive faf-block injection.

Python twin of faf-cli's src/interop/inject.ts. faf owns the block between the
markers; the user owns everything else. Enhance, never replace.
"""
from pathlib import Path

FAF_START = "<!-- faf:start -->"
FAF_END = "<!-- faf:end -->"

# faf's own metastamp fingerprint. Every faf-generated file begins with it, and a
# user never hand-writes it — so a markerless file led by it is legacy faf output
# we can safely reclaim, never genuine user content.
FAF_METASTAMP = "<!-- faf:"


def inject_faf_block(
    path,
    block: str,
    start: str = FAF_START,
    end: str = FAF_END,
) -> None:
    """Non-destructively write a faf-managed block into a file.

      - no file                                 -> create it with just the block
      - markers present                         -> replace ONLY between them (update in place)
      - legacy faf file (metastamp, no markers) -> reclaim in place (no duplication)
      - genuine user file                       -> prefix the block; preserve everything below

    Idempotent: re-runs update the block, never duplicate or destroy user content.
    """
    p = Path(path)
    wrapped = f"{start}\n{block.strip()}\n{end}"

    if not p.exists():
        p.write_text(wrapped + "\n", encoding="utf-8")
        return

    existing = p.read_text(encoding="utf-8")
    s = existing.find(start)
    e = existing.find(end)

    if s != -1 and e != -1 and e > s:
        before = existing[:s]
        after = existing[e + len(end):]
        p.write_text(before + wrapped + after, encoding="utf-8")
        return

    if existing.lstrip().startswith(FAF_METASTAMP):
        # Legacy faf output — reclaim in place, no duplication.
        p.write_text(wrapped + "\n", encoding="utf-8")
        return

    # Genuine user file — prefix the block, preserve everything.
    p.write_text(wrapped + "\n\n" + existing, encoding="utf-8")
