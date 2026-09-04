"""Instala a AppCCT numa estação sem acesso à internet.

Usa apenas as bibliotecas que estão em `vendor/wheels/`, preparadas antes com
`scripts/preparar_pacote_offline.py`. Não faz um único pedido de rede: o pip é
chamado com --no-index, pelo que nem sequer tenta falar com o proxy.

Uso normal: duplo clique em scripts/instalar_offline.bat (Windows) ou
scripts/instalar_offline.command (macOS).

Uso por linha de comandos:
    python scripts/instalar_offline.py
    python scripts/instalar_offline.py --refazer   # deita abaixo o .venv e repete
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WHEELS = RAIZ / "vendor" / "wheels"
VENV = RAIZ / ".venv"
MODULOS = [("pdfplumber", "pdfplumber"), ("openpyxl", "openpyxl"),
           ("yaml", "pyyaml"), ("jsonschema", "jsonschema")]


def python_do_venv() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def parar(mensagem: str, solucao: str) -> None:
    print()
    print(f"PAROU AQUI: {mensagem}")
    print(f"  → {solucao}")
    raise SystemExit(1)


def verificar_pre_requisitos() -> None:
    print("== Verificação prévia")
    if sys.version_info < (3, 11):
        parar(f"esta máquina tem Python {sys.version.split()[0]}, que é antigo",
              "instalar Python 3.11 ou superior e repetir")
    print(f"  ✓ Python {sys.version.split()[0]}")

    try:
        import venv  # noqa: F401
        print("  ✓ módulo venv disponível")
    except ImportError:
        parar("o módulo venv não está disponível",
              "reinstalar o Python com a instalação completa (instalador oficial)")

    if not WHEELS.is_dir() or not any(WHEELS.glob("*.whl")):
        parar(f"não há bibliotecas em {WHEELS}",
              "copiar a pasta do projeto completa, incluindo vendor/wheels/ — "
              "essa pasta é preparada com scripts/preparar_pacote_offline.py "
              "numa máquina com internet")
    n = len(list(WHEELS.glob("*.whl")))
    mb = sum(w.stat().st_size for w in WHEELS.glob("*.whl")) / 1e6
    print(f"  ✓ {n} bibliotecas em vendor/wheels/ ({mb:.0f} MB)")


def criar_venv(refazer: bool) -> None:
    print("== Ambiente isolado (.venv)")
    if VENV.exists():
        if refazer:
            print("  · a apagar o .venv anterior")
            shutil.rmtree(VENV)
        elif python_do_venv().exists():
            print("  ✓ já existe (a reaproveitar; usar --refazer para recomeçar)")
            return
        else:
            print("  · .venv existente está incompleto — a refazer")
            shutil.rmtree(VENV)
    r = subprocess.run([sys.executable, "-m", "venv", str(VENV)], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        print(r.stdout)
        parar("não foi possível criar o ambiente isolado",
              "confirmar que há espaço em disco e permissão de escrita na pasta")
    print("  ✓ criado")


def instalar() -> None:
    print("== Instalação das bibliotecas (sem rede)")
    # As quatro dependências diretas. Não se usa o requirements.txt porque
    # esse ficheiro inclui o pytest, que só faz parte do pacote offline se
    # tiver sido pedido com --incluir-testes; pedi-lo sem ele estar presente
    # faria o pip falhar sem necessidade.
    pacotes = [nome for _, nome in MODULOS]
    if any(WHEELS.glob("pytest-*.whl")):
        pacotes.append("pytest")
        print("  · o pacote inclui o pytest (suite de testes disponível)")
    comando = [
        str(python_do_venv()), "-m", "pip", "install",
        "--no-index",                       # nunca contacta o PyPI nem o proxy
        "--find-links", str(WHEELS),        # só o que está nesta pasta
        "--disable-pip-version-check",
        "--no-cache-dir",
        *pacotes,
    ]
    r = subprocess.run(comando, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    if r.returncode != 0:
        print(r.stdout)
        parar("o pip não conseguiu instalar a partir de vendor/wheels/",
              "se a mensagem falar em versão de Python ou plataforma, o pacote "
              "offline foi preparado para outra versão: voltar a correr "
              "preparar_pacote_offline.py com o alvo certo "
              "(ver docs/institucional/instalacao-offline.md, secção 5)")
    for linha in r.stdout.splitlines():
        if linha.startswith("Successfully installed"):
            print("  ✓ " + linha.strip())


def confirmar() -> int:
    print("== Confirmação")
    codigo = f"import {', '.join(m for m, _ in MODULOS)}"
    r = subprocess.run([str(python_do_venv()), "-c", codigo], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        print(r.stdout)
        parar("as bibliotecas instalaram mas não carregam",
              "correr o diagnóstico e enviar o resultado: "
              ".venv\\Scripts\\python -m cct.doctor")
    print("  ✓ as quatro bibliotecas carregam")

    print()
    print("Instalado. A partir daqui:")
    print("  · abrir a aplicação com duplo clique em scripts/AppCCT.bat "
          "(Windows) ou AppCCT.command (macOS)")
    print("  · diagnóstico completo do ambiente: botão 'Verificar instalação' "
          "dentro da aplicação")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--refazer", action="store_true",
                   help="apagar o .venv existente e instalar de novo")
    args = p.parse_args()

    print("Instalação offline da AppCCT")
    print(f"Pasta do projeto: {RAIZ}")
    print()
    verificar_pre_requisitos()
    criar_venv(args.refazer)
    instalar()
    return confirmar()


if __name__ == "__main__":
    raise SystemExit(main())
