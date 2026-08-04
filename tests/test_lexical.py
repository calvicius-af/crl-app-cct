"""Testes da codificação lexical mínima a partir de codebook YAML — Fase 0."""
from pathlib import Path

from cct.adapter_v2 import adaptar_v2
from cct.lexical import codificar
from cct.schemas import validar_anotacoes

FIXTURE = Path(__file__).parent / "fixtures" / "exemplo_v2.txt"

CODEBOOK = {
    "tema": "demo",
    "codigos": [
        {"id": "DEMO/Tabela_Salarial", "termos": ["tabela salarial"]},
        {"id": "DEMO/Subsidio_Refeicao", "termos": ["valor da alimentação", "subsídio de refeição"]},
        {"id": "DEMO/Teletrabalho", "termos": ["teletrabalho"]},
    ],
}


def _codificar():
    doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    return codificar(doc, texto, CODEBOOK), texto


def test_anotacoes_validam_schema():
    anot, _ = _codificar()
    validar_anotacoes(anot)


def test_termos_encontrados_nos_nos_certos():
    anot, _ = _codificar()
    por_codigo = {a["codigo"]: a for a in anot["anotacoes"]}
    assert "DEMO/Tabela_Salarial" in por_codigo
    assert "DEMO/Subsidio_Refeicao" in por_codigo
    assert "DEMO/Teletrabalho" not in por_codigo  # termo ausente do texto


def test_propagacao_para_eixo_pai():
    codebook = {
        "tema": "t",
        "eixos": ["4.08.5"],
        "codigos": [{"id": "4.08.5.1", "termos": ["tabela salarial"]}],
    }
    doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    anot = codificar(doc, texto, codebook)
    codigos = {a["codigo"] for a in anot["anotacoes"]}
    assert "4.08.5.1" in codigos
    assert "4.08.5" in codigos  # eixo-pai propagado
    # sem duplicados por nó+código
    pares = [(a["no_id"], a["codigo"]) for a in anot["anotacoes"]]
    assert len(pares) == len(set(pares))


def test_offsets_da_anotacao_cobrem_o_no():
    anot, texto = _codificar()
    for a in anot["anotacoes"]:
        if a["codigo"].startswith("Estrutura/"):
            continue
        trecho = texto[a["char_start"]:a["char_end"]]
        assert a["evidencia"].lower() in trecho.lower()
        assert 0.0 <= a["confianca"] <= 1.0
        assert a["metodo"] == "lexical"
