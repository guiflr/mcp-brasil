<div align="center">

<img src="docs/assets/logo.png" alt="mcp-brasil logo" width="100">

# mcp-brasil

**MCP Server para 27 APIs públicas brasileiras**


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

204 tools · 58 resources · 47 prompts

Conecte AI agents (Claude, GPT, Copilot, etc.) a dados governamentais do Brasil — economia, legislação, transparência, judiciário, eleições, meio ambiente, saúde e mais.

**24 APIs não requerem chave** · 2 usam chaves gratuitas (cadastro em 1 min)

[Quick Start](#quick-start) · [Fontes de dados](#fontes-de-dados) · [Casos de Uso](#casos-de-uso) · [Documentação](#documentação) · [Desenvolvimento](#desenvolvimento)

</div>

---

## Features

- **204 tools** em 27 features — econômico, legislativo, transparência, judiciário, eleitoral, ambiental, saúde, compras públicas
- **Cross-referencing** com `planejar_consulta` — cria planos de execução combinando múltiplas APIs (ex: gastos de um deputado + votações + proposições)
- **Execução em lote** com `executar_lote` — dispara consultas em paralelo numa única chamada
- **Smart discovery** — BM25 search transform filtra 204 tools para só mostrar as relevantes ao contexto
- **Auto-registry** — adicionar uma feature é criar uma pasta; zero configuração manual
- **Async everywhere** — httpx async + Pydantic v2 + rate limiting com backoff

## Quick Start

### Instalar

```bash
pip install mcp-brasil
```

```bash
uv add mcp-brasil
```

### Claude Desktop

Adicione ao `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-brasil": {
      "command": "uvx",
      "args": ["--from", "mcp-brasil", "python", "-m", "mcp_brasil.server"],
      "env": {
        "TRANSPARENCIA_API_KEY": "sua-chave-aqui",
        "DATAJUD_API_KEY": "sua-chave-aqui"
      }
    }
  }
}
```

> As chaves são opcionais — sem elas, as 24 APIs restantes funcionam normalmente.

### VS Code / Cursor

Crie `.vscode/mcp.json` na raiz do projeto:

```json
{
  "servers": {
    "mcp-brasil": {
      "command": "uvx",
      "args": ["--from", "mcp-brasil", "python", "-m", "mcp_brasil.server"],
      "env": {
        "TRANSPARENCIA_API_KEY": "sua-chave-aqui",
        "DATAJUD_API_KEY": "sua-chave-aqui"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add mcp-brasil -- uvx --from mcp-brasil python -m mcp_brasil.server
```

### HTTP (outros clientes)

```bash
fastmcp run mcp_brasil.server:mcp --transport http --port 8000
# Server disponível em http://localhost:8000/mcp
```

## Exemplos

Conecte o server e faça perguntas em linguagem natural:

> **Legislativo:** "Quais projetos de lei sobre inteligência artificial tramitaram na Câmara em 2024? Quem foram os autores?"

> **Econômico:** "Qual a tendência da taxa Selic nos últimos 12 meses? Compare com a inflação (IPCA) no mesmo período."

> **Transparência:** "Quais os 10 maiores contratos do governo federal em 2024? Quem são os fornecedores?"

> **Cross-reference:** "Compare os gastos per capita com saúde em São Paulo e Minas Gerais cruzando dados do TCE-SP e IBGE."

> **Judiciário:** "Busque processos sobre licitação irregular no TCU. Quais foram as penalidades aplicadas?"

> **Eleitoral:** "Quais os maiores doadores da campanha do candidato X? Qual o total arrecadado?"

## Fontes de dados

| Categoria | Feature | API | Tools |
|-----------|---------|-----|-------|
| **Econômico** | `ibge` | IBGE — estados, municípios, nomes, agregados estatísticos | 9 |
| | `bacen` | Banco Central — Selic, IPCA, câmbio, PIB e +190 séries | 9 |
| **Legislativo** | `camara` | Câmara dos Deputados — deputados, proposições, votações, despesas | 10 |
| | `senado` | Senado Federal — senadores, matérias, votações, comissões | 26 |
| **Transparência / Fiscal** | `transparencia` | Portal da Transparência — contratos, despesas, servidores, sanções | 18 |
| | `tcu` | Tribunal de Contas da União — acórdãos, licitantes inidôneos | 8 |
| | `tce_sp` | TCE-SP — despesas e receitas de 645 municípios paulistas | 3 |
| | `tce_rj` | TCE-RJ — licitações, contratos, obras, penalidades | 7 |
| | `tce_rs` | TCE-RS — educação, saúde, gestão fiscal (LRF) | 5 |
| | `tce_sc` | TCE-SC — municípios e unidades gestoras | 2 |
| | `tce_pe` | TCE-PE — licitações, contratos, despesas, fornecedores | 5 |
| | `tce_ce` | TCE-CE — licitações, contratos, empenhos | 4 |
| | `tce_rn` | TCE-RN — jurisdicionados, licitações, contratos | 5 |
| | `tce_pi` | TCE-PI — prefeituras, despesas, receitas | 5 |
| | `tce_to` | TCE-TO — processos, pautas de sessões | 3 |
| **Judiciário** | `datajud` | DataJud/CNJ — processos judiciais, movimentações | 7 |
| | `jurisprudencia` | STF, STJ e TST — acórdãos, súmulas, decisões | 6 |
| **Eleitoral** | `tse` | TSE — eleições, candidatos, prestação de contas | 15 |
| **Ambiental** | `inpe` | INPE — focos de queimadas e desmatamento | 4 |
| | `ana` | ANA — estações hidrológicas, telemetria, reservatórios | 3 |
| **Saúde** | `saude` | CNES/DataSUS — estabelecimentos, profissionais, leitos | 4 |
| **Compras Públicas** | `pncp` | PNCP — contratações públicas (Lei 14.133/2021) | 6 |
| | `dadosabertos` | Compras.gov.br — SIASG/ComprasNet | 8 |
| **Utilidades** | `brasilapi` | BrasilAPI — CEP, CNPJ, DDD, bancos, câmbio, FIPE, PIX | 16 |
| | `dados_abertos` | Dados Abertos (dados.gov.br) — catálogo de datasets | 4 |
| | `diario_oficial` | Querido Diário — diários oficiais de 5.000+ cidades | 4 |
| | `transferegov` | TransfereGov — emendas parlamentares PIX | 5 |
| **Agentes IA** | `redator` | Redator Oficial — ofício, despacho, portaria, parecer, nota técnica | 5 |

Além das tools das features, o server raiz expõe 4 meta-tools: `listar_features`, `recomendar_tools`, `planejar_consulta` e `executar_lote`.

## Chaves de API

| API | Obrigatória? | Como obter |
|-----|-------------|------------|
| Portal da Transparência | Opcional | [Cadastro gratuito](https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email) |
| DataJud/CNJ | Opcional | [Cadastro gratuito](https://datajud-wiki.cnj.jus.br/api-publica/acesso) |
| Todas as outras (24) | Nenhuma chave | — |

Configure via variáveis de ambiente ou `.env`:

```bash
TRANSPARENCIA_API_KEY=sua-chave
DATAJUD_API_KEY=sua-chave
```

## Configuração

| Variável | Default | Descrição |
|----------|---------|-----------|
| `TRANSPARENCIA_API_KEY` | — | Chave do Portal da Transparência |
| `DATAJUD_API_KEY` | — | Chave do DataJud/CNJ |
| `MCP_BRASIL_TOOL_SEARCH` | `bm25` | Modo de discovery: `bm25`, `code_mode` ou `none` |
| `MCP_BRASIL_HTTP_TIMEOUT` | `30.0` | Timeout HTTP em segundos |
| `MCP_BRASIL_HTTP_MAX_RETRIES` | `3` | Máximo de retentativas HTTP |

## Documentação

| Página | Descrição |
|--------|-----------|
| [Quick Start](docs/guide/quickstart.md) | Instalação e configuração em 2 minutos |
| [Arquitetura](docs/concepts/architecture.md) | Como o projeto funciona por dentro |
| [Catálogo de Features](docs/reference/features.md) | Todas as 27 features e suas 204 tools |
| [Smart Tools](docs/reference/smart-tools.md) | Meta-tools: planner, batch, discovery |
| [Adicionando Features](docs/guide/adding-features.md) | Guia para contribuir com novas APIs |
| [Configuração](docs/reference/configuration.md) | Variáveis de ambiente e opções |
| [Desenvolvimento](docs/guide/development.md) | Setup de dev, testes, lint, CI |

## Casos de Uso

Exemplos detalhados de como usar o mcp-brasil em diferentes contextos profissionais:

| Caso de Uso | Descrição | APIs Combinadas |
|-------------|-----------|-----------------|
| [Raio-X Parlamentar](docs/examples/raio-x-parlamentar.md) | Conflito de interesses: doações × votações × contratos | Câmara, TSE, Transparência, TCU |
| [Panorama Econômico](docs/examples/panorama-economico.md) | Dashboard econômico com Selic, IPCA, câmbio, PIB | Bacen, IBGE, Transparência |
| [Fiscalização Municipal](docs/examples/fiscalizacao-municipal.md) | Onde vai o dinheiro da sua cidade — 9 TCEs cruzados | TCEs, PNCP, TransfereGov, IBGE |
| [Análise Legislativa](docs/examples/analise-legislativa.md) | Ciclo completo de um PL: Câmara → Senado → Diário Oficial → STF | Câmara, Senado, Diário Oficial, DataJud |
| [Cientista Político](docs/examples/cientista-politico.md) | Fidelidade partidária, coalizões, emendas como poder | Câmara, Senado, TSE, Transparência |
| [Economista](docs/examples/economista.md) | Séries temporais, política fiscal, câmbio, crédito | Bacen (40K+ séries), IBGE |
| [Jornalista Investigativo](docs/examples/jornalista-investigativo.md) | Rastrear emendas, licitações dirigidas, fornecedores suspeitos | Transparência, TCEs, TCU, PNCP, TSE |
| [Jornalista — Matérias](docs/examples/jornalista-materias.md) | Produção de matérias data-driven com dados verificáveis | Bacen, IBGE, Câmara, INPE, TSE |
| [Relatório Parlamentar](docs/examples/parlamentar-report.md) | Votação + emendas + despesas + financiamento de um parlamentar | Câmara, Senado, TSE, TransfereGov |
| [Políticas Públicas](docs/examples/politicas-publicas.md) | Avaliar impacto: recursos investidos vs. resultados | TCEs, IBGE, CNES, Transparência, INPE |
| [Redator Oficial](docs/examples/redator-oficial.md) | Gerar ofícios, pareceres e notas técnicas com dados reais | Redator + Bacen, Transparência, TCU |

## Desenvolvimento

```bash
git clone https://github.com/jxnxts/mcp-brasil.git
cd mcp-brasil
make dev              # Instalar dependências (prod + dev)
make test             # Rodar todos os testes
make test-feature F=ibge  # Testes de uma feature
make lint             # Lint + format check
make ruff             # Auto-fix lint + format
make types            # mypy strict
make ci               # lint + types + test
make run              # Server stdio
make serve            # Server HTTP :8000
make inspect          # Listar tools/resources/prompts
```

## Arquitetura

O projeto usa **Package by Feature** com **Auto-Registry** — cada feature é uma pasta auto-contida:

```
src/mcp_brasil/
├── server.py              # Auto-registry (nunca editado manualmente)
├── _shared/               # Utilitários compartilhados
├── data/                  # 26 features de consulta a APIs
│   ├── ibge/
│   │   ├── __init__.py    # FEATURE_META
│   │   ├── server.py      # FastMCP instance
│   │   ├── tools.py       # Lógica das tools
│   │   ├── client.py      # HTTP async
│   │   ├── schemas.py     # Pydantic models
│   │   └── constants.py   # URLs, códigos
│   ├── bacen/
│   └── ...
└── agentes/               # Features de agentes inteligentes
    └── redator/
```

Para adicionar uma nova feature, basta criar o diretório seguindo a convenção — o registry descobre automaticamente.

## Contribuindo

1. Fork o repositório
2. Crie uma feature em `src/mcp_brasil/data/{feature}/` ou `agentes/{feature}/`
3. Exporte `FEATURE_META` no `__init__.py` e `mcp: FastMCP` no `server.py`
4. Adicione testes em `tests/data/{feature}/`
5. Rode `make ci` e abra um PR

## Disclaimer

Este projeto integra um número significativo de APIs governamentais brasileiras, muitas com documentação inconsistente ou incompleta. Embora todo esforço tenha sido feito para garantir precisão, alguns endpoints podem retornar resultados inesperados ou ter cobertura parcial de parâmetros.

Este é um projeto open-source da comunidade — se encontrar algo quebrado ou que possa ser melhorado, **abra uma issue ou envie um PR**. O objetivo é tornar dados públicos brasileiros acessíveis via IA, juntos.

Todos os dados vêm de APIs oficiais do governo brasileiro — o server não gera, modifica ou editorializa nenhum dado.

## Licença

MIT
