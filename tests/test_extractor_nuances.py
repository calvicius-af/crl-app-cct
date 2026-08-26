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


# ---------- número de parágrafo sem separador ----------

def test_numero_sem_separador_recuperado():
    # AguasSerraEstrela: o PDF tem "3- São considerados", o docling dá "3São"
    texto = "Artigo 5.º\nCargos\n3São considerados cargos de interesse público.\n"
    _doc, final = estruturar(texto, "t")
    assert "3- São considerados" in final


def test_numero_composto_sem_separador():
    texto = "Artigo 5.º\nFatores\n2.1No fator antiguidade entra o número de anos.\n"
    _doc, final = estruturar(texto, "t")
    assert "2.1- No fator" in final


def test_nao_mexe_em_ano_nem_em_ordinal():
    texto = ("Cláusula 1.ª\nÂmbito\n"
             "1- O acordo de 2025 aplica-se.\n"
             "2- Vigora desde o 12.º ano de escolaridade.\n")
    _doc, final = estruturar(texto, "t")
    assert "de 2025 aplica-se" in final and "12.º ano" in final


# ---------- numeração: ordinais a sério ----------

def test_titulo_de_capitulo_nao_vira_clausula_vazia():
    # AguasNorte: o CAPÍTULO XV chama-se "Cláusula geral e transitória" e
    # a palavra "geral" era lida como número de cláusula
    texto = ("CAPÍTULO XV\nCláusula geral e transitória\n"
             "Cláusula 73.ª\nCláusula geral e transitória\n"
             "1- Todas as disposições que violem a lei não são aplicáveis.\n")
    doc, _ = estruturar(texto, "t")
    rotulos = [n["rotulo"] for n in doc["nos"] if n["tipo"] == "clausula"]
    assert rotulos == ["Cláusula 73.ª - Cláusula geral e transitória"]
    cap = [n["rotulo"] for n in doc["nos"] if n["tipo"] == "capitulo"]
    assert cap == ["CAPÍTULO XV - Cláusula geral e transitória"]


def test_numeracao_por_extenso_continua_reconhecida():
    texto = ("Cláusula décima segunda\nFérias\n1- O trabalhador tem direito.\n")
    doc, _ = estruturar(texto, "t")
    cl = [n["rotulo"] for n in doc["nos"] if n["tipo"] == "clausula"]
    assert cl == ["Cláusula décima segunda - Férias"]


def test_marcador_de_travessao_colado_faz_paragrafo():
    # TRATOLIXO: "-25 % pela primeira hora" é uma alínea, não texto corrido
    texto = ("Cláusula 76.ª - Acréscimos\n1- Os acréscimos são:\n"
             "-25 % pela primeira hora;\n-37,5 % pelas seguintes;\n")
    doc, _ = estruturar(texto, "t")
    assert sum(1 for n in doc["nos"] if n["tipo"] == "paragrafo") == 3
