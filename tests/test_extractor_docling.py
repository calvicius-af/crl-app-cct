"""Testes do extrator docling — limpeza APP_CCT do Markdown.

Cobrem os problemas do QA MaxQDA de 2026-08-24 (4 convenções verificadas)
e os artefactos observados no ensaio docling desse dia: placeholder de
imagem do logótipo BTE, mobiliário de cabeçalho, translineação residual,
tabelas Markdown e escapes.
"""
from cct.extractor import MARCA_TABELA_FIM, MARCA_TABELA_INI, estruturar
from cct.extractor_docling import markdown_para_texto


def test_remove_placeholder_de_imagem():
    texto = markdown_para_texto("1- Primeiro número.\n\n<!-- image -->\n\n2- Segundo número.")
    assert "image" not in texto
    assert "1- Primeiro número." in texto and "2- Segundo número." in texto


def test_remove_mobiliario_bte():
    md = "Boletim do Trabalho e Emprego   40\n\n29 outubro 2025\n\n42\n\nTexto útil."
    texto = markdown_para_texto(md)
    assert texto.strip() == "Texto útil."


def test_dissolve_cabecalhos_markdown():
    md = "## Cláusula 22.ª\n\n## Descanso diário\n\n1- O trabalhador tem direito."
    texto = markdown_para_texto(md)
    assert "##" not in texto
    assert "Cláusula 22.ª" in texto


def test_estruturar_reconhece_clausula_com_titulo_em_linhas_separadas():
    md = "## Cláusula 22.ª\n\n## Descanso diário\n\n1- O trabalhador tem direito."
    doc, _ = estruturar(markdown_para_texto(md), "t")
    cl = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    assert cl and cl[0]["rotulo"] == "Cláusula 22.ª - Descanso diário"


def test_repara_translineacao_residual():
    texto = markdown_para_texto("As admissões respeitam o enquadramento do recruta -mento.")
    assert "recrutamento" in texto


def test_nao_junta_travessao_legitimo():
    texto = markdown_para_texto("O AE - adiante designado acordo - aplica-se.")
    assert " - adiante" in texto


def test_tabela_markdown_vira_sentinelas():
    md = ("## ANEXO I\n\n"
          "| Níveis | Escalão 1 | Escalão 2 |\n"
          "|--------|-----------|-----------|\n"
          "| 1      | 2 984,59  | 3 282,18  |\n")
    texto = markdown_para_texto(md)
    assert MARCA_TABELA_INI in texto and MARCA_TABELA_FIM in texto
    assert "Níveis | Escalão 1 | Escalão 2" in texto
    assert "1 | 2 984,59 | 3 282,18" in texto
    assert "|---" not in texto


def test_item_de_lista_markdown_mantem_marcador_proprio():
    md = "- a) Ficha número 1 ao diretor;\n- 4- O presente AE aplica-se.\n- ponto solto"
    texto = markdown_para_texto(md)
    assert "a) Ficha número 1 ao diretor;" in texto
    assert "4- O presente AE aplica-se." in texto
    assert "- ponto solto" in texto  # bala sem marcador próprio mantém-se


def test_clausula_com_sufixo_de_letra():
    # LAGOSemFORMA 2025 tem "Cláusula 16.ª-A" … "16.ª-D" (aditadas em revisão)
    md = "## Cláusula 16.ª-D\n\n## Isenção de horário\n\n1- O regime aplica-se."
    doc, _ = estruturar(markdown_para_texto(md), "t")
    cl = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    assert cl and cl[0]["rotulo"] == "Cláusula 16.ª-D - Isenção de horário"


def test_desfaz_escapes_e_entidades():
    texto = markdown_para_texto("AVALIAÇÃO - 20\\_\n\nPontuação &gt;=17,5.")
    assert "20_" in texto and ">=17,5" in texto
