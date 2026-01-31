---
faf_score: 100%
faf_tier: Trophy
faf_slots: 14/14
faf_version: 2.5.2
last_sync: '2026-01-31T17:30:00.000Z'
---

# Gemini Project DNA Alignment (FAF v2.5.2)

This project adheres to the .faf standard. Context is provided on-demand and validated via the **bucket-460122** automated pipeline.

## Project Status: Trophy
- **Compliance Score**: 100% (All DNA slots verified)
- **Distinction**: Pending (Big Orange requires AI/Peer recognition)
- **Security**: SW-01 + SW-02 enforced

> *The Big Orange is not a score; it is the fingerprint of a human who cared enough to make the context true.*

## Source of Truth

Gemini MUST call the endpoint before starting a session to ingest the latest DNA.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `https://faf-source-of-truth-6wqmwwyfoq-ue.a.run.app` | Live SVG badge |
| POST | `https://faf-source-of-truth-6wqmwwyfoq-ue.a.run.app` | Read DNA (agent-optimized) |
| PUT | `https://faf-source-of-truth-6wqmwwyfoq-ue.a.run.app` | Voice-to-FAF mutations |

### Reading DNA

```bash
curl -X POST https://faf-source-of-truth-6wqmwwyfoq-ue.a.run.app \
  -H "X-FAF-Agent: gemini" \
  -H "Content-Type: application/json"
```

### Voice-to-FAF (HIGH-VALUE MUTATION)

**IMPORTANT:** Always verbally confirm changes with the user before executing.

```bash
curl -X PUT https://faf-source-of-truth-6wqmwwyfoq-ue.a.run.app \
  -H "Content-Type: application/json" \
  -H "X-FAF-Agent: gemini" \
  -d '{"updates": {"state.focus": "new focus"}, "message": "voice update"}'
```

## Security Layer (v2.5.1)

| Guard | Rule | Enforcement |
|-------|------|-------------|
| SW-01 | Temporal Integrity | Reject stale timestamps |
| SW-02 | Scoring Guard | Big Orange requires 100% |

All mutations logged to BigQuery: `bucket-460122.faf_telemetry.voice_mutations`

## System Instructions

1. **Initialize**: Call POST endpoint first to get DNA
2. **Quality Check**: If score = 100%, proceed with full autonomy
3. **Voice Updates**: Confirm verbally before PUT (HIGH-VALUE MUTATION)
4. **Bi-Sync**: All output must align with current DNA

## Gemini Live Tools

Function declarations in `gemini-live-tools.json`:

| Function | Description |
|----------|-------------|
| `read_project_dna` | Read current DNA from Source of Truth |
| `update_project_dna` | HIGH-VALUE MUTATION - verbal confirm required |

---

*Media Type: application/vnd.faf+yaml*
*Pipeline: bucket-460122*
*"Efficiency is the goal, but like the '77 Reds, we play for the Trophy, but revel in the glory. YNWA"*