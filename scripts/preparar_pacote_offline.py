"""Prepara o pacote de instalação offline da AppCCT.

Corre-se UMA VEZ, numa máquina com acesso à internet (por exemplo, a máquina
pessoal). Descarrega as bibliotecas necessárias para `vendor/wheels/`, calcula
os hashes e escreve um manifesto. A pasta resultante é depois copiada para a
partilha de rede e instalada nas estações sem qualquer acesso à internet.

Uso:
    python scripts/preparar_pacote_offline.py
    python scripts/preparar_pacote_offline.py --alvos win_amd64:311,win_amd64:312
    python scripts/preparar_pacote_offline.py --incluir-testes

Depois de correr, ver vendor/wheels/MANIFESTO.txt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "vendor" / "wheels"

# Alvos por omissão: as estações do CRL são Windows 64 bits; as versões de
# Python cobertas são as suportadas pelo projeto (3.11+). Cobrir várias
# versões evita ter de repetir isto quando uma máquina for actualizada.
ALVOS_OMISSAO = [
    ("win_amd64", "311"),
    ("win_amd64", "312"),
    ("win_amd64", "313"),
]

# As quatro dependências diretas, alinhadas com requirements.txt. O pip
# resolve e traz também as dependências indirectas (pdfminer.six, Pillow,
# pypdfium2, et-xmlfile, attrs, referencing, rpds-py).
PACOTES = ["pdfplumber>=0.11", "openpyxl>=3.1", "pyyaml>=6.0", "jsonschema>=4.0"]
PACOTES_TESTES = ["pytest>=8.0"]


def _analisar_alvo(texto: str) -> tuple[str, str]:
    plataforma, _, versao = texto.partition(":")
    if not plataforma or not versao.isdigit():
        raise ValueError(
            f"alvo inválido: {texto!r} — usar o formato plataforma:versão, "
            "por exemplo win_amd64:311"
        )
    return plataforma, versao


def descarregar(alvos: list[tuple[str, str]], pacotes: list[str]) -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for plataforma, versao in alvos:
        legivel = f"{plataforma}, Python {versao[0]}.{versao[1:]}"
        print(f"== A descarregar para {legivel}")
        comando = [
            sys.executable, "-m", "pip", "download",
            "--only-binary=:all:",
            "--platform", plataforma,
            "--python-version", versao,
            "--dest", str(DESTINO),
            *pacotes,
        ]
        resultado = subprocess.run(comando, text=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        if resultado.returncode != 0:
            print(resultado.stdout)
            raise SystemExit(
                f"O pip falhou para {legivel}. Se a mensagem acima falar em "
                "proxy ou ligação, esta máquina também está bloqueada: correr "
                "o script noutra máquina com acesso à internet."
            )
        for linha in resultado.stdout.splitlines():
            if linha.startswith("Saved ") or "Using cached" in linha:
                print("  " + linha.strip())


def escrever_manifesto(alvos: list[tuple[str, str]]) -> Path:
    """Regista o que ficou na pasta, com hashes, para conferência posterior."""
    wheels = sorted(DESTINO.glob("*.whl"))
    linhas = [
        "MANIFESTO DO PACOTE OFFLINE — AppCCT",
        f"Gerado em {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Alvos: {', '.join(f'{p}/py{v}' for p, v in alvos)}",
        f"Ficheiros: {len(wheels)}  "
        f"({sum(w.stat().st_size for w in wheels) / 1e6:.1f} MB)",
        "",
        "SHA-256                                                           "
        "  ficheiro",
    ]
    registo = []
    for wheel in wheels:
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        linhas.append(f"{digest}  {wheel.name}")
        registo.append({"ficheiro": wheel.name, "sha256": digest,
                        "bytes": wheel.stat().st_size})

    manifesto = DESTINO / "MANIFESTO.txt"
    manifesto.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    (DESTINO / "manifesto.json").write_text(
        json.dumps({"gerado": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
            "alvos": [f"{p}/py{v}" for p, v in alvos],
            "wheels": registo}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return manifesto


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--alvos", default=None,
                   help="lista separada por vírgulas, formato plataforma:versão "
                        "(omissão: win_amd64 para Python 3.11, 3.12 e 3.13)")
    p.add_argument("--incluir-testes", action="store_true",
                   help="incluir o pytest, para poder correr a suite na estação")
    args = p.parse_args()

    alvos = ALVOS_OMISSAO
    if args.alvos:
        alvos = [_analisar_alvo(t.strip()) for t in args.alvos.split(",") if t.strip()]

    pacotes = PACOTES + (PACOTES_TESTES if args.incluir_testes else [])
    descarregar(alvos, pacotes)
    manifesto = escrever_manifesto(alvos)

    total = sum(w.stat().st_size for w in DESTINO.glob("*.whl")) / 1e6
    print()
    print(f"Pronto. {len(list(DESTINO.glob('*.whl')))} ficheiros, {total:.1f} MB "
          f"em {DESTINO.relative_to(RAIZ)}")
    print(f"Manifesto: {manifesto.relative_to(RAIZ)}")
    print()
    print("Passo seguinte: copiar a pasta do projeto (com vendor/wheels/) para a")
    print("partilha de rede e, em cada estação, correr scripts/instalar_offline.bat")
    print("(Windows) ou scripts/instalar_offline.command (macOS).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
