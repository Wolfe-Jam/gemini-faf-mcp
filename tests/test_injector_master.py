"""WJTTC — the managed-block injector (port of the Master, grok-faf-mcp #186)

The cases are the WJTTC MCP-family audit's reproductions (2026-11-04, §B3/§B4),
the same contract grok-faf-mcp, faf-mcp and claude-faf-mcp pass through faf-cli:

  1. a first line that looks like a faf stamp is never reclaimed — the human's
     lines stay, and a note says why the block went on top
  2. a START with no END is not a block — nothing after it is cut
  3. a marker quoted in prose is not a marker — only whole lines count
  4. a file that isn't UTF-8 is refused and left byte-for-byte as it was
  5. a dangling link is refused — nothing is written through it
  6. markers present -> only the block changes, idempotently
  7. the tool reply carries the note, and a refusal is reported, not hidden
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from inject import FAF_END, FAF_START, InjectRefused, inject_faf_block  # noqa: E402


def _blocks(text: str) -> int:
    return sum(1 for line in text.splitlines() if line == FAF_START)


def test_1_legacy_looking_first_line_kept_with_note(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text("<!-- faf: my own note, hand-written -->\n# Team rules\nNever deploy on Friday.\n", encoding="utf-8")
    note = inject_faf_block(p, "generated block")
    out = p.read_text(encoding="utf-8")
    assert "Never deploy on Friday." in out
    assert "<!-- faf: my own note, hand-written -->" in out
    assert "generated block" in out
    assert _blocks(out) == 1
    assert note and note.startswith("AGENTS.md: ")


def test_2_start_without_end_cuts_nothing(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text(f"{FAF_START}\nold block\n## My notes\nKeep this line.\n", encoding="utf-8")
    inject_faf_block(p, "new block")
    out = p.read_text(encoding="utf-8")
    assert "Keep this line." in out
    assert "new block" in out


def test_3_marker_quoted_in_prose_is_not_a_marker(tmp_path):
    p = tmp_path / "GEMINI.md"
    p.write_text(
        f"## Rule\nOur block runs from `{FAF_START}` to `{FAF_END}` — do not edit inside it.\n\n"
        f"{FAF_START}\nv1\n{FAF_END}\n\n## Rule two\nStill here.\n",
        encoding="utf-8",
    )
    inject_faf_block(p, "v2")
    out = p.read_text(encoding="utf-8")
    assert "v2" in out and "v1" not in out
    assert "do not edit inside it." in out
    assert "Still here." in out


def test_3b_marker_inside_a_code_fence_is_not_a_marker(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text(f"```\n{FAF_START}\nexample\n{FAF_END}\n```\n\n{FAF_START}\nv1\n{FAF_END}\n", encoding="utf-8")
    inject_faf_block(p, "v2")
    out = p.read_text(encoding="utf-8")
    assert "example" in out
    assert "v2" in out and "v1" not in out


def test_4_not_utf8_refused_byte_identical(tmp_path):
    p = tmp_path / "GEMINI.md"
    data = b"# Notes\nCaf\xe9 au lait\n"
    p.write_bytes(data)
    with pytest.raises(InjectRefused):
        inject_faf_block(p, "block")
    assert p.read_bytes() == data


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_5_dangling_link_refused_nothing_written(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-elsewhere.txt"
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "AGENTS.md").symlink_to(outside)
    with pytest.raises(InjectRefused):
        inject_faf_block(proj / "AGENTS.md", "block")
    assert not outside.exists()


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_5b_link_out_of_project_refused(tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("theirs\n", encoding="utf-8")
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "AGENTS.md").symlink_to(outside)
    with pytest.raises(InjectRefused):
        inject_faf_block(proj / "AGENTS.md", "block")
    assert outside.read_text(encoding="utf-8") == "theirs\n"


def test_6_markers_present_update_in_place_idempotent(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text(f"# Mine\n\n{FAF_START}\nv1\n{FAF_END}\n\nTail notes.\n", encoding="utf-8")
    assert inject_faf_block(p, "v2") is None
    first = p.read_text(encoding="utf-8")
    inject_faf_block(p, "v2")
    out = p.read_text(encoding="utf-8")
    assert out == first
    assert "# Mine" in out and "Tail notes." in out
    assert "v2" in out and "v1" not in out
    assert _blocks(out) == 1


@pytest.mark.skipif(os.name == "nt", reason="no Unix mode bits on Windows")
def test_mode_kept_and_no_temp_left(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text("# Mine\n", encoding="utf-8")
    p.chmod(0o640)
    inject_faf_block(p, "block")
    assert oct(p.stat().st_mode & 0o777) == oct(0o640)
    assert [f.name for f in tmp_path.iterdir()] == ["AGENTS.md"]


def _tool(name):
    import server  # noqa: E402
    fn = getattr(server, name)
    return getattr(fn, "fn", fn)


FAF = "faf_version: '3.0'\nproject:\n  name: demo\n  goal: ship\n  main_language: Python\n"


def test_7_tool_reply_carries_the_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "project.faf").write_text(FAF, encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("<!-- faf: mine -->\n# Rules\nKeep me.\n", encoding="utf-8")
    r = _tool("faf_agents")(path=str(tmp_path / "project.faf"))
    assert r["success"] is True
    assert "Keep me." in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert r["message"].startswith("AGENTS.md: ")
    assert "preserved" not in r["message"]


def test_7b_tool_reports_a_refusal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "project.faf").write_text(FAF, encoding="utf-8")
    data = b"Caf\xe9\n"
    (tmp_path / "GEMINI.md").write_bytes(data)
    r = _tool("faf_gemini")(path=str(tmp_path / "project.faf"))
    assert r["success"] is False
    assert "not UTF-8" in r["error"]
    assert (tmp_path / "GEMINI.md").read_bytes() == data


# ── From the independent review of #45 ──────────────────────────────────

@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_review_f1_tool_refuses_link_into_git(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "project.faf").write_text(FAF, encoding="utf-8")
    git = tmp_path / ".git"
    git.mkdir()
    cfg = git / "config"
    cfg.write_text("[core]\n\tbare = false\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").symlink_to(cfg)
    r = _tool("faf_gemini")(path=str(tmp_path / "project.faf"))
    assert r["success"] is False
    assert cfg.read_text(encoding="utf-8") == "[core]\n\tbare = false\n"


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_review_f1_tool_refuses_link_out_of_the_project(tmp_path, monkeypatch):
    proj = tmp_path / "proj"
    proj.mkdir()
    monkeypatch.chdir(proj)
    (proj / "project.faf").write_text(FAF, encoding="utf-8")
    outside = tmp_path / "theirs.md"
    outside.write_text("theirs\n", encoding="utf-8")
    (proj / "AGENTS.md").symlink_to(outside)
    r = _tool("faf_agents")(path=str(proj / "project.faf"))
    assert r["success"] is False
    assert outside.read_text(encoding="utf-8") == "theirs\n"


def test_review_f2_info_string_line_does_not_close_a_fence(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text(
        f"```\nnot closed by the next line\n```bash\n{FAF_START}\nexample to keep\n{FAF_END}\n```\n\nTail.\n",
        encoding="utf-8",
    )
    inject_faf_block(p, "real block")
    out = p.read_text(encoding="utf-8")
    assert "example to keep" in out
    assert out.startswith(FAF_START + "\nreal block")


def test_review_f2_shorter_fence_inside_a_longer_one(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text(f"````md\n```\n{FAF_START}\nexample to keep\n{FAF_END}\n```\n````\n", encoding="utf-8")
    inject_faf_block(p, "real block")
    assert "example to keep" in p.read_text(encoding="utf-8")


@pytest.mark.skipif(os.name == "nt", reason="no Unix mode bits on Windows")
def test_review_f3_new_file_follows_the_umask(tmp_path):
    old = os.umask(0o022)
    try:
        p = tmp_path / "GEMINI.md"
        inject_faf_block(p, "block")
        assert oct(p.stat().st_mode & 0o777) == oct(0o644)
    finally:
        os.umask(old)


@pytest.mark.skipif(os.name == "nt", reason="no Unix mode bits on Windows")
def test_review_f5_read_only_file_refused_by_its_mode(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text("# Mine\n", encoding="utf-8")
    p.chmod(0o444)
    try:
        with pytest.raises(InjectRefused):
            inject_faf_block(p, "block")
        assert p.read_text(encoding="utf-8") == "# Mine\n"
    finally:
        p.chmod(0o644)


def test_review_f4_export_command_does_not_tell_the_model_to_write_files():
    toml = (Path(__file__).resolve().parent.parent / "commands" / "faf" / "export.toml").read_text(encoding="utf-8")
    assert "Write the content to" not in toml
    assert "Do not write `GEMINI.md` yourself" in toml


def test_review_f7_crlf_file_stays_crlf(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_bytes(b"# mine\r\nline two\r\n")
    inject_faf_block(p, "a\nb")
    data = p.read_bytes()
    assert b"\r\n" in data
    assert b"\n" not in data.replace(b"\r\n", b"")


def test_review_f9_block_containing_a_marker_line_is_refused(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text("# Mine\n", encoding="utf-8")
    with pytest.raises(InjectRefused):
        inject_faf_block(p, f"x\n{FAF_END}\ny")
    assert p.read_text(encoding="utf-8") == "# Mine\n"
