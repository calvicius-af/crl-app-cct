import json
import subprocess

from cct.proveniencia import (construir_manifesto, escrever_manifesto,
                              estado_git, registo_ficheiro)


# ---------------------------------------------- estado_git (ISSUE-0013)

def test_estado_git_distingue_git_ausente(monkeypatch, tmp_path):
    """Estação sem git: o null tem de vir com o motivo, não mudo."""
    def sem_git(*_a, **_k):
        raise FileNotFoundError("git")
    monkeypatch.setattr(subprocess, "check_output", sem_git)
    estado = estado_git(tmp_path)
    assert estado == {"commit": None, "dirty": None, "motivo": "git_ausente"}


def test_estado_git_distingue_fora_de_repositorio(monkeypatch, tmp_path):
    def fora_de_repositorio(*_a, **_k):
        raise subprocess.CalledProcessError(128, "git")
    monkeypatch.setattr(subprocess, "check_output", fora_de_repositorio)
    estado = estado_git(tmp_path)
    assert estado["motivo"] == "fora_de_repositorio"


def test_estado_git_com_repositorio_devolve_commit_e_dirty(monkeypatch, tmp_path):
    respostas = iter(["abc123\n", "M ficheiro.py\n"])

    def falso_check_output(comando, **_k):
        return next(respostas)
    monkeypatch.setattr(subprocess, "check_output", falso_check_output)
    estado = estado_git(tmp_path)
    assert estado == {"commit": "abc123", "dirty": True}


def test_manifesto_regista_o_motivo_quando_nao_ha_commit(monkeypatch, tmp_path):
    """O manifesto de uma corrida sem git tem de explicar o null."""
    def sem_git(*_a, **_k):
        raise FileNotFoundError("git")
    monkeypatch.setattr(subprocess, "check_output", sem_git)
    manifesto = construir_manifesto(
        raiz=tmp_path,
        inicio_utc="2026-09-19T10:00:00+00:00",
        parametros={},
        entradas=[],
        saidas=[],
        resumo={},
        problemas=[],
    )
    assert manifesto["environment"]["git"]["motivo"] == "git_ausente"


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
