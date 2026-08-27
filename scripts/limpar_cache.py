"""Remove caches locais com mais de 30 dias.

Por omissão apenas mostra o que seria removido. Use ``--apply`` para aplicar a
limpeza. Nunca actua fora de ``data/interim/cache*``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path


def candidatos(raiz: Path, dias: int) -> list[Path]:
    limite = datetime.now(timezone.utc) - timedelta(days=dias)
    interim = raiz / "data" / "interim"
    return sorted(
        caminho for pasta in interim.glob("cache*") if pasta.is_dir()
        for caminho in pasta.rglob("*")
        if caminho.is_file()
        and datetime.fromtimestamp(caminho.stat().st_mtime, timezone.utc) < limite
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days tem de ser pelo menos 1")

    ficheiros = candidatos(args.root.resolve(), args.days)
    tamanho = sum(f.stat().st_size for f in ficheiros)
    acao = "Removidos" if args.apply else "Candidatos"
    for ficheiro in ficheiros:
        if args.apply:
            ficheiro.unlink()
        print(ficheiro)
    print(f"{acao}: {len(ficheiros)} ficheiros, {tamanho} bytes")


if __name__ == "__main__":
    main()
