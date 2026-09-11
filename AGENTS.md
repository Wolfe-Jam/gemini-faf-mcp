<!-- faf:start -->
<!-- faf: gemini-faf-mcp | Python | mcp-server | MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI -->
<!-- faf: claim=project.faf | family=FAF -->

# AGENTS.md — gemini-faf-mcp

MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI — Python · type: mcp-server · v2.8.2

> Authored by faf — do not edit the managed block; refresh with `faf export --agents` or the `faf_agents` MCP tool. Hand-written content outside it is preserved.

## Setup & build

```bash
pip install -e ".[dev]"    # install
python -m build    # build
```

## Run the tests

```bash
pytest -q
ruff check .
mypy server.py models.py safe_path.py inject.py src/
```

## Where things live

| Path | Role |
|------|------|
| `server.py` | the FastMCP server, every @mcp.tool |
| `models.py` | 15 reference project.faf templates for faf_model |
| `safe_path.py` | confine_file_op, every write stays in the project root |
| `inject.py` | non-destructive faf-managed-block injection |
| `interrogate.py` | Full-Facts grounding for faf_auto (docker-compose + Makefile signals) |
| `src/gemini_faf_mcp/` | client.py + parser helpers over faf-python-sdk |
| `main.py` | Cloud Run / functions-framework entry point |
| `tests/` | pytest, the WJTTC 9-tier suite |
| `pyproject.toml` |  |

## Conventions

- **Quality Bar:** zero_errors
- **Testing:** required

## Guardrails

- All changes must pass 245 tests before commit
- faf-python-sdk handles parsing — server.py delegates
- Version must match in pyproject.toml, __init__.py, client.py, server.py, main.py
- **Always OK:** read the tree · run the tests (`pytest -q`) · build the project · `ruff check .`.
- **Ask first:** dependency installs, deletions, migrations, schema changes, publish/release.
- **Never:** force-push · push straight to `main` (branch and open a PR) · commit secrets.

## Definition of Done

Done when: `ruff check .` exits 0 · `mypy server.py models.py safe_path.py inject.py src/` exits 0 · `pytest -q` passes · changes committed with a conventional message.

## When stuck

Ask a clarifying question, propose a short plan, or open a draft PR with notes — do not push large speculative changes to `main`.

## Commit & PR

- Commit style: conventional
- Branch off `main` and open a PR — never commit to `main` directly.
- If build/test scripts or layout change, refresh this file in the **same PR**.

## Stack

- **Backend:** Python
- **Main Language:** Python
- **Runtime:** Python 3.11+
- **Package Manager:** pip
- **Build:** setuptools
- **Database:** BigQuery
- **API:** MCP (stdio) + HTTP/REST
- **Connection:** MCP (stdio) + HTTP/REST
- **Testing:** pytest + WJTTC 9-tier championship suite
- **Hosting:** Google Cloud Run
- **CI/CD:** GitHub Actions

*Context authored: 2026-08-20 15:59:03+00:00*
<!-- faf:end -->


## Notes faf can't know

- **Deploy:** `Dockerfile` -> Cloud Run (`pip install .`, stateless Streamable
  HTTP on $PORT). The `mcpaas.live` edge fronts it as the tool executor.
- **faf-python-sdk does the work.** Parsing, validation, scoring, and the
  AGENTS.md / GEMINI.md authoring all live in `faf_sdk` — `server.py` wires
  tools to it, never reimplements.
- **Publish:** PyPI + MCP Registry on a `v*` tag (DNS auth, namespace
  `one.faf/gemini-faf-mcp`).
