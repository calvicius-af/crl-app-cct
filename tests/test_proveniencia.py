import json
from pathlib import Path

from cct.proveniencia import (construir_manifesto, escrever_manifesto,
                              registo_ficheiro)


def test_registo_tem_caminho_portavel_tamanho_e_hash(tmp_path):
    entrada = tmp_path / "data" / "fonte.txt"
    entrada.parent.mkdir()
    entrada.write_text("abc", encoding="utf-8")

    registo = registo_ficheiro(entrada, tmp_path)

    assert registo["path"] == "data/fonte.txt"
    assert registo["size_bytes"] == 3
    assert registo["sha256"] == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


def test_manifesto_preserva_parametros_problemas_e_outputs(tmp_path):
    entrada = tmp_path / "entrada.pdf"
    saida = tmp_path / "saida.qdpx"
    entrada.write_bytes(b"pdf")
    saida.write_bytes(b"qdpx")

    manifesto = construir_manifesto(
        raiz=tmp_path,
        inicio_utc="2026-08-26T10:00:00+00:00",
        parametros={"extrator": "docling"},
        entradas=[entrada, entrada],
        saidas=[saida],
        resumo={"documentos": 1},
        problemas=["aviso conhecido"],
    )
    destino = escrever_manifesto(tmp_path / "manifest.json", manifesto)
    guardado = json.loads(destino.read_text(encoding="utf-8"))

    assert guardado["status"] == "completed_with_warnings"
    assert guardado["parameters"]["extrator"] == "docling"
    assert guardado["problems"] == ["aviso conhecido"]
    assert len(guardado["inputs"]) == 1
    assert guardado["outputs"][0]["path"] == "saida.qdpx"


def test_manifesto_inicial_fica_marcado_como_corrida_em_curso(tmp_path):
    entrada = tmp_path / "entrada.pdf"
    entrada.write_bytes(b"pdf")

    manifesto = construir_manifesto(
        raiz=tmp_path,
        inicio_utc="2026-08-26T10:00:00+00:00",
        parametros={},
        entradas=[entrada],
        saidas=[],
        resumo={"documentos_encontrados": 1},
        problemas=[],
        status="running",
    )

    assert manifesto["status"] == "running"
    assert manifesto["finished_at_utc"] is None
