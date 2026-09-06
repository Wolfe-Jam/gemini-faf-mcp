# AGENTS.md — gemini-faf-mcp

MCP server that gives Google Gemini persistent project context: it reads,
validates, auto-detects, scores, and exports IANA-registered `.faf` project
DNA, and unifies `CLAUDE.md` / `GEMINI.md` / `AGENTS.md`. Runs over stdio for
the Gemini CLI and as a stateless Streamable-HTTP service on Cloud Run
(fronted by the `mcpaas.live` edge).

## Project

- **Goal:** eliminate re-explaining your project every Gemini session — the
  `.faf` file is the answer key.
- **Who it's for:** Gemini CLI developers who want instant project context.
- **How it loads:** install the extension, run `/gemini-faf-mcp:setup`, and
  project DNA flows to Gemini through `GEMINI.md` every session.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"      # runtime + pytest / ruff / mypy
```

Python 3.10 or newer.

## Build

Packaging is `setuptools` via `pyproject.toml` — `server.py`, `models.py`,
`safe_path.py`, `inject.py` are top-level `py-modules`, `src/gemini_faf_mcp/`
is the package.

```bash
python -m build              # sdist + wheel (what pypi.yml / testpypi.yml ship)
```

The container is `pip install .` on `python:3.12-slim` (see `Dockerfile`);
Cloud Run injects `$PORT` and the server serves stateless Streamable HTTP.

## Test

```bash
pytest -q                    # 243 tests — the WJTTC 9-tier championship suite
ruff check .
mypy server.py models.py safe_path.py inject.py src/
```

CI runs all three on Python 3.10–3.13 plus `faf-cli check project.faf --strict`
for every push and PR to `main` (`.github/workflows/ci.yml`). PyPI and the MCP
Registry publish on a tag (`pypi.yml`, `publish-mcp-registry.yml` — DNS auth,
namespace `one.faf/gemini-faf-mcp`).

## Layout

| Path | What |
|---|---|
| `server.py` | the FastMCP server — every `@mcp.tool`, plus the transport wiring |
| `models.py` | 16 reference `project.faf` templates by project type, for `faf_model` |
| `safe_path.py` | `confine_file_op` — every file write is confined to the project root |
| `inject.py` | non-destructive faf-managed-block injection (Python twin of faf-cli's `inject.ts`) |
| `src/gemini_faf_mcp/client.py` | the HTTP/REST client surface |
| `src/gemini_faf_mcp/parser.py` | thin parse helpers over `faf-python-sdk` |
| `main.py` | Cloud Run / functions-framework entry point |
| `tests/` | pytest — `test_fastmcp_server.py`, `test_wjttc_mk4.py`, security path-confinement, write-guard, Dart detection |
| `agent.fafa` · `server.json` · `.well-known/ai-catalog.json` | identity + discovery surfaces |

## Conventions

- Parsing, validation, and scoring are `faf-python-sdk`'s job — `server.py`
  delegates, it never reimplements the Mk4 kernel.
- Every file write goes through `confine_file_op` (`safe_path.py`). No tool
  writes outside the project root.
- `ruff` (line length 120, `E/F/I/UP/B`) and `mypy` clean before commit.
- Conventional Commit messages (`feat:`, `fix:`, `chore:`, `test:`, `docs:`).
- Version must match across `pyproject.toml`, `src/gemini_faf_mcp/__init__.py`,
  `client.py`, `server.py`, `main.py`.

## Safety

- Branch off `main`; CI green before merge.
- No secrets in the repo. Cloud Run reads them from Secret Manager at runtime.
- Transports are passed to FastMCP **explicitly** — never rely on its default.

## Definition of done

`ruff check . && mypy … && pytest -q` all green, `faf-cli check project.faf
--strict` still Trophy, and — on a version bump — every version-bearing spot
moved together. If you changed the tool surface, update `README.md`, the
`gemini-extension.json` tool list, and `.well-known/ai-catalog.json`.

## Authoring this file

The `faf_agents` MCP tool (or `faf export --agents`) writes a faf-managed block
into `AGENTS.md` from `project.faf`, non-destructively — it never overwrites the
prose above. This file is maintained by hand; the tool keeps its block in sync.
