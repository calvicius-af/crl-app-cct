"""Manifesto verificável das corridas do pipeline."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def agora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as ficheiro:
        for bloco in iter(lambda: ficheiro.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def caminho_portavel(caminho: Path, raiz: Path) -> str:
    try:
        return caminho.resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return caminho.resolve().as_posix()


def registo_ficheiro(caminho: Path, raiz: Path) -> dict:
    return {
        "path": caminho_portavel(caminho, raiz),
        "size_bytes": caminho.stat().st_size,
        "sha256": sha256(caminho),
    }


def estado_git(raiz: Path) -> dict:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=raiz, text=True,
            stderr=subprocess.DEVNULL).strip()
        alteracoes = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=raiz, text=True,
            stderr=subprocess.DEVNULL)
        return {"commit": commit, "dirty": bool(alteracoes.strip())}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def construir_manifesto(*, raiz: Path, inicio_utc: str, parametros: dict,
                         entradas: list[Path], saidas: list[Path],
                         resumo: dict, problemas: list[str],
                         status: str | None = None,
                         comando: list[str] | None = None) -> dict:
    entradas_unicas = sorted({p.resolve() for p in entradas if p.is_file()})
    saidas_unicas = sorted({p.resolve() for p in saidas if p.is_file()})
    return {
        "schema_version": 1,
        "started_at_utc": inicio_utc,
        "finished_at_utc": None if status == "running" else agora_utc(),
        "status": status or ("completed_with_warnings" if problemas else "completed"),
        "command": comando or list(sys.argv),
        "parameters": parametros,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git": estado_git(raiz),
        },
        "inputs": [registo_ficheiro(p, raiz) for p in entradas_unicas],
        "outputs": [registo_ficheiro(p, raiz) for p in saidas_unicas],
        "summary": resumo,
        "problems": problemas,
    }


def escrever_manifesto(destino: Path, manifesto: dict) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(destino.suffix + ".tmp")
    temporario.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    temporario.replace(destino)
    return destino
