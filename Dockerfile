FROM python:3.12-slim

WORKDIR /app

# server.py + models.py + safe_path.py ARE the MCP server (py-modules in
# pyproject.toml). Copy them before install so `pip install .` packages them.
COPY pyproject.toml README.md server.py models.py safe_path.py inject.py ./
COPY src ./src

RUN pip install --no-cache-dir .

# Cloud Run injects $PORT (8080); server.py reads it and serves Streamable HTTP.
# Stateless + JSON responses: the mcpaas.live RC edge fronts this as the tool
# executor, forwarding tools/list + tools/call as plain JSON-RPC POSTs — no
# session handshake, no SSE. The edge owns the MCP protocol (2026-07-28).
ENV MCP_TRANSPORT=http
ENV FASTMCP_STATELESS_HTTP=true
ENV FASTMCP_JSON_RESPONSE=true
EXPOSE 8080

CMD ["python", "server.py"]
