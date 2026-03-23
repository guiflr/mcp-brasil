# TECH_DEBT.md — Interactive TODO for Technical Debt

> Track bugs, incompatibilities, mocks, and incomplete implementations.
> Update this file whenever you find something that needs attention later.

## Legend

- `[ ]` — Open (needs work)
- `[~]` — In progress
- `[x]` — Resolved

---

## Bootstrap Phase

- [x] **mount() API mismatch** — `feature.py` used `mount("/path", server)` instead of FastMCP v3's `mount(server, namespace=name)`. Fixed.
- [x] **list_tools() accessed private API** — `_tool_manager._tools` is private FastMCP internals. Removed method to avoid mypy strict failures.
- [x] **_shared/http_client.py** — `create_client()` + `http_get()` with retry + exponential backoff + 429/5xx.
- [x] **_shared/formatting.py** — `markdown_table`, `format_brl`, `format_number_br`, `format_percent`, `truncate_list`.
- [x] **_shared/cache.py** — `TTLCache` class + `@ttl_cache(ttl=300)` decorator for async functions.
- [x] **settings.py** — Env var overrides: `HTTP_TIMEOUT`, `HTTP_MAX_RETRIES`, `HTTP_BACKOFF_BASE`, `USER_AGENT`.
- [x] **pyproject.toml dependency-groups** — Migrated from `[project.optional-dependencies]` to `[dependency-groups]`. `make dev` uses `uv sync --group dev`.
- [x] **justfile removed** — Replaced by Makefile.

## Core — Open

- [x] **Response size limiting for LLM context** — APIs can return huge payloads (e.g., 5000+ municipios). Need a strategy to truncate/summarize responses to avoid blowing LLM context windows. See `_shared/formatting.py:truncate_list` as starting point.

## Transparência Feature

- [x] **Resources e prompts faltando** — Feature tinha apenas tools/client/schemas. Adicionados resources.py (endpoints, bases de sanções, info da API) e prompts.py (auditoria_fornecedor, analise_despesas, verificacao_compliance) + server.py atualizado + 27 testes novos.
- [x] **API response shapes unverified** — Resolvido. Adicionado `_safe_parse_list()` com logging de warning para respostas inesperadas, guards em `_parse_bolsa_*` contra strings no lugar de dicts, e 20+ testes de edge cases (non-list, null fields, string fields).
- [x] **Rate limiting not enforced client-side** — Resolvido. Adicionado `_shared/rate_limiter.py` (sliding window 80 req/min) aplicado via `_get()`. `buscar_sancoes` refatorado para usar `_get()` ao invés de `http_get()` direto.
- [x] **Pagination not automatic** — Resolvido. Adicionado `_pagination_hint()` em tools.py que mostra "Use pagina=N+1" quando resultados >= DEFAULT_PAGE_SIZE e "Última página" quando < PAGE_SIZE em pagina > 1.
- [x] **Pre-existing mypy errors in lifespan.py and ibge/client.py** — Resolvido. mypy passa limpo em todos os 35+ arquivos.
- [x] **Cobertura limitada a 8 tools** — Expandido de 8 para 18 tools. Adicionados: convênios, cartões corporativos, PEP, acordos de leniência, notas fiscais, benefícios sociais, consulta CPF/CNPJ, detalhe de contrato/servidor. Resource `categorias-beneficios` adicionada. 148 testes passam.
- [ ] **API endpoints unverified against production** — 10 novos endpoints adicionados baseados na documentação da API. Os nomes de parâmetros e shapes de resposta precisam ser validados contra a API real do Portal da Transparência.

## Câmara Feature

- [x] **Envelope extraction** — API wraps all responses in `{"dados": [...], "links": [...]}`. Handled by `_get()` helper that auto-extracts `dados` field. Tested with empty/missing dados.
- [x] **No client-side rate limiting** — Resolvido. RateLimiter(60 req/min) aplicado via `_get()`.
- [x] **Pagination is server-controlled** — By design. `_pagination_hint()` provides LLM-facing hints ("Use pagina=N+1"). Auto-pagination is not needed for MCP tools since the LLM controls iteration.

## Senado Feature

- [x] **Deeply nested JSON responses** — API returns structures like `data.ListaParlamentarEmExercicio.Parlamentares.Parlamentar`. Handled by `_deep_get(*keys)` helper with safe navigation.
- [x] **Single result as dict instead of list** — When only 1 result, API returns `{}` instead of `[{}]`. Handled by `_ensure_list()` coercion in all parsers.
- [x] **JSON via Accept header** — API requires `Accept: application/json` header. `JSON_HEADERS` constant passed through all requests.
- [x] **No client-side rate limiting** — Resolvido. RateLimiter(60 req/min) aplicado via `_get()`.
- [x] **No pagination support** — By design. `_pagination_hint()` suggests refining filters. Senado API returns full datasets; LLM-facing hints guide users to narrow queries.
- [x] **Votação nominal endpoint may vary** — Resolvido. Old plenário endpoint (`/plenario/lista/votacao`) deprecated and deactivated 2026-02-01. Migrated `listar_votacoes`, `obter_votacao`, `votacoes_recentes` to new `/votacao` API (flat JSON, camelCase). Parsers handle both old PascalCase and new camelCase formats. `votos_materia` still uses `/materia/votacoes/{id}` which remains active.
- [ ] **E-Cidadania tools not implemented** — Plan includes 9 web-scraping tools for e-Cidadania. Deferred to future sessions.
- [x] **dados_abertos auxiliary tools not implemented** — Resolvido. Senado feature expandida. Feature `dados_abertos/` também criada como feature separada para Portal Dados Abertos (dados.gov.br) com 4 tools.

## DataJud Feature

- [x] **Elasticsearch POST API** — DataJud uses POST with JSON body (not GET). Client uses `httpx.AsyncClient.post()` directly instead of shared `http_get()`. Rate limited at 30 req/min.
- [ ] **API key required** — Feature requires `DATAJUD_API_KEY` env var. Auto-discovery skips the feature if not set. Registration: https://datajud.cnj.jus.br
- [x] **Elasticsearch query DSL limited** — Resolvido. `buscar_processos` migrado de `_all` (deprecated) para `multi_match`. Adicionado `buscar_processos_avancado` com `bool.must` query por códigos (classe.codigo + orgaoJulgador.codigo).
- [x] **No pagination (offset/from)** — Resolvido. Implementado `search_after` com `sort` por `@timestamp` (padrão recomendado pela Wiki DataJud). Token de paginação retornado para o LLM.
- [x] **Tribunais incompletos** — Resolvido. Adicionados 27 TREs (tre-ac a tre-to) e 3 TJMs (tjmmg, tjmrs, tjmsp). Total: 91 tribunais cobrindo toda a documentação oficial.

## TSE Feature

- [x] **REST API without CORS** — TSE DivulgaCandContas API blocks browser requests but works fine with httpx. No auth required.
- [x] **Nested response shapes** — Candidatos endpoint wraps results in `{"candidatos": [...]}`, cargos in `{"cargos": [...]}`. Handled by extracting nested fields.
- [ ] **API is unofficial** — DivulgaCandContas API is reverse-engineered. No official documentation. Endpoints may change without notice.
- [x] **No result totalization** — Resolvido. Adicionada tool `resultado_eleicao` que rankeia candidatos por votos. `buscar_candidato` enriquecido com `descricao_totalizacao` e `total_votos`. Novo modelo `ResultadoCandidato`. 47 testes passam.
- [x] **Sem dados de votação por município** — Resolvido para eleições municipais. Adicionadas `listar_municipios_eleitorais` e `resultado_por_municipio` (CDN formato `-u.json`). Disponível para 2024 (prefeito, vereador).
- [x] **CDN tem dados por município para eleições federais** — Resolvido. O CDN usa sufixo `-v.json` (votos) para 2022 e `-u.json` (unificado) para 2024. O formato `-v.json` não inclui nomes de candidatos (apenas números), enriquecido automaticamente via dados estaduais (`-r.json`). `resultado_municipio()` agora detecta o formato pelo ano.
- [x] **CDN paths com election code padded causavam 404** — URLs usavam `/000544/` (padded) no path quando o CDN exige `/544/` (unpadded). Padded é usado apenas no filename (`e000544`). Corrigido `ELEICOES_CDN` para armazenar 3 valores `(ciclo, padded, unpadded)`.
- [x] **CDN usa election codes separados por cargo** — O CDN do TSE usa election codes diferentes por tipo de cargo: 544/545 = presidente, 546/547 = governador+senador+deputados, 619/620 = prefeito+vereador. `ELEICOES_CDN` agora indexa por `(ano, turno, cargo_code)`. Adicionado `_resolve_eleicao_any()` para config files compartilhados.

## Jurisprudência Feature

- [x] **REST APIs for STF/STJ/TST** — Implemented using httpx GET requests to court search APIs. Browser automation (Playwright) not needed.
- [ ] **API response shapes unverified against real data** — STF/STJ/TST APIs are reverse-engineered from web UIs. Real response formats may differ from what parsers expect. Graceful fallback returns empty lists on errors.
- [ ] **STJ SCON may return HTML** — STJ's search endpoint (`pesquisar.jsp`) may return HTML instead of JSON depending on parameters. Current implementation assumes JSON; needs real API validation.
- [ ] **TST backend API undocumented** — TST jurisprudence backend endpoint may not accept the parameters currently used. Needs real API testing.
- [ ] **Súmulas search limited to STF** — Only STF súmulas are implemented. STJ and TST súmula APIs need investigation.
- [ ] **No informativo-specific endpoint** — `buscar_informativos` currently delegates to the main search with "informativo" as query. A dedicated informativo API would give better results.

## BrasilAPI Feature

- [x] **Falsy `status_code=0` bug** — `status_map.get(info.status_code or -1, ...)` treated `status_code=0` as `-1` because `0` is falsy in Python. Fixed to use explicit `is not None` check.
- [ ] **FIPE endpoints may be slow/unreliable** — BrasilAPI proxies FIPE data; upstream can be slow. No retry/fallback implemented beyond shared `http_get()` retries.
- [x] **CNPJ rate limiting** — Resolvido. RateLimiter(60 req/min) aplicado via `_get()` wrapper em todas as 16 funções do client. Mesmo padrão de transparência/câmara.

## Diário Oficial Feature

- [x] **Limited to 3 tools** — Resolvido. Adicionada `buscar_trechos` (GET /gazettes/{territory_id}/excerpts). Feature agora tem 4 tools.
- [x] **No excerpt highlighting** — Resolvido. HTML tags (`<em>`, `<b>`, etc.) são removidas dos excerpts via `re.sub(r"<[^>]+>", "")` antes de truncar a 500 chars.
- [x] **JSONDecodeError em respostas vazias** — API Querido Diário pode retornar respostas vazias/non-JSON. Adicionado try/except `HttpClientError` em `buscar_diarios` e `buscar_trechos` que retorna resultado vazio ao invés de crashar.

## Compras Feature

- [x] **PNCP: 8 bugs corrigidos em batch** — Validação real contra OpenAPI spec (`/v3/api-docs`):
  1. `buscar_contratacoes` não exigia `dataInicial`/`dataFinal`/`modalidade` (obrigatórios na API)
  2. API PNCP **não tem parâmetro `q`** (busca textual) — ignorava silenciosamente. Implementado filtro client-side `_filtrar_por_texto()`
  3. `buscar_itens` removido — endpoint `/v1/itens` retorna 404 (não existe no OpenAPI spec)
  4. `buscar_contratos`/`buscar_atas` não exigiam datas (obrigatórias na API)
  5. Formato de data errado — API exige YYYYMMDD, não DD/MM/YYYY. Adicionado `normalizar_data()` que aceita 3 formatos
  6. Limite de 365 dias não documentado/validado — Adicionado `validar_periodo()`
  7. MODALIDADES incompleto (1-14 → 1-19 códigos reais)
  8. Feature agora tem 5 tools (era 6, removido `buscar_itens`)
- [x] **ComprasNet Legacy descontinuado** — API original `compras.dados.gov.br` retorna 404 (descontinuada). O substituto `dadosabertos.compras.gov.br` já está implementado em `compras/dadosabertos/` com 8 tools (licitações, pregões, dispensas, contratos, fornecedores, CATMAT, CATSER, UASGs).
- [x] **Contratos.gov.br descontinuado** — API `contratos.comprasnet.gov.br/api` retorna 404 (deprecada). Funcionalidade coberta por `compras/dadosabertos/buscar_contratos` e `compras/pncp/`.

## TransfereGov Feature

- [x] **Feature criada do zero** — 5 tools (buscar_emendas_pix, buscar_emenda_por_autor, detalhe_emenda, emendas_por_municipio, resumo_emendas_ano) + resource + prompt + 36 testes. API PostgREST pública sem auth.
- [x] **API endpoint e colunas errados** — Endpoint apontava para `/transferenciasespeciais` (Swagger docs) ao invés de `/transferenciasespeciais/plano_acao_especial`. Colunas usavam nomes fictícios (`autor_emenda`, `nr_emenda`) ao invés dos reais (`nome_parlamentar_emenda_plano_acao`, `numero_emenda_parlamentar_plano_acao`). Schema, client, tools e testes completamente reescritos.
- [ ] **Sem agregação server-side** — `resumo_emendas_ano` retorna registros individuais paginados, não um resumo agregado. PostgREST suporta RPC functions para agregação, mas não as usamos.

## IBGE Feature

- [x] **Agregados populares com IDs errados** — `pib_per_capita` apontava para tabela 5938/variável 38 (inexistente). Corrigido para tabela 6784/variável 9812. `area_territorial` apontava para tabela 8419 (biomassa). Corrigido para tabela 1301/variável 615.
- [x] **PIB per capita só nível nacional** — Tabela 6784 só tem dados em nível N1 (país). Tool agora auto-corrige para `nivel="pais"` com warning via `ctx.warning()`.

## Bacen Feature

- [x] **Expectativas Focus não implementada** — Resolvido. Adicionada `expectativas_focus` com API OData do Boletim Focus (IPCA, IGP-M, Selic, Câmbio, PIB). Feature agora tem 9 tools.

## Dados Abertos Feature (NOVO)

- [x] **Feature criada do zero** — 4 tools (buscar_conjuntos, detalhar_conjunto, listar_organizacoes, buscar_recursos) + resource + prompt + 24 testes. API dados.gov.br sem auth.
- [ ] **API response format unverified** — Endpoints baseados em documentação pública. Shapes de resposta (`registros`, `totalRegistros`) precisam validação contra API real.

## Saúde Feature (NOVO)

- [x] **Feature criada do zero** — 4 tools (buscar_estabelecimentos, buscar_profissionais, listar_tipos_estabelecimento, consultar_leitos) + resource + prompt + 36 testes. API CNES/DataSUS sem auth.
- [ ] **API response format unverified** — Endpoints CNES podem ter rate limiting agressivo ou retornar formatos diferentes. Necessita validação contra API real.
- [ ] **Sem filtro por nome de estabelecimento** — API CNES pode não aceitar busca por texto livre em todos os campos. Filtros são por codigo_municipio e codigo_uf.

## ANA Feature (NOVO)

- [x] **Feature criada do zero** — 3 tools (buscar_estacoes, consultar_telemetria, monitorar_reservatorios) + resource + prompt + 30 testes. APIs Hidroweb/SAR sem auth.
- [ ] **APIs não-REST** — Hidroweb e SAR da ANA podem não seguir padrões REST. Endpoints e formatos de resposta precisam validação contra APIs reais.
- [ ] **Reservatórios endpoint incerto** — URL do SAR (`/sar0/Medicao`) pode não aceitar os parâmetros utilizados. Necessita investigação.

## INPE Feature (NOVO)

- [x] **Feature criada do zero** — 4 tools (buscar_focos_queimadas, consultar_desmatamento, alertas_deter, dados_satelite) + resources + prompt + 31 testes. APIs TerraBrasilis sem auth.
- [ ] **APIs não padronizadas** — BD Queimadas e TerraBrasilis APIs podem ter formatos diferentes dos implementados. Endpoints precisam validação real.
- [ ] **DETER/PRODES endpoints incertos** — Business API do TerraBrasilis pode não expor dados via REST diretamente. Formato de resposta baseado em documentação parcial.

## Tool Discovery & Search

- [x] **Tags on all tools** — Added semantic tags to all 154+ tools across 19 features. Tags use action type (consulta, busca, listagem, detalhe, calculo, validacao, formatacao, comparacao) + domain-specific tags.
- [x] **BM25 search transform** — `BM25SearchTransform` replaces 154+ tool listing with `search_tools` + `call_tool`. Configurable via `MCP_BRASIL_TOOL_SEARCH` env var (`bm25`|`none`|`code_mode`).
- [x] **recomendar_tools** — LLM-powered tool recommendation using Anthropic API (claude-haiku-4-5). `anthropic` is optional dependency (`pip install mcp-brasil[llm]`). Gracefully degrades when not installed or API key missing.
- [x] **CodeMode experimental** — Opt-in via `MCP_BRASIL_TOOL_SEARCH=code_mode`. Uses Search + GetTags + GetSchemas + execute sandbox. Requires `fastmcp[code-mode]` extra.
- [ ] **BM25 may not index tags** — BM25SearchTransform searches tool names, descriptions, and parameter names but may not directly index tags. Tags are useful for CodeMode's GetTags discovery tool.
- [ ] **recomendar_tools catalog uses private API** — `build_catalog()` accesses `server._tool_manager._tools` which is a private FastMCP internal. May break on FastMCP upgrades.

## TCE Features (NOVO — 9 features)

- [x] **TCE-RJ** — 7 tools. API `dados.tcerj.tc.br/api/v1/`. Resposta wrappada em `{"Licitacoes": [...], "Count": N}` etc. Sem auth.
- [x] **TCE-SP** — 3 tools. API `transparencia.tce.sp.gov.br/api/json/`. Valores monetários como strings no formato BR (`"5.034,11"`). Parsing requer strip de pontos e troca de vírgula por ponto. Dados de 2014 até presente.
- [x] **TCE-CE** — 4 tools. API `api-dados-abertos.tce.ce.gov.br/`. Duas patterns de resposta (array simples vs paginado com `length/total/data`). Precisa append `"00"` ao ano para `exercicio_orcamento`.
- [x] **TCE-PE** — 5 tools. API `sistemas.tce.pe.gov.br/DadosAbertos/`. URL com `!json` separator. Encoding ISO-8859-1 (não UTF-8). Hard limit de 100k registros sem paginação.
- [x] **TCE-RS** — 5 tools. Portal CKAN `dados.tce.rs.gov.br`. DataStore NÃO habilitado — dados via download de JSON bulk. Datasets grandes (100s MB) não são práticos; implementação foca em datasets pequenos (educação, saúde, fiscal, municípios).
- [x] **TCE-SC** — 2 tools. Apenas 2 endpoints abertos (`municipios`, `unidades-gestoras`). API real (e-Sfinge) requer auth institucional.
- [x] **TCE-RN** — 5 tools. API `apidadosabertos.tce.rn.gov.br/api/`. Todos parâmetros são path params (não query params). Formato controlado por segmento `Json`/`Csv` no path.
- [x] **TCE-TO** — 3 tools. API `api.tceto.tc.br/econtas/api`. Requer header `Accept: application/json`. Endpoint `/decisoes` retorna 501 (broken). Paginação do `/pautas` ignorada pela API (retorna mesmos dados em todas as páginas).
- [x] **TCE-PI** — 5 tools. API `sistemas.tce.pi.gov.br/api/portaldacidadania/`. Docs JS-rendered (endpoints extraídos do bundle JS). ~48 endpoints disponíveis. Implementação foca em prefeituras, despesas, receitas, órgãos.
- [ ] **TCE-TO /decisoes broken** — Endpoint retorna 501 "Falha interna". Não implementado. Monitorar se volta a funcionar.
- [ ] **TCE-TO /pautas ignora paginação** — Parâmetro `pagina` é aceito mas não produz efeito (retorna mesmos dados). Documentado no client mas pode confundir usuários.
- [ ] **TCE-SC API extremamente limitada** — Apenas 2 endpoints públicos (municipios e unidades gestoras). A API real do e-Sfinge requer credenciais institucionais. Feature é minimal por design.
- [ ] **TCE-RS sem DataStore** — Portal CKAN não tem DataStore habilitado, impossibilitando queries SQL via API. Dados acessíveis apenas via download de arquivos JSON completos.
- [ ] **TCE-PE encoding ISO-8859-1** — Respostas da API usam ISO-8859-1, não UTF-8. O `http_get()` padrão assume UTF-8. Se caracteres acentuados aparecerem corrompidos, o client precisa decodificar explicitamente.
- [ ] **APIs de TCEs não verificadas periodicamente** — 9 APIs de TCEs estaduais implementadas. Endpoints podem mudar sem aviso. Não há health check automatizado.

## Known Limitations

- [x] **No CONTRIBUTING.md** — Resolvido. CONTRIBUTING.md criado com getting started, estrutura, como adicionar features, convenções, testes e PR guidelines.
- [x] **_shared/validators.py** — Adicionado. Validadores de CPF, CNPJ e CEP com algoritmo de dígitos verificadores + formatadores. 29 testes.

---

*Last updated: 2026-03-23*
