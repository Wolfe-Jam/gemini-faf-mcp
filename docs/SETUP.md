# Setup Guide — gemini-faf-mcp

gemini-faf-mcp keeps your project's facts (stack, goal, commands) in one small YAML file, `project.faf`, and gives Gemini MCP tools to read it, score it and write `GEMINI.md` or `AGENTS.md` from it. This guide covers install, the first run, and fixes for common problems. For every tool with a real example, see [TOOLS.md](TOOLS.md).

## Install in Antigravity CLI

Antigravity CLI (`agy`) is Google's successor to Gemini CLI ([announcement](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)). Install gemini-faf-mcp as a plugin:

```bash
agy plugin install https://github.com/Wolfe-Jam/gemini-faf-mcp
```

The plugin brings the MCP server and three skills: `/setup`, `/score` and `/export`. Check it's there:

```bash
agy plugin list
```

## Move from Gemini CLI to Antigravity

If you already have the Gemini CLI extension, convert it:

```bash
agy plugin import gemini
```

If the import stops on `.gemini/project.faf` (a link that versions up to 3.2.0 shipped), remove it and run the import again:

```bash
rm -f ~/.gemini/extensions/gemini-faf-mcp/.gemini/project.faf
agy plugin import gemini
```

## Install in Gemini CLI (work accounts)

```bash
gemini extensions install https://github.com/Wolfe-Jam/gemini-faf-mcp
```

The skills are `/faf:setup`, `/faf:score` and `/faf:export` in Gemini CLI.

## Install in any other MCP client

gemini-faf-mcp is a standard stdio MCP server on PyPI. No account needed:

```json
{ "mcpServers": { "gemini-faf": { "command": "uvx", "args": ["gemini-faf-mcp==3.3.1"] } } }
```

Claude Code:

```bash
claude mcp add gemini-faf-mcp -- uvx gemini-faf-mcp==3.3.1
```

## First run: create project.faf with /setup

Start `agy` inside your project folder, then run the setup skill:

```bash
cd ~/my-project && agy
```

```
/setup
```

`/setup` looks for a `project.faf` in this folder. If there isn't one, it detects your stack from the repo's own files (`pyproject.toml`, `package.json`, `docker-compose`, `Makefile` and others) and writes `project.faf`. On a small FastAPI project it shows:

```
Created: project.faf
Detected: Python/FastAPI
Score: 42% (RED)

Fill in what only you know: the goal, who it's for, and why it exists.
Suggested goal: A small weather API
```

The goal and the six W's (who, what, why, where, when, how) are yours to write: `/setup` never fills them in. A description it finds, such as the one in `pyproject.toml`, is shown as a suggestion only. A RED score on a new project is normal until you add them.

If `project.faf` already exists, `/setup` scores it instead and lists what's missing.

## Check your score with /score

```
/score
```

It shows the score and the tier, lists any errors and warnings, and below 85% (Bronze) suggests what to fill in next. 100% is Trophy ✪: every slot your kind of project needs is filled.

## Write GEMINI.md or AGENTS.md with /export

```
/export
```

It asks which file to write (`GEMINI.md`, `AGENTS.md` or both), then writes its own block from `project.faf` and keeps anything you wrote outside that block.

## Ask in plain words

The tools also answer ordinary requests:

```
> Score my project.faf
> Fill in project.faf from this repo
> Write a GEMINI.md from my project.faf
> What's in my project.faf?
```

## Working directory: start agy in your project

Start `agy` from your project folder. Antigravity starts the plugin's server in the plugin's own folder; the server finds your project from the folder you ran `agy` in.

```bash
# Good: inside the project
cd ~/my-project && agy

# Not this: from your home folder
cd ~ && agy
```

From your home folder (or `/`), the server stays in its plugin folder and refuses writes, so it can never write outside a project.

## Troubleshooting

### The faf tools aren't available

Check the plugin is installed and enabled, then start a new `agy` session (MCP servers connect at session start):

```bash
agy plugin list
agy plugin enable gemini-faf-mcp
```

### The first start is slow on an Intel Mac

The first start installs the server's Python dependencies. On an Intel Mac, one of them (cryptography, since 49.0) has no prebuilt wheel and compiles once, which can take a few minutes. Apple silicon, Linux and Windows get prebuilt wheels. Later starts are fast.

### An update doesn't show up right after a release

uv caches PyPI's index for a few minutes, so a release published minutes ago can still start the previous version. Wait a few minutes, or refresh once:

```bash
uvx --refresh --from "gemini-faf-mcp>=3.2.1" python -I -X utf8 -m server --version
```

### "Security error: path escapes" when writing

The server only writes inside your project (or the folders in `FAF_ALLOWED_ROOTS`). Start `agy` from your project folder, or pass a path inside it.

### Windows

Not tested yet. Windows shells usually don't set the working-folder variable the server uses to find your project, so it may stay in its plugin folder.

### Gemini CLI: server shows "Disconnected"

Quit and restart Gemini CLI: the MCP server connects at startup. If it stays disconnected, run `/trust` in Gemini CLI to trust your workspace, then `/mcp refresh`.

## Working on gemini-faf-mcp itself

Clone, dev install and the test suite are in [CONTRIBUTING.md](../CONTRIBUTING.md).

## Requirements

- Python 3.11+ and [uv](https://docs.astral.sh/uv/) (for `uvx`)
- Antigravity CLI, Gemini CLI, or any MCP client
- See [SYS-REQS.md](SYS-REQS.md) for full requirements
