"""Testes da Fase 2: leitor do gabarito XLSX e harness de métricas.

O harness é validado com dados fabricados de precisão conhecida
antes de ser usado com dados reais (plano, Fase 2).
"""
from pathlib import Path

import pytest

from cct.gabarito import normalizar_codigo, carregar_gabarito
from cct.harness import avaliar

XLSX = Path(__file__).parent.parent / "data" / "raw" / "maxqda" / "4_08_ParaClaudeAppCCT.xlsx"


def test_normalizar_codigo():
    bruto = ("4.08 Direitos Personalidade e Proteção Dados > "
             "4.08.5 Processo individual e fluxo de dados > "
             "4.08.5.1 Registo de pessoal, atualização e direito de consulta")
    assert normalizar_codigo(bruto) == "4.08.5.1"
    assert normalizar_codigo("4.08 Direitos Personalidade e Proteção Dados") == "4.08"


@pytest.mark.skipif(not XLSX.exists(), reason="XLSX do gabarito não disponível")
def test_carregar_gabarito_real():
    g = carregar_gabarito(XLSX)
    assert len(g) > 700
    docs = {r["doc_id"] for r in g}
    assert len(docs) == 89
    assert all(r["codigo"].startswith("4.08") for r in g)
    assert all(r["segmento"] for r in g)


# ---------- harness com dados fabricados ----------

GABARITO = [
    {"doc_id": "D1", "codigo": "4.08.5.1", "segmento": "o processo individual do trabalhador"},
    {"doc_id": "D1", "codigo": "4.08.2.1", "segmento": "instalação de videovigilância"},
    {"doc_id": "D2", "codigo": "4.08.5.1", "segmento": "registo de pessoal atualizado"},
]

def _anot(doc, codigo, texto_no):
    return {"doc_id": doc, "codigo": codigo, "texto": texto_no}


def test_harness_metricas_por_construcao():
    # 2 verdadeiros positivos, 1 falso positivo, 1 falso negativo (doc-nível)
    previstos = [
        _anot("D1", "4.08.5.1", "…sobre o processo individual do trabalhador…"),  # VP
        _anot("D1", "4.08.4.1", "…utilização de email…"),                          # FP
        _anot("D2", "4.08.5.1", "…registo de pessoal atualizado…"),                # VP
        # falta 4.08.2.1 em D1 → FN
    ]
    m = avaliar(previstos, GABARITO)
    r = m["por_codigo"]["4.08.5.1"]
    assert r["precisao"] == 1.0 and r["cobertura"] == 1.0
    r2 = m["por_codigo"]["4.08.2.1"]
    assert r2["cobertura"] == 0.0
    assert m["global"]["vp"] == 2 and m["global"]["fp"] == 1 and m["global"]["fn"] == 1
    assert abs(m["global"]["precisao"] - 2 / 3) < 1e-9
    assert abs(m["global"]["cobertura"] - 2 / 3) < 1e-9


def test_harness_nivel_segmento():
    previstos = [
        _anot("D1", "4.08.5.1", "texto completamente diferente sem relação"),
    ]
    m = avaliar(previstos, GABARITO)
    # a nível de documento conta como VP (doc+código certos)…
    assert m["global"]["vp"] == 1
    # …mas a nível de segmento não há sobreposição de texto
    assert m["global"]["vp_segmento"] == 0
