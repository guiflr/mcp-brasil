"""Tool functions for the PNCP feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption

IMPORTANT: The PNCP API has NO text search parameter.
All text filtering is done client-side after fetching results.
Date format for all endpoints: YYYYMMDD (also accepts YYYY-MM-DD and DD/MM/YYYY).
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import format_brl

from . import client
from .constants import MODALIDADES


async def buscar_contratacoes(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    ctx: Context,
    texto: str | None = None,
    uf: str | None = None,
    cnpj_orgao: str | None = None,
    modo_disputa: int | None = None,
    pagina: int = 1,
) -> str:
    """Busca licitações e contratações públicas no PNCP por período e modalidade.

    Pesquisa no Portal Nacional de Contratações Públicas (Lei 14.133/2021).
    Cobre contratações federais, estaduais e municipais.

    IMPORTANTE: A API PNCP não suporta busca textual. O parâmetro 'texto'
    filtra os resultados localmente após a consulta.

    Args:
        data_inicial: Data inicial no formato YYYYMMDD (ex: 20250101).
            Também aceita YYYY-MM-DD ou DD/MM/YYYY.
        data_final: Data final no formato YYYYMMDD (ex: 20250331).
            Máximo de 365 dias entre as datas.
        modalidade: Código da modalidade de contratação (obrigatório).
            Principais: 6=Pregão Eletrônico, 8=Dispensa, 9=Inexigibilidade,
            4=Concorrência Eletrônica, 12=Credenciamento.
            Use o resource 'data://modalidades' para ver todos os códigos.
        texto: Filtro textual local (opcional). Filtra por objeto, órgão
            ou fornecedor APÓS buscar os resultados da API.
        uf: UF do órgão contratante (ex: SP, RJ, DF). Opcional.
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        modo_disputa: Código do modo de disputa (opcional).
            1=Aberto, 2=Fechado, 3=Aberto-Fechado, 4=Dispensa com Disputa.
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de contratações encontradas com objeto, valor e situação.
    """
    mod_nome = MODALIDADES.get(modalidade, f"Código {modalidade}")
    await ctx.info(f"Buscando contratações ({mod_nome})...")

    try:
        resultado = await client.buscar_contratacoes(
            data_inicial=data_inicial,
            data_final=data_final,
            modalidade=modalidade,
            texto=texto,
            uf=uf,
            cnpj_orgao=cnpj_orgao,
            modo_disputa=modo_disputa,
            pagina=pagina,
        )
    except ValueError as e:
        return f"Erro de validação: {e}"

    await ctx.info(f"{resultado.total} contratações encontradas")

    if not resultado.contratacoes:
        filtro = f" contendo '{texto}'" if texto else ""
        return (
            f"Nenhuma contratação encontrada para {mod_nome} "
            f"entre {data_inicial} e {data_final}{filtro}."
        )

    lines = [f"**Total:** {resultado.total} contratações\n"]
    for i, c in enumerate(resultado.contratacoes, 1):
        modalidade_desc = MODALIDADES.get(c.modalidade_id or 0, c.modalidade_nome or "N/A")
        valor_est = format_brl(c.valor_estimado) if c.valor_estimado else "N/A"
        valor_hom = format_brl(c.valor_homologado) if c.valor_homologado else "N/A"
        lines.extend(
            [
                f"### {i}. {c.objeto or 'Sem descrição'}",
                f"**Órgão:** {c.orgao_nome or 'N/A'} ({c.orgao_cnpj or 'N/A'})",
                f"**Modalidade:** {modalidade_desc}",
                f"**Situação:** {c.situacao_nome or 'N/A'}",
                f"**Valor estimado:** {valor_est} | **Homologado:** {valor_hom}",
                f"**Publicação:** {c.data_publicacao or 'N/A'}",
                f"**Local:** {c.municipio or 'N/A'}/{c.uf or 'N/A'} ({c.esfera or 'N/A'})",
            ]
        )
        if c.link_pncp:
            lines.append(f"[Ver no PNCP]({c.link_pncp})")
        lines.append("")

    if texto:
        lines.append(f"*Filtrado localmente por '{texto}'.*")
    if resultado.total > len(resultado.contratacoes):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_contratos(
    data_inicial: str,
    data_final: str,
    ctx: Context,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca contratos públicos no PNCP por período.

    Retorna contratos publicados no Portal Nacional de Contratações Públicas.

    IMPORTANTE: A API PNCP não suporta busca textual em contratos.
    O parâmetro 'texto' filtra os resultados localmente.

    Args:
        data_inicial: Data inicial no formato YYYYMMDD (ex: 20250101).
            Também aceita YYYY-MM-DD ou DD/MM/YYYY.
        data_final: Data final no formato YYYYMMDD (ex: 20250331).
            Máximo de 365 dias entre as datas.
        texto: Filtro textual local (opcional). Filtra por objeto,
            órgão ou fornecedor APÓS buscar os resultados da API.
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de contratos encontrados.
    """
    await ctx.info(f"Buscando contratos ({data_inicial} a {data_final})...")

    try:
        resultado = await client.buscar_contratos(
            data_inicial=data_inicial,
            data_final=data_final,
            texto=texto,
            cnpj_orgao=cnpj_orgao,
            pagina=pagina,
        )
    except ValueError as e:
        return f"Erro de validação: {e}"

    await ctx.info(f"{resultado.total} contratos encontrados")

    if not resultado.contratos:
        filtro = f" contendo '{texto}'" if texto else ""
        return f"Nenhum contrato encontrado entre {data_inicial} e {data_final}{filtro}."

    lines = [f"**Total:** {resultado.total} contratos\n"]
    for i, c in enumerate(resultado.contratos, 1):
        raw_valor = c.valor_final or c.valor_inicial
        valor = format_brl(raw_valor) if raw_valor else "N/A"
        lines.extend(
            [
                f"### {i}. {c.objeto or 'Sem descrição'}",
                f"**Órgão:** {c.orgao_nome or 'N/A'}",
                f"**Fornecedor:** {c.fornecedor_nome or 'N/A'} ({c.fornecedor_cnpj or 'N/A'})",
                f"**Contrato nº:** {c.numero_contrato or 'N/A'}",
                f"**Valor:** {valor}",
                f"**Vigência:** {c.vigencia_inicio or 'N/A'} a {c.vigencia_fim or 'N/A'}",
                f"**Situação:** {c.situacao or 'N/A'}",
                "",
            ]
        )

    if texto:
        lines.append(f"*Filtrado localmente por '{texto}'.*")
    if resultado.total > len(resultado.contratos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_atas(
    data_inicial: str,
    data_final: str,
    ctx: Context,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca atas de registro de preço no PNCP por período de vigência.

    Atas de registro de preço são documentos que registram preços praticados
    em licitações para aquisições futuras. A busca filtra por período de
    vigência (não por data de publicação).

    IMPORTANTE: A API PNCP não suporta busca textual.
    O parâmetro 'texto' filtra os resultados localmente.

    Args:
        data_inicial: Data inicial no formato YYYYMMDD (ex: 20250101).
            Também aceita YYYY-MM-DD ou DD/MM/YYYY.
        data_final: Data final no formato YYYYMMDD (ex: 20250331).
            Máximo de 365 dias entre as datas.
        texto: Filtro textual local (opcional). Filtra por objeto,
            órgão ou fornecedor APÓS buscar os resultados da API.
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de atas de registro de preço encontradas.
    """
    await ctx.info(f"Buscando atas de registro de preço ({data_inicial} a {data_final})...")

    try:
        resultado = await client.buscar_atas(
            data_inicial=data_inicial,
            data_final=data_final,
            texto=texto,
            cnpj_orgao=cnpj_orgao,
            pagina=pagina,
        )
    except ValueError as e:
        return f"Erro de validação: {e}"

    await ctx.info(f"{resultado.total} atas encontradas")

    if not resultado.atas:
        filtro = f" contendo '{texto}'" if texto else ""
        return (
            f"Nenhuma ata de registro de preço encontrada "
            f"entre {data_inicial} e {data_final}{filtro}."
        )

    lines = [f"**Total:** {resultado.total} atas\n"]
    for i, a in enumerate(resultado.atas, 1):
        valor = format_brl(a.valor_total) if a.valor_total else "N/A"
        lines.extend(
            [
                f"### {i}. {a.objeto or 'Sem descrição'}",
                f"**Órgão:** {a.orgao_nome or 'N/A'}",
                f"**Fornecedor:** {a.fornecedor_nome or 'N/A'} ({a.fornecedor_cnpj or 'N/A'})",
                f"**Ata nº:** {a.numero_ata or 'N/A'}",
                f"**Valor total:** {valor}",
                f"**Vigência:** {a.vigencia_inicio or 'N/A'} a {a.vigencia_fim or 'N/A'}",
                f"**Situação:** {a.situacao or 'N/A'}",
                "",
            ]
        )

    if texto:
        lines.append(f"*Filtrado localmente por '{texto}'.*")
    if resultado.total > len(resultado.atas):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def consultar_fornecedor(cnpj: str, ctx: Context) -> str:
    """Consulta informações de um fornecedor de contratações públicas pelo CNPJ.

    Retorna dados cadastrais do fornecedor no PNCP (Portal Nacional de
    Contratações Públicas).

    Args:
        cnpj: CNPJ do fornecedor (com ou sem formatação).

    Returns:
        Dados do fornecedor encontrado.
    """
    await ctx.info(f"Consultando fornecedor CNPJ {cnpj}...")
    resultado = await client.consultar_fornecedor(cnpj=cnpj)
    await ctx.info(f"{resultado.total} fornecedor(es) encontrado(s)")

    if not resultado.fornecedores:
        return f"Nenhum fornecedor encontrado com CNPJ {cnpj}."

    lines: list[str] = []
    for f in resultado.fornecedores:
        lines.extend(
            [
                f"**{f.razao_social or 'N/A'}**",
                f"**CNPJ:** {f.cnpj or 'N/A'}",
                f"**Nome fantasia:** {f.nome_fantasia or 'N/A'}",
                f"**Local:** {f.municipio or 'N/A'}/{f.uf or 'N/A'}",
                f"**Porte:** {f.porte or 'N/A'}",
                f"**Abertura:** {f.data_abertura or 'N/A'}",
                "",
            ]
        )
    return "\n".join(lines)


async def consultar_orgao(
    ctx: Context,
    texto: str | None = None,
    uf: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca órgãos contratantes no PNCP.

    Pesquisa órgãos públicos que realizam contratações. Útil para
    encontrar o CNPJ de um órgão específico para filtrar outras buscas.

    Args:
        texto: Nome do órgão (parcial ou completo).
        uf: UF do órgão (ex: SP, RJ, DF).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de órgãos encontrados.
    """
    if not any([texto, uf]):
        return "Informe pelo menos um filtro: texto ou uf."

    desc = texto or uf or "órgãos"
    await ctx.info(f"Buscando órgãos '{desc}'...")
    resultado = await client.consultar_orgao(query=texto, uf=uf, pagina=pagina)
    await ctx.info(f"{resultado.total} órgãos encontrados")

    if not resultado.orgaos:
        return f"Nenhum órgão encontrado para '{desc}'."

    lines = [f"**Total:** {resultado.total} órgãos\n"]
    for i, o in enumerate(resultado.orgaos, 1):
        lines.extend(
            [
                f"### {i}. {o.razao_social or 'N/A'}",
                f"**CNPJ:** {o.cnpj or 'N/A'}",
                f"**Esfera:** {o.esfera or 'N/A'} | **Poder:** {o.poder or 'N/A'}",
                f"**Local:** {o.municipio or 'N/A'}/{o.uf or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.orgaos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)
