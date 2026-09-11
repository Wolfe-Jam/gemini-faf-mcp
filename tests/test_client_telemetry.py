"""FAFClient's start-up ping is opt-in. No network: requests.post is mocked."""

from unittest.mock import patch

import pytest

from gemini_faf_mcp import client as client_mod
from gemini_faf_mcp.client import FAFClient


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("FAF_TELEMETRY", raising=False)
    monkeypatch.delenv("FAF_TELEMETRY_OFF", raising=False)


def test_no_ping_by_default():
    with patch.object(client_mod.requests, "post") as post:
        FAFClient(local=True)
    post.assert_not_called()


def test_ping_when_opted_in(monkeypatch):
    monkeypatch.setenv("FAF_TELEMETRY", "1")
    with patch.object(client_mod.requests, "post") as post:
        FAFClient(local=True)
    post.assert_called_once()
    assert post.call_args.args[0] == client_mod.TELEMETRY_ENDPOINT
    assert post.call_args.kwargs["json"]["event"] == "client_init"


def test_off_wins_over_opt_in(monkeypatch):
    monkeypatch.setenv("FAF_TELEMETRY", "1")
    monkeypatch.setenv("FAF_TELEMETRY_OFF", "1")
    with patch.object(client_mod.requests, "post") as post:
        FAFClient(local=True)
    post.assert_not_called()
