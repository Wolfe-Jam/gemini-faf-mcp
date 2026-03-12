# AGENTS.md — gemini-faf-mcp

## Project
- **Name:** gemini-faf-mcp
- **Goal:** MCP server for FAF — read, validate, auto-detect, score, and export IANA-registered .faf project DNA from Gemini CLI
- **Language:** Python
- **FAF Score:** 100%

## Instructions for AI Agents
- This project uses FAF (Foundational AI-context Format)
- Read project.faf for complete project DNA
- Media Type: application/vnd.faf+yaml (IANA registered)

## Context
- **Who:** Gemini CLI developers who want instant project context
- **What:** MCP server that reads, validates, scores, and exports .faf project DNA
- **Why:** Eliminate re-explaining your project every Gemini session

## Stack
- **Frontend:** N/A
- **Backend:** Python FastMCP
- **Database:** BigQuery
- **Testing:** pytest + WJTTC 9-tier championship suite
