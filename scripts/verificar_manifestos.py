"""Verifica a presença e os hashes dos outputs declarados nos manifestos locais."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cct.proveniencia import sha256


def verificar(raiz: Path, manifesto: Path) -> list[str]:
    dados = json.loads(manifesto.read_text(encoding="utf-8"))
    problemas = []
    for registo in dados.get("outputs", []):
        caminho = (raiz / registo["path"]).resolve()
        try:
            caminho.relative_to(raiz)
        except ValueError:
            problemas.append(f"{manifesto}: caminho fora do projecto: {registo['path']}")
            continue
        if not caminho.is_file():
            problemas.append(f"{manifesto}: falta {registo['path']}")
        elif sha256(caminho) != registo["sha256"]:
            problemas.append(f"{manifesto}: hash diferente em {registo['path']}")
    return problemas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    raiz = args.root.resolve()
    manifestos = sorted(
        list((raiz / "results").rglob("manifest.json"))
        + list((raiz / "data" / "reference").rglob("manifest.json")))
    problemas = [erro for manifesto in manifestos for erro in verificar(raiz, manifesto)]
    if problemas:
        print("\n".join(problemas))
        raise SystemExit(1)
    print(f"Manifestos verificados: {len(manifestos)}")


if __name__ == "__main__":
    main()
