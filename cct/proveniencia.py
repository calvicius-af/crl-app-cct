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
    """Estado do git, distinguindo porque é que não há commit (ISSUE-0013).

    Nas estações do CRL o git não está instalado: o caso em que a proveniência
    mais importa é precisamente aquele em que ela se degradava em silêncio,
    com um `null` sem explicação. Um null com motivo vale muito mais do que
    um null mudo.
    """
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=raiz, text=True,
            stderr=subprocess.DEVNULL).strip()
    except FileNotFoundError:
        # git não está no PATH (estação institucional sem git)
        return {"commit": None, "dirty": None, "motivo": "git_ausente"}
    except subprocess.CalledProcessError:
        # git existe mas a pasta não é um repositório (ou HEAD não existe)
        return {"commit": None, "dirty": None, "motivo": "fora_de_repositorio"}
    except OSError:
        return {"commit": None, "dirty": None, "motivo": "erro"}
    alteracoes = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=raiz, text=True,
        stderr=subprocess.DEVNULL)
    return {"commit": commit, "dirty": bool(alteracoes.strip())}


def versao_aplicacao(raiz: Path) -> str | None:
    """A versão declarada em `pyproject.toml`, que viaja sempre com o código.

    É o que identifica a aplicação numa estação sem git (ISSUE-0013, ponto 2).
    """
    import tomllib

    try:
        with open(raiz / "pyproject.toml", "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return None


def origem_do_pacote_offline(raiz: Path) -> dict | None:
    """De que commit foi preparado o pacote offline instalado nesta estação.

    `scripts/preparar_pacote_offline.py` corre numa máquina com git e regista
    no `vendor/wheels/manifesto.json` a versão e o commit de onde partiu. Uma
    estação sem git não sabe o seu commit, mas sabe o do pacote que instalou.
    """
    try:
        dados = json.loads((raiz / "vendor" / "wheels" / "manifesto.json")
                           .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    origem = dados.get("aplicacao")
    return origem if isinstance(origem, dict) else None


def estado_git_ou_pacote(raiz: Path) -> dict:
    """`estado_git`, completado pelo commit do pacote offline quando o git falta."""
    estado = estado_git(raiz)
    if estado.get("commit") is None:
        origem = origem_do_pacote_offline(raiz)
        if origem and origem.get("commit"):
            estado["commit_do_pacote_offline"] = origem["commit"]
    return estado


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
            "git": estado_git_ou_pacote(raiz),
            "app_version": versao_aplicacao(raiz),
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
