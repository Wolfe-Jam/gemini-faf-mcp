"""
WJTTC — Dart/Flutter detection wiring (gemini-faf-mcp).

Tier 6: CONTRACT (Parity) — gemini DELEGATES Dart detection to the SDK
(faf_sdk.detect_dart_project); it does NOT fork pubspec parsing. This is the
fix for the drift Randal Schwartz exposed: a pubspec was invisible to the MCP.
Now the .faf-bound `detected` dict reflects the SDK's classification, and the
SDK is the single source (faf-cli src/detect/dart.ts <-> faf_sdk/detect.py).
"""

import sys
from pathlib import Path
from typing import Dict

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from server import _detect_stack, FRONTEND_FRAMEWORKS, BACKEND_FRAMEWORKS
from faf_sdk import detect_dart_project


def _write(d: Path, files: Dict[str, str]) -> None:
    for rel, content in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def test_flutter_app_detected(tmp_path):
    _write(tmp_path, {
        "pubspec.yaml": (
            "name: my_app\n"
            "description: A demo app\n"
            "version: 1.2.0+3\n"
            "dependencies:\n  flutter:\n    sdk: flutter\n  flutter_riverpod: ^2.5.0\n"
            "dev_dependencies:\n  flutter_test:\n    sdk: flutter\n"
        ),
        "lib/main.dart": "",
    })
    d = _detect_stack(str(tmp_path))
    assert d["main_language"] == "Dart"
    assert d["package_manager"] == "pub"
    assert d["framework"] == "Flutter"
    assert d["testing"] == "flutter_test"
    assert d["name"] == "my_app"
    assert d["version"] == "1.2.0+3"
    assert d["goal"] == "A demo app"
    assert "Flutter" in FRONTEND_FRAMEWORKS  # lands in the frontend slot


def test_dart_mcp_server_detected(tmp_path):
    _write(tmp_path, {"pubspec.yaml": "name: my_mcp\ndependencies:\n  dart_mcp: ^0.2.0\n"})
    d = _detect_stack(str(tmp_path))
    assert d["main_language"] == "Dart"
    assert d["api_type"] == "MCP"
    assert "framework" not in d  # an MCP server has no UI/web framework slot


def test_dart_backend_detected(tmp_path):
    _write(tmp_path, {"pubspec.yaml": "name: my_api\ndependencies:\n  serverpod: ^2.1.0\n"})
    d = _detect_stack(str(tmp_path))
    assert d["main_language"] == "Dart"
    assert d["framework"] == "Serverpod"
    assert d["api_type"] == "REST"
    assert "Serverpod" in BACKEND_FRAMEWORKS  # lands in the backend slot


def test_pure_dart_package_is_not_flutter(tmp_path):
    # The drift Randal exposed: a pure-Dart package must NOT read as Flutter.
    _write(tmp_path, {"pubspec.yaml": "name: my_pkg\ndependencies:\n  meta: ^1.12.0\n"})
    d = _detect_stack(str(tmp_path))
    assert d["main_language"] == "Dart"
    assert d.get("framework") != "Flutter"
    assert "framework" not in d  # a library has no framework slot


@pytest.mark.parametrize("body,files", [
    ("name: a\ndependencies:\n  flutter:\n    sdk: flutter\n", {"lib/main.dart": ""}),
    ("name: b\ndependencies:\n  serverpod: ^2.0.0\n", {}),
    ("name: c\ndependencies:\n  dart_mcp: ^0.2.0\n", {}),
    ("name: d\ndependencies:\n  meta: ^1.0.0\n", {}),
])
def test_delegates_to_sdk_no_fork(tmp_path, body, files):
    # CONTRACT: gemini's framework value IS the SDK's framework value — same brain.
    _write(tmp_path, {"pubspec.yaml": body, **files})
    d = _detect_stack(str(tmp_path))
    dp = detect_dart_project(str(tmp_path))
    assert dp is not None
    # empty SDK framework => gemini omits the key (so default to "")
    assert d.get("framework", "") == dp.framework
