"""Contratos de dados entre fases do pipeline (JSON Schema).

doc.json  — estrutura hierárquica de uma convenção, com offsets sobre doc.txt
anotacoes.json — codificações propostas, com confiança e método
registo_bte.jsonl — uma linha por documento adquirido (cct/recolha.py)
"""
from jsonschema import validate

SUBTIPOS = [
    "primeira_convencao",
    "revisao_global",
    "revisao_parcial",
    "revisao_parcial_com_consolidado",
    "texto_consolidado",
    "desconhecido",
]

TIPOS_NO = [
    "preambulo", "capitulo", "seccao", "clausula", "artigo",
    "anexo", "tabela", "regulamento", "bloco", "paragrafo",
]

_NO = {
    "type": "object",
    "required": ["id", "tipo", "rotulo", "char_start", "char_end"],
    "properties": {
        "id": {"type": "string"},
        "tipo": {"enum": TIPOS_NO},
        "rotulo": {"type": "string"},
        "char_start": {"type": "integer", "minimum": 0},
        "char_end": {"type": "integer", "minimum": 0},
        "pai": {"type": ["string", "null"]},
        "origem": {"enum": ["novo", "consolidado"]},
    },
}

DOC_SCHEMA = {
    "type": "object",
    "required": ["versao_schema", "doc_id", "tipo", "subtipo", "nos"],
    "properties": {
        "versao_schema": {"type": "string"},
        "doc_id": {"type": "string", "minLength": 1},
        "tipo": {"type": "string"},
        "subtipo": {"enum": SUBTIPOS},
        "nos": {"type": "array", "items": _NO, "minItems": 1},
    },
}

_ANOTACAO = {
    "type": "object",
    "required": ["no_id", "char_start", "char_end", "codigo",
                 "confianca", "metodo"],
    "properties": {
        "no_id": {"type": "string"},
        "char_start": {"type": "integer", "minimum": 0},
        "char_end": {"type": "integer", "minimum": 0},
        "codigo": {"type": "string", "minLength": 1},
        "confianca": {"type": "number", "minimum": 0, "maximum": 1},
        "metodo": {"enum": ["lexical", "contexto", "semantico", "llm", "manual"]},
        "nivel": {"enum": ["clausula", "paragrafo"]},
        "evidencia": {"type": "string"},
    },
}

ANOTACOES_SCHEMA = {
    "type": "object",
    "required": ["versao_schema", "doc_id", "anotacoes"],
    "properties": {
        "versao_schema": {"type": "string"},
        "doc_id": {"type": "string"},
        "anotacoes": {"type": "array", "items": _ANOTACAO},
    },
}


ESTADOS_DESCARGA = ["descarregado", "ja_existente", "inalterado", "falhado",
                    "ignorado", "por_descarregar"]
ESTADOS_NOMEACAO = ["nomeado", "ja_existente", "por_nomear", "por_confirmar",
                    "conflito", "sem_origem"]

# Deliberadamente permissivo: uma entrada é uma linha de registo_bte.jsonl,
# escrita e relida entre corridas (às vezes de anos diferentes do código), por
# isso só se exige o que o resto do pipeline realmente lê para não falhar
# (ver PR #35, achado nº10) — "chave" identifica o documento; "ano"/"num_bte",
# quando presentes, têm de ser inteiros (não strings nem outra coisa), porque
# cct/nomeacao.py faz int(entrada.get("ano") or 0) sem validar de novo.
REGISTO_SCHEMA = {
    "type": "object",
    "required": ["chave"],
    "properties": {
        "chave": {"type": "string", "minLength": 1},
        "ano": {"type": ["integer", "null"]},
        "num_bte": {"type": ["integer", "null"]},
        "descarga": {
            "type": "object",
            "properties": {
                "estado": {"enum": ESTADOS_DESCARGA},
            },
        },
        "nomeacao": {
            "type": "object",
            "properties": {
                "ordinal": {"type": ["integer", "null"], "minimum": 1},
                "estado": {"enum": ESTADOS_NOMEACAO},
            },
        },
    },
}


def validar_doc(doc: dict) -> None:
    validate(doc, DOC_SCHEMA)


def validar_anotacoes(anotacoes: dict) -> None:
    validate(anotacoes, ANOTACOES_SCHEMA)


def validar_registo(entrada: dict) -> None:
    validate(entrada, REGISTO_SCHEMA)
