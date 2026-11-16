# Tools — gemini-faf-mcp

gemini-faf-mcp has 13 MCP tools. Every example below is real output from gemini-faf-mcp 3.3.1, run on a small FastAPI project (`pyproject.toml` with `fastapi`, `uvicorn` and `pytest`). Long output is shortened where marked, and the project path is shown as `/path/to/weather-api`.

Every `path` argument defaults to `project.faf` and must stay inside your project. Read-only tools: `faf_read`, `faf_validate`, `faf_score`, `faf_discover`, `faf_stringify`, `faf_context`, `faf_about`, `faf_model`. Tools that write: `faf_init`, `faf_auto`, `faf_gemini`, `faf_agents`, `faf_migrate`. None of them reaches the network.

## Create project.faf from your repo: faf_auto

Detects the stack from the repo's own files and writes `project.faf`. On an existing file it fills only empty slots, never a value you set. It never writes the goal or the six W's: a description it finds is returned as `suggested.goal` for you to confirm.

```json
{ "directory": "." }
```

```json
{
  "success": true,
  "path": "/path/to/weather-api/project.faf",
  "created": true,
  "written": [],
  "not_written": {},
  "suggested": { "goal": "A small weather API" },
  "detected": {
    "main_language": "Python",
    "package_manager": "pip",
    "build_tool": null,
    "framework": "FastAPI",
    "api_type": "REST",
    "database": null,
    "cache": null,
    "search": null,
    "hosting": null,
    "commands": null
  },
  "score": 42,
  "tier": "RED",
  "message": "Detected Python/FastAPI Created project.faf at 42%. Suggested goal (confirm before adding): A small weather API"
}
```

## Fill an existing project.faf: faf_auto on a file that exists

`written` lists the slots it filled. Here the file came from `faf_init`, which leaves the stack empty:

```json
{
  "written": ["main_language", "backend", "testing"],
  "not_written": {},
  "message": "Detected Python/FastAPI Updated project.faf at 9%: wrote main_language, backend, testing. Suggested goal (confirm before adding): A small weather API"
}
```

(shortened to the three fields that change)

## See what faf_auto skipped: not_written

A slot you set yourself, including `slotignored`, is never overwritten. `not_written` says what was detected and what the slot holds:

```json
{
  "written": [],
  "not_written": { "backend": { "detected": "FastAPI", "current": "slotignored" } },
  "message": "Detected Python/FastAPI ig.faf unchanged at 6%: no empty slot for what was detected. Suggested goal (confirm before adding): A small weather API Not written (slot already set): backend is slotignored, detected FastAPI."
}
```

(shortened)

## Create a starter file by hand: faf_init

Writes a starter `.faf` with the name, goal and language you pass. It never overwrites an existing file. Stack slots and the six W's start empty; use `faf_auto` next to fill the stack.

```json
{ "name": "notes-app", "goal": "Keep meeting notes searchable", "language": "TypeScript", "path": "notes.faf" }
```

```json
{
  "success": true,
  "path": "/path/to/weather-api/notes.faf",
  "message": "Created notes.faf — edit to match your project"
}
```

## Check the score: faf_score

The same always-33 score as faf-cli: populated slots out of the active ones (slotignored slots don't count against you).

```json
{}
```

```json
{ "score": 42, "tier": "RED", "populated": 5, "active": 12, "total": 33 }
```

Tiers: 100% Trophy ✪ · 99% Gold · 95% Silver · 85% Bronze · 70% Green · 55% Yellow · below 55% Red · 0% White.

## Validate the file: faf_validate

The score plus errors and warnings.

```json
{
  "success": true,
  "valid": true,
  "score": 42,
  "tier": "RED",
  "populated": 5,
  "active": 12,
  "total": 33,
  "errors": [],
  "warnings": ["Missing recommended section: instant_context"]
}
```

## Find project.faf: faf_discover

Walks up from `start_dir` (default: the current folder) to the nearest `.faf` file.

```json
{
  "found": true,
  "path": "/path/to/weather-api/project.faf",
  "searched_from": "/path/to/weather-api"
}
```

## Read the whole file: faf_read

Returns the parsed structure.

```json
{
  "success": true,
  "path": "project.faf",
  "data": {
    "faf_version": "3.0",
    "project": { "name": "weather-api", "goal": "", "main_language": "Python" },
    "stack": { "backend": "FastAPI", "api_type": "REST", "package_manager": "pip", "testing": "pytest" }
  }
}
```

(shortened: `stack` also lists the slotignored slots, and the other sections follow)

## Get Gemini-ready context: faf_context

The sections an AI needs first: project, score, human context, stack.

```json
{
  "success": true,
  "context": {
    "project": { "name": "weather-api", "goal": "", "language": "Python" },
    "score": 42,
    "tier": "RED",
    "human_context": { "who": "", "what": "", "why": "" },
    "stack": { "frontend": "slotignored", "backend": "FastAPI", "database": "slotignored", "testing": "pytest" }
  }
}
```

## Get the file as YAML: faf_stringify

```json
{
  "success": true,
  "yaml": "faf_version: '3.0'\nproject:\n  name: weather-api\n  goal: ''\n  main_language: Python\nstack:\n  frontend: slotignored\n  ..."
}
```

(shortened)

## Write GEMINI.md: faf_gemini

Writes its own block into `GEMINI.md` from `project.faf` and keeps everything you wrote outside it. It refuses a file it can't write safely (not UTF-8, or a link out of the project) and says why.

```json
{
  "success": true,
  "path": "/path/to/weather-api/GEMINI.md",
  "score": 42,
  "tier": "RED",
  "message": "GEMINI.md updated — faf block written, the rest of the file kept"
}
```

The block it wrote (from `content`, shortened):

```markdown
# GEMINI.md — weather-api

Project: weather-api
Language: Python

## Stack
- Backend: FastAPI
- API: REST
- Package Manager: pip
- Testing: pytest
```

## Write AGENTS.md: faf_agents

The same for `AGENTS.md`: conventions, guardrails, definition of done. Your own text outside the block is kept.

```markdown
# AGENTS.md — weather-api

## Conventions

- **Quality Bar:** zero_errors
- **Testing:** required

## Guardrails

- **Always OK:** read the tree.
- **Ask first:** dependency installs, deletions, migrations, schema changes, publish/release.
- **Never:** force-push · push straight to `main` (branch and open a PR) · commit secrets.
```

(shortened)

## Bring an old file up to date: faf_migrate

Moves a `.faf` to the current format (3.0). Use `dry_run` to see what would change first.

```json
{ "dry_run": true }
```

```json
{ "success": true, "changed": false, "message": "Already at faf_version 3.0" }
```

## Get a complete example: faf_model

A 100% Trophy example `.faf` for a project type. Unknown types return an error that lists the available ones (`mcp-server`, `web-app`, `saas`, and more).

```json
{ "project_type": "mcp-server" }
```

```json
{
  "type": "mcp-server",
  "description": "MCP server for AI tool integration (stdio or HTTP)",
  "covers": ["MCP servers", "Gemini extensions", "Claude tools", "AI integrations"],
  "faf": "faf_version: \"3.0\"\nproject:\n  name: \"weather-mcp\"\n  goal: \"Real-time weather data for AI assistants via MCP tools\"\n  ..."
}
```

(shortened)

## About the format: faf_about

```json
{
  "name": "FAF (Foundational AI-context Format)",
  "media_type": "application/vnd.faf+yaml",
  "iana_registered": true,
  "spec": "https://faf.one",
  "server": "gemini-faf-mcp",
  "server_version": "3.3.1",
  "tools": 13
}
```

(shortened: the ecosystem and tier list follow)

## Errors

A failure comes back as an MCP error (`isError: true`) with the reason:

```json
{ "path": "missing.faf" }
```

```json
{ "success": false, "error": "File not found: missing.faf" }
```
