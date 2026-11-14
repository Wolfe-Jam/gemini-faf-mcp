<!-- faf:start -->
<!-- faf: gemini-faf-mcp | Python | mcp | MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI -->
<!-- faf: claim=project.faf | family=FAF -->

# CLAUDE.md — gemini-faf-mcp

## What This Is

MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI

## Stack

- **Language:** Python
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
- **Target User:** developers
- **Core Problem:** AI tools lack structured project context
- **Mission Purpose:** Give any AI structured project context via IANA-registered .faf files
- **Frameworks:** FastMCP,faf-python-sdk,functions-framework

## Context

- **Who:** Developers using Gemini in Antigravity CLI (or Gemini CLI on work accounts) who want instant, persistent project context
- **What:** MCP server that reads, validates, scores, and exports .faf project DNA
- **Why:** Eliminate re-explaining your project every Gemini session
- **Where:** Antigravity CLI plugin (agy plugin install), Gemini CLI extension, any MCP client via uvx
- **When:** Stable since Jan 2026; moving to Antigravity CLI
- **How:** Install the plugin, run the setup skill; Gemini reads project.faf through the faf tools

---

*STATUS: SYNC ACTIVE — 2026-11-14T05:56:10.851Z*
<!-- faf:end -->
