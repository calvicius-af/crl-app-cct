"""Cria manifestos de migração para resultados históricos sem proveniência completa.

Não tenta reconstruir o comando original nem atribui uma aprovação humana.
Regista apenas os ficheiros presentes, os seus hashes e a origem conhecida.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Permite executar ``python scripts/manifestar_legado.py`` a partir da raiz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cct.proveniencia import registo_ficheiro, estado_git


def criar_manifesto(raiz: Path, pasta: Path, origem: str, classificacao: str) -> dict:
    ficheiros = sorted(p for p in pasta.rglob("*")
                       if p.is_file() and p.name != "manifest.json")
    agora = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "status": "legacy_migrated",
        "started_at_utc": agora,
        "finished_at_utc": agora,
        "command": [],
        "parameters": {
            "migration": "2026-08",
            "origin_path": origem,
            "classification": classificacao,
            "provenance_quality": "partial",
        },
        "environment": {"git": estado_git(raiz)},
        "inputs": [],
        "outputs": [registo_ficheiro(p, raiz) for p in ficheiros],
        "summary": {"files": len(ficheiros), "human_approval": "pending"},
        "problems": [
            "Comando e inputs originais não foram preservados no artefacto.",
            "Este manifesto confirma integridade local, não qualidade do resultado.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    raiz = args.root.resolve()
    alvos = [
        (raiz / "results/validated/2025_4_08_issue0004",
         "results/2025_4_08_issue0004", "resultado_validado_preservar"),
        (raiz / "results/runs/2026/2026_4_08",
         "results/2026_4_08", "resultado_reproduzivel_manifestar"),
        (raiz / "results/benchmarks/tema-4.08/metricas",
         "results/metricas", "benchmark_reproduzivel_manifestar"),
        (raiz / "results/benchmarks/tema-4.08/comparacoes",
         "results/comparacoes", "benchmark_reproduzivel_manifestar"),
    ]
    for pasta, origem, classificacao in alvos:
        if not pasta.is_dir():
            continue
        destino = pasta / "manifest.json"
        manifesto = criar_manifesto(raiz, pasta, origem, classificacao)
        destino.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        print(destino)


if __name__ == "__main__":
    main()
