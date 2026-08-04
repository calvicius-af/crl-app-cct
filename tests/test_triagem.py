"""Testes da triagem AUTO/REVER calibrada por precisão medida."""
from cct.triagem import codigos_auto, triar

METRICAS = {"por_codigo": {
    "A": {"precisao": 0.95, "n_gabarito": 10},
    "B": {"precisao": 0.40, "n_gabarito": 10},
    "C": {"precisao": 1.00, "n_gabarito": 1},   # gabarito insuficiente
    "D": {"precisao": None, "n_gabarito": 0},
}}


def test_codigos_auto_por_precisao_e_dimensao():
    assert codigos_auto(METRICAS) == {"A"}


def test_triar_prefixa():
    anot = {"doc_id": "d", "versao_schema": "0.1", "anotacoes": [
        {"no_id": "n1", "char_start": 0, "char_end": 5, "codigo": "A",
         "confianca": 0.8, "metodo": "lexical"},
        {"no_id": "n2", "char_start": 5, "char_end": 9, "codigo": "B",
         "confianca": 0.6, "metodo": "lexical"},
    ]}
    t = triar(anot, codigos_auto(METRICAS))
    codigos = [a["codigo"] for a in t["anotacoes"]]
    assert codigos == ["AUTO/A", "REVER/B"]
