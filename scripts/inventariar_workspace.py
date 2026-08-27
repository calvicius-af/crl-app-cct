"""Inventaria os artefactos locais que ficam fora do Git.

Não move nem apaga ficheiros. Produz um JSON verificável e um resumo Markdown
em ``results/_inventory/`` para apoiar uma migração posterior sem perda.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


AREAS = ("data", "results", "archive", "vendor")
IGNORAR = {".DS_Store"}


def sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as ficheiro:
        for bloco in iter(lambda: ficheiro.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def classificar(caminho_relativo: Path) -> str:
    partes = caminho_relativo.parts
    texto = caminho_relativo.as_posix().lower()
    sufixo = caminho_relativo.suffix.lower()

    if partes[:2] == ("data", "raw"):
        return "preservar_fonte"
    if len(partes) >= 3 and partes[:2] == ("data", "interim"):
        if partes[2].startswith("cache"):
            return "cache_descartavel"
        return "intermedio_regeneravel"
    if partes and partes[0] == "archive":
        return "historico_preservar"
    if partes and partes[0] == "vendor":
        return "terceiro_repor_da_origem"
    if partes and partes[0] == "results":
        # Decisões explícitas para os conjuntos já reconhecidos no workspace.
        if texto.startswith("results/2025_4_08_issue0004/"):
            return "resultado_validado_preservar"
        if texto.startswith("results/2026_4_08/"):
            return "resultado_reproduzivel_manifestar"
        if texto.startswith("results/comparacoes/"):
            return "benchmark_reproduzivel_manifestar"
        if texto.startswith("results/metricas/"):
            return "benchmark_reproduzivel_manifestar"
        if texto.startswith("results/xlsx_peritas/"):
            return "confirmar_trabalho_humano"
        if texto.startswith("results/qdpx/") and "anotad" in texto:
            return "possivel_trabalho_humano_preservar"
        if texto.startswith("results/qdpx/"):
            return "resultado_reproduzivel_manifestar"
        if sufixo == ".mqda" or any(marca in texto for marca in ("anotad", "triado")):
            return "possivel_trabalho_humano_preservar"
        if any(marca in texto for marca in ("docling", "prova_richtext")):
            return "experiencia_preservar_ate_documentar"
        return "resultado_por_classificar"
    return "por_classificar"


def inventariar(raiz: Path, destino_json: Path) -> dict:
    entradas = []
    destino_resolvido = destino_json.resolve()
    for area in AREAS:
        pasta = raiz / area
        if not pasta.exists():
            continue
        for caminho in sorted(p for p in pasta.rglob("*") if p.is_file()):
            if (caminho.name in IGNORAR
                    or caminho.resolve() == destino_resolvido
                    or caminho.parent.resolve() == destino_resolvido.parent):
                continue
            relativo = caminho.relative_to(raiz)
            stat = caminho.stat()
            entradas.append({
                "path": relativo.as_posix(),
                "size_bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc).isoformat(),
                "sha256": sha256(caminho),
                "classification": classificar(relativo),
            })

    por_classe = Counter(e["classification"] for e in entradas)
    bytes_por_classe = Counter()
    for entrada in entradas:
        bytes_por_classe[entrada["classification"]] += entrada["size_bytes"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "areas": list(AREAS),
        "summary": {
            "files": len(entradas),
            "size_bytes": sum(e["size_bytes"] for e in entradas),
            "files_by_classification": dict(sorted(por_classe.items())),
            "bytes_by_classification": dict(sorted(bytes_por_classe.items())),
        },
        "files": entradas,
    }


def resumo_markdown(inventario: dict) -> str:
    linhas = [
        "# Inventário local do workspace",
        "",
        f"Gerado em `{inventario['generated_at_utc']}`.",
        "",
        "> Este inventário não autoriza eliminações. As classificações são",
        "> conservadoras e devem ser confirmadas por uma pessoa antes de mover dados.",
        "",
        f"- Ficheiros: **{inventario['summary']['files']}**",
        f"- Volume: **{inventario['summary']['size_bytes']} bytes**",
        "",
        "| Classificação | Ficheiros | Bytes |",
        "|---|---:|---:|",
    ]
    ficheiros = inventario["summary"]["files_by_classification"]
    volumes = inventario["summary"]["bytes_by_classification"]
    for classe in sorted(ficheiros):
        linhas.append(f"| `{classe}` | {ficheiros[classe]} | {volumes[classe]} |")
    linhas.extend([
        "",
        "O detalhe, incluindo SHA-256 e caminhos, está em `workspace_inventory.json`.",
        "",
    ])
    return "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    raiz = args.root.resolve()
    destino = (args.out or raiz / "results" / "_inventory" /
               "workspace_inventory.json").resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    inventario = inventariar(raiz, destino)
    destino.write_text(json.dumps(inventario, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    resumo = destino.with_name("RESUMO.md")
    resumo.write_text(resumo_markdown(inventario), encoding="utf-8")
    print(f"Inventário: {destino}")
    print(f"Resumo: {resumo}")
    print(f"Ficheiros: {inventario['summary']['files']}")


if __name__ == "__main__":
    main()
