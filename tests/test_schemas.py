"""Testes dos contratos de dados (JSON Schema) — Fase 0."""
import pytest
from jsonschema import ValidationError

from cct.schemas import validar_doc, validar_anotacoes

DOC_VALIDO = {
    "versao_schema": "0.1",
    "doc_id": "25_PR_001_BTE_01_AHP_SITESE",
    "tipo": "CCT",
    "subtipo": "revisao_parcial",
    "nos": [
        {"id": "n0", "tipo": "preambulo", "rotulo": "PREÂMBULO",
         "char_start": 0, "char_end": 10, "pai": None, "origem": "novo"},
        {"id": "n1", "tipo": "artigo", "rotulo": "Artigo 1.º",
         "char_start": 10, "char_end": 20, "pai": None, "origem": "novo"},
    ],
}

ANOTACOES_VALIDAS = {
    "versao_schema": "0.1",
    "doc_id": "25_PR_001_BTE_01_AHP_SITESE",
    "anotacoes": [
        {"no_id": "n1", "char_start": 10, "char_end": 20,
         "codigo": "AUTO/4.8.1", "confianca": 0.8,
         "metodo": "lexical", "evidencia": "tabela salarial"},
    ],
}


def test_doc_valido_passa():
    validar_doc(DOC_VALIDO)


def test_doc_sem_offsets_falha():
    doc = {**DOC_VALIDO, "nos": [{"id": "n0", "tipo": "preambulo", "rotulo": "x"}]}
    with pytest.raises(ValidationError):
        validar_doc(doc)


def test_doc_subtipo_invalido_falha():
    with pytest.raises(ValidationError):
        validar_doc({**DOC_VALIDO, "subtipo": "coisa_inventada"})


def test_anotacoes_validas_passam():
    validar_anotacoes(ANOTACOES_VALIDAS)


def test_anotacao_confianca_fora_de_gama_falha():
    mau = {**ANOTACOES_VALIDAS,
           "anotacoes": [{**ANOTACOES_VALIDAS["anotacoes"][0], "confianca": 1.5}]}
    with pytest.raises(ValidationError):
        validar_anotacoes(mau)
