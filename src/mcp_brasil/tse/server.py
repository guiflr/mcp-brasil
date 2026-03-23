"""TSE feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_candidato, comparativo_eleicao
from .resources import cargos_eleitorais, info_api
from .tools import (
    anos_eleitorais,
    buscar_candidato,
    consultar_prestacao_contas,
    listar_candidatos,
    listar_cargos,
    listar_eleicoes,
    listar_eleicoes_suplementares,
    listar_estados_suplementares,
    resultado_eleicao,
)

mcp = FastMCP("mcp-brasil-tse")

# Tools (9)
mcp.tool(anos_eleitorais)
mcp.tool(listar_eleicoes)
mcp.tool(listar_eleicoes_suplementares)
mcp.tool(listar_estados_suplementares)
mcp.tool(listar_cargos)
mcp.tool(listar_candidatos)
mcp.tool(buscar_candidato)
mcp.tool(resultado_eleicao)
mcp.tool(consultar_prestacao_contas)

# Resources
mcp.resource("data://cargos-eleitorais", mime_type="application/json")(cargos_eleitorais)
mcp.resource("data://info-api", mime_type="application/json")(info_api)

# Prompts
mcp.prompt(analise_candidato)
mcp.prompt(comparativo_eleicao)
