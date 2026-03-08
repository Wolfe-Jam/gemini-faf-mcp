# Setup Guide — gemini-faf-mcp

## Install

```bash
gemini extensions install https://github.com/Wolfe-Jam/gemini-faf-mcp
```

## First Run

Restart Gemini CLI after install. Verify the server is connected:

```bash
gemini mcp list
```

You should see:
```
✓ faf (from gemini-faf-mcp): ...run.sh (stdio) - Connected
```

**If Disconnected:** Quit Gemini CLI and restart. The MCP server connects at session start, not mid-session. If it stays disconnected, run `/trust` inside Gemini CLI to trust your workspace.

## Usage

From inside a project directory:

```bash
cd my-project
gemini
```

Then in Gemini CLI:

```
/gemini-faf-mcp:setup
```

This creates a `project.faf` file and scores it. If one already exists, it scores the existing file.

You can also use tools directly:

```
> Score my project.faf
> Export a GEMINI.md from my .faf
> What's in my project DNA?
```

## Important: Working Directory

Gemini CLI uses your shell's current directory. Always `cd` into your project before launching `gemini`. Running from `~` (home directory) will not find your project's `.faf` file.

```bash
# Good — inside a project
cd ~/my-project && gemini

# Bad — from home directory
gemini
```

## Commands

| Command | What It Does |
|---------|-------------|
| `/gemini-faf-mcp:setup` | Create or score project.faf |
| `/gemini-faf-mcp:score` | Quick score check with improvement suggestions |
| `/gemini-faf-mcp:export` | Export to GEMINI.md, AGENTS.md, or both |

## Troubleshooting

### Server shows "Disconnected"

Quit and restart Gemini CLI. The MCP server connects at startup.

### "Permission denied" writing files

Gemini CLI can only write within your workspace directories. Run `gemini` from inside your project, not from `/tmp` or other system paths.

### Tools not available

1. Run `/trust` to trust your workspace
2. Run `/mcp refresh` to reload tools
3. If still missing, restart Gemini CLI

### pytest-asyncio errors when running tests

Install dev dependencies first:

```bash
pip install -e ".[dev]"
```

This installs `pytest-asyncio` which is required for the MCP server tests. See `docs/SYS-REQS.md` for full environment setup.

## Dev Environment

```bash
# Clone and install
git clone https://github.com/Wolfe-Jam/gemini-faf-mcp
cd gemini-faf-mcp
pip install -e ".[dev]"

# Run MCP server tests (111 tests)
python -m pytest tests/test_fastmcp_server.py -v

# Run Cloud Run tests (57 tests, needs network)
python -m pytest tests/test_gemini_faf_mcp.py -v

# Run all (168 tests)
python -m pytest tests/ -v
```

## Requirements

- Python 3.10+
- Gemini CLI installed
- See `docs/SYS-REQS.md` for full requirements
