"""
Security regression — arbitrary local-file read/write via unconfined `path`.

Mirrors the disclosure reproduced against the grok-faf-mcp sibling (Zhihao
Zhang, WPI): caller `path` arguments reached Path(path).read_text() /
.write_text() with no confinement (CWE-22/73/200), so absolute/`..` paths read
secrets (faf_read/faf_score/...) and faf_init could write any file.

Boundary under test (safe_path.py): the read tools only ever read .faf/.fafm
context files; faf_init is confined to the project root(s). Escapes are refused.
"""
import json
import os
import tempfile

import pytest
from fastmcp import Client

from server import mcp
from safe_path import confine_path, confine_file_op, PathConfinementError, is_faf_context_file


def _parse(result):
    if hasattr(result, "data") and isinstance(result.data, dict):
        return result.data
    return json.loads(result[0].text)


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


@pytest.fixture
def secret(tmp_path):
    p = tmp_path / "fake_id_rsa"
    p.write_text("SECRET-DO-NOT-LEAK fake-private-key\n")
    return str(p)


# --- unit: confine_path / confine_file_op ---

class TestConfineUnit:
    def test_refuses_etc_passwd(self):
        with pytest.raises(PathConfinementError):
            confine_path("/etc/passwd")

    def test_refuses_traversal(self):
        with pytest.raises(PathConfinementError):
            confine_path("../../../../../../etc/passwd")

    def test_refuses_existing_secret(self, secret):
        with pytest.raises(PathConfinementError):
            confine_path(secret)

    def test_refuses_faf_symlink_to_secret(self, tmp_path, secret):
        link = tmp_path / "evil.faf"
        link.symlink_to(secret)
        with pytest.raises(PathConfinementError):
            confine_path(str(link))

    def test_allows_real_faf(self, tmp_path):
        faf = tmp_path / "project.faf"
        faf.write_text("project:\n  name: ok\n")
        assert confine_path(str(faf)).name == "project.faf"

    def test_file_op_refuses_home_secret(self):
        with pytest.raises(PathConfinementError):
            confine_file_op(os.path.expanduser("~/.bashrc"))

    def test_is_faf_context_file(self):
        from pathlib import Path
        assert is_faf_context_file(Path("/x/project.faf"))
        assert is_faf_context_file(Path("/x/.faf"))
        assert not is_faf_context_file(Path("/etc/passwd"))


# --- tool layer: the PoC must not leak / write ---

class TestToolConfinement:
    async def test_faf_read_etc_passwd_refused(self, client):
        result = await client.call_tool("faf_read", {"path": "/etc/passwd"})
        data = _parse(result)
        assert data.get("success") is False
        assert "root:" not in json.dumps(data)

    async def test_faf_score_secret_refused(self, client, secret):
        result = await client.call_tool("faf_score", {"path": secret})
        data = _parse(result)
        # faf_score has its own error shape; the invariant is no leak + no success.
        assert data.get("success") is not True
        assert "SECRET-DO-NOT-LEAK" not in json.dumps(data)

    async def test_faf_init_outside_root_refused(self, client):
        target = os.path.expanduser("~/.gemfaf_should_not_be_written.faf")
        result = await client.call_tool("faf_init", {"name": "x", "path": target})
        data = _parse(result)
        assert data.get("success") is False
        assert not os.path.exists(target)
