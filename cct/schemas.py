"""Contratos de dados entre fases do pipeline (JSON Schema).

doc.json  — estrutura hierárquica de uma convenção, com offsets sobre doc.txt
anotacoes.json — codificações propostas, com confiança e método
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


def validar_doc(doc: dict) -> None:
    validate(doc, DOC_SCHEMA)


def validar_anotacoes(anotacoes: dict) -> None:
    validate(anotacoes, ANOTACOES_SCHEMA)
