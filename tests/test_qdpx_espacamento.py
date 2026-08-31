"""Espaçamento do texto exportado para QDPX (ISSUE-0003 ponto 3, ISSUE-0004).

O texto canónico não tem linhas em branco — o estruturar descarta-as para
garantir a propriedade zero-perda e offsets estáveis. A legibilidade no
MaxQDA é conquistada na exportação: linha em branco antes de cada
cláusula/artigo e à volta das tabelas, com os offsets das seleções
remapeados no mesmo passo.

Contrato provado aqui (o exportador não promete igualdade literal): os
extremos apontam para o mesmo intervalo semântico e, dentro dele, só
podem existir as quebras que o exportador inseriu. A comparação remove
exatamente os índices de `indices_inseridos` — nunca normaliza espaço,
porque isso esconderia perda ou alteração real.
"""
import zipfile
import xml.etree.ElementTree as ET

from cct.extractor import MARCA_TABELA_FIM, MARCA_TABELA_INI, estruturar
from cct.qdpx import (espacar, exportar_qdpx, indices_inseridos,
                      pontos_de_espacamento, _remapear)

NS = {"q": "urn:QDA-XML:project:1.0"}

# como os extratores o entregam: as tabelas vêm entre sentinelas (é o que
# impede o juntar_linhas de as fundir num parágrafo)
TEXTO = ("Cláusula 21.ª - Retribuição\n"
         "1- A retribuição consta do anexo I.\n"
         "Cláusula 22.ª - Descanso diário\n"
         "1- O trabalhador tem direito a onze horas.\n"
         f"{MARCA_TABELA_INI}\n"
         "Níveis | Escalão 1 | Escalão 2\n"
         "1 | 1 234,56 | 1 345,67\n"
         f"{MARCA_TABELA_FIM}\n"
         "Assinaturas seguem-se ao texto.\n")


def _canonico():
    return estruturar(TEXTO, "teste")


def _sem_insercoes(exportado: str, inseridos: set[int],
                   inicio: int, fim: int) -> str:
    """Trecho exportado sem as quebras que o exportador acrescentou."""
    return "".join(c for i, c in enumerate(exportado[inicio:fim], start=inicio)
                   if i not in inseridos)


def _verificar_contrato(texto, doc, inicio, fim):
    """O trecho exportado, retiradas as inserções, é o trecho canónico."""
    pontos = pontos_de_espacamento(texto, doc)
    exportado = espacar(texto, pontos)
    inseridos = set(indices_inseridos(pontos))
    ini2, fim2 = _remapear(inicio, fim, pontos)
    assert _sem_insercoes(exportado, inseridos, ini2, fim2) == texto[inicio:fim]
    return exportado, inseridos, ini2, fim2


def _anotacao(doc, texto, trecho):
    inicio = texto.index(trecho)
    return {"doc_id": "teste", "anotacoes": [{
        "no_id": doc["nos"][0]["id"], "codigo": "4.08.1", "metodo": "lexical",
        "confianca": 1.0, "evidencia": "prova",
        "char_start": inicio, "char_end": inicio + len(trecho)}]}


# ---------- o espaçamento em si ----------

def test_insere_linha_em_branco_antes_das_clausulas():
    doc, texto = _canonico()
    saida = espacar(texto, pontos_de_espacamento(texto, doc))
    assert "\n\nCláusula 22.ª" in saida
    assert not saida.startswith("\n")  # nada antes do primeiro nó


def test_isola_o_bloco_de_tabela():
    doc, texto = _canonico()
    saida = espacar(texto, pontos_de_espacamento(texto, doc))
    assert "\n\nNíveis | Escalão 1" in saida
    assert "\n\nAssinaturas seguem-se" in saida


def test_texto_canonico_intacto():
    # o espaçamento é só de apresentação: sem linhas vazias, é o mesmo texto
    doc, texto = _canonico()
    saida = espacar(texto, pontos_de_espacamento(texto, doc))
    assert [l for l in saida.split("\n") if l] == [l for l in texto.split("\n") if l]


def test_indices_inseridos_apontam_para_as_quebras():
    doc, texto = _canonico()
    pontos = pontos_de_espacamento(texto, doc)
    exportado = espacar(texto, pontos)
    inseridos = indices_inseridos(pontos)
    assert len(inseridos) == len(pontos)
    assert all(exportado[i] == "\n" for i in inseridos)
    # retirando-as todas, volta o texto canónico carácter por carácter
    restante = "".join(c for i, c in enumerate(exportado)
                       if i not in set(inseridos))
    assert restante == texto


# ---------- contrato das seleções ----------

def test_selecao_sem_insercoes_dentro():
    doc, texto = _canonico()
    trecho = "1- O trabalhador tem direito a onze horas."
    inicio = texto.index(trecho)
    exportado, _ins, ini2, fim2 = _verificar_contrato(
        texto, doc, inicio, inicio + len(trecho))
    assert exportado[ini2:fim2] == trecho  # aqui é mesmo igual


def test_selecao_de_clausula_que_contem_tabela():
    doc, texto = _canonico()
    no = next(n for n in doc["nos"]
              if n["tipo"] == "clausula" and "22.ª" in n["rotulo"])
    exportado, _ins, ini2, fim2 = _verificar_contrato(
        texto, doc, no["char_start"], no["char_end"])
    # a seleção atravessa inserções: contém-nas, e por isso não é literal
    assert exportado[ini2:fim2] != texto[no["char_start"]:no["char_end"]]
    assert "Níveis | Escalão 1" in exportado[ini2:fim2]


def test_selecao_que_atravessa_a_fronteira_de_dois_nos():
    doc, texto = _canonico()
    inicio = texto.index("1- A retribuição")
    fim = texto.index("1- O trabalhador") + len("1- O trabalhador")
    _verificar_contrato(texto, doc, inicio, fim)


def test_selecao_com_varios_pontos_de_insercao():
    doc, texto = _canonico()
    inicio = texto.index("Cláusula 21.ª")
    fim = texto.index("Assinaturas seguem-se ao texto.") + len(
        "Assinaturas seguem-se ao texto.")
    pontos = pontos_de_espacamento(texto, doc)
    dentro = [p for p in pontos if inicio < p < fim]
    assert len(dentro) == 3  # cláusula 22.ª, início e fim da tabela
    exportado, _ins, ini2, fim2 = _verificar_contrato(texto, doc, inicio, fim)
    # as três quebras estão lá dentro, e são só elas a diferença
    assert exportado[ini2:fim2].count("\n\n") == 3


def test_inicio_coincide_com_ponto_de_insercao():
    doc, texto = _canonico()
    pontos = pontos_de_espacamento(texto, doc)
    inicio = texto.index("Cláusula 22.ª")
    assert inicio in pontos
    exportado, _ins, ini2, fim2 = _verificar_contrato(
        texto, doc, inicio, inicio + len("Cláusula 22.ª"))
    # a linha em branco fica ANTES da seleção, não dentro
    assert exportado[ini2:fim2] == "Cláusula 22.ª"
    assert exportado[ini2 - 1] == "\n" and exportado[ini2 - 2] == "\n"


def test_fim_coincide_com_ponto_de_insercao():
    doc, texto = _canonico()
    pontos = pontos_de_espacamento(texto, doc)
    fim = texto.index("Cláusula 22.ª")
    inicio = texto.index("1- A retribuição")
    assert fim in pontos
    exportado, _ins, ini2, fim2 = _verificar_contrato(texto, doc, inicio, fim)
    # o fim é exclusivo: a quebra acrescentada fica FORA da seleção
    assert not exportado[ini2:fim2].endswith("\n\n")


def test_offsets_exportados_recortam_o_mesmo_trecho(tmp_path):
    doc, texto = _canonico()
    trecho = "1- O trabalhador tem direito a onze horas."
    anot = _anotacao(doc, texto, trecho)
    destino = exportar_qdpx([(doc, texto, anot)], tmp_path / "t.qdpx")

    with zipfile.ZipFile(destino) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
        fonte = next(n for n in zf.namelist() if n.endswith(".txt"))
        exportado = zf.read(fonte).decode("utf-8")

    sel = raiz.find(".//q:PlainTextSelection", NS)
    ini, fim = int(sel.get("startPosition")), int(sel.get("endPosition"))
    inseridos = set(indices_inseridos(pontos_de_espacamento(texto, doc)))
    assert _sem_insercoes(exportado, inseridos, ini, fim) == trecho


def test_espacado_desligavel(tmp_path):
    doc, texto = _canonico()
    anot = _anotacao(doc, texto, "1- O trabalhador tem direito a onze horas.")
    destino = exportar_qdpx([(doc, texto, anot)], tmp_path / "t.qdpx",
                            espacado=False)
    with zipfile.ZipFile(destino) as zf:
        fonte = next(n for n in zf.namelist() if n.endswith(".txt"))
        assert zf.read(fonte).decode("utf-8") == texto


def test_contrato_vale_para_qualquer_intervalo():
    """Propriedade: o contrato não depende dos casos escolhidos à mão.

    Para 500 intervalos aleatórios do texto canónico, o trecho exportado
    menos as inserções é sempre o trecho canónico.
    """
    import random
    aleatorio = random.Random(7)
    doc, texto = _canonico()
    pontos = pontos_de_espacamento(texto, doc)
    exportado = espacar(texto, pontos)
    inseridos = set(indices_inseridos(pontos))
    assert pontos, "o fixture tem de ter pontos de inserção"
    for _ in range(500):
        i = aleatorio.randrange(0, len(texto))
        j = aleatorio.randrange(i + 1, len(texto) + 1)
        ini, fim = _remapear(i, j, pontos)
        assert _sem_insercoes(exportado, inseridos, ini, fim) == texto[i:j]
