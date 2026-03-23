"""Integration tests for the TSE feature using fastmcp.Client."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_brasil.tse.server import mcp

CLIENT_MODULE = "mcp_brasil.tse.client"


class TestToolsRegistered:
    @pytest.mark.asyncio
    async def test_all_9_tools_registered(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            names = {t.name for t in tool_list}
            expected = {
                "anos_eleitorais",
                "listar_eleicoes",
                "listar_eleicoes_suplementares",
                "listar_estados_suplementares",
                "listar_cargos",
                "listar_candidatos",
                "buscar_candidato",
                "resultado_eleicao",
                "consultar_prestacao_contas",
            }
            assert expected.issubset(names), f"Missing: {expected - names}"

    @pytest.mark.asyncio
    async def test_tools_have_docstrings(self) -> None:
        async with Client(mcp) as c:
            tool_list = await c.list_tools()
            for tool in tool_list:
                assert tool.description, f"Tool {tool.name} has no description"


class TestResourcesRegistered:
    @pytest.mark.asyncio
    async def test_all_2_resources_registered(self) -> None:
        async with Client(mcp) as c:
            resources = await c.list_resources()
            uris = {str(r.uri) for r in resources}
            expected = {"data://cargos-eleitorais", "data://info-api"}
            assert expected.issubset(uris), f"Missing: {expected - uris}"


class TestPromptsRegistered:
    @pytest.mark.asyncio
    async def test_all_2_prompts_registered(self) -> None:
        async with Client(mcp) as c:
            prompts = await c.list_prompts()
            names = {p.name for p in prompts}
            expected = {"analise_candidato", "comparativo_eleicao"}
            assert expected.issubset(names), f"Missing: {expected - names}"


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_anos_eleitorais_e2e(self) -> None:
        with patch(
            f"{CLIENT_MODULE}.anos_eleitorais",
            new_callable=AsyncMock,
            return_value=[2020, 2022],
        ):
            async with Client(mcp) as c:
                result = await c.call_tool("anos_eleitorais", {})
                assert "2020" in result.data
                assert "2022" in result.data

    @pytest.mark.asyncio
    async def test_resultado_eleicao_e2e(self) -> None:
        from mcp_brasil.tse.schemas import ResultadoCandidato

        mock_data = [
            ResultadoCandidato(
                nome_urna="CANDIDATO A",
                numero=44,
                partido="PT",
                total_votos=10000,
                percentual="60,00%",
                descricao_totalizacao="Eleito",
            ),
        ]
        with patch(
            f"{CLIENT_MODULE}.resultado_eleicao",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            async with Client(mcp) as c:
                result = await c.call_tool(
                    "resultado_eleicao",
                    {"ano": 2020, "municipio": 35157, "eleicao_id": 2030402020, "cargo": 11},
                )
                assert "CANDIDATO A" in result.data
                assert "10.000" in result.data
