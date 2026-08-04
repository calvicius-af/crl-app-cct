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
from cct.qdpx import exportar_qdpx
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


def test_texto_fonte_identico(qdpx_path):
    _doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    with zipfile.ZipFile(qdpx_path) as zf:
        fonte = next(n for n in zf.namelist() if n.startswith("Sources/"))
        conteudo = zf.read(fonte).decode("utf-8")
    assert not conteudo.startswith("﻿")
    assert "\r" not in conteudo
    assert conteudo == texto


def test_offsets_das_selecoes_batem_com_o_texto(qdpx_path):
    doc, texto = adaptar_v2(FIXTURE.read_text(encoding="utf-8"))[0]
    anot = codificar(doc, texto, CODEBOOK)
    esperadas = {(a["char_start"], a["char_end"]) for a in anot["anotacoes"]}

    with zipfile.ZipFile(qdpx_path) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))

    selecoes = raiz.findall(".//q:TextSource/q:PlainTextSelection", NS)
    assert len(selecoes) == len(anot["anotacoes"]) > 0
    obtidas = set()
    for sel in selecoes:
        ini, fim = int(sel.get("startPosition")), int(sel.get("endPosition"))
        obtidas.add((ini, fim))
        assert 0 <= ini < fim <= len(texto)
        assert sel.find("q:Coding/q:CodeRef", NS) is not None
    assert obtidas == esperadas


def test_codigos_referenciados_existem_no_codebook(qdpx_path):
    with zipfile.ZipFile(qdpx_path) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
    guids_codigos = {c.get("guid") for c in raiz.findall(".//q:CodeBook//q:Code", NS)}
    refs = {r.get("targetGUID") for r in raiz.findall(".//q:CodeRef", NS)}
    assert refs <= guids_codigos
