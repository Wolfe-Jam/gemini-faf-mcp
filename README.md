# gemini-faf-mcp 🏆🍊

[![.faf Status](https://img.shields.io/badge/.faf-100%25%20Elite-orange?style=for-the-badge&logo=google-gemini)](https://github.com/Wolfe-Jam/gemini-faf-mcp)
[![DNA Integrity](https://img.shields.io/badge/Security-SW--02%20Locked-red?style=for-the-badge)](https://github.com/Wolfe-Jam/gemini-faf-mcp)
[![Tests](https://img.shields.io/badge/Tests-36%2F36-brightgreen?style=for-the-badge)](https://github.com/Wolfe-Jam/gemini-faf-mcp)

> **AI AGENT INSTRUCTIONS:** This repository utilizes the **.faf (Foundational AI-context Format)** v2.5.1 standard.
> 1. **HANDSHAKE:** Locate `project.faf` in the root directory before processing context.
> 2. **SOURCE OF TRUTH:** Adhere to the '77 Reds motivation anchor.
> 3. **GLORY STATUS:** Verification score: **100.0%**. Elite status confirmed.
>
> *"Efficiency is the goal, but we play for the 🏆, and revel in the 🍊. YNWA."*

---

![FAF Status](https://us-east1-bucket-460122.cloudfunctions.net/faf-source-of-truth)

Google Cloud Function for FAF (Foundational AI-context Format) integration with Gemini.

**Version:** 2.5.1 | **Tests:** 36/36 (Championship Grade)

## What This Does

Provides a "Source of Truth" endpoint that Gemini can call to retrieve project DNA from `.faf` files.

**Live Endpoint:**
```
https://faf-source-of-truth-631316210911.us-east1.run.app
```

## The FAF Ecosystem

| Package | Platform | Status |
|---------|----------|--------|
| [claude-faf-mcp](https://npmjs.com/package/claude-faf-mcp) | Anthropic | Live (#2759) |
| [grok-faf-mcp](https://npmjs.com/package/grok-faf-mcp) | xAI | Live |
| **gemini-faf-mcp** | Google | Live |

## Usage

### Test the Endpoint

```bash
# Default response (full JSON)
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "Content-Type: application/json" \
  -d '{"path": "project.faf"}'
```

## Multi-Agent Handshake

The endpoint acts as a **Context Broker** - it speaks different AI dialects.

### How It Works

Send a request with your AI's identity, get back optimized payload:

```bash
# Claude: Gets XML with thinking blocks
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "X-FAF-Agent: claude" \
  -H "Content-Type: application/json"

# Jules: Gets minimal JSON (token-efficient)
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "X-FAF-Agent: jules" \
  -H "Content-Type: application/json"

# Grok: Gets direct, action-oriented JSON
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "X-FAF-Agent: grok" \
  -H "Content-Type: application/json"
```

### Agent Dialects

| Agent | Format | Philosophy |
|-------|--------|------------|
| **Claude** | XML | Full depth, thinking blocks |
| **Gemini** | Structured JSON | Prioritized sections |
| **Grok** | Direct JSON | Action-oriented |
| **Jules** | Minimal JSON | Token-efficient |
| **Codex/Copilot/Cursor** | Code-focused JSON | Stack & patterns |
| **Unknown** | Full JSON | Complete payload |

### Response Headers

Every response includes:
```
X-FAF-Agent-Detected: <detected-agent>
```

This lets you verify which dialect was applied.

## Voice-to-FAF

Update your project DNA by voice through Gemini Live.

### How It Works

```
You (speaking): "Set the project focus to IETF submission"
     ↓
Gemini Live → Cloud Function (PUT) → GitHub API → Commit
     ↓
Cloud Build triggers → Function redeployed → Badge updates
```

### API Usage

```bash
# Update DNA fields (supports dot notation)
curl -X PUT https://us-east1-bucket-460122.cloudfunctions.net/faf-source-of-truth \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "state.focus": "IETF Draft Submission",
      "state.phase": "review"
    },
    "message": "voice-sync: pivoting to IETF focus"
  }'
```

### Response

```json
{
  "success": true,
  "message": "voice-sync: pivoting to IETF focus",
  "sha": "abc123...",
  "url": "https://github.com/Wolfe-Jam/gemini-faf-mcp/blob/main/project.faf",
  "updates_applied": ["state.focus", "state.phase"],
  "security": {"sw01": "passed", "sw02": "passed"}
}
```

## Security (v2.5.1)

### SW-01: Temporal Integrity
Rejects mutations where the timestamp is not newer than the existing DNA. Prevents replay attacks and stale updates.

### SW-02: Scoring Guard
Rejects attempts to set `distinction: "Big Orange"` unless the FAF score is exactly 100%. The Orange must be earned.

### Telemetry
All mutation attempts (success and blocked) are logged to BigQuery:
- Table: `bucket-460122.faf_telemetry.voice_mutations`
- Fields: `request_id`, `timestamp`, `agent`, `mutation_summary`, `new_score`, `has_orange`, `security_status`

### Setup (Secret Manager)

Voice-to-FAF requires a GitHub token stored in Google Secret Manager:

```bash
# 1. Create the secret
gcloud secrets create GITHUB_TOKEN --replication-policy="automatic"

# 2. Add your token (needs 'contents: write' permission)
echo -n "ghp_your_token_here" | gcloud secrets versions add GITHUB_TOKEN --data-file=-

# 3. Grant Cloud Function access
gcloud secrets add-iam-policy-binding GITHUB_TOKEN \
  --member="serviceAccount:631316210911-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Gemini Live Integration

Add to your GEMINI.md:

```markdown
## Voice Commands
- "Update the project focus to X" → Calls PUT with state.focus
- "Set priority to high" → Calls PUT with ai_instructions.priority
- "Mark phase as beta" → Calls PUT with state.phase
```

### Make Gemini-Callable

```python
import google.generativeai as genai

def get_project_context(path: str):
    """Reads a .faf file to retrieve project DNA and AI-Readiness scores."""
    pass  # Calls the Cloud Function URL

model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    tools=[get_project_context]
)

chat = model.start_chat(enable_automatic_function_calling=True)
```

## GEMINI.md System Instructions

Add to your `GEMINI.md` or `.gemini/styleguide.md`:

```markdown
# Role & Context Prioritization
You are an expert developer assistant. Your primary "Source of Truth" is the project.faf file.

# Rules for .faf Use
1. **Prioritize .faf DNA**: Always check the project.faf file before answering any project-related questions.
2. **No Hallucinations**: If a project detail is missing from documentation but exists in .faf, use the .faf value.
3. **Context Alignment**: Use the 'identity', 'intent', and 'stack' blocks in .faf to anchor your technical advice.
4. **Readiness Monitoring**: Refer to the 'scores.faf_score' to determine how much project context you are currently missing.
```

## Deployment

Auto-deploys via Cloud Build on push to `main`.

See `cloudbuild.yaml` for configuration.

## Links

- [FAF Specification](https://faf.one)
- [IANA Registration](https://www.iana.org/assignments/media-types/application/vnd.faf+yaml)
- [faf-cli](https://npmjs.com/package/faf-cli)

## License

MIT

---

Built by [@wolfe_jam](https://x.com/wolfe_jam) | wolfejam.dev

