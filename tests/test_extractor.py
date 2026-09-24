"""Testes do extrator PDF→doc.json — Fase 1.

Cobrem diretamente o feedback do gate da Fase 0 (memos MaxQDA de 2026-07-05):
- Anotações 1, 5, 6: quebras de linha a meio de frase são inaceitáveis;
- Anotação 2: rótulo da cláusula deve incluir o título ("Cláusula 1.ª - Âmbito");
- Anotação 3: cabeçalho de capítulo numa só linha ("CAPÍTULO I - Âmbito, ...");
- Anotação 7: fronteiras de segmento corretas.
"""
from pathlib import Path

import pytest

from cct.extractor import (MARCA_COLUNA, MARCA_TABELA_FIM, MARCA_TABELA_INI,
                           _remover_cabecalhos_rodapes, juntar_linhas,
                           estruturar, extrair_pdf)
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


def test_marcas_de_tabela_repetidas_nao_sao_cabecalho_bte():
    """BTE 31: tabelas em 2 de 3 páginas não podem perder delimitadores."""
    paginas = [
        "Boletim do Trabalho e Emprego\nTexto inicial.",
        ("Boletim do Trabalho e Emprego\nANEXO III - Tabela salarial\n"
         f"{MARCA_TABELA_INI}\nGrupo | Valor\nA | 100\nB | 200\n"
         f"{MARCA_TABELA_FIM}"),
        ("Boletim do Trabalho e Emprego\n"
         f"{MARCA_TABELA_INI}\nGrupo | Valor\nC | 300\nD | 400\n"
         f"{MARCA_TABELA_FIM}\nAssinaturas."),
    ]
    limpas = _remover_cabecalhos_rodapes(paginas)
    assert all("Boletim do Trabalho e Emprego" not in p for p in limpas)
    assert sum(p.count(MARCA_TABELA_INI) for p in limpas) == 2
    assert sum(p.count(MARCA_TABELA_FIM) for p in limpas) == 2
    assert sum(p.count("Grupo | Valor") for p in limpas) == 2, (
        "cabeçalhos de tabela repetidos são conteúdo, não mobiliário do BTE")
    _, texto = estruturar("\n".join(limpas), "teste")
    assert "Grupo | Valor\nA | 100\nB | 200" in texto
    assert "C | 300\nD | 400" in texto


def _pagina(n: int, corpo: str) -> str:
    return (f"Boletim do Trabalho e Emprego, n.º 31, 22/8/2026\n{corpo}\n"
            f"BTE 31 | {n}\n{n}")


def test_frase_repetida_no_corpo_nao_e_mobiliario():
    """Issue #47: uma frase legítima repetida em várias páginas desaparecia
    só por atingir o limiar de repetição. Agora só se remove o que se
    repete no topo ou no fundo das páginas."""
    corpo = ("Cláusula {n}.ª - Revogada\nTexto anterior da cláusula.\n"
             "O disposto no número anterior não prejudica os direitos adquiridos.\n"
             "Texto posterior da cláusula.")
    paginas = [_pagina(n, corpo.format(n=n)) for n in range(1, 6)]
    junto = "\n".join(_remover_cabecalhos_rodapes(paginas))
    assert junto.count("O disposto no número anterior não prejudica") == 5
    assert "Boletim do Trabalho e Emprego" not in junto
    assert "BTE 31 |" not in junto
    assert not any(l.strip().isdigit() for l in junto.split("\n")), \
        "o número da página, sozinho no fundo, é mobiliário"


def test_numero_sozinho_a_meio_da_pagina_fica():
    """Um número numa linha própria a meio da página é conteúdo (por
    exemplo, uma célula de uma grelha que o pdfplumber não detetou)."""
    corpo = "Primeira linha.\nSegunda linha.\nTerceira linha.\n1250\nQuarta linha.\nQuinta."
    limpas = _remover_cabecalhos_rodapes([_pagina(n, corpo) for n in range(1, 4)])
    assert all("\n1250\n" in p for p in limpas)


def test_mobiliario_de_paginas_em_duas_colunas():
    """Numa página em duas colunas o cabeçalho parte-se entre as duas; cada
    coluna tem as suas margens, e a marca de coluna não chega ao texto."""
    paginas = [
        (f"Boletim do Trabalho\nTexto da esquerda {n}.\nMais texto {n}.\n"
         f"Continua a esquerda {n}.\n{n}\n{MARCA_COLUNA}\n"
         f"e Emprego, n.º 3\nTexto da direita {n}.\nAinda a direita {n}.\n"
         f"Fim da direita {n}.")
        for n in range(10, 14)
    ]
    junto = "\n".join(_remover_cabecalhos_rodapes(paginas))
    assert MARCA_COLUNA not in junto
    assert "Boletim do Trabalho" not in junto and "e Emprego, n.º 3" not in junto
    assert junto.count("Texto da direita") == 4 and junto.count("Fim da direita") == 4


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


# ---------- PDF sintéticos: rotação e colunas (corpus de 24-09-2026) ----------

def _tabela_rodada(sentido, y0=300, logica=None):
    """Tabela «Nível | Valor» desenhada a 90º, com grelha, como as dos CARRISTUR.

    Na página, cada linha lógica da tabela é uma coluna; «btt» lê-se de baixo
    para cima (cabeçalho à esquerda), «ttb» de cima para baixo (à direita).
    """
    from tests.pdf_sintetico import grelha
    logica = logica or [["Nível", "Valor"], ["A", "1 355,48"], ["B", "1 200,00"]]
    x0, w, h = 100, 20, 70
    itens = grelha(x0, y0, [w] * 3, [h] * 2)
    for i, linha in enumerate(logica):
        for j, texto in enumerate(linha):
            if sentido == "btt":        # linha i: coluna i; coluna j: de baixo
                itens.append((x0 + w * i + 15, y0 + h * j + 5, texto, "rodado"))
            else:                       # linha i: coluna da direita; coluna j: de cima
                itens.append((x0 + w * (2 - i) + 5, y0 + h * (2 - j) - 5, texto,
                              "rodado_horario"))
    return [[(72, 780, "Assim, na página 225, onde se lê:"), *itens]]


@pytest.mark.parametrize("sentido", ["btt", "ttb"])
def test_tabela_rodada_sai_de_pe_e_legivel(tmp_path, sentido):
    """ISSUE-0020 e #42: as tabelas rodadas saíam com as palavras invertidas
    («levíN», «rolaV») e com as linhas trocadas pelas colunas."""
    from tests.pdf_sintetico import escrever_pdf
    pdf = escrever_pdf(tmp_path / "x.pdf", _tabela_rodada(sentido))
    _doc, texto = extrair_pdf(pdf)
    assert "Nível | Valor\nA | 1 355,48\nB | 1 200,00" in texto, texto


def test_tabela_com_coluna_do_meio_vazia_nao_e_cortada_em_colunas(tmp_path):
    """377, «Enquadramento das profissões»: a coluna do meio quase vazia fazia
    a página passar por duas colunas; o corte separava a primeira coluna da
    terceira e punha o cabeçalho do BTE a meio do texto."""
    from tests.pdf_sintetico import escrever_pdf, grelha
    linhas = 10
    itens = grelha(40, 200, [200, 60, 200], [30] * linhas)
    for k in range(linhas):
        y = 200 + 30 * (linhas - 1 - k) + 10
        itens.append((45, y, f"Categoria profissional número {k}"))
        itens.append((305, y, f"Técnico administrativo de segunda {k}"))
    pdf = escrever_pdf(tmp_path / "x.pdf", [[(200, 760, "Enquadramento das profissões"), *itens]])
    _doc, texto = extrair_pdf(pdf)
    assert "Categoria profissional número 3 |  | Técnico administrativo de segunda 3" in texto, texto


def test_duas_colunas_de_texto_sem_grelha_continuam_a_ser_cortadas(tmp_path):
    """O BTE antigo em duas colunas continua a ler-se coluna a coluna."""
    from tests.pdf_sintetico import escrever_pdf
    itens = []
    for k in range(25):
        itens.append((40, 760 - 14 * k, f"Esquerda linha {k} do texto."))
        itens.append((320, 760 - 14 * k, f"Direita linha {k} do texto."))
    pdf = escrever_pdf(tmp_path / "x.pdf", [itens])
    _doc, texto = extrair_pdf(pdf)
    assert texto.index("Esquerda linha 24") < texto.index("Direita linha 0"), texto


def test_texto_ao_lado_de_uma_tabela_nao_se_perde(tmp_path):
    """As bandas só liam acima e abaixo das tabelas: o que estava ao lado,
    na mesma altura, desaparecia (CARRISTUR: «Deve ler-se:» e o título)."""
    from tests.pdf_sintetico import escrever_pdf, grelha
    itens = [(72, 780, "Texto antes da tabela."), *grelha(300, 500, [100, 100], [30, 30])]
    itens += [(305, 540, "Nível"), (405, 540, "Valor"), (305, 510, "A"), (405, 510, "100")]
    itens += [(72, 530, "Deve ler-se:"), (72, 400, "Texto depois da tabela.")]
    pdf = escrever_pdf(tmp_path / "x.pdf", [itens])
    _doc, texto = extrair_pdf(pdf)
    assert "Deve ler-se:" in texto
    assert texto.index("Deve ler-se:") < texto.index("Nível | Valor"), texto


def test_pagina_rodada_com_titulo_ao_lado_da_tabela(tmp_path):
    """A página inteira rodada dos CARRISTUR: o título está «acima» da tabela
    na leitura, mas à esquerda dela na página."""
    from tests.pdf_sintetico import escrever_pdf
    pagina = _tabela_rodada("btt")
    pagina[0].append((80, 300, "ANEXO II Quadro remuneratório", "rodado"))
    pdf = escrever_pdf(tmp_path / "x.pdf", pagina)
    _doc, texto = extrair_pdf(pdf)
    # o estruturar reconhece o anexo e escreve o rótulo «ANEXO II - …»
    assert "ANEXO II - Quadro remuneratório\nNível | Valor" in texto, texto
    assert "\no\n" not in texto and not texto.rstrip().endswith("\nA"), \
        "nenhuma letra solta de uma linha rodada partida"


def test_cabecalho_vertical_numa_tabela_direita(tmp_path):
    """382: células de cabeçalho escritas na vertical, numa grelha direita,
    saíam invertidas («levíN») ou faltavam."""
    from tests.pdf_sintetico import escrever_pdf, grelha
    # de baixo para cima: duas linhas de dados e o cabeçalho, mais alto
    itens = grelha(100, 400, [60, 60, 60], [20, 20, 80])
    itens += [(135, 445, "Nível", "rodado"), (195, 445, "Escalão", "rodado"),
              (255, 445, "Valor", "rodado")]
    for y, (a, b, c) in ((425, ("I", "1", "900")), (405, ("II", "2", "950"))):
        itens += [(105, y, a), (165, y, b), (225, y, c)]
    itens += [(72, 780, "Categoria profissional e remuneração mensal."),
              (72, 766, "Texto da página em linhas direitas, como no corpo da convenção.")]
    pdf = escrever_pdf(tmp_path / "x.pdf", [itens])
    _doc, texto = extrair_pdf(pdf)
    assert "Nível | Escalão | Valor\nI | 1 | 900\nII | 2 | 950" in texto, texto
    assert "levíN" not in texto


def test_tabelas_rodadas_lado_a_lado_nao_se_repetem(tmp_path):
    """382, p34: várias grelhas rodadas na mesma página deitada. As faixas
    entre tabelas cobriam a página inteira e voltavam a ler as outras
    tabelas: 2527 palavras a mais no corpus."""
    from tests.pdf_sintetico import escrever_pdf
    [a] = _tabela_rodada("btt", y0=150)
    [b] = _tabela_rodada("btt", y0=450, logica=[["Carreira", "Nível"],
                                               ["Técnico", "XII"], ["Diretor", "XVI"]])
    pdf = escrever_pdf(tmp_path / "x.pdf", [a + b[1:]])
    _doc, texto = extrair_pdf(pdf)
    assert texto.count("1 355,48") == 1 and texto.count("Diretor") == 1, texto
    assert "Nível | Valor\nA | 1 355,48" in texto
    assert "Carreira | Nível\nTécnico | XII\nDiretor | XVI" in texto


def test_negrito_simulado_nao_duplica_letras(tmp_path):
    """O mesmo carácter desenhado duas vezes, meio ponto ao lado: «CCaarrrreeiirraa»."""
    from tests.pdf_sintetico import escrever_pdf
    pdf = escrever_pdf(tmp_path / "x.pdf", [[(72, 700, "Carreira Técnica"),
                                             (72.3, 700, "Carreira Técnica")]])
    _doc, texto = extrair_pdf(pdf)
    assert texto.strip() == "Carreira Técnica", texto
