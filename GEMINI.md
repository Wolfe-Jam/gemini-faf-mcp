<!-- faf:start -->
<!-- faf: gemini-faf-mcp | Python | mcp-server | MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI -->
<!-- faf: claim=project.faf | family=FAF -->

# GEMINI.md — gemini-faf-mcp

> Authored from project.faf — refresh with `faf export --gemini`.

Project: gemini-faf-mcp
Goal: MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI
Language: Python

## Test & verify

```bash
pytest
```

## Where things live

- `pyproject.toml`
- `main.py`
- `README.md`

## Stack
- Backend: Python
- Main Language: Python
- Runtime: Python 3.10+
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
