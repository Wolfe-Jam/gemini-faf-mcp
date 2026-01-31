# Welcome to the Terrace

> We build in public because context shouldn't be a black box.
>
> Whether you're a solo dev or part of a "Little Monster" startup, the rules are the same: Keep your DNA clean, your telemetry live, and remember—You'll Never Work Alone.
>
> *"If you want to make a format for AI-Context persistent, you better be persistent."*
>
> 🏆🍊

---

## The .faf Open Standard

This repository is part of the FAF Trifecta:

| Repository | Platform | Status |
|------------|----------|--------|
| [claude-faf-mcp](https://github.com/anthropics/claude-faf-mcp) | Anthropic | ✅ |
| [grok-faf-mcp](https://github.com/Wolfe-Jam/grok-faf-mcp) | xAI | ✅ |
| [gemini-faf-mcp](https://github.com/Wolfe-Jam/gemini-faf-mcp) | Google | ✅ |

One format. Three platforms. Zero drift.

---

## How to Contribute

### Reporting Issues

Found a bug? Open an issue with:
- What you expected
- What happened
- Steps to reproduce
- Your agent type (Claude, Gemini, Grok, etc.)

### Suggesting Features

Ideas welcome. Before opening a feature request:
1. Check existing issues
2. Explain the use case
3. Consider how it affects all three platforms (Trifecta compatibility)

### Pull Requests

1. Fork the repo
2. Create a feature branch
3. Write tests (WJTTC standard: Tier 1 for critical, Tier 2 for core)
4. Ensure all 36 tests pass
5. Submit PR with clear description

---

## Code Standards

### Security First

All mutations must pass:
- **SW-01**: Temporal Integrity (no replays)
- **SW-02**: Scoring Guard (Big Orange requires 100%)

### Test Standards (WJTTC)

We use Championship-grade testing:

| Tier | Name | Purpose |
|------|------|---------|
| 1 | BRAKE | Critical - must never fail |
| 2 | ENGINE | Core functionality |
| 3 | AERO | Polish and edge cases |
| 4 | VOICE | Voice-to-FAF specific |
| 5 | SECURITY | SW-01/SW-02 enforcement |

Run tests:
```bash
pytest tests/test_gemini_faf_mcp.py -v
```

All tests use `dry_run=true` to prevent production pollution.

---

## The Spirit

This project follows the '77 Reds philosophy:

> "Efficiency is the goal, but like the '77 Reds, we play for the Trophy, but revel in the glory."

We ship fast, we ship right, and we never forget why we're here.

---

## Questions?

- Check the [FAQ](FAQ.md)
- Open a discussion
- Read the [OpenAPI spec](openapi.yaml)

---

**From the Terrace to the Terminal.**

YNWA. 🏆🍊
