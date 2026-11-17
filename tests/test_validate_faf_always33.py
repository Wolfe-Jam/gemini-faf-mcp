"""validate_faf gives the always-33 number, the same as faf_score and faf-cli.

It used to count its own 10 slots "against v2.5.2". Reviews of #64 (goose, claude.ai)
found: issues/valid disagreeing with the score, a silent 0 on unusual input, duplicate
keys scoring where faf-cli refuses the file, and tests that compared the code with itself.
These tests compare a file's TEXT with validate_faf(parse_faf(file)) and with the faf_score tool.
"""

import collections
import decimal
import enum
import json
import pathlib

import pytest
import yaml
from faf_sdk import score_faf
from fastmcp.client import Client

from gemini_faf_mcp import parse_faf, validate_faf
from server import mcp

W = ("who", "what", "why", "where", "when", "how")

FILES = {
    "basics": 'faf_version: "3.0"\nproject:\n  name: weather-api\n  goal: Weather by city\n  main_language: Python\n'
    "human_context:\n" + "".join(f"  {w}: real {w}\n" for w in W),
    "stack": 'faf_version: "3.0"\nproject:\n  name: w\n  goal: g\n  main_language: Python\n'
    "stack:\n  backend: FastAPI\n  frontend: slotignored\n  testing: pytest\n",
    "placeholders": 'faf_version: "3.0"\nproject:\n  name: tbd\n  goal: n/a\n  main_language: unknown\n'
    "human_context:\n" + "".join(f"  {w}: todo\n" for w in W),
    "yaml11": "project:\n  name: x\n  goal: 'yes'\nhuman_context:\n  who: no\n  when: 2026-11-16\n",
}


def _write(tmp_path, name, text):
    p = tmp_path / f"{name}.faf"
    p.write_text(text, encoding="utf-8")
    return p


@pytest.mark.parametrize("name", list(FILES))
def test_same_number_as_the_files_text(tmp_path, name):
    text = FILES[name]
    k = score_faf(text)
    r = validate_faf(parse_faf(str(_write(tmp_path, name, text))))
    assert (r["score"], r["tier"], r["populated"], r["active"]) == (k.score, k.tier, k.populated, k.active)


def _data(res):
    return res.data if isinstance(getattr(res, "data", None), dict) else json.loads(res.content[0].text)


@pytest.mark.parametrize("name", list(FILES))
async def test_same_as_the_faf_score_and_faf_validate_tools(tmp_path, name):
    p = _write(tmp_path, name, FILES[name])
    async with Client(transport=mcp) as c:
        score = _data(await c.call_tool("faf_score", {"path": str(p)}))
        valid = _data(await c.call_tool("faf_validate", {"path": str(p)}))
    r = validate_faf(parse_faf(str(p)))
    assert (r["score"], r["tier"]) == (score["score"], score["tier"])
    assert r["valid"] == valid["valid"]


def test_issues_list_every_empty_slot():
    r = validate_faf(yaml.safe_load(FILES["placeholders"]))
    assert r["score"] == 0
    assert "Missing or placeholder: project.name" in r["issues"]
    assert "Missing or placeholder: human_context.who" in r["issues"]
    empty = [i for i in r["issues"] if i.startswith("Missing or placeholder:")]
    assert len(empty) == r["active"] - r["populated"]


@pytest.mark.parametrize(
    "keys",
    ["yes: 1\ntrue: 2\n", "Yes: 1\nyes: 2\n", "on: push\ntrue: 2\n", "1: a\ntrue: b\n",
     "1_000: a\n1000: b\n", "010: a\n8: b\n"],
)
def test_parse_faf_accepts_what_the_kernel_accepts(tmp_path, keys):
    text = FILES["basics"] + keys
    k = score_faf(text)
    assert k.score > 0
    r = validate_faf(parse_faf(str(_write(tmp_path, "keys", text))))
    assert (r["score"], r["tier"]) == (k.score, k.tier)


def test_merge_keys_still_load(tmp_path):
    text = "base: &b\n  name: x\nproject:\n  <<: *b\n  name: y\n"
    assert parse_faf(str(_write(tmp_path, "merge", text)))["project"]["name"] == "y"


@pytest.mark.parametrize(
    "extra",
    [{"x": pathlib.Path("/a")}, {"x": decimal.Decimal("1.5")}, {"x": type("S", (str,), {})("s")}],
)
def test_unusual_values_do_not_move_the_score(extra):
    base = {"faf_version": "3.0", "project": {"name": "x", "goal": "g", "main_language": "Python"}}
    assert validate_faf({**base, **extra})["score"] == validate_faf(base)["score"] > 0


def test_mapping_subclasses_score_like_dicts():
    plain = {"project": {"name": "x", "goal": "g", "main_language": "Python"}}
    od = {"project": collections.OrderedDict(plain["project"])}
    dd = {"project": collections.defaultdict(str, plain["project"])}
    assert validate_faf(od)["score"] == validate_faf(dd)["score"] == validate_faf(plain)["score"] > 0


@pytest.mark.parametrize("bad", [None, [], "text"])
def test_non_mapping_is_an_issue_not_a_crash(bad):
    r = validate_faf(bad)
    assert r["valid"] is False and r["issues"][0].startswith("Could not score: expected a mapping")


def test_self_reference_is_an_issue_not_a_silent_zero():
    d: dict = {}
    d["self"] = d
    r = validate_faf(d)
    assert r["valid"] is False and r["issues"] == ["Could not score: the data refers to itself"]


def test_total_slots_is_active_and_can_be_zero():
    k = score_faf("project:\n  name: x\n")
    r = validate_faf({"project": {"name": "x"}})
    assert r["total"] == 33 and r["total_slots"] == r["active"] == k.active
    slots = [s for s, _ in score_faf("{}").slots]
    tree: dict = {}
    for slot in slots:
        a, b = slot.split(".")
        tree.setdefault(a, {})[b] = "slotignored"
    z = validate_faf(tree)
    assert z["total_slots"] == z["active"] == 0


def test_str_enum_keys_score_like_plain_keys():
    class K(str, enum.Enum):  # noqa: UP042 — the str + Enum case the recheck found
        P = "project"

    assert validate_faf({K.P: {"name": "x"}})["score"] == validate_faf({"project": {"name": "x"}})["score"] > 0


@pytest.mark.parametrize("empty", [b"", collections.deque(), range(0)])
def test_empty_unusual_values_stay_empty(empty):
    assert validate_faf({"project": {"name": empty}})["populated"] == 0


@pytest.mark.parametrize("extra", [{"note": "\ud83c"}, {"0o14": "a", 12: "b"}, {"1e3": "a", 1000.0: "b"}])
def test_data_the_kernel_cannot_read_is_reported(extra):
    base = yaml.safe_load(FILES["basics"])
    r = validate_faf({**base, **extra})
    assert r["valid"] is False and r["issues"] == ["Could not score: the kernel could not read the data"]


def test_missing_faf_version_is_invalid_as_in_faf_validate():
    r = validate_faf({"project": {"name": "x"}})
    assert r["valid"] is False
    assert "Missing required field: faf_version" in r["issues"]
