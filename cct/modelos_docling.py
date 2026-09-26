"""Os modelos do docling: descarregar uma vez, verificar sempre, correr sem rede (#25).

O docling precisa de modelos (o de layout, o TableFormer, o OCR), que vai
buscar à internet na primeira corrida. Numa estação sem acesso à internet,
ou para garantir que nada sai da máquina durante a extração, os modelos
descarregam-se uma vez numa máquina com rede, copiam-se para a partilha e
verificam-se pelo SHA-256 de cada ficheiro:

    python -m cct.modelos_docling descarregar --destino PASTA   # máquina com rede
    python -m cct.modelos_docling inventariar --pasta PASTA     # escreve PASTA/manifesto_modelos.json
    python -m cct.modelos_docling verificar --pasta PASTA       # na estação, antes de usar

Na extração, `CCT_DOCLING_MODELOS=PASTA` faz o docling ler os modelos dessa
pasta e correr em modo offline (cct/extractor_docling.py): sem descarga, e sem
nenhum serviço remoto.

Origem: os modelos `docling-project/*` vêm do Hugging Face
(https://huggingface.co/docling-project), com a revisão fixada pela versão do
docling instalada; os do RapidOCR vêm da origem que o pacote `rapidocr` define.
O manifesto regista, para cada ficheiro, o caminho, o tamanho e o SHA-256, e a
versão do docling que os descarregou.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFESTO = "manifesto_modelos.json"


def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _ficheiros(pasta: Path) -> list[Path]:
    """Os ficheiros dos modelos, sem o manifesto nem as caches de descarga."""
    return sorted(p for p in pasta.rglob("*")
                  if p.is_file() and p.name != MANIFESTO
                  and ".cache" not in p.relative_to(pasta).parts)


def inventariar(pasta: Path) -> dict:
    """O manifesto da pasta: cada ficheiro com o tamanho e o SHA-256."""
    from importlib.metadata import PackageNotFoundError, version
    try:
        versao = version("docling")
    except PackageNotFoundError:
        versao = None
    ficheiros: list[dict[str, str | int]] = [
        {"caminho": p.relative_to(pasta).as_posix(), "bytes": p.stat().st_size,
         "sha256": _sha256(p)} for p in _ficheiros(pasta)]
    return {
        "gerado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "docling": versao,
        "modelos": sorted({str(f["caminho"]).split("/")[0] for f in ficheiros}),
        "bytes": sum(int(f["bytes"]) for f in ficheiros),
        "ficheiros": ficheiros,
    }


def verificar(pasta: Path) -> list[str]:
    """O que não bate com o manifesto: ficheiros em falta, alterados ou a mais."""
    caminho = pasta / MANIFESTO
    if not caminho.exists():
        return [f"sem {MANIFESTO} em {pasta}: correr primeiro `inventariar`"]
    manifesto = json.loads(caminho.read_text(encoding="utf-8"))
    esperados = {f["caminho"]: f for f in manifesto.get("ficheiros", [])}
    presentes = {p.relative_to(pasta).as_posix(): p for p in _ficheiros(pasta)}
    problemas = []
    for nome, f in esperados.items():
        if nome not in presentes:
            problemas.append(f"em falta: {nome}")
        elif _sha256(presentes[nome]) != f["sha256"]:
            problemas.append(f"alterado (SHA-256 diferente): {nome}")
    problemas += [f"a mais (não está no manifesto): {n}" for n in presentes if n not in esperados]
    return problemas


def descarregar(destino: Path) -> Path:
    """Descarrega os modelos que a extração usa para `destino` (precisa de rede)."""
    from docling.utils.model_downloader import download_models
    return download_models(output_dir=destino, progress=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m cct.modelos_docling")
    sub = p.add_subparsers(dest="comando", required=True)
    d = sub.add_parser("descarregar", help="descarrega os modelos (máquina com rede)")
    d.add_argument("--destino", type=Path, required=True)
    for nome, ajuda in (("inventariar", "escreve o manifesto com o SHA-256 de cada ficheiro"),
                        ("verificar", "confirma os ficheiros contra o manifesto")):
        s = sub.add_parser(nome, help=ajuda)
        s.add_argument("--pasta", type=Path, required=True)
    args = p.parse_args(argv)
    if args.comando == "descarregar":
        pasta = descarregar(args.destino)
        (pasta / MANIFESTO).write_text(
            json.dumps(inventariar(pasta), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Modelos em {pasta}, com o manifesto {MANIFESTO}. Copiar a pasta inteira.")
        return 0
    if args.comando == "inventariar":
        manifesto = inventariar(args.pasta)
        (args.pasta / MANIFESTO).write_text(
            json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{len(manifesto['ficheiros'])} ficheiros, {manifesto['bytes'] / 1e6:.0f} MB, "
              f"modelos: {', '.join(manifesto['modelos'])} → {args.pasta / MANIFESTO}")
        return 0
    problemas = verificar(args.pasta)
    for problema in problemas:
        print(f"PROBLEMA: {problema}")
    if not problemas:
        print(f"OK: os modelos em {args.pasta} batem com o manifesto.")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
