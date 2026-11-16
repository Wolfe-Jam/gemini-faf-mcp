# FAQ - Frequently Asked Questions

## How do I get the Big Orange?

The Big Orange 🍊 is a planned honor, not a score. The score stops at 100% (Trophy ✪), and no single score earns the Big Orange. Think of it as a star for a repo, not a grade for a file.

**It isn't awarded yet.** The criteria are set; the checks that would award it aren't built. When they are, a repo earns it by meeting all four at once:

- **Sustained Trophy:** 100% on three published releases
- **Tests:** at least 100 passing tests in CI
- **Receipts:** at least 30 TAF test receipts
- **AI nomination:** at least one AI (Claude, Grok, Gemini, ChatGPT or Cursor) publicly names the repo as exemplary, in its own voice

> "The Big Orange is not a score; it is the fingerprint of a human who cared enough to make the context true."

YNWA.

---

## What is SW-01?

**SW-01: Temporal Integrity**

SW-01 is a check in the hosted function: it rejects an update whose `generated` timestamp isn't newer than the one already stored, so an old update can't be replayed over a newer one.

---

## What is SW-02?

**SW-02: Meritocratic Guard**

SW-02 refuses an update that sets the Big Orange 🍊 when the project's score, recomputed from the updated file, is below 100%. Typing the distinction into the file isn't enough. The refusal reads:

```
SW-02: Scoring guard - Big Orange requires 100%, current: 42%
```

---

## Can I use this with [Claude / Grok / Other AI]?

Absolutely. The whole point of the `.faf` Trifecta is interoperability.

Whether you're using Gemini, Claude, or Grok, they all read the same DNA. The Multi-Agent Handshake adapts the response format to each agent's dialect:

| Agent | Format | Content-Type |
|-------|--------|--------------|
| Claude | XML | application/xml |
| Gemini | Structured JSON | application/json |
| Grok | Direct JSON | application/json |
| Jules | Minimal | application/json |
| Codex | Code-focused | application/json |

Use the `X-FAF-Agent` header to identify your agent, or let the system auto-detect via User-Agent.

One standard. Every platform.

---

## How do I test without polluting production?

Use **dry-run mode**.

```bash
curl -X PUT "https://us-east1-bucket-460122.cloudfunctions.net/faf-source-of-truth?dry_run=true" \
  -H "Content-Type: application/json" \
  -d '{"updates": {"state.test": "value"}, "message": "test run"}'
```

Dry-run validates your mutation, shows what would change, and returns a preview—without committing to GitHub or logging to telemetry.

---

## Where is the telemetry stored?

Every mutation is logged to BigQuery:

```
Project: bucket-460122
Dataset: faf_telemetry
Table: voice_mutations
```

Schema:
- `request_id` - Unique mutation ID
- `timestamp` - When it happened
- `agent` - Which AI made the request
- `mutation_summary` - What changed
- `new_score` - Score after mutation
- `has_orange` - Big Orange status
- `security_status` - SW-01/SW-02 result
- `raw_input` - Full request payload

---

## What's the media type?

FAF is IANA registered:

```
application/vnd.faf+yaml
```

---

## More questions?

Open an issue or join the discussion. We build in public.

YNWA. ✪
