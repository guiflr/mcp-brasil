# mcp-brasil — task runner

# Instalar dependências
install:
    uv sync

# Rodar testes
test:
    uv run pytest -v

# Rodar testes de uma feature específica
test-feature feature:
    uv run pytest tests/{{feature}}/ -v

# Lint e formatação
lint:
    uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/

# Corrigir lint e formatação
fix:
    uv run ruff check --fix src/ tests/ && uv run ruff format src/ tests/

# Type checking
types:
    uv run mypy src/mcp_brasil/

# Rodar server (stdio)
run:
    uv run fastmcp run mcp_brasil.server:mcp

# Rodar server (HTTP)
serve port="8000":
    uv run fastmcp run mcp_brasil.server:mcp --transport http --port {{port}}

# Inspecionar server
inspect:
    uv run fastmcp inspect mcp_brasil.server:mcp

# CI completo
ci: lint types test
