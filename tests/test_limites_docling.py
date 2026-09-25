"""Perímetro da extração (#25): limites dos PDF, opções do docling e modelos.

Os limites e o manifesto dos modelos testam-se sem o docling. A prova de que a
conversão corre sem rede só corre onde o docling e os modelos estão
instalados (CCT_DOCLING_MODELOS, ou a cache por omissão); noutro sítio,
ignora-se e diz porquê.
"""
import json
import os
import socket
from pathlib import Path

import pytest

from cct import modelos_docling
from cct.extractor import extrair_pdf
from cct.extractor_docling import opcoes_seguras
from cct.limites import PDFRecusado, verificar_pdf
from tests.pdf_sintetico import escrever_pdf, pagina_bte


def _pdf(tmp_path, paginas=1):
    return escrever_pdf(tmp_path / "x.pdf", [pagina_bte(n, ["Cláusula 1.ª - Férias", "Texto."])
                                            for n in range(1, paginas + 1)])


def test_pdf_normal_passa_e_diz_as_paginas(tmp_path):
    assert verificar_pdf(_pdf(tmp_path, 2)) == 2


def test_pdf_corrompido_recusado_com_o_que_fazer(tmp_path):
    lixo = tmp_path / "lixo.pdf"
    lixo.write_bytes(b"%PDF-1.4 isto nao e um pdf")
    with pytest.raises(PDFRecusado, match="corrompido.*Descarregar de novo"):
        verificar_pdf(lixo)
    with pytest.raises(PDFRecusado):
        extrair_pdf(lixo)


def test_pdf_com_paginas_ou_tamanho_a_mais(tmp_path, monkeypatch):
    pdf = _pdf(tmp_path, 3)
    monkeypatch.setenv("CCT_MAX_PAGINAS", "2")
    with pytest.raises(PDFRecusado, match="3 páginas, acima do limite de 2"):
        verificar_pdf(pdf)
    monkeypatch.delenv("CCT_MAX_PAGINAS")
    monkeypatch.setenv("CCT_MAX_MB", "0.0001")
    with pytest.raises(PDFRecusado, match="acima do limite de 0.0001 MB"):
        verificar_pdf(pdf)


def test_pdf_protegido_por_palavra_passe(tmp_path, monkeypatch):
    import pypdfium2 as pdfium

    def protegido(*_a, **_k):
        raise pdfium.PdfiumError("Failed to load document (PDFium: Incorrect password error).")
    monkeypatch.setattr(pdfium, "PdfDocument", protegido)
    with pytest.raises(PDFRecusado, match="protegido por palavra-passe"):
        verificar_pdf(_pdf(tmp_path))


def test_opcoes_do_docling_sem_servicos_remotos_e_com_tempo_maximo(monkeypatch):
    opcoes = opcoes_seguras()
    assert opcoes["enable_remote_services"] is False
    assert opcoes["allow_external_plugins"] is False
    assert opcoes["document_timeout"] > 0 and "artifacts_path" not in opcoes
    monkeypatch.setenv("CCT_DOCLING_TEMPO_MAX_S", "30")
    assert opcoes_seguras(Path("/modelos")) == {
        "enable_remote_services": False, "allow_external_plugins": False,
        "document_timeout": 30.0, "artifacts_path": "/modelos", "do_ocr": False}
    monkeypatch.setenv("CCT_DOCLING_OCR", "1")
    assert opcoes_seguras(Path("/modelos"))["do_ocr"] is True


def test_manifesto_dos_modelos_apanha_ficheiros_alterados_em_falta_e_a_mais(tmp_path):
    pasta = tmp_path / "modelos"
    (pasta / "docling-project--layout").mkdir(parents=True)
    (pasta / "docling-project--layout" / "model.safetensors").write_bytes(b"pesos")
    (pasta / "RapidOcr").mkdir()
    (pasta / "RapidOcr" / "det.onnx").write_bytes(b"ocr")
    assert modelos_docling.main(["inventariar", "--pasta", str(pasta)]) == 0
    manifesto = json.loads((pasta / modelos_docling.MANIFESTO).read_text(encoding="utf-8"))
    assert manifesto["modelos"] == ["RapidOcr", "docling-project--layout"]
    assert all(len(f["sha256"]) == 64 for f in manifesto["ficheiros"])
    assert modelos_docling.verificar(pasta) == []

    (pasta / "RapidOcr" / "det.onnx").write_bytes(b"outro")
    (pasta / "docling-project--layout" / "model.safetensors").unlink()
    (pasta / "extra.bin").write_bytes(b"x")
    problemas = modelos_docling.verificar(pasta)
    assert "alterado (SHA-256 diferente): RapidOcr/det.onnx" in problemas
    assert "em falta: docling-project--layout/model.safetensors" in problemas
    assert "a mais (não está no manifesto): extra.bin" in problemas
    assert modelos_docling.main(["verificar", "--pasta", str(pasta)]) == 1


def _pasta_de_modelos():
    pasta = Path(os.environ.get("CCT_DOCLING_MODELOS", Path.home() / ".cache" / "docling" / "models"))
    return pasta if (pasta / "docling-project--docling-layout-heron").is_dir() else None


def test_conversao_com_modelos_locais_nao_usa_a_rede(tmp_path, monkeypatch):
    """Com os modelos numa pasta, a extração corre com a rede bloqueada."""
    pytest.importorskip("docling", reason="docling não instalado (dependência opcional)")
    pasta = _pasta_de_modelos()
    if pasta is None:
        pytest.skip("sem modelos do docling descarregados (CCT_DOCLING_MODELOS)")
    from cct import extractor_docling
    monkeypatch.setenv("CCT_DOCLING_MODELOS", str(pasta))
    monkeypatch.setattr(extractor_docling, "_conversor", None)

    def sem_rede(*_a, **_k):
        raise AssertionError("a extração tentou abrir uma ligação de rede")
    monkeypatch.setattr(socket.socket, "connect", sem_rede)
    monkeypatch.setattr(socket, "create_connection", sem_rede)
    doc, texto = extractor_docling.extrair_pdf_docling(_pdf(tmp_path))
    assert "Férias" in texto
    monkeypatch.setattr(extractor_docling, "_conversor", None)
