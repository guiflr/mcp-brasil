"""Tests for the PNCP HTTP client."""

import httpx
import pytest
import respx

from mcp_brasil.data.compras.pncp import client
from mcp_brasil.data.compras.pncp.constants import (
    ATAS_URL,
    CONTRATACOES_URL,
    CONTRATOS_URL,
    FORNECEDORES_URL,
    ITENS_URL,
    ORGAOS_URL,
)

# ---------------------------------------------------------------------------
# buscar_contratacoes
# ---------------------------------------------------------------------------


class TestBuscarContratacoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_contratacoes(self) -> None:
        respx.get(CONTRATACOES_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "orgaoEntidade": {
                                "cnpj": "00394460000141",
                                "razaoSocial": "Ministério da Educação",
                                "ufSigla": "DF",
                                "municipioNome": "Brasília",
                                "esferaNome": "Federal",
                            },
                            "anoCompra": 2024,
                            "sequencialCompra": 1,
                            "numeroControlePNCP": "00394460000141-1-000001/2024",
                            "objetoCompra": "Aquisição de computadores",
                            "modalidadeId": 1,
                            "modalidadeNome": "Pregão eletrônico",
                            "situacaoCompraId": 1,
                            "situacaoCompraNome": "Publicada",
                            "valorTotalEstimado": 500000.0,
                            "valorTotalHomologado": 480000.0,
                            "dataPublicacaoPncp": "2024-03-15",
                            "dataAberturaProposta": "2024-04-01",
                            "linkPncp": "https://pncp.gov.br/app/editais/123",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_contratacoes(query="computadores")
        assert result.total == 1
        assert len(result.contratacoes) == 1
        c = result.contratacoes[0]
        assert c.orgao_cnpj == "00394460000141"
        assert c.orgao_nome == "Ministério da Educação"
        assert c.objeto == "Aquisição de computadores"
        assert c.modalidade_id == 1
        assert c.valor_estimado == 500000.0
        assert c.valor_homologado == 480000.0
        assert c.uf == "DF"
        assert c.municipio == "Brasília"
        assert c.link_pncp == "https://pncp.gov.br/app/editais/123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(CONTRATACOES_URL).mock(
            return_value=httpx.Response(
                200,
                json={"totalRegistros": 0, "data": []},
            )
        )
        result = await client.buscar_contratacoes(query="inexistente")
        assert result.total == 0
        assert result.contratacoes == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_fallback_resultado_key(self) -> None:
        respx.get(CONTRATACOES_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "count": 1,
                    "resultado": [
                        {
                            "orgaoEntidade": {"cnpj": "11111111000100"},
                            "objetoCompra": "Teste fallback",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_contratacoes(query="teste")
        assert result.total == 1
        assert len(result.contratacoes) == 1
        assert result.contratacoes[0].objeto == "Teste fallback"


# ---------------------------------------------------------------------------
# buscar_contratos
# ---------------------------------------------------------------------------


class TestBuscarContratos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_contratos(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "orgaoEntidade": {
                                "cnpj": "00394460000141",
                                "razaoSocial": "Ministério da Saúde",
                            },
                            "fornecedor": {
                                "cnpj": "12345678000199",
                                "razaoSocial": "Empresa Pharma LTDA",
                            },
                            "numeroContratoEmpenho": "2024/001",
                            "objetoContrato": "Fornecimento de medicamentos",
                            "valorInicial": 100000.0,
                            "valorFinal": 95000.0,
                            "dataVigenciaInicio": "2024-01-01",
                            "dataVigenciaFim": "2024-12-31",
                            "dataPublicacaoPncp": "2024-01-10",
                            "nomeStatus": "Vigente",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_contratos(query="medicamentos")
        assert result.total == 1
        assert len(result.contratos) == 1
        c = result.contratos[0]
        assert c.orgao_cnpj == "00394460000141"
        assert c.orgao_nome == "Ministério da Saúde"
        assert c.fornecedor_cnpj == "12345678000199"
        assert c.fornecedor_nome == "Empresa Pharma LTDA"
        assert c.numero_contrato == "2024/001"
        assert c.objeto == "Fornecimento de medicamentos"
        assert c.valor_inicial == 100000.0
        assert c.valor_final == 95000.0
        assert c.vigencia_inicio == "2024-01-01"
        assert c.vigencia_fim == "2024-12-31"
        assert c.situacao == "Vigente"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={"totalRegistros": 0, "data": []},
            )
        )
        result = await client.buscar_contratos(query="inexistente")
        assert result.total == 0
        assert result.contratos == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_fornecedor_cpfcnpj_fallback(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "orgaoEntidade": {},
                            "fornecedor": {
                                "cpfCnpj": "99988877000166",
                                "nomeRazaoSocial": "Fornecedor Alt",
                            },
                            "objetoContrato": "Teste fallback fornecedor",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_contratos(query="teste")
        c = result.contratos[0]
        assert c.fornecedor_cnpj == "99988877000166"
        assert c.fornecedor_nome == "Fornecedor Alt"


# ---------------------------------------------------------------------------
# buscar_atas
# ---------------------------------------------------------------------------


class TestBuscarAtas:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_atas(self) -> None:
        respx.get(ATAS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "orgaoEntidade": {
                                "cnpj": "00394460000141",
                                "razaoSocial": "Universidade Federal",
                            },
                            "fornecedor": {
                                "cnpj": "98765432000155",
                                "razaoSocial": "Papelaria Central LTDA",
                            },
                            "numeroAtaRegistroPreco": "2024/010",
                            "objetoContrato": "Material de escritório",
                            "valorInicial": 250000.0,
                            "dataVigenciaInicio": "2024-06-01",
                            "dataVigenciaFim": "2025-05-31",
                            "nomeStatus": "Vigente",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_atas(query="escritório")
        assert result.total == 1
        assert len(result.atas) == 1
        a = result.atas[0]
        assert a.orgao_cnpj == "00394460000141"
        assert a.orgao_nome == "Universidade Federal"
        assert a.fornecedor_cnpj == "98765432000155"
        assert a.fornecedor_nome == "Papelaria Central LTDA"
        assert a.numero_ata == "2024/010"
        assert a.objeto == "Material de escritório"
        assert a.valor_total == 250000.0
        assert a.vigencia_inicio == "2024-06-01"
        assert a.vigencia_fim == "2025-05-31"
        assert a.situacao == "Vigente"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(ATAS_URL).mock(
            return_value=httpx.Response(
                200,
                json={"totalRegistros": 0, "data": []},
            )
        )
        result = await client.buscar_atas(query="inexistente")
        assert result.total == 0
        assert result.atas == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_ata_fields_fallback(self) -> None:
        respx.get(ATAS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "orgaoEntidade": {},
                            "fornecedor": {
                                "cpfCnpj": "11122233000144",
                                "nomeRazaoSocial": "Fornecedor Ata Alt",
                            },
                            "numeroAta": "ATA-001",
                            "objetoAta": "Objeto via campo ata",
                            "valorTotal": 300000.0,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_atas(query="ata")
        a = result.atas[0]
        assert a.fornecedor_cnpj == "11122233000144"
        assert a.fornecedor_nome == "Fornecedor Ata Alt"
        assert a.numero_ata == "ATA-001"
        assert a.objeto == "Objeto via campo ata"
        assert a.valor_total == 300000.0


# ---------------------------------------------------------------------------
# consultar_fornecedor
# ---------------------------------------------------------------------------


class TestConsultarFornecedor:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_fornecedor(self) -> None:
        respx.get(FORNECEDORES_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "cnpj": "12345678000199",
                            "razaoSocial": "Empresa Teste LTDA",
                            "nomeFantasia": "Teste Corp",
                            "municipio": {"nome": "São Paulo"},
                            "uf": {"sigla": "SP"},
                            "porte": "Médio",
                            "dataAbertura": "2010-05-20",
                        }
                    ],
                },
            )
        )
        result = await client.consultar_fornecedor(cnpj="12345678000199")
        assert result.total == 1
        assert len(result.fornecedores) == 1
        f = result.fornecedores[0]
        assert f.cnpj == "12345678000199"
        assert f.razao_social == "Empresa Teste LTDA"
        assert f.nome_fantasia == "Teste Corp"
        assert f.municipio == "São Paulo"
        assert f.uf == "SP"
        assert f.porte == "Médio"
        assert f.data_abertura == "2010-05-20"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(FORNECEDORES_URL).mock(
            return_value=httpx.Response(
                200,
                json={"totalRegistros": 0, "data": []},
            )
        )
        result = await client.consultar_fornecedor(cnpj="00000000000000")
        assert result.total == 0
        assert result.fornecedores == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_fornecedor_fields_fallback(self) -> None:
        respx.get(FORNECEDORES_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "count": 1,
                    "resultado": [
                        {
                            "cpfCnpj": "99988877000166",
                            "nomeRazaoSocial": "Fornecedor Alt",
                            "municipioNome": "Rio de Janeiro",
                            "ufSigla": "RJ",
                            "porteEmpresa": "Grande",
                        }
                    ],
                },
            )
        )
        result = await client.consultar_fornecedor(cnpj="99988877000166")
        f = result.fornecedores[0]
        assert f.cnpj == "99988877000166"
        assert f.razao_social == "Fornecedor Alt"
        assert f.municipio == "Rio de Janeiro"
        assert f.uf == "RJ"
        assert f.porte == "Grande"


# ---------------------------------------------------------------------------
# buscar_itens
# ---------------------------------------------------------------------------


class TestBuscarItens:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_itens(self) -> None:
        respx.get(ITENS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "numeroItem": 1,
                            "descricao": "Computador desktop",
                            "quantidade": 50.0,
                            "unidadeMedida": "UN",
                            "valorUnitarioEstimado": 5000.0,
                            "valorTotal": 250000.0,
                            "situacaoCompraItemNome": "Homologado",
                        }
                    ],
                },
            )
        )
        result = await client.buscar_itens(query="computador")
        assert result.total == 1
        assert len(result.itens) == 1
        item = result.itens[0]
        assert item.numero_item == 1
        assert item.descricao == "Computador desktop"
        assert item.quantidade == 50.0
        assert item.unidade_medida == "UN"
        assert item.valor_unitario == 5000.0
        assert item.valor_total == 250000.0
        assert item.situacao == "Homologado"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(ITENS_URL).mock(
            return_value=httpx.Response(
                200,
                json={"totalRegistros": 0, "data": []},
            )
        )
        result = await client.buscar_itens(query="inexistente")
        assert result.total == 0
        assert result.itens == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_item_fields_fallback(self) -> None:
        respx.get(ITENS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "count": 1,
                    "resultado": [
                        {
                            "numeroItem": 2,
                            "materialServico": "Monitor LED 24 polegadas",
                            "quantidade": 100.0,
                        }
                    ],
                },
            )
        )
        result = await client.buscar_itens(query="monitor")
        item = result.itens[0]
        assert item.numero_item == 2
        assert item.descricao == "Monitor LED 24 polegadas"
        assert item.quantidade == 100.0


# ---------------------------------------------------------------------------
# consultar_orgao
# ---------------------------------------------------------------------------


class TestConsultarOrgao:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_orgaos(self) -> None:
        respx.get(ORGAOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "totalRegistros": 1,
                    "data": [
                        {
                            "cnpj": "00394460000141",
                            "razaoSocial": "Ministério da Educação",
                            "esferaNome": "Federal",
                            "poderNome": "Executivo",
                            "ufSigla": "DF",
                            "municipioNome": "Brasília",
                        }
                    ],
                },
            )
        )
        result = await client.consultar_orgao(query="educação")
        assert result.total == 1
        assert len(result.orgaos) == 1
        o = result.orgaos[0]
        assert o.cnpj == "00394460000141"
        assert o.razao_social == "Ministério da Educação"
        assert o.esfera == "Federal"
        assert o.poder == "Executivo"
        assert o.uf == "DF"
        assert o.municipio == "Brasília"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(ORGAOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={"totalRegistros": 0, "data": []},
            )
        )
        result = await client.consultar_orgao(query="inexistente")
        assert result.total == 0
        assert result.orgaos == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_orgao_fields_fallback(self) -> None:
        respx.get(ORGAOS_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "count": 1,
                    "resultado": [
                        {
                            "cnpj": "11111111000100",
                            "razaoSocial": "Prefeitura Municipal",
                            "esferaId": "Municipal",
                            "poderId": "Executivo",
                            "ufNome": "São Paulo",
                            "municipioNome": "Campinas",
                        }
                    ],
                },
            )
        )
        result = await client.consultar_orgao(query="prefeitura")
        o = result.orgaos[0]
        assert o.cnpj == "11111111000100"
        assert o.razao_social == "Prefeitura Municipal"
        assert o.esfera == "Municipal"
        assert o.poder == "Executivo"
        assert o.uf == "São Paulo"
        assert o.municipio == "Campinas"
