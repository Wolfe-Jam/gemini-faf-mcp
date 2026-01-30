# gemini-faf-mcp

![FAF Status](https://us-east1-bucket-460122.cloudfunctions.net/faf-source-of-truth)

Google Cloud Function for FAF (Foundational AI-context Format) integration with Gemini.

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
curl -X POST https://faf-source-of-truth-631316210911.us-east1.run.app \
  -H "Content-Type: application/json" \
  -d '{"path": "project.faf"}'
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

