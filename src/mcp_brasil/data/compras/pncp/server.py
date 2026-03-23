"""PNCP sub-server — registers PNCP tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import investigar_fornecedor
from .resources import modalidades_licitacao
from .tools import (
    buscar_atas,
    buscar_contratacoes,
    buscar_contratos,
    consultar_fornecedor,
    consultar_orgao,
)

mcp = FastMCP("pncp")

# Tools (buscar_itens removed — endpoint /v1/itens returns 404)
mcp.tool(buscar_contratacoes, tags={"busca", "contratacoes", "licitacoes"})
mcp.tool(buscar_contratos, tags={"busca", "contratos", "compras"})
mcp.tool(buscar_atas, tags={"busca", "atas", "registro-preco"})
mcp.tool(consultar_fornecedor, tags={"consulta", "fornecedores", "compras"})
mcp.tool(consultar_orgao, tags={"consulta", "orgaos", "compras"})

# Resources
mcp.resource("data://modalidades", mime_type="application/json")(modalidades_licitacao)

# Prompts
mcp.prompt(investigar_fornecedor)
