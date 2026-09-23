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
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "vendor" / "wheels"

# Constraints com as versões exactas que o CI testa. O requirements.txt declara
# mínimos (">="), o que é bom para uma instalação local tolerante e mau para um
# pacote institucional: sem isto, um pacote preparado hoje traria a versão mais
# recente de cada biblioteca, que pode não ser a que passou nos testes. Ver
# ADR-0020, lacuna 1.
CONSTRAINTS_RUNTIME = RAIZ / "requirements" / "runtime.txt"
CONSTRAINTS_DEV = RAIZ / "requirements" / "dev.txt"

sys.path.insert(0, str(RAIZ))
from cct.proveniencia import (agora_utc, escrever_manifesto as escrever_json,
                              estado_git, sha256, versao_aplicacao)

# Alvos por omissão: as estações do CRL são Windows 64 bits; as versões de
# Python cobertas são as suportadas pelo projeto (3.11+). Cobrir várias
# versões evita ter de repetir isto quando uma máquina for actualizada.
ALVOS_OMISSAO = [
    ("win_amd64", "311"),
    ("win_amd64", "312"),
    ("win_amd64", "313"),
]

# Nome do pacote de testes tal como aparece em requirements.txt. Só entra no
# pacote offline com --incluir-testes.
PACOTE_TESTES = "pytest"

# Separa "pdfplumber>=0.11" em nome e resto, para reconhecer o pytest sem
# depender da versão declarada.
_NOME_PACOTE = re.compile(r"^[A-Za-z0-9._-]+")


def parar(mensagem: str, solucao: str) -> None:
    """Termina com o mesmo formato de erro que o instalador usa."""
    raise SystemExit(f"\nPAROU AQUI: {mensagem}\n  → {solucao}")


def ficheiros_de_constraints(incluir_testes: bool) -> list[Path]:
    """Constraints a aplicar: sempre runtime, mais dev quando entra o pytest."""
    ficheiros = [CONSTRAINTS_RUNTIME]
    if incluir_testes:
        ficheiros.append(CONSTRAINTS_DEV)
    for ficheiro in ficheiros:
        if not ficheiro.is_file():
            parar(f"não encontrei {ficheiro}",
                  "correr o script a partir de uma cópia completa do projeto; "
                  "as constraints fazem parte do repositório")
    return ficheiros


def argumentos_de_constraints(ficheiros: list[Path]) -> list[str]:
    """Traduz a lista de constraints para argumentos -c do pip."""
    argumentos = []
    for ficheiro in ficheiros:
        argumentos += ["-c", str(ficheiro)]
    return argumentos


def pacotes_de_requirements(incluir_testes: bool) -> list[str]:
    """Lê requirements.txt: uma só fonte de verdade para as dependências.

    O pytest é a única exclusão condicional — está no requirements.txt porque
    é preciso para desenvolver, mas só faz sentido no pacote offline quando a
    estação vai correr a suite de testes.
    """
    ficheiro = RAIZ / "requirements.txt"
    if not ficheiro.is_file():
        parar(f"não encontrei {ficheiro}",
              "correr o script a partir de uma cópia completa do projeto")

    pacotes = []
    for linha in ficheiro.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        nome = _NOME_PACOTE.match(linha)
        if nome and nome.group(0).lower() == PACOTE_TESTES and not incluir_testes:
            continue
        pacotes.append(linha)

    if not pacotes:
        parar("requirements.txt não declara nenhuma dependência",
              "confirmar que o ficheiro não foi esvaziado por engano")
    return pacotes


def _analisar_alvo(texto: str) -> tuple[str, str]:
    plataforma, _, versao = texto.partition(":")
    if not plataforma or not versao.isdigit():
        raise ValueError(
            f"alvo inválido: {texto!r} — usar o formato plataforma:versão, "
            "por exemplo win_amd64:311"
        )
    return plataforma, versao


def descarregar(alvos: list[tuple[str, str]], pacotes: list[str],
                constraints: list[Path] | None = None) -> None:
    # A pasta é recriada de raiz: acrescentar wheels a uma pasta já povoada
    # deixaria lá versões antigas, e o instalador (que pede os pacotes pelo
    # nome, sem versão) poderia resolver para a errada, sem aviso nenhum.
    if DESTINO.exists():
        print(f"== A limpar {DESTINO.relative_to(RAIZ)} (recriada a cada corrida)")
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)

    for plataforma, versao in alvos:
        legivel = f"{plataforma}, Python {versao[0]}.{versao[1:]}"
        print(f"== A descarregar para {legivel}")
        comando = [
            sys.executable, "-m", "pip", "download",
            "--only-binary=:all:",
            "--platform", plataforma,
            "--python-version", versao,
            # --abi e --implementation são obrigatórios aqui: sem eles o pip
            # filtra as wheels pelo ABI do interpretador que corre ESTE script,
            # não pelo da versão pedida. Um script corrido em 3.12 traria
            # wheels cp312 para o alvo 3.11, e a falha só apareceria na
            # estação, longe da causa.
            "--abi", f"cp{versao}",
            "--implementation", "cp",
            "--dest", str(DESTINO),
            *argumentos_de_constraints(constraints or []),
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


def escrever_manifesto(alvos: list[tuple[str, str]],
                       constraints: list[Path] | None = None) -> Path:
    """Regista o que ficou na pasta, com hashes, para conferência posterior.

    O `manifesto.json` é lido por scripts/instalar_offline.py antes de
    instalar; o `MANIFESTO.txt` existe para leitura humana e auditoria. Os
    dois são escritos de forma atómica, para que uma interrupção não deixe um
    manifesto parcial que pareça íntegro.
    """
    wheels = sorted(DESTINO.glob("*.whl"))
    gerado = agora_utc()
    registo = [{"ficheiro": w.name, "sha256": sha256(w),
                "bytes": w.stat().st_size} for w in wheels]
    # O hash de cada ficheiro de constraints entra no manifesto para que uma
    # auditoria possa dizer, sem adivinhar, contra que versões este pacote foi
    # preparado.
    registo_constraints = [
        {"ficheiro": c.relative_to(RAIZ).as_posix(), "sha256": sha256(c)}
        for c in (constraints or [])
    ]

    linhas = [
        "MANIFESTO DO PACOTE OFFLINE — AppCCT",
        f"Gerado em {gerado}",
        f"Alvos: {', '.join(f'{p}/py{v}' for p, v in alvos)}",
        f"Constraints: {', '.join(c['ficheiro'] for c in registo_constraints) or 'nenhumas'}",
        f"Ficheiros: {len(wheels)}  "
        f"({sum(w['bytes'] for w in registo) / 1e6:.1f} MB)",
        "",
        "SHA-256                                                           "
        "  ficheiro",
    ]
    linhas += [f"{w['sha256']}  {w['ficheiro']}" for w in registo]

    manifesto = DESTINO / "MANIFESTO.txt"
    temporario = manifesto.with_suffix(".txt.tmp")
    temporario.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    temporario.replace(manifesto)

    # schema_version 2 acrescenta "constraints". O instalador só lê "wheels",
    # pelo que um manifesto antigo continua a ser aceite. "aplicacao" diz de
    # que versão e commit o pacote foi preparado: as estações não têm git, e é
    # daqui que o manifesto de cada corrida tira o commit (ISSUE-0013).
    git = estado_git(RAIZ)
    escrever_json(DESTINO / "manifesto.json", {
        "schema_version": 2,
        "gerado": gerado,
        "aplicacao": {"versao": versao_aplicacao(RAIZ), "commit": git.get("commit"),
                      "alteracoes_por_commitar": git.get("dirty")},
        "alvos": [f"{p}/py{v}" for p, v in alvos],
        "constraints": registo_constraints,
        "wheels": registo,
    })
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
        try:
            alvos = [_analisar_alvo(t.strip())
                     for t in args.alvos.split(",") if t.strip()]
        except ValueError as erro:
            parar(str(erro),
                  "usar o formato plataforma:versão, separando vários por "
                  "vírgulas, por exemplo --alvos win_amd64:311,win_amd64:312")
        if not alvos:
            parar("--alvos ficou vazio depois de separar por vírgulas",
                  "indicar pelo menos um alvo, por exemplo win_amd64:311")
    else:
        print("Sem --alvos: a gerar só para Windows 64 bits (Python 3.11 a 3.13).")
        print("Para estações macOS, repetir com "
              "--alvos macosx_11_0_arm64:311 (Apple Silicon) ou "
              "macosx_10_9_x86_64:311 (Intel).")
        print()

    pacotes = pacotes_de_requirements(args.incluir_testes)
    constraints = ficheiros_de_constraints(args.incluir_testes)
    print(f"Dependências lidas de requirements.txt: {', '.join(pacotes)}")
    print("Versões fixadas por: "
          f"{', '.join(str(c.relative_to(RAIZ)) for c in constraints)}")
    print()
    descarregar(alvos, pacotes, constraints)
    manifesto = escrever_manifesto(alvos, constraints)

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
