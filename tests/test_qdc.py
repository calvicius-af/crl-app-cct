"""Testes da integração com o codebook master (.qdc) do MaxQDA."""
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cct.qdc import carregar_qdc, procurar_codigo
from cct.qdpx import exportar_qdpx, _guid_deterministico

QDC = Path(__file__).parent.parent / "data" / "raw" / "maxqda" / "MAXQDA_RNC_2026_DADOS_2025_master_20260521 - Lista de Códigos.qdc"
NS = {"q": "urn:QDA-XML:project:1.0"}


@pytest.mark.skipif(not QDC.exists(), reason="QDC master não disponível")
class TestMaster:
    @pytest.fixture(scope="class")
    def reg(self):
        return carregar_qdc(QDC)

    def test_carrega_e_indexa_por_id(self, reg):
        r = procurar_codigo(reg, "4.03")
        assert r and "492" in r["nome"]
        assert r["guid"] and "{" not in r["guid"]

    def test_descricoes_presentes(self, reg):
        r = procurar_codigo(reg, "4.03")
        assert "DEFINIÇÃO" in r["descricao"]

    def test_estrutura_do_master(self, reg):
        assert procurar_codigo(reg, "Preâmbulo") is not None
        assert procurar_codigo(reg, "Texto Consolidado") is not None


def test_guid_deterministico_estavel():
    a = _guid_deterministico(("REVER", "4.08", "4.08.4"))
    b = _guid_deterministico(("REVER", "4.08", "4.08.4"))
    c = _guid_deterministico(("AUTO", "4.08", "4.08.4"))
    assert a == b != c
    uuid.UUID(a)  # é um GUID válido


def test_qdpx_usa_master_e_descricoes(tmp_path):
    doc = {"versao_schema": "0.1", "doc_id": "d", "tipo": "CCT",
           "subtipo": "desconhecido",
           "nos": [{"id": "n0", "tipo": "clausula", "rotulo": "Cláusula 1.ª",
                    "char_start": 0, "char_end": 20, "pai": None,
                    "origem": "novo", "folha": True}]}
    texto = "Texto de exemplo aqui"
    anot = {"versao_schema": "0.1", "doc_id": "d", "anotacoes": [
        {"no_id": "n0", "char_start": 0, "char_end": 20, "codigo": "REVER/4.08.5.1",
         "confianca": 0.7, "metodo": "lexical", "nivel": "clausula"},
    ]}
    descricoes = {"4.08.5.1": {"nome": "4.08.5.1 Registo de pessoal",
                               "descricao": "DEFINIÇÃO\nProcesso individual.",
                               "guid": "11111111-2222-3333-4444-555555555555",
                               "cor": "#aabbcc"}}
    destino = tmp_path / "t.qdpx"
    exportar_qdpx([(doc, texto, anot)], destino, master=descricoes)
    with zipfile.ZipFile(destino) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
    codes = {c.get("name"): c for c in raiz.iter(f"{{{'urn:QDA-XML:project:1.0'}}}Code")}
    folha = codes["4.08.5.1 Registo de pessoal"]
    # o GUID é determinístico (o mesmo código pode existir em várias faixas;
    # GUIDs duplicados seriam inválidos) — do master vêm nome e descrição
    uuid.UUID(folha.get("guid"))
    desc = folha.find("q:Description", NS)
    assert desc is not None and "DEFINIÇÃO" in desc.text
    # GUIDs de dois exports são idênticos para códigos fora do master
    destino2 = tmp_path / "t2.qdpx"
    exportar_qdpx([(doc, texto, anot)], destino2, master=descricoes)
    with zipfile.ZipFile(destino2) as zf:
        raiz2 = ET.fromstring(zf.read("project.qde").decode("utf-8"))
    guids1 = {c.get("name"): c.get("guid") for c in raiz.iter(f"{{{'urn:QDA-XML:project:1.0'}}}Code")}
    guids2 = {c.get("name"): c.get("guid") for c in raiz2.iter(f"{{{'urn:QDA-XML:project:1.0'}}}Code")}
    assert guids1 == guids2
