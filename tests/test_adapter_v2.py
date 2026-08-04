"""Testes do adaptador V2 → doc.json — Fase 0.

Propriedade central: zero perda de texto — a concatenação dos nós
(segundo os offsets) reconstrói exatamente o doc.txt.
"""
from pathlib import Path

from cct.adapter_v2 import adaptar_v2
from cct.schemas import validar_doc

FIXTURE = Path(__file__).parent / "fixtures" / "exemplo_v2.txt"


def _adaptar():
    docs = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))
    assert len(docs) == 1
    return docs[0]


def test_doc_id_extraido():
    doc, _texto = _adaptar()
    assert doc["doc_id"] == "25_PR_001_BTE_01_AHP_SITESE"


def test_estrutura_de_nos():
    doc, _texto = _adaptar()
    tipos = [n["tipo"] for n in doc["nos"]]
    assert tipos == ["preambulo", "artigo", "artigo"]
    assert doc["nos"][1]["rotulo"].startswith("Artigo 1.º")


def test_schema_valido():
    doc, _texto = _adaptar()
    validar_doc(doc)


def test_zero_perda_de_texto():
    doc, texto = _adaptar()
    reconstruido = "".join(texto[n["char_start"]:n["char_end"]] for n in doc["nos"])
    assert reconstruido == texto


def test_offsets_correspondem_ao_conteudo():
    doc, texto = _adaptar()
    n1 = doc["nos"][1]
    trecho = texto[n1["char_start"]:n1["char_end"]]
    assert "valor da alimentação" in trecho
    assert "tabela salarial" not in trecho  # pertence ao artigo 2


def test_sem_marcadores_no_texto():
    _doc, texto = _adaptar()
    assert "#CODE" not in texto and "#ENDCODE" not in texto and "#TEXT" not in texto
