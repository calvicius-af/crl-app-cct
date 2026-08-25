"""Espaçamento do texto exportado para QDPX (ISSUE-0003, ponto 3).

O texto canónico não tem linhas em branco — o estruturar descarta-as para
garantir a propriedade zero-perda e offsets estáveis. A legibilidade no
MaxQDA é conquistada na exportação: linha em branco antes de cada
cláusula/artigo e à volta das tabelas, com os offsets das seleções
remapeados no mesmo passo.
"""
import zipfile
import xml.etree.ElementTree as ET

from cct.extractor import MARCA_TABELA_FIM, MARCA_TABELA_INI, estruturar
from cct.qdpx import espacar, exportar_qdpx, pontos_de_espacamento

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


def _doc_e_anotacoes():
    doc, texto = estruturar(TEXTO, "teste")
    alvo = "1- O trabalhador tem direito a onze horas."
    ini = texto.index(alvo)
    anot = {"doc_id": "teste", "anotacoes": [{
        "no_id": doc["nos"][0]["id"], "codigo": "4.08.1", "metodo": "lexical",
        "confianca": 1.0, "evidencia": "descanso",
        "char_start": ini, "char_end": ini + len(alvo)}]}
    return doc, texto, anot


def test_insere_linha_em_branco_antes_das_clausulas():
    doc, texto = estruturar(TEXTO, "teste")
    saida = espacar(texto, pontos_de_espacamento(texto, doc))
    assert "\n\nCláusula 22.ª" in saida
    assert not saida.startswith("\n")  # nada antes do primeiro nó


def test_isola_o_bloco_de_tabela():
    doc, texto = estruturar(TEXTO, "teste")
    saida = espacar(texto, pontos_de_espacamento(texto, doc))
    assert "\n\nNíveis | Escalão 1" in saida
    assert "\n\nAssinaturas seguem-se" in saida


def test_texto_canonico_intacto():
    # o espaçamento é só de apresentação: sem linhas vazias, é o mesmo texto
    doc, texto = estruturar(TEXTO, "teste")
    saida = espacar(texto, pontos_de_espacamento(texto, doc))
    assert [l for l in saida.split("\n") if l] == [l for l in texto.split("\n") if l]


def test_offsets_exportados_recortam_o_mesmo_trecho(tmp_path):
    doc, texto, anot = _doc_e_anotacoes()
    original = texto[anot["anotacoes"][0]["char_start"]:
                     anot["anotacoes"][0]["char_end"]]
    destino = exportar_qdpx([(doc, texto, anot)], tmp_path / "t.qdpx")

    with zipfile.ZipFile(destino) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
        fonte = next(n for n in zf.namelist() if n.endswith(".txt"))
        exportado = zf.read(fonte).decode("utf-8")

    sel = raiz.find(".//q:PlainTextSelection", NS)
    ini, fim = int(sel.get("startPosition")), int(sel.get("endPosition"))
    assert exportado[ini:fim] == original


def test_espacado_desligavel(tmp_path):
    doc, texto, anot = _doc_e_anotacoes()
    destino = exportar_qdpx([(doc, texto, anot)], tmp_path / "t.qdpx",
                            espacado=False)
    with zipfile.ZipFile(destino) as zf:
        fonte = next(n for n in zf.namelist() if n.endswith(".txt"))
        assert zf.read(fonte).decode("utf-8") == texto
