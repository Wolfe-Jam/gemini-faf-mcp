#!/usr/bin/env bash
# Self-bootstrapping wrapper for gemini-faf-mcp MCP server
# Creates a venv and installs dependencies on first run
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV" >&2
  "$VENV/bin/pip" install --quiet "$DIR" >&2   # installs from pyproject.toml — all runtime deps
fi
exec "$VENV/bin/python3" "$DIR/server.py"
