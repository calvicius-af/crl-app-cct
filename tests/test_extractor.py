"""Testes do extrator PDF→doc.json — Fase 1.

Cobrem diretamente o feedback do gate da Fase 0 (memos MaxQDA de 2026-07-05):
- Anotações 1, 5, 6: quebras de linha a meio de frase são inaceitáveis;
- Anotação 2: rótulo da cláusula deve incluir o título ("Cláusula 1.ª - Âmbito");
- Anotação 3: cabeçalho de capítulo numa só linha ("CAPÍTULO I - Âmbito, ...");
- Anotação 7: fronteiras de segmento corretas.
"""
from pathlib import Path

import pytest

from cct.extractor import juntar_linhas, estruturar, extrair_pdf
from cct.schemas import validar_doc

PDF_BTE = Path(__file__).parent.parent / "data" / "raw" / "bte" / "bte2_2025.pdf"


# ---------- junção de linhas ----------

def test_junta_frase_partida_apos_virgula():
    # caso real da anotação 1: quebra após vírgula, linha seguinte com maiúscula
    texto = ("Contrato coletivo entre a Associação do Comércio e da Indústria de Panificação,\n"
             "Pastelaria e Similares - ACIP e a FESAHT - Federação dos Sindicatos")
    assert "Panificação, Pastelaria" in juntar_linhas(texto)


def test_junta_frase_sem_pontuacao_final():
    # caso real da anotação 5: quebra a meio de frase sem pontuação
    texto = ("2- O dever de obediência, a que se refere a alínea d) do número anterior, respeita tanto às ordens e\n"
             "instruções dadas directamente pelo empregador como às emanadas dos superiores hierárquicos")
    assert "ordens e instruções" in juntar_linhas(texto)


def test_mantem_quebra_apos_ponto_final():
    texto = "A cláusula termina aqui.\nOutra frase começa."
    assert juntar_linhas(texto) == texto


def test_mantem_quebra_antes_de_alinea_e_numero():
    texto = "os seguintes deveres:\na) Cumprir o horário;\nb) Zelar pelos bens;\n1- Primeiro número"
    assert juntar_linhas(texto) == texto


def test_mantem_quebra_antes_de_clausula_e_capitulo():
    texto = "texto anterior sem pontuacao final\nCláusula 2.ª\nCAPÍTULO II"
    saida = juntar_linhas(texto)
    assert "\nCláusula 2.ª" in saida
    assert "\nCAPÍTULO II" in saida


# ---------- estruturação ----------

EXEMPLO = """Contrato coletivo entre a ACIP e a FESAHT - Alteração salarial e outras/texto consolidado
CAPÍTULO I
Âmbito, área, vigência e denúncia do contrato
Cláusula 1.ª
Âmbito
1- O presente CCT obriga as empresas associadas da ACIP.
2- Este CCT abrange 3500 empresas e 13 500 trabalhadores.
Cláusula 2.ª
Área
O presente CCT aplica-se em todo o território nacional.
SECÇÃO I
Disposições gerais
Cláusula 3.ª - Vigência
Este CCT entra em vigor após a sua publicação.
ANEXO I
Tabela salarial
Artigo 1.º
Os valores são os constantes do quadro seguinte.
"""


def _estruturado():
    return estruturar(EXEMPLO, doc_id="teste")


def test_rotulo_da_clausula_inclui_titulo():
    doc, texto = _estruturado()
    rotulos = [n["rotulo"] for n in doc["nos"] if n["tipo"] == "clausula"]
    assert "Cláusula 1.ª - Âmbito" in rotulos
    assert "Cláusula 2.ª - Área" in rotulos
    assert "Cláusula 3.ª - Vigência" in rotulos  # título já na mesma linha


def test_titulo_da_clausula_fundido_no_texto():
    doc, texto = _estruturado()
    assert "Cláusula 1.ª - Âmbito\n" in texto
    # a linha do título não fica duplicada
    assert "Cláusula 1.ª\nÂmbito" not in texto


def test_capitulo_numa_so_linha():
    doc, texto = _estruturado()
    caps = [n for n in doc["nos"] if n["tipo"] == "capitulo"]
    assert caps and caps[0]["rotulo"] == "CAPÍTULO I - Âmbito, área, vigência e denúncia do contrato"
    assert "CAPÍTULO I - Âmbito" in texto


def test_hierarquia_pai():
    doc, _ = _estruturado()
    por_id = {n["id"]: n for n in doc["nos"]}
    cl1 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))
    assert por_id[cl1["pai"]]["tipo"] == "capitulo"
    cl3 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 3.ª"))
    assert por_id[cl3["pai"]]["tipo"] == "seccao"
    art = next(n for n in doc["nos"] if n["tipo"] == "artigo")
    assert por_id[art["pai"]]["tipo"] == "anexo"


def test_preambulo_e_zero_perda():
    doc, texto = _estruturado()
    assert doc["nos"][0]["tipo"] == "preambulo"
    folhas = [n for n in doc["nos"] if n.get("folha")]
    assert "".join(texto[n["char_start"]:n["char_end"]] for n in folhas) == texto
    validar_doc(doc)


# ---------- integração com o PDF real ----------

@pytest.mark.skipif(not PDF_BTE.exists(), reason="bte2_2025.pdf não disponível")
def test_pdf_real_acip_fesaht():
    doc, texto = extrair_pdf(PDF_BTE, paginas=(15, 49), doc_id="25_CCT_BTE_02_ACIP_FESAHT")
    validar_doc(doc)
    clausulas = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    assert len(clausulas) >= 80
    assert any(n["rotulo"] == "Cláusula 1.ª - Âmbito" for n in clausulas)
    # anotação 5: parágrafo do dever de obediência sem quebra interna
    assert "ordens e instruções dadas" in texto.replace("directamente", "directamente")
    assert "às ordens e\ninstruções" not in texto
    # sem cabeçalhos do BTE no corpo
    assert "Boletim do Trabalho e Emprego 2 15 janeiro 2025" not in texto
    # zero perda
    folhas = [n for n in doc["nos"] if n.get("folha")]
    assert "".join(texto[n["char_start"]:n["char_end"]] for n in folhas) == texto
