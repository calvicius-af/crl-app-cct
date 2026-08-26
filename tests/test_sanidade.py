"""Controlos de sanidade da extração (revisão MaxQDA de 2026-08-25).

Os dois padrões foram medidos no corpus antes de virarem controlo: a nota
de depósito do art. 494.º CT existe nas 4 convenções verificadas e fecha
o documento; cláusulas sem corpo só aparecem quando algo correu mal na
ordem de leitura.
"""
from cct.extractor import estruturar
from cct.sanidade import clausulas_sem_corpo, deposito_no_fim, verificar

DEPOSITO = ("Depositado em 23 de janeiro de 2025, a fl. 87 do livro n.º 13, "
            "com o n.º 23/2025, nos termos do artigo 494.º do Código do "
            "Trabalho, aprovado pela Lei n.º 7/2009, de 12 de fevereiro.")

BOM = ("Cláusula 8.ª - Deveres\n"
       "1- O trabalhador deve cumprir as disposições deste AE.\n"
       "Cláusula 9.ª - Garantias\n"
       "É proibido à empresa opor-se ao exercício dos direitos.\n"
       + DEPOSITO + "\n")


# ---------- nota de depósito ----------

def test_deposito_no_fim_aceita_as_duas_formas():
    assert deposito_no_fim("Texto.\n" + DEPOSITO + "\n") is None
    assert deposito_no_fim("Texto.\nDepositado a 17 de julho de 2025, a fl. 111.\n") is None


def test_deteta_texto_depois_do_deposito():
    # AguasNorte e AguasSerraEstrela: matéria de anexos aparecia no fim
    aviso = deposito_no_fim(DEPOSITO + "\n2- Reenquadramento nas categorias.\n")
    assert aviso and "depois da nota de depósito" in aviso


def test_deteta_ausencia_do_deposito():
    aviso = deposito_no_fim("Cláusula 1.ª - Âmbito\n1- Aplica-se a todos.\n")
    assert aviso and "sem nota de depósito" in aviso


# ---------- cláusulas sem corpo ----------

def test_clausula_vazia_e_detetada():
    # LAGOSemFORMA: o conteúdo da cláusula 9.ª tinha ido parar antes do
    # cabeçalho, deixando a cláusula vazia
    texto = ("Cláusula 9.ª - Garantias do trabalhador\n"
             "CAPÍTULO IV - Categorias profissionais\n"
             "Cláusula 10.ª - Categorias\n"
             "1- As categorias constam do anexo II.\n")
    doc, final = estruturar(texto, "t")
    falhas = clausulas_sem_corpo(doc, final)
    assert any("Cláusula 9.ª" in f and "sem conteúdo" in f for f in falhas)


def test_corpo_sem_ponto_final_e_detetado():
    texto = ("Cláusula 1.ª - Âmbito\n"
             "1- Aplica-se a todos os trabalhadores\n")
    doc, final = estruturar(texto, "t")
    assert any("sem frase terminada" in f for f in clausulas_sem_corpo(doc, final))


def test_documento_saudavel_nao_gera_avisos():
    doc, final = estruturar(BOM, "t")
    assert verificar(doc, final) == []


def test_tabela_no_corpo_conta_como_conteudo():
    # uma cláusula que remete para tabela tem texto antes dela; o controlo
    # não pode disparar por a tabela em si não ter ponto final
    texto = ("Cláusula 21.ª - Retribuição\n"
             "1- A retribuição consta da tabela seguinte.\n"
             "Níveis | Escalão 1\n"
             "1 | 1 234,56\n")
    doc, final = estruturar(texto, "t")
    assert clausulas_sem_corpo(doc, final) == []
