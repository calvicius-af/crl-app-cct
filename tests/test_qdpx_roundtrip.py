"""Round-trip do exportador QDPX — Fase 0 (o gate crítico).

Exporta 1 documento + anotações para .qdpx, reabre com leitura independente
(zipfile + ElementTree, sem usar o código do exportador) e verifica que:
- o project.qde é XML REFI-QDA válido (namespace, CodeBook, Sources);
- o texto fonte dentro do zip é exatamente o doc.txt (UTF-8, sem BOM, LF);
- cada PlainTextSelection recorta no texto o trecho onde está a evidência.
"""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cct.adapter_v2 import adaptar_v2
from cct.lexical import codificar
from cct.qdpx import (exportar_qdpx, indices_inseridos,
                      pontos_de_espacamento)
from tests.test_lexical import CODEBOOK

NS = {"q": "urn:QDA-XML:project:1.0"}
FIXTURE = Path(__file__).parent / "fixtures" / "exemplo_v2.txt"


@pytest.fixture()
def qdpx_path(tmp_path):
    doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    anot = codificar(doc, texto, CODEBOOK)
    destino = tmp_path / "teste.qdpx"
    exportar_qdpx([(doc, texto, anot)], destino, nome_projeto="Teste CRL")
    return destino


def test_zip_contem_project_e_source(qdpx_path):
    with zipfile.ZipFile(qdpx_path) as zf:
        nomes = zf.namelist()
    assert "project.qde" in nomes
    assert any(n.startswith("Sources/") and n.endswith(".txt") for n in nomes)


def test_xml_valido_e_namespace(qdpx_path):
    with zipfile.ZipFile(qdpx_path) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
    assert raiz.tag == "{urn:QDA-XML:project:1.0}Project"
    assert raiz.find(".//q:CodeBook/q:Codes", NS) is not None
    assert len(raiz.findall(".//q:Sources/q:TextSource", NS)) == 1
    assert len(raiz.findall(".//q:Users/q:User", NS)) >= 1


def test_texto_fonte_preserva_o_conteudo(qdpx_path):
    # a exportação separa cláusulas e tabelas com linhas em branco para
    # leitura no MaxQDA (ISSUE-0003); tirando essas, o texto é o mesmo
    _doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    with zipfile.ZipFile(qdpx_path) as zf:
        fonte = next(n for n in zf.namelist() if n.startswith("Sources/"))
        conteudo = zf.read(fonte).decode("utf-8")
    assert not conteudo.startswith("﻿")
    assert "\r" not in conteudo
    assert [l for l in conteudo.split("\n") if l] == \
           [l for l in texto.split("\n") if l]


def test_offsets_das_selecoes_batem_com_o_texto(qdpx_path):
    # O gate real. A exportação separa cláusulas e tabelas com linhas em
    # branco (ISSUE-0003), por isso uma seleção que atravesse pontos de
    # inserção CONTÉM essas quebras: o contrato não é igualdade literal,
    # é que removendo exatamente as inserções se obtém o trecho canónico
    # (ISSUE-0004). Não se normaliza espaço — isso esconderia perdas.
    doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    anot = codificar(doc, texto, CODEBOOK)
    inseridos = set(indices_inseridos(pontos_de_espacamento(texto, doc)))

    with zipfile.ZipFile(qdpx_path) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
        fonte = next(n for n in zf.namelist() if n.startswith("Sources/"))
        exportado = zf.read(fonte).decode("utf-8")

    selecoes = raiz.findall(".//q:TextSource/q:PlainTextSelection", NS)
    assert len(selecoes) == len(anot["anotacoes"]) > 0
    obtidos = []
    for sel in selecoes:
        ini, fim = int(sel.get("startPosition")), int(sel.get("endPosition"))
        assert 0 <= ini < fim <= len(exportado)
        assert sel.find("q:Coding/q:CodeRef", NS) is not None
        obtidos.append("".join(
            c for i, c in enumerate(exportado[ini:fim], start=ini)
            if i not in inseridos))
    esperados = [texto[a["char_start"]:a["char_end"]] for a in anot["anotacoes"]]
    assert sorted(obtidos) == sorted(esperados)


def test_codigos_referenciados_existem_no_codebook(qdpx_path):
    with zipfile.ZipFile(qdpx_path) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
    guids_codigos = {c.get("guid") for c in raiz.findall(".//q:CodeBook//q:Code", NS)}
    refs = {r.get("targetGUID") for r in raiz.findall(".//q:CodeRef", NS)}
    assert refs <= guids_codigos
