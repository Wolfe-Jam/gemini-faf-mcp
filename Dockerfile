FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 3001

CMD ["python", "-m", "gemini_faf_mcp", "--transport", "sse", "--port", "3001"]
