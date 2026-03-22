"""Pydantic models for Portal da Transparência API responses."""

from __future__ import annotations

from pydantic import BaseModel


class ContratoFornecedor(BaseModel):
    """Contrato federal por CPF/CNPJ do fornecedor."""

    id: int | None = None
    numero: str | None = None
    objeto: str | None = None
    valor_inicial: float | None = None
    valor_final: float | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    orgao: str | None = None
    fornecedor: str | None = None


class RecursoRecebido(BaseModel):
    """Recurso recebido (despesa) por favorecido."""

    ano: int | None = None
    mes: int | None = None
    valor: float | None = None
    favorecido_nome: str | None = None
    orgao_nome: str | None = None
    uf: str | None = None


class Servidor(BaseModel):
    """Servidor público federal."""

    id: int | None = None
    cpf: str | None = None
    nome: str | None = None
    tipo_servidor: str | None = None
    situacao: str | None = None
    orgao: str | None = None


class Licitacao(BaseModel):
    """Licitação federal."""

    id: int | None = None
    numero: str | None = None
    objeto: str | None = None
    modalidade: str | None = None
    situacao: str | None = None
    valor_estimado: float | None = None
    data_abertura: str | None = None
    orgao: str | None = None


class BolsaFamiliaMunicipio(BaseModel):
    """Dados do Novo Bolsa Família por município."""

    municipio: str | None = None
    uf: str | None = None
    quantidade: int | None = None
    valor: float | None = None
    data_referencia: str | None = None


class BolsaFamiliaSacado(BaseModel):
    """Dados do Novo Bolsa Família por NIS do sacado."""

    nis: str | None = None
    nome: str | None = None
    municipio: str | None = None
    uf: str | None = None
    valor: float | None = None


class Sancao(BaseModel):
    """Sanção de pessoa física ou jurídica."""

    fonte: str | None = None
    tipo: str | None = None
    nome: str | None = None
    cpf_cnpj: str | None = None
    orgao: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    fundamentacao: str | None = None


class Emenda(BaseModel):
    """Emenda parlamentar."""

    numero: str | None = None
    autor: str | None = None
    tipo: str | None = None
    localidade: str | None = None
    valor_empenhado: float | None = None
    valor_pago: float | None = None
    ano: int | None = None


class Viagem(BaseModel):
    """Viagem a serviço de servidor federal."""

    id: int | None = None
    cpf: str | None = None
    nome: str | None = None
    cargo: str | None = None
    orgao: str | None = None
    destino: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    valor_passagens: float | None = None
    valor_diarias: float | None = None


class Convenio(BaseModel):
    """Convênio ou transferência voluntária."""

    numero: str | None = None
    objeto: str | None = None
    situacao: str | None = None
    valor_convenio: float | None = None
    valor_liberado: float | None = None
    orgao: str | None = None
    convenente: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None


class CartaoPagamento(BaseModel):
    """Pagamento com cartão corporativo / suprimento de fundos."""

    portador: str | None = None
    cpf: str | None = None
    orgao: str | None = None
    valor: float | None = None
    data: str | None = None
    tipo: str | None = None
    estabelecimento: str | None = None


class PessoaExpostaPoliticamente(BaseModel):
    """Pessoa Exposta Politicamente (PEP)."""

    cpf: str | None = None
    nome: str | None = None
    orgao: str | None = None
    funcao: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None


class AcordoLeniencia(BaseModel):
    """Acordo de leniência (anticorrupção)."""

    empresa: str | None = None
    cnpj: str | None = None
    orgao: str | None = None
    situacao: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    valor: float | None = None


class NotaFiscal(BaseModel):
    """Nota fiscal eletrônica."""

    numero: str | None = None
    serie: str | None = None
    emitente: str | None = None
    cnpj_emitente: str | None = None
    valor: float | None = None
    data_emissao: str | None = None


class BeneficioSocial(BaseModel):
    """Benefício social (BPC, seguro-desemprego, etc.)."""

    tipo: str | None = None
    nome_beneficiario: str | None = None
    cpf: str | None = None
    nis: str | None = None
    valor: float | None = None
    mes_referencia: str | None = None
    municipio: str | None = None
    uf: str | None = None


class PessoaFisicaVinculos(BaseModel):
    """Vínculos e benefícios de pessoa física por CPF."""

    cpf: str | None = None
    nome: str | None = None
    tipo_vinculo: str | None = None
    orgao: str | None = None
    beneficios: str | None = None


class PessoaJuridicaVinculos(BaseModel):
    """Sanções e contratos de pessoa jurídica por CNPJ."""

    cnpj: str | None = None
    razao_social: str | None = None
    sancoes: str | None = None
    contratos: str | None = None


class ContratoDetalhe(BaseModel):
    """Detalhe completo de um contrato federal."""

    id: int | None = None
    numero: str | None = None
    objeto: str | None = None
    valor_inicial: float | None = None
    valor_final: float | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    orgao: str | None = None
    fornecedor: str | None = None
    modalidade: str | None = None
    situacao: str | None = None
    licitacao: str | None = None


class ServidorDetalhe(BaseModel):
    """Detalhe completo de servidor com remuneração."""

    id: int | None = None
    cpf: str | None = None
    nome: str | None = None
    tipo_servidor: str | None = None
    situacao: str | None = None
    orgao: str | None = None
    cargo: str | None = None
    funcao: str | None = None
    remuneracao_basica: float | None = None
    remuneracao_apos_deducoes: float | None = None
