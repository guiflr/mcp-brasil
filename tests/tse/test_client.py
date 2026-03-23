"""Tests for the TSE HTTP client."""

import httpx
import pytest
import respx

from mcp_brasil.tse import client
from mcp_brasil.tse.constants import CANDIDATURA_URL, ELEICAO_URL, PRESTADOR_URL


class TestAnosEleitorais:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_years(self) -> None:
        respx.get(f"{ELEICAO_URL}/anos-eleitorais").mock(
            return_value=httpx.Response(200, json=[2016, 2018, 2020, 2022])
        )
        result = await client.anos_eleitorais()
        assert result == [2016, 2018, 2020, 2022]

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty(self) -> None:
        respx.get(f"{ELEICAO_URL}/anos-eleitorais").mock(return_value=httpx.Response(200, json=[]))
        result = await client.anos_eleitorais()
        assert result == []


class TestListarEleicoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_elections(self) -> None:
        respx.get(f"{ELEICAO_URL}/ordinarias").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 2030402020,
                        "siglaUF": None,
                        "ano": 2020,
                        "codigo": "2030402020",
                        "nomeEleicao": "Eleições Municipais 2020",
                        "tipoEleicao": "Municipal",
                        "turno": "1",
                        "tipoAbrangencia": "Municipal",
                        "dataEleicao": "15/11/2020",
                        "descricaoEleicao": "Eleições Municipais 2020 - 1º Turno",
                    }
                ],
            )
        )
        result = await client.listar_eleicoes()
        assert len(result) == 1
        assert result[0].ano == 2020
        assert result[0].tipo == "Municipal"


class TestListarEleicoesSupplementares:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed(self) -> None:
        respx.get(f"{ELEICAO_URL}/suplementares/2021/SP").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 2040402021,
                        "ano": 2021,
                        "nomeEleicao": "Eleição Suplementar Mauá",
                        "tipoEleicao": "Suplementar",
                        "dataEleicao": "06/06/2021",
                    }
                ],
            )
        )
        result = await client.listar_eleicoes_suplementares(2021, "SP")
        assert len(result) == 1
        assert result[0].ano == 2021

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty(self) -> None:
        respx.get(f"{ELEICAO_URL}/suplementares/2021/SP").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await client.listar_eleicoes_suplementares(2021, "SP")
        assert result == []


class TestListarEstadosSupplementares:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_states(self) -> None:
        respx.get(f"{ELEICAO_URL}/estados/2021/ano").mock(
            return_value=httpx.Response(
                200,
                json=[{"uf": "SP"}, {"uf": "RJ"}],
            )
        )
        result = await client.listar_estados_suplementares(2021)
        assert result == ["SP", "RJ"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty(self) -> None:
        respx.get(f"{ELEICAO_URL}/estados/2021/ano").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await client.listar_estados_suplementares(2021)
        assert result == []


class TestListarCargos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_positions(self) -> None:
        url = f"{ELEICAO_URL}/listar/municipios/2030402020/35157/cargos"
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "unidadeEleitoralDTO": {"sigla": "BA"},
                    "cargos": [{"codigo": 11, "nome": "Prefeito", "titular": True, "contagem": 5}],
                },
            )
        )
        result = await client.listar_cargos(2030402020, 35157)
        assert len(result) == 1
        assert result[0].nome == "Prefeito"
        assert result[0].contagem == 5


class TestListarCandidatos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_candidates(self) -> None:
        url = f"{CANDIDATURA_URL}/listar/2020/35157/2030402020/11/candidatos"
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "unidadeEleitoral": {},
                    "cargo": {},
                    "candidatos": [
                        {
                            "id": 50000867342,
                            "nomeUrna": "CANDIDATO TESTE",
                            "numero": 44000,
                            "partido": {"sigla": "PT"},
                            "descricaoSituacao": "Deferido",
                        }
                    ],
                },
            )
        )
        result = await client.listar_candidatos(2020, 35157, 2030402020, 11)
        assert len(result) == 1
        assert result[0].nome_urna == "CANDIDATO TESTE"
        assert result[0].partido == "PT"


class TestBuscarCandidato:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_full_candidate(self) -> None:
        url = f"{CANDIDATURA_URL}/buscar/2020/35157/2030402020/candidato/50000867342"
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 50000867342,
                    "nomeUrna": "CANDIDATO TESTE",
                    "nomeCompleto": "Candidato Teste da Silva",
                    "numero": 44000,
                    "partido": {"sigla": "PT"},
                    "descricaoSexo": "Masculino",
                    "grauInstrucao": "Superior completo",
                    "totalDeBens": 150000.0,
                    "descricaoSituacao": "Deferido",
                    "emails": ["teste@email.com"],
                    "sites": [],
                },
            )
        )
        result = await client.buscar_candidato(2020, 35157, 2030402020, 50000867342)
        assert result is not None
        assert result.nome_completo == "Candidato Teste da Silva"
        assert result.total_bens == 150000.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_not_found(self) -> None:
        url = f"{CANDIDATURA_URL}/buscar/2020/999/999/candidato/999"
        respx.get(url).mock(return_value=httpx.Response(200, json={}))
        result = await client.buscar_candidato(2020, 999, 999, 999)
        assert result is None


class TestResultadoEleicao:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_ranked_results(self) -> None:
        url = f"{CANDIDATURA_URL}/listar/2020/35157/2030402020/11/candidatos"
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "candidatos": [
                        {
                            "nomeUrna": "CANDIDATO B",
                            "numero": 15,
                            "partido": {"sigla": "MDB"},
                            "totalVotos": 5000,
                            "percentual": "30,00%",
                            "descricaoTotalizacao": "Não eleito",
                        },
                        {
                            "nomeUrna": "CANDIDATO A",
                            "numero": 44,
                            "partido": {"sigla": "PT"},
                            "totalVotos": 10000,
                            "percentual": "60,00%",
                            "descricaoTotalizacao": "Eleito",
                        },
                    ]
                },
            )
        )
        result = await client.resultado_eleicao(2020, 35157, 2030402020, 11)
        assert len(result) == 2
        assert result[0].nome_urna == "CANDIDATO A"
        assert result[0].total_votos == 10000
        assert result[1].nome_urna == "CANDIDATO B"
        assert result[1].total_votos == 5000

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty(self) -> None:
        url = f"{CANDIDATURA_URL}/listar/2020/999/999/11/candidatos"
        respx.get(url).mock(return_value=httpx.Response(200, json={"candidatos": []}))
        result = await client.resultado_eleicao(2020, 999, 999, 11)
        assert result == []


class TestBuscarCandidatoEnriched:
    @pytest.mark.asyncio
    @respx.mock
    async def test_includes_totalizacao(self) -> None:
        url = f"{CANDIDATURA_URL}/buscar/2020/35157/2030402020/candidato/123"
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 123,
                    "nomeUrna": "CANDIDATO X",
                    "partido": {"sigla": "PT"},
                    "descricaoTotalizacao": "Eleito",
                    "totalVotos": 25000,
                },
            )
        )
        result = await client.buscar_candidato(2020, 35157, 2030402020, 123)
        assert result is not None
        assert result.descricao_totalizacao == "Eleito"
        assert result.total_votos == 25000


class TestConsultarPrestacaoContas:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_accounts(self) -> None:
        url = f"{PRESTADOR_URL}/consulta/2030402020/2020/35157/11/90/90/50000867342"
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "idCandidato": "50000867342",
                    "nomeCandidato": "Candidato Teste",
                    "siglaPartido": "PT",
                    "cnpj": "12.345.678/0001-99",
                    "dadosConsolidados": {
                        "totalRecebido": 100000,
                        "totalReceitaPF": 50000,
                        "totalReceitaPJ": 30000,
                        "totalPartidos": 20000,
                        "totalDoacaoFcc": 0,
                    },
                    "despesas": {
                        "totalDespesasPagas": 80000,
                        "valorLimiteDeGastos": 200000,
                    },
                },
            )
        )
        result = await client.consultar_prestacao_contas(2030402020, 2020, 35157, 11, 50000867342)
        assert result is not None
        assert result.total_recebido == 100000
        assert result.total_despesas == 80000


class TestParserEdgeCases:
    def test_eleicao_empty(self) -> None:
        result = client._parse_eleicao({})
        assert result.id is None
        assert result.ano is None

    def test_cargo_empty(self) -> None:
        result = client._parse_cargo({})
        assert result.codigo is None
        assert result.nome is None

    def test_candidato_resumo_partido_string(self) -> None:
        result = client._parse_candidato_resumo({"partido": "PT"})
        assert result.partido == "PT"

    def test_candidato_resumo_partido_dict(self) -> None:
        result = client._parse_candidato_resumo({"partido": {"sigla": "PL"}})
        assert result.partido == "PL"

    def test_resultado_candidato_empty(self) -> None:
        result = client._parse_resultado_candidato({})
        assert result.nome_urna is None
        assert result.total_votos is None
        assert result.partido is None

    def test_resultado_candidato_partido_string(self) -> None:
        result = client._parse_resultado_candidato({"partido": "PSOL"})
        assert result.partido == "PSOL"

    def test_presta_contas_empty(self) -> None:
        result = client._parse_presta_contas({})
        assert result.total_recebido is None
        assert result.total_despesas is None
