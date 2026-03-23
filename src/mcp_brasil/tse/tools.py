"""Tool functions for the TSE (Tribunal Superior Eleitoral) feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from mcp_brasil._shared.formatting import format_brl, format_number_br, markdown_table

from . import client


async def anos_eleitorais() -> str:
    """Lista os anos com dados eleitorais disponíveis no TSE.

    Retorna todos os anos em que houve eleições com dados registrados.

    Returns:
        Lista de anos eleitorais disponíveis.
    """
    anos = await client.anos_eleitorais()
    if not anos:
        return "Nenhum ano eleitoral disponível."
    return "Anos eleitorais disponíveis: " + ", ".join(str(a) for a in sorted(anos))


async def listar_eleicoes() -> str:
    """Lista todas as eleições ordinárias registradas no TSE.

    Inclui eleições municipais, estaduais e federais de todos os anos.

    Returns:
        Tabela com eleições disponíveis.
    """
    eleicoes = await client.listar_eleicoes()
    if not eleicoes:
        return "Nenhuma eleição encontrada."

    rows = [
        (
            str(e.id or "—"),
            str(e.ano or "—"),
            (e.nome or "—")[:40],
            e.tipo or "—",
            e.tipo_abrangencia or "—",
            e.data_eleicao or "—",
        )
        for e in eleicoes
    ]
    return f"Eleições ordinárias ({len(eleicoes)} registros):\n\n" + markdown_table(
        ["ID", "Ano", "Nome", "Tipo", "Abrangência", "Data"], rows
    )


async def listar_eleicoes_suplementares(ano: int, uf: str) -> str:
    """Lista eleições suplementares de um estado em um ano específico.

    Eleições suplementares ocorrem quando eleições regulares são anuladas
    ou quando há vacância de cargo eletivo.

    Args:
        ano: Ano da eleição (ex: 2020, 2022).
        uf: Sigla do estado (ex: SP, RJ, MG).

    Returns:
        Tabela com eleições suplementares encontradas.
    """
    eleicoes = await client.listar_eleicoes_suplementares(ano, uf)
    if not eleicoes:
        return f"Nenhuma eleição suplementar encontrada para {uf.upper()} em {ano}."

    rows = [
        (
            str(e.id or "—"),
            str(e.ano or "—"),
            (e.nome or "—")[:40],
            e.tipo or "—",
            e.data_eleicao or "—",
        )
        for e in eleicoes
    ]
    return f"Eleições suplementares {uf.upper()} {ano} ({len(eleicoes)}):\n\n" + markdown_table(
        ["ID", "Ano", "Nome", "Tipo", "Data"], rows
    )


async def listar_estados_suplementares(ano: int) -> str:
    """Lista estados que tiveram eleições suplementares em um ano.

    Útil para descobrir quais UFs tiveram eleições suplementares antes
    de consultar os detalhes com listar_eleicoes_suplementares().

    Args:
        ano: Ano para consulta (ex: 2020, 2022).

    Returns:
        Lista de siglas de estados com eleições suplementares.
    """
    estados = await client.listar_estados_suplementares(ano)
    if not estados:
        return f"Nenhum estado com eleição suplementar em {ano}."
    return f"Estados com eleições suplementares em {ano}: {', '.join(sorted(estados))}"


async def listar_cargos(eleicao_id: int, municipio: int) -> str:
    """Lista os cargos disponíveis em um município para uma eleição.

    Use o ID da eleição obtido com listar_eleicoes() e o código
    do município (código IBGE ou TSE).

    Args:
        eleicao_id: ID da eleição (ex: 2030402020).
        municipio: Código do município (ex: 35157 para Feira de Santana).

    Returns:
        Tabela com cargos e quantidade de candidatos.
    """
    cargos = await client.listar_cargos(eleicao_id, municipio)
    if not cargos:
        return "Nenhum cargo encontrado para esta eleição/município."

    rows = [
        (
            str(c.codigo or "—"),
            c.nome or "—",
            "Sim" if c.titular else "Não",
            str(c.contagem or 0),
        )
        for c in cargos
    ]
    return f"Cargos disponíveis ({len(cargos)}):\n\n" + markdown_table(
        ["Código", "Cargo", "Titular", "Candidatos"], rows
    )


async def listar_candidatos(
    ano: int,
    municipio: int,
    eleicao_id: int,
    cargo: int,
) -> str:
    """Lista candidatos para um cargo em um município.

    Requer os IDs de eleição e cargo obtidos com listar_eleicoes()
    e listar_cargos().

    Args:
        ano: Ano da eleição (ex: 2020, 2022).
        municipio: Código do município.
        eleicao_id: ID da eleição.
        cargo: Código do cargo (ex: 11=Prefeito, 13=Vereador).

    Returns:
        Tabela com candidatos e suas situações.
    """
    candidatos = await client.listar_candidatos(ano, municipio, eleicao_id, cargo)
    if not candidatos:
        return "Nenhum candidato encontrado para os filtros informados."

    rows = [
        (
            str(c.id or "—"),
            (c.nome_urna or "—")[:30],
            str(c.numero or "—"),
            c.partido or "—",
            c.situacao or "—",
        )
        for c in candidatos
    ]
    return f"Candidatos ({len(candidatos)}):\n\n" + markdown_table(
        ["ID", "Nome de Urna", "Número", "Partido", "Situação"], rows
    )


async def buscar_candidato(
    ano: int,
    municipio: int,
    eleicao_id: int,
    candidato_id: int,
) -> str:
    """Busca detalhes completos de um candidato.

    Retorna informações pessoais, eleitorais, bens declarados
    e situação da candidatura.

    Args:
        ano: Ano da eleição.
        municipio: Código do município.
        eleicao_id: ID da eleição.
        candidato_id: ID do candidato (obtido com listar_candidatos).

    Returns:
        Ficha completa do candidato.
    """
    cand = await client.buscar_candidato(ano, municipio, eleicao_id, candidato_id)
    if cand is None:
        return "Candidato não encontrado."

    lines = [
        f"**Nome de urna:** {cand.nome_urna or '—'}",
        f"**Nome completo:** {cand.nome_completo or '—'}",
        f"**Número:** {cand.numero or '—'}",
        f"**Partido:** {cand.partido or '—'}",
        f"**Coligação:** {cand.coligacao or '—'}",
        f"**Situação:** {cand.situacao or '—'}",
        f"**Situação do candidato:** {cand.situacao_candidato or '—'}",
    ]

    # Totalização
    if cand.descricao_totalizacao:
        lines.append(f"**Resultado:** {cand.descricao_totalizacao}")
    if cand.total_votos is not None:
        lines.append(f"**Total de votos:** {format_number_br(cand.total_votos, 0)}")

    # Dados pessoais
    lines.append("\n**Dados pessoais:**")
    lines.append(f"  Sexo: {cand.sexo or '—'}")
    lines.append(f"  Cor/Raça: {cand.cor_raca or '—'}")
    lines.append(f"  Estado civil: {cand.estado_civil or '—'}")
    lines.append(f"  Escolaridade: {cand.grau_instrucao or '—'}")
    lines.append(f"  Ocupação: {cand.ocupacao or '—'}")
    lines.append(f"  Naturalidade: {cand.municipio_nascimento or '—'}/{cand.uf_nascimento or '—'}")

    # Patrimônio
    if cand.total_bens is not None:
        lines.append(f"\n**Total de bens declarados:** {format_brl(cand.total_bens)}")

    if cand.gasto_campanha is not None and cand.gasto_campanha > 0:
        lines.append(f"**Gasto de campanha:** {format_brl(cand.gasto_campanha)}")

    # Ficha limpa
    if cand.candidato_inapto:
        lines.append("\n**CANDIDATO INAPTO**")
    if cand.motivo_ficha_limpa:
        lines.append("**Motivo Ficha Limpa aplicado**")

    return "\n".join(lines)


async def resultado_eleicao(
    ano: int,
    municipio: int,
    eleicao_id: int,
    cargo: int,
) -> str:
    """Mostra o resultado de uma eleição com candidatos rankeados por votos.

    Retorna a totalização de votos para todos os candidatos de um cargo
    em um município, ordenados do mais votado ao menos votado.

    Args:
        ano: Ano da eleição (ex: 2020, 2022).
        municipio: Código do município.
        eleicao_id: ID da eleição.
        cargo: Código do cargo (ex: 11=Prefeito, 13=Vereador).

    Returns:
        Tabela com ranking de candidatos por votos.
    """
    resultados = await client.resultado_eleicao(ano, municipio, eleicao_id, cargo)
    if not resultados:
        return "Nenhum resultado encontrado para os filtros informados."

    rows = [
        (
            str(i),
            (r.nome_urna or "—")[:30],
            str(r.numero or "—"),
            r.partido or "—",
            format_number_br(r.total_votos, 0) if r.total_votos is not None else "—",
            r.percentual or "—",
            (r.descricao_totalizacao or "—")[:20],
        )
        for i, r in enumerate(resultados, 1)
    ]
    return f"Resultado da eleição ({len(resultados)} candidatos):\n\n" + markdown_table(
        ["#", "Nome", "Nº", "Partido", "Votos", "%", "Resultado"], rows
    )


async def consultar_prestacao_contas(
    eleicao_id: int,
    ano: int,
    municipio: int,
    cargo: int,
    candidato_id: int,
) -> str:
    """Consulta a prestação de contas de campanha de um candidato.

    Retorna receitas, despesas, doadores, fornecedores e limites de gastos.

    Args:
        eleicao_id: ID da eleição.
        ano: Ano da eleição.
        municipio: Código do município.
        cargo: Código do cargo.
        candidato_id: ID do candidato.

    Returns:
        Resumo financeiro da campanha.
    """
    contas = await client.consultar_prestacao_contas(
        eleicao_id, ano, municipio, cargo, candidato_id
    )
    if contas is None:
        return "Prestação de contas não encontrada para este candidato."

    lines = [
        f"**Candidato:** {contas.nome or '—'}",
        f"**Partido:** {contas.partido or '—'}",
        f"**CNPJ campanha:** {contas.cnpj or '—'}",
    ]

    lines.append("\n**Receitas:**")
    lines.append(f"  Total recebido: {format_brl(contas.total_recebido or 0)}")
    lines.append(f"  Pessoa física: {format_brl(contas.total_receita_pf or 0)}")
    lines.append(f"  Pessoa jurídica: {format_brl(contas.total_receita_pj or 0)}")
    lines.append(f"  Fundo partidário: {format_brl(contas.total_fundo_partidario or 0)}")
    lines.append(f"  Fundo especial: {format_brl(contas.total_fundo_especial or 0)}")

    lines.append("\n**Despesas:**")
    lines.append(f"  Total despesas: {format_brl(contas.total_despesas or 0)}")
    lines.append(f"  Limite de gastos: {format_brl(contas.limite_gastos or 0)}")

    if contas.divida_campanha:
        lines.append(f"\n**Dívida de campanha:** {contas.divida_campanha}")
    if contas.sobra_financeira:
        lines.append(f"**Sobra financeira:** {contas.sobra_financeira}")

    return "\n".join(lines)
