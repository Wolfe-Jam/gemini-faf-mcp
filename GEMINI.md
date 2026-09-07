<!-- faf:start -->
<!-- faf: gemini-faf-mcp | Python | mcp-server | MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI -->
<!-- faf: claim=project.faf | family=FAF -->

# GEMINI.md — gemini-faf-mcp

> Authored from project.faf — refresh with the `faf_gemini` MCP tool or `faf export --gemini`.

Project: gemini-faf-mcp
Goal: MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI
Language: Python

## Setup & build

```bash
pip install -e ".[dev]"    # install
python -m build    # build
```

## Test & verify

```bash
pytest -q
ruff check .
mypy server.py models.py safe_path.py inject.py src/
```

## Where things live

- `server.py — the FastMCP server, every @mcp.tool`
- `models.py — 15 reference project.faf templates for faf_model`
- `safe_path.py — confine_file_op, every write stays in the project root`
- `inject.py — non-destructive faf-managed-block injection`
- `src/gemini_faf_mcp/ — client.py + parser helpers over faf-python-sdk`
- `main.py — Cloud Run / functions-framework entry point`
- `tests/ — pytest, the WJTTC 9-tier suite`
- `pyproject.toml`

## Stack
- Backend: Python
- Main Language: Python
- Runtime: Python 3.11+
- Package Manager: pip
- Build: setuptools
- Database: BigQuery
- API: MCP (stdio) + HTTP/REST
- Connection: MCP (stdio) + HTTP/REST
- Testing: pytest + WJTTC 9-tier championship suite
- Hosting: Google Cloud Run
- CI/CD: GitHub Actions

## Before changing things

- Ask first: dependency installs, deletions, migrations, schema changes, publish/release.
- Never: force-push · push straight to `main` · commit secrets.
<!-- faf:end -->
