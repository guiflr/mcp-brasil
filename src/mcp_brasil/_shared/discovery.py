"""LLM-powered tool recommendation for mcp-brasil.

Uses the Anthropic API (claude-haiku-4-5) to understand user intent
and recommend the most relevant tools from the mcp-brasil catalog.
"""

from __future__ import annotations

import logging

from ..settings import ANTHROPIC_API_KEY

logger = logging.getLogger("mcp-brasil.discovery")

# Catalog is built once and cached at module level
_catalog_cache: str = ""


def build_catalog(registry: object) -> str:
    """Build a text catalog of all tools from the registry.

    Args:
        registry: FeatureRegistry instance with discovered features.

    Returns:
        Markdown-formatted catalog of tool names and descriptions.
    """
    global _catalog_cache
    if _catalog_cache:
        return _catalog_cache

    lines: list[str] = []
    # Access features from registry
    for feat in getattr(registry, "features", []):
        feature_name = feat.meta.name
        feature_desc = feat.meta.description
        lines.append(f"\n## {feature_name}: {feature_desc}")

        # Get tools from the feature's server
        server = feat.server
        if hasattr(server, "_tool_manager") and hasattr(server._tool_manager, "_tools"):
            for tool_name, tool in server._tool_manager._tools.items():
                desc = (tool.description or "").split("\n")[0]
                lines.append(f"- **{feature_name}_{tool_name}**: {desc}")

    _catalog_cache = "\n".join(lines)
    return _catalog_cache


async def recomendar_tools_impl(query: str, catalog: str) -> str:
    """Call Anthropic API to recommend tools based on user query.

    Args:
        query: Natural language question from the user.
        catalog: Pre-built catalog string of all tools.

    Returns:
        LLM-generated recommendations with explanations.
    """
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError:
        return (
            "Erro: O pacote 'anthropic' não está instalado. "
            "Instale com: pip install 'mcp-brasil[llm]'\n\n"
            "Alternativa: use a tool 'search_tools' para buscar por palavras-chave."
        )

    api_key = ANTHROPIC_API_KEY
    if not api_key:
        return (
            "Erro: ANTHROPIC_API_KEY não configurada. "
            "Defina a variável de ambiente ANTHROPIC_API_KEY para usar esta tool.\n\n"
            "Alternativa: use a tool 'search_tools' para buscar por palavras-chave."
        )

    client = anthropic.AsyncAnthropic(api_key=api_key)

    system_prompt = (
        "Você é um assistente que recomenda tools do mcp-brasil. "
        "Dado o catálogo de tools disponíveis e a pergunta do usuário, "
        "recomende as 3-5 tools mais relevantes. Para cada tool:\n"
        "1. Nome completo da tool (com prefixo da feature)\n"
        "2. Por que é relevante para a pergunta\n"
        "3. Exemplo de como usar (parâmetros principais)\n\n"
        "Responda em português. Seja conciso e prático.\n\n"
        f"## Catálogo de Tools\n{catalog}"
    )

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )
        block = response.content[0]
        return str(getattr(block, "text", ""))
    except Exception as e:
        logger.error("Erro ao chamar Anthropic API: %s", e)
        return f"Erro ao consultar IA: {e}\n\nUse 'search_tools' como alternativa."
