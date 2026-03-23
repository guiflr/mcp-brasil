"""mcp-brasil root server — auto-discovers and mounts all features.

This file uses FeatureRegistry for zero-touch feature onboarding.
You should NEVER need to edit this file to add a new feature.
Just create a new directory following the convention in ADR-001/002.

Usage:
    fastmcp run mcp_brasil.server:mcp
    fastmcp run mcp_brasil.server:mcp --transport http --port 8000
"""

import logging
import time

import mcp.types as mt
from fastmcp import Context, FastMCP
from fastmcp.prompts import PromptResult
from fastmcp.resources import ResourceResult
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult

from ._shared.feature import FeatureRegistry
from ._shared.lifespan import http_lifespan
from .settings import TOOL_SEARCH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("mcp-brasil")


# ---------------------------------------------------------------------------
# Middleware — lightweight request logging
# ---------------------------------------------------------------------------
class RequestLoggingMiddleware(Middleware):
    """Log all tool calls, resource reads, and prompt requests."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        name = context.message.name
        logger.info("Tool call: %s", name)
        start = time.monotonic()
        result = await call_next(context)
        elapsed = time.monotonic() - start
        logger.info("Tool %s completed in %.2fs", name, elapsed)
        return result

    async def on_read_resource(
        self,
        context: MiddlewareContext[mt.ReadResourceRequestParams],
        call_next: CallNext[mt.ReadResourceRequestParams, ResourceResult],
    ) -> ResourceResult:
        uri = context.message.uri
        logger.info("Resource read: %s", uri)
        return await call_next(context)

    async def on_get_prompt(
        self,
        context: MiddlewareContext[mt.GetPromptRequestParams],
        call_next: CallNext[mt.GetPromptRequestParams, PromptResult],
    ) -> PromptResult:
        name = context.message.name
        logger.info("Prompt get: %s", name)
        return await call_next(context)


# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

# Create the root server
mcp = FastMCP("mcp-brasil 🇧🇷", lifespan=http_lifespan)

# Add middleware
mcp.add_middleware(RequestLoggingMiddleware())

# Auto-discover and mount all features
registry = FeatureRegistry()
registry.discover("mcp_brasil.data")
registry.discover("mcp_brasil.agentes")
registry.mount_all(mcp)

logger.info("\n%s", registry.summary())


# Expose a meta-tool for introspection
@mcp.tool(tags={"meta", "discovery"})
def listar_features() -> str:
    """Lista todas as features (APIs) disponíveis no mcp-brasil.

    Use esta tool para saber quais APIs governamentais estão conectadas
    e quais tools cada uma oferece.

    Returns:
        Resumo das features ativas com descrição e status de autenticação.
    """
    return registry.summary()


# Expose an LLM-powered recommendation tool
@mcp.tool(tags={"meta", "discovery"})
async def recomendar_tools(query: str, ctx: Context) -> str:
    """Recomenda tools relevantes a partir de uma pergunta em linguagem natural.

    Usa IA para entender sua intenção e sugerir as tools mais adequadas
    do mcp-brasil, explicando quando e como usar cada uma.

    Args:
        query: Pergunta ou descrição do que você precisa
               (ex: "quero dados sobre gastos do governo federal").
    """
    from ._shared.discovery import build_catalog, recomendar_tools_impl

    await ctx.info(f"Buscando recomendações para: {query}")
    catalog = build_catalog(registry)
    return await recomendar_tools_impl(query, catalog)


# ---------------------------------------------------------------------------
# Tool Search Transform — configurable via MCP_BRASIL_TOOL_SEARCH
# ---------------------------------------------------------------------------
_always_visible = ["listar_features", "recomendar_tools"]

if TOOL_SEARCH == "bm25":
    from fastmcp.server.transforms.search import BM25SearchTransform

    mcp.add_transform(
        BM25SearchTransform(
            max_results=10,
            always_visible=_always_visible,
        )
    )
    logger.info("Tool search: BM25 (search_tools + call_tool)")

elif TOOL_SEARCH == "code_mode":
    from fastmcp.experimental.transforms.code_mode import (
        CodeMode,
        GetSchemas,
        GetTags,
        Search,
    )

    mcp.add_transform(
        CodeMode(
            discovery_tools=[GetTags(name="get_tags"), Search(name="search"), GetSchemas()],
        )
    )
    logger.info("Tool search: CodeMode (experimental)")

else:
    logger.info("Tool search: none (all %d+ tools visible)", len(registry.features))


if __name__ == "__main__":
    mcp.run()
