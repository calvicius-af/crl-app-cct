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
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WHEELS = RAIZ / "vendor" / "wheels"
VENV = RAIZ / ".venv"

sys.path.insert(0, str(RAIZ))
from cct.proveniencia import sha256
from scripts.preparar_pacote_offline import pacotes_de_requirements

# Só o mapeamento módulo -> pacote, que não está em lado nenhum senão aqui: os
# nomes a instalar vêm de requirements.txt (ver pacotes_de_requirements), para
# não haver duas listas a divergir uma da outra.
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


def verificar_integridade() -> None:
    """Confere os SHA-256 das wheels contra o manifesto, antes de instalar.

    A cópia entre a máquina que preparou o pacote e a estação passa por uma
    partilha de rede ou por uma pen: um ficheiro truncado ou alterado pelo
    caminho é exactamente o que o manifesto existe para apanhar. Sem esta
    verificação, o manifesto só serviria se alguém decidisse compará-lo à mão.
    """
    print("== Integridade das bibliotecas")
    manifesto = WHEELS / "manifesto.json"
    if not manifesto.is_file():
        print("  · sem manifesto.json — integridade não verificada "
              "(pacote preparado por uma versão anterior do preparador)")
        return
    try:
        dados = json.loads(manifesto.read_text(encoding="utf-8"))
        registos = dados["wheels"]
    except (ValueError, KeyError, OSError):
        parar("o manifesto.json está ilegível ou incompleto",
              "voltar a copiar a pasta vendor/wheels/ a partir da origem")

    for registo in registos:
        caminho = WHEELS / registo["ficheiro"]
        if not caminho.is_file():
            parar(f"falta a biblioteca {registo['ficheiro']}",
                  "a cópia de vendor/wheels/ está incompleta — repeti-la")
        if sha256(caminho) != registo["sha256"]:
            parar(f"a biblioteca {registo['ficheiro']} não corresponde ao manifesto",
                  "o ficheiro alterou-se ou corrompeu-se na cópia — repetir a "
                  "cópia de vendor/wheels/ a partir da origem")
    print(f"  ✓ {len(registos)} ficheiro(s) conferidos contra o manifesto")


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
    # As dependências vêm de requirements.txt, a fonte de verdade única. O
    # pytest só se pede quando a wheel correspondente está presente: entra no
    # pacote offline apenas com --incluir-testes, e pedi-lo sem ele lá estar
    # faria o pip falhar sem necessidade.
    incluir_testes = bool(list(WHEELS.glob("pytest-*.whl")))
    pacotes = pacotes_de_requirements(incluir_testes)
    if incluir_testes:
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
              f"{python_do_venv()} -m cct.doctor")
    print(f"  ✓ as {len(MODULOS)} bibliotecas carregam")

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
    verificar_integridade()
    criar_venv(args.refazer)
    instalar()
    return confirmar()


if __name__ == "__main__":
    raise SystemExit(main())
