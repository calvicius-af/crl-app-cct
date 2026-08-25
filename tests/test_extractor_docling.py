"""Testes do extrator docling — limpeza APP_CCT dos itens do documento.

Cobrem os problemas do QA MaxQDA de 2026-08-24/25 (4 convenções
verificadas) e os artefactos do ensaio docling: mobiliário do BTE,
translineação residual, e as células repetidas que a grelha do docling
produz para cada coluna abrangida por um colspan (ISSUE-0003).
"""
from types import SimpleNamespace

from cct.extractor import estruturar
from cct.extractor_docling import (celulas_sem_colspan, limpar_texto_item)


def _celula(texto: str, inicio: int):
    return SimpleNamespace(text=texto, start_col_offset_idx=inicio)


# ---------- limpeza de itens de texto ----------

def test_descarta_mobiliario_bte():
    assert limpar_texto_item("Boletim do Trabalho e Emprego   40") is None
    assert limpar_texto_item("29 outubro 2025") is None
    assert limpar_texto_item("42") is None
    assert limpar_texto_item("   ") is None


def test_mantem_texto_util():
    assert limpar_texto_item("1- O trabalhador tem direito.") == \
        "1- O trabalhador tem direito."


def test_repara_translineacao_residual():
    assert "recrutamento" in limpar_texto_item(
        "As admissões respeitam o enquadramento do recruta -mento.")


def test_nao_junta_travessao_legitimo():
    assert " - adiante" in limpar_texto_item("O AE - adiante designado acordo.")


def test_normaliza_quebras_internas():
    assert limpar_texto_item("primeira\nsegunda") == "primeira segunda"


# ---------- tabelas: colspan vs repetição legítima ----------

def test_colapsa_celulas_de_colspan():
    # perfil de função do TRATOLIXO: "Competência" abrange 3 colunas
    linha = [_celula("Competência", 0), _celula("Competência", 0),
             _celula("Competência", 0), _celula("Encarregado geral (DI)", 3)]
    assert celulas_sem_colspan(linha) == ["Competência", "Encarregado geral (DI)"]


def test_mantem_valores_repetidos_em_colunas_distintas():
    # tabela de remunerações do AguasNorte: nível M é "n.a." em todas as
    # colunas — são células distintas, não um colspan; têm de sobreviver
    linha = [_celula("M", 0)] + [_celula("n.a.", i) for i in range(1, 5)]
    assert celulas_sem_colspan(linha) == ["M", "n.a.", "n.a.", "n.a.", "n.a."]


def test_celula_vazia_mantem_a_coluna():
    linha = [_celula("Montante", 0), None, _celula("1 385,99 €", 2)]
    assert celulas_sem_colspan(linha) == ["Montante", "", "1 385,99 €"]


# ---------- integração com o estruturar ----------

def test_clausula_com_titulo_em_itens_separados():
    texto = "Cláusula 22.ª\nDescanso diário\n1- O trabalhador tem direito.\n"
    doc, _ = estruturar(texto, "t")
    cl = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    assert cl and cl[0]["rotulo"] == "Cláusula 22.ª - Descanso diário"


def test_clausula_com_sufixo_de_letra():
    # LAGOSemFORMA 2025 tem "Cláusula 16.ª-A" … "16.ª-D" (aditadas em revisão)
    texto = "Cláusula 16.ª-D\nIsenção de horário\n1- O regime aplica-se.\n"
    doc, _ = estruturar(texto, "t")
    cl = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    assert cl and cl[0]["rotulo"] == "Cláusula 16.ª-D - Isenção de horário"


# ---------- ordem de leitura pela geometria ----------

def _bbox(l, r, t, origem_em_baixo=True):
    from docling_core.types.doc.base import CoordOrigin
    return SimpleNamespace(
        l=l, r=r, t=t,
        coord_origin=CoordOrigin.BOTTOMLEFT if origem_em_baixo
        else CoordOrigin.TOPLEFT)


def test_repoe_bloco_emitido_fora_de_sitio():
    # LAGOSemFORMA p.5: o docling emitia o corpo da cláusula 9.ª (mais
    # abaixo na página) antes das alíneas da 8.ª e do próprio cabeçalho
    from cct.extractor_docling import ordenar_por_leitura
    A, L = 841.0, 595.0
    itens = [("corpo da 9.ª", 5, _bbox(79, 518, 400.0), A, L),
             ("alíneas da 8.ª", 5, _bbox(79, 518, 742.0), A, L),
             ("Cláusula 9.ª", 5, _bbox(273, 324, 436.0), A, L)]
    assert [i[0] for i in ordenar_por_leitura(itens)] == \
        ["alíneas da 8.ª", "Cláusula 9.ª", "corpo da 9.ª"]


def test_respeita_a_ordem_das_paginas():
    from cct.extractor_docling import ordenar_por_leitura
    A, L = 841.0, 595.0
    itens = [("p2 topo", 2, _bbox(79, 518, 700.0), A, L),
             ("p1 fundo", 1, _bbox(79, 518, 100.0), A, L)]
    assert [i[0] for i in ordenar_por_leitura(itens)] == ["p1 fundo", "p2 topo"]


def test_duas_colunas_lidas_uma_de_cada_vez():
    # BTE antigos: a coluna esquerda inteira antes da direita
    from cct.extractor_docling import ordenar_por_leitura
    A, L = 841.0, 595.0
    itens = ([(f"dir {i}", 1, _bbox(310, 560, 700.0 - i * 20), A, L) for i in range(6)]
             + [(f"esq {i}", 1, _bbox(40, 280, 700.0 - i * 20), A, L) for i in range(6)])
    nomes = [i[0] for i in ordenar_por_leitura(itens)]
    assert nomes[:6] == [f"esq {i}" for i in range(6)]
    assert nomes[6:] == [f"dir {i}" for i in range(6)]


def test_item_sem_geometria_fica_onde_estava():
    from cct.extractor_docling import ordenar_por_leitura
    A, L = 841.0, 595.0
    itens = [("primeiro", 1, _bbox(79, 518, 700.0), A, L),
             ("sem prov", 0, None, 0.0, 0.0),
             ("terceiro", 1, _bbox(79, 518, 500.0), A, L)]
    assert [i[0] for i in ordenar_por_leitura(itens)] == \
        ["primeiro", "sem prov", "terceiro"]


# ---------- bala de lista duplicada ----------

def test_bala_nao_duplica_marcador_proprio():
    from cct.extractor_docling import RE_MARCADOR_PROPRIO
    # "- -25 % pela primeira hora" no TRATOLIXO (1321 ocorrências)
    assert RE_MARCADOR_PROPRIO.match("-25 % pela primeira hora ou fração desta;")
    assert RE_MARCADOR_PROPRIO.match("–Técnica superior;")
    assert not RE_MARCADOR_PROPRIO.match("Texto normal sem marcador")
