"""Server instructions: sent in initialize, short, and every tool they name is registered."""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp.client import Client  # noqa: E402

from server import SERVER_INSTRUCTIONS, mcp  # noqa: E402


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


async def test_initialize_carries_them(client):
    assert client.instructions == SERVER_INSTRUCTIONS


def test_under_1000_characters():
    assert len(SERVER_INSTRUCTIONS) < 1000


async def test_every_named_tool_is_registered(client):
    listed = {t.name for t in await client.list_tools()}
    named = set(re.findall(r"\bfaf_[a-z_]+", SERVER_INSTRUCTIONS))
    assert named
    assert sorted(named - listed) == []
