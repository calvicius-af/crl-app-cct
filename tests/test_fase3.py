"""Testes da Fase 3: granularidade cláusula/parágrafo, contexto e XLSX.

Convenção do CRL para 2025: o código de nível cláusula (_identif) marca a
cláusula inteira; os subcódigos marcam números/alíneas (parágrafos).
As peritas recebem XLSX com o contexto de cada segmento.
"""
from pathlib import Path

import openpyxl

from cct.extractor import estruturar
from cct.lexical import codificar
from cct.export_xlsx import exportar_xlsx

EXEMPLO = """Preâmbulo do contrato coletivo.
CAPÍTULO I
Disposições gerais
Cláusula 1.ª
Processo individual
1- O empregador mantém um registo de pessoal de cada trabalhador.
2- O trabalhador tem direito a consultar o seu processo individual.
a) A consulta é gratuita;
b) A consulta pode ser acompanhada.
Cláusula 2.ª
Quotização sindical
1- O empregador desconta a quota sindical mediante autorização.
"""

CODEBOOK = {
    "tema": "t",
    "eixos": ["4.08.5"],
    "codigos": [
        {"id": "4.08.5.1", "termos": ["registo de pessoal", "processo individual"]},
        {"id": "4.08.5.3", "termos": ["quota sindical"],
         "condicoes": {"requer_algum": ["dados", "tratamento", "informação"]}},
    ],
}


def _doc():
    return estruturar(EXEMPLO, doc_id="teste")


# ---------- parágrafos ----------

def test_clausula_subsegmentada_em_paragrafos():
    doc, texto = _doc()
    cl1 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))
    paras = [n for n in doc["nos"] if n["tipo"] == "paragrafo" and n["pai"] == cl1["id"]]
    assert len(paras) == 4  # 1-, 2-, a), b)
    assert all(not p.get("folha") for p in paras)
    # offsets dentro da cláusula e conteúdo certo
    assert texto[paras[0]["char_start"]:paras[0]["char_end"]].startswith("1- O empregador")
    assert texto[paras[2]["char_start"]:paras[2]["char_end"]].startswith("a) A consulta")


def test_zero_perda_mantida_com_paragrafos():
    doc, texto = _doc()
    folhas = [n for n in doc["nos"] if n.get("folha")]
    assert "".join(texto[n["char_start"]:n["char_end"]] for n in folhas) == texto


# ---------- anotação a dois níveis ----------

def test_anotacao_nivel_paragrafo_e_identif():
    # convenção atualizada (memo 1 de 06/07): o eixo-pai marca a cláusula
    # inteira; o subcódigo marca apenas os números/alíneas com match
    doc, texto = _doc()
    anot = codificar(doc, texto, CODEBOOK)["anotacoes"]
    a51 = [a for a in anot if a["codigo"] == "4.08.5.1"]
    assert {a.get("nivel") for a in a51} == {"paragrafo"}
    trechos = [texto[a["char_start"]:a["char_end"]] for a in a51]
    assert any(t.startswith("1- O empregador") for t in trechos)
    assert any(t.startswith("2- O trabalhador") for t in trechos)
    # a alínea a) não contém termos → não é anotada
    assert not any(t.startswith("a)") for t in trechos)
    # o eixo 4.08.5 marca a cláusula inteira, uma única vez
    eixo = [a for a in anot if a["codigo"] == "4.08.5"]
    assert len(eixo) == 1 and eixo[0]["nivel"] == "clausula"
    assert "1- O empregador" in texto[eixo[0]["char_start"]:eixo[0]["char_end"]]


def test_condicao_requer_algum_bloqueia_falso_positivo():
    doc, texto = _doc()
    anot = codificar(doc, texto, CODEBOOK)["anotacoes"]
    # "quota sindical" existe, mas a cláusula não fala de dados/tratamento
    assert not any(a["codigo"] == "4.08.5.3" for a in anot)


def test_condicao_excluir():
    cb = {"tema": "t", "codigos": [
        {"id": "X", "termos": ["vigilância"],
         "condicoes": {"excluir": ["comissão de vigilância"]}}]}
    doc, texto = estruturar(
        "Cláusula 1.ª\nFiscalização\n1- A comissão de vigilância reúne mensalmente.\n",
        doc_id="t")
    anot = codificar(doc, texto, cb)["anotacoes"]
    assert not anot


# ---------- XLSX para as peritas ----------

def test_xlsx_com_contexto(tmp_path):
    doc, texto = _doc()
    anot = codificar(doc, texto, CODEBOOK)
    destino = tmp_path / "peritas.xlsx"
    exportar_xlsx([(doc, texto, anot)], destino)
    ws = openpyxl.load_workbook(destino).active
    linhas = list(ws.iter_rows(values_only=True))
    cab = list(linhas[0])
    for col in ["Código", "Nível", "Segmento", "Cláusula", "Contexto",
                "Documento", "Confiança", "Método"]:
        assert col in cab
    dados = [dict(zip(cab, l)) for l in linhas[1:]]
    seg = next(d for d in dados if d["Nível"] == "paragrafo"
               and str(d["Segmento"]).startswith("2- O trabalhador"))
    assert seg["Cláusula"].startswith("Cláusula 1.ª - Processo individual")
    assert "CAPÍTULO I" in seg["Contexto"]
    assert seg["Documento"] == "teste"
