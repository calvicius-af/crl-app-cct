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
