"""Instala a AppCCT numa estação sem acesso à internet.

Usa apenas as bibliotecas que estão em `vendor/wheels/`, preparadas antes com
`scripts/preparar_pacote_offline.py`. Não faz um único pedido de rede: o pip é
chamado com --no-index, pelo que nem sequer tenta falar com o proxy.

Uso normal: duplo clique em scripts/instalar_offline.bat (Windows) ou
scripts/instalar_offline.command (macOS).

Uso por linha de comandos:
    python scripts/instalar_offline.py
    python scripts/instalar_offline.py --refazer   # deita abaixo o .venv e repete

Sem `vendor/wheels/manifesto.json` a instalação pára: um pacote sem manifesto
não é verificável. Para um pacote antigo, de origem de confiança, a saída
explícita é `--aceitar-sem-manifesto`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath

# abspath em vez de resolve(): em Windows, resolve() sobre um ficheiro numa
# unidade mapeada de rede devolve o caminho UNC de destino (L:\... vira
# \\servidor\...), e é essa forma que o pip depois não consegue abrir
# (ISSUE-0009). abspath normaliza sem seguir o mapeamento, preservando a
# letra de unidade com que a estação chegou ao projeto.
RAIZ = Path(os.path.abspath(__file__)).parent.parent
WHEELS = RAIZ / "vendor" / "wheels"
VENV = RAIZ / ".venv"

sys.path.insert(0, str(RAIZ))
from cct.proveniencia import sha256
from cct.subprocesso import ambiente_utf8
from scripts.preparar_pacote_offline import (
    argumentos_de_constraints, ficheiros_de_constraints,
    pacotes_de_requirements,
)

# Só o mapeamento módulo -> pacote, que não está em lado nenhum senão aqui: os
# nomes a instalar vêm de requirements.txt (ver pacotes_de_requirements), para
# não haver duas listas a divergir uma da outra.
MODULOS = [("pdfplumber", "pdfplumber"), ("openpyxl", "openpyxl"),
           ("yaml", "pyyaml"), ("jsonschema", "jsonschema")]


def python_do_venv() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def pip_do_venv() -> Path:
    """O pip tem de existir no .venv reaproveitado (ISSUE-0009, notas).

    Um .venv deixado a meio por uma falha anterior pode ter o interpretador
    mas não o pip; reaproveitá-lo levava a uma instalação parcial silenciosa.
    """
    if os.name == "nt":
        return VENV / "Scripts" / "pip.exe"
    return VENV / "bin" / "pip"


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


def verificar_integridade(aceitar_sem_manifesto: bool = False) -> None:
    """Confere os SHA-256 das wheels contra o manifesto, antes de instalar.

    A cópia entre a máquina que preparou o pacote e a estação passa por uma
    partilha de rede ou por uma pen: um ficheiro truncado pelo caminho é
    exactamente o que o manifesto existe para apanhar. Sem esta verificação, o
    manifesto só serviria se alguém decidisse compará-lo à mão.

    O que isto garante é integridade, não autenticidade: o manifesto viaja
    dentro da mesma pasta que verifica e não é assinado, pelo que não resiste a
    quem altere as duas coisas de propósito. Ver ADR-0020.
    """
    print("== Integridade das bibliotecas")
    manifesto = WHEELS / "manifesto.json"
    if not manifesto.is_file():
        # Falha por omissão: um pacote sem manifesto não é verificável, e
        # deixar passar em silêncio transformava a garantia em opcional. A
        # saída explícita existe para pacotes preparados por versões antigas
        # do preparador, e obriga quem a usa a saber o que está a dispensar.
        if aceitar_sem_manifesto:
            print("  · sem manifesto.json — integridade NÃO verificada, por "
                  "indicação expressa (--aceitar-sem-manifesto)")
            return
        parar("não encontrei vendor/wheels/manifesto.json",
              "voltar a preparar o pacote com scripts/preparar_pacote_offline.py, "
              "ou, se o pacote for antigo e a origem for de confiança, repetir "
              "com --aceitar-sem-manifesto")
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

    # Ficheiros a mais são tão graves como ficheiros a menos: o pip resolve as
    # dependências a partir de tudo o que estiver em --find-links, pelo que uma
    # wheel que não conste do manifesto pode acabar instalada sem nunca ter
    # sido conferida. Verificar só o que o manifesto lista deixava esse caminho
    # aberto.
    esperados = {registo["ficheiro"] for registo in registos}
    intrusos = sorted(w.name for w in WHEELS.glob("*.whl")
                      if w.name not in esperados)
    if intrusos:
        parar(f"há {len(intrusos)} ficheiro(s) em vendor/wheels/ fora do "
              f"manifesto: {', '.join(intrusos)}",
              "a pasta não é a que foi preparada — repetir a cópia de "
              "vendor/wheels/ a partir da origem, sem acrescentar ficheiros")

    print(f"  ✓ {len(registos)} ficheiro(s) conferidos contra o manifesto")


def aviso_unc() -> None:
    """Avisa quando o projeto está num caminho UNC (\\\\servidor\\...).

    A instalação a partir de um caminho UNC é conhecida por falhar no pip
    (ISSUE-0009); as correcções de RAIZ e do --find-links em URI devem
    resolver o caso comum, mas o aviso transforma uma eventual falha num
    diagnóstico imediato em vez de um erro obscuro.
    """
    if str(RAIZ).startswith("\\\\"):
        print(f"  · atenção: o projeto está num caminho de rede ({RAIZ}).")
        print("    Se a instalação falhar, copiar o projeto para um disco")
        print("    local (ou usar a letra da unidade mapeada) e repetir.")


def criar_venv(refazer: bool) -> None:
    print("== Ambiente isolado (.venv)")
    if VENV.exists():
        if refazer:
            print("  · a apagar o .venv anterior")
            shutil.rmtree(VENV)
        elif python_do_venv().exists() and pip_do_venv().exists():
            print("  ✓ já existe (a reaproveitar; usar --refazer para recomeçar)")
            return
        else:
            print("  · .venv existente está incompleto — a refazer")
            shutil.rmtree(VENV)
    r = subprocess.run([sys.executable, "-m", "venv", str(VENV)], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=ambiente_utf8())
    if r.returncode != 0:
        print(r.stdout)
        parar("não foi possível criar o ambiente isolado",
              "confirmar que há espaço em disco e permissão de escrita na pasta")
    print("  ✓ criado")


def endereco_para_o_pip(pasta: Path) -> str:
    """O --find-links que o pip abre sem perder o servidor (ISSUE-0009).

    Um URI e não um caminho: o pip converte os caminhos em URI e de volta, e
    é nessa volta que o servidor se perde. E nunca com o servidor
    `localhost`: o pip segue a RFC 8089, para a qual `file://localhost/x` é
    o `/x` do disco local, e `\\\\localhost\\crl\\...` virava `\\crl\\...` — o
    erro da estação, e o que o CI reproduz (.github/workflows/instalacao-rede.yml).
    `127.0.0.1` é a mesma máquina, e o pip já o trata como servidor.
    """
    texto = str(pasta)
    if not texto.startswith("\\\\"):
        return pasta.as_uri()
    servidor, _, resto = texto[2:].partition("\\")
    if servidor.lower() == "localhost":
        servidor = "127.0.0.1"
    return PureWindowsPath(f"\\\\{servidor}\\{resto}").as_uri()


def instalar() -> None:
    print("== Instalação das bibliotecas (sem rede)")
    # As dependências vêm de requirements.txt, a fonte de verdade única. O
    # pytest só se pede quando a wheel correspondente está presente: entra no
    # pacote offline apenas com --incluir-testes, e pedi-lo sem ele lá estar
    # faria o pip falhar sem necessidade.
    incluir_testes = bool(list(WHEELS.glob("pytest-*.whl")))
    pacotes = pacotes_de_requirements(incluir_testes)
    # As mesmas constraints que fixaram a descarga fixam a instalação: sem
    # elas, o pip escolheria de entre o que estivesse na pasta, e o pacote
    # deixaria de instalar necessariamente as versões que o CI testou.
    constraints = ficheiros_de_constraints(incluir_testes)
    if incluir_testes:
        print("  · o pacote inclui o pytest (suite de testes disponível)")
    comando = [
        str(python_do_venv()), "-m", "pip", "install",
        "--no-index",                       # nunca contacta o PyPI nem o proxy
        "--find-links", endereco_para_o_pip(WHEELS),
        "--disable-pip-version-check",
        "--no-cache-dir",
        *argumentos_de_constraints(constraints),
        *pacotes,
    ]
    r = subprocess.run(comando, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, env=ambiente_utf8())
    if r.returncode != 0:
        print(r.stdout)
        parar("o pip não conseguiu instalar a partir de vendor/wheels/",
              diagnostico_do_pip(r.stdout))
    for linha in r.stdout.splitlines():
        if linha.startswith("Successfully installed"):
            print("  ✓ " + linha.strip())


def diagnostico_do_pip(saida: str) -> str:
    """Classifica a falha do pip em famílias de causa, com a saída certa.

    A mensagem única de antes apontava sempre para versão/plataforma, o que
    no gate de 2026-09-17 mandou procurar no sítio errado: a causa era um
    caminho de rede (ISSUE-0009). O stdout do pip já foi impresso; falta a
    orientação estar alinhada com ele.
    """
    s = saida.lower()
    if ("no such file or directory" in s or "errno 2" in s or "unc" in s
            or "neither a file nor a directory" in s):
        return ("a causa parece ser o caminho das bibliotecas, não as "
                "bibliotecas: se o projeto estiver numa unidade de rede "
                "(\\\\servidor\\... ou letra mapeada), copiá-lo para um disco "
                "local e repetir a instalação")
    if "access is denied" in s or "permission" in s:
        return ("a causa parece ser permissões: confirmar que a conta tem "
                "escrita na pasta do projeto e no .venv, e repetir")
    if ("python" in s and "version" in s) or "platform" in s \
            or "not a supported wheel" in s or "incompatible" in s:
        return ("o pacote offline foi preparado para outra versão de Python "
                "ou plataforma: voltar a correr preparar_pacote_offline.py "
                "com o alvo certo (ver docs/institucional/instalacao-offline.md, "
                "secção 5)")
    return ("repetir a instalação e, se voltar a falhar, enviar a saída "
            "completa acima junto com o resultado de: "
            f"{python_do_venv()} -m cct.doctor")


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
    p.add_argument("--aceitar-sem-manifesto", action="store_true",
                   help="instalar mesmo sem manifesto.json, dispensando a "
                        "conferência de integridade (só para pacotes antigos, "
                        "de origem de confiança)")
    args = p.parse_args()

    print("Instalação offline da AppCCT")
    print(f"Pasta do projeto: {RAIZ}")
    print()
    aviso_unc()
    verificar_pre_requisitos()
    verificar_integridade(args.aceitar_sem_manifesto)
    criar_venv(args.refazer)
    instalar()
    return confirmar()


if __name__ == "__main__":
    raise SystemExit(main())
