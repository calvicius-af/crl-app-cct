"""Nuances de reconhecimento apanhadas na revisão MaxQDA de 2026-08-25.

Três padrões que escapavam, com os respetivos guardas contra falsos
positivos (o objetivo é flexibilidade sem ruído novo):

- ordinal separado do número pelo PDF ("Artigo 1. º");
- pontuação forte seguida de fecho de parêntesis ("(Valores em euros.)");
- fim do bloco de título da convenção ("… - Revisão global").
"""
from cct.extractor import estruturar, juntar_linhas


# ---------- ordinal separado ----------

def test_rotulo_de_artigo_com_ordinal_separado():
    # AguasSerraEstrela: o docling devolve "Artigo 1. º" e o rótulo saía
    # partido ao meio ("Artigo 1. - º")
    texto = "Artigo 1. º\nValoração das habilitações\n1- Por «habilitação» entende-se.\n"
    doc, _ = estruturar(texto, "t")
    art = [n for n in doc["nos"] if n["tipo"] == "artigo"]
    assert art and art[0]["rotulo"] == "Artigo 1.º - Valoração das habilitações"


def test_ordinal_separado_tambem_no_corpo():
    texto = "Artigo 1.º\nHabilitações\n1- Inferior ao 12. º ano de escolaridade.\n"
    _doc, final = estruturar(texto, "t")
    assert "12.º ano" in final


def test_nao_mexe_em_numeros_com_ponto_final():
    # "…do número 2. Os restantes…" não é um ordinal partido
    texto = "Cláusula 1.ª\nÂmbito\n1- Aplica-se o número 2. Os restantes seguem.\n"
    _doc, final = estruturar(texto, "t")
    assert "número 2. Os restantes" in final


# ---------- pontuação forte com fecho de parêntesis ----------

def test_parentesis_depois_do_ponto_fecha_a_frase():
    # TRATOLIXO: "(Valores em euros.)" colava-se ao título seguinte
    texto = "(Valores em euros.)\nRegulamento de Admissões e Carreiras"
    assert juntar_linhas(texto) == texto


def test_aspas_depois_do_ponto_fecham_a_frase():
    texto = 'Diz a norma «o trabalhador tem direito.»\nSegue-se outro parágrafo.'
    assert juntar_linhas(texto) == texto


def test_parentesis_sem_pontuacao_continua_a_juntar():
    # sem pontuação forte lá dentro, o parêntesis não fecha nada
    texto = "O acordo (adiante designado AE)\naplica-se a todos."
    assert juntar_linhas(texto) == "O acordo (adiante designado AE) aplica-se a todos."


# ---------- fim do bloco de título ----------

def test_titulo_da_convencao_separa_se_do_preambulo():
    texto = ("Acordo de empresa entre a Empresa X e o Sindicato Y - Revisão global\n"
             "Aos vinte dias do mês de janeiro de 2025, as partes acordam.")
    assert juntar_linhas(texto) == texto


def test_titulo_com_texto_consolidado():
    texto = ("Acordo coletivo entre a Empresa X e outras - Alteração salarial "
             "e outras e texto consolidado\n"
             "Aos dez dias do mês de março de 2025, as partes acordam.")
    assert juntar_linhas(texto) == texto


def test_a_regra_do_titulo_nao_se_aplica_ao_corpo():
    # a mesma expressão a meio do documento continua a juntar-se: a regra
    # vale só no cabeçalho, onde o bloco de título vive
    corpo = "\n".join(f"{i}- Número de enchimento do documento." for i in range(1, 25))
    texto = (corpo + "\nAs partes acordam proceder a uma revisão global\n"
             "do clausulado no prazo de um ano.")
    assert "revisão global do clausulado" in juntar_linhas(texto)
