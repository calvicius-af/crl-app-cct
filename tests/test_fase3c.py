"""Testes dos memos 19-28 (06/07, 4_08_triado_v3).

- 19/22: consolidado detetado pela marca explícita mesmo em revisões globais;
- 20/24-28: assinaturas em qualquer ponto do documento, com padrão de data
  por extenso antes ou depois de "Pela/Pelo/Pelas/Pelos";
- 23: "Preâmbulo" reconhecido como cabeçalho (mantém quebras à volta).
"""
from cct.extractor import estruturar, juntar_linhas

GENERALI = """Acordo de empresa entre a Generali Seguros, SA e o SINAPSA - Alteração salarial e outras e texto consolidado.
Cláusula 1.ª - Objeto
O presente acordo altera as cláusulas seguintes.
Cláusula 2.ª - Tabela
A tabela salarial é atualizada.
Lisboa, 12 de maio de 2025.
Pela Generali Seguros, SA:
António Silva, mandatário.
Pelo SINAPSA:
José Costa, mandatário.
Texto consolidado
CAPÍTULO I
Âmbito
Cláusula 1.ª - Âmbito
O presente acordo obriga a Generali.
"""


def test_consolidado_por_marca_mesmo_em_revisao_global():
    # memo 19: o gate por subtipo falhava o GENERALI (revisão global c/ consolidado)
    doc, _ = estruturar(GENERALI, doc_id="t", subtipo="revisao_global")
    ambito = [n for n in doc["nos"] if n["rotulo"] == "Cláusula 1.ª - Âmbito"]
    objeto = [n for n in doc["nos"] if n["rotulo"] == "Cláusula 1.ª - Objeto"]
    assert ambito and ambito[0]["origem"] == "consolidado"
    assert objeto and objeto[0]["origem"] == "novo"


def test_assinaturas_no_meio_do_documento():
    # memo 20: assinaturas entre as alterações e o texto consolidado
    doc, texto = estruturar(GENERALI, doc_id="t", subtipo="revisao_global")
    ass = [n for n in doc["nos"] if n["rotulo"] == "ASSINATURAS"]
    assert ass, "bloco de assinaturas não detetado"
    trecho = texto[ass[0]["char_start"]:ass[0]["char_end"]]
    assert "Pela Generali" in trecho
    assert "Texto consolidado" not in trecho  # termina antes do consolidado


def test_assinaturas_comecam_na_data_por_extenso():
    # memo 24: data por extenso seguida de "Pela …" pertence às assinaturas
    doc, texto = estruturar(GENERALI, doc_id="t", subtipo="revisao_global")
    ass = next(n for n in doc["nos"] if n["rotulo"] == "ASSINATURAS")
    assert "Lisboa, 12 de maio de 2025" in texto[ass["char_start"]:ass["char_end"]]


def test_assinaturas_antes_da_data():
    # memos 27/28: padrão invertido — "Pela …" antes da data de outorga
    texto = ("Cláusula 30.ª - Vigência\nO acordo vigora por 24 meses.\n"
             "Pela Caixa Económica:\nJoão Sousa.\nPelo SNQTB:\nRui Melo.\n"
             "Lisboa, 3 de março de 2025.\n")
    doc, t = estruturar(texto, doc_id="t")
    ass = next(n for n in doc["nos"] if n["rotulo"] == "ASSINATURAS")
    trecho = t[ass["char_start"]:ass["char_end"]]
    assert trecho.startswith("Pela Caixa") and "3 de março" in trecho


def test_preambulo_como_cabecalho():
    # memo 23: a linha "Preâmbulo" não pode ser fundida com o texto seguinte
    texto = ("Acordo de empresa entre a AdIN e o STAL\nPreâmbulo\n"
             "Cumpre em primeiro lugar referir que a existência de qualquer organização,\n"
             "pressupõe respostas colectivas.")
    saida = juntar_linhas(texto)
    assert "\nPreâmbulo\n" in saida
    assert "organização, pressupõe" in saida  # parágrafo continua a juntar-se
