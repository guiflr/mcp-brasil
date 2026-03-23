"""Fixtures globais para testes do mcp-brasil."""

import os

# Disable BM25 search transform for tests so the root server exposes all tools
# directly. This must happen before any mcp_brasil module is imported.
os.environ.setdefault("MCP_BRASIL_TOOL_SEARCH", "none")
