#!/usr/bin/env python3
"""Verificador de referências documentais locais quebradas.

Corre localmente e no CI para apanhar dois tipos de erro que passam
despercebidos em macOS/Windows mas partem em Linux (issue #6):

1. Links Markdown locais (``[texto](caminho)``) em ficheiros ``.md``
   versionados cujo destino não existe no disco.
2. Caminhos de documentação (``docs/...`` ou qualquer ``*.md``) mencionados
   em strings de código Python, em ``cct/`` e ``scripts/``, que apontem para
   um ficheiro inexistente — por exemplo uma mensagem do ``doctor`` que
   sugere ao utilizador um guia que já não existe com esse nome.

Em ambos os casos, a comparação é sensível a maiúsculas/minúsculas: um
destino que só existe com outra caixa (por exemplo ``GUIA.md`` em vez de
``guia.md``) passa despercebido em macOS e Windows (sistemas de ficheiros
insensíveis à caixa por omissão) mas falha em Linux. É por isso o erro mais
traiçoeiro, e este script reporta-o com uma mensagem distinta.

URLs (``http://``, ``https://``, ``mailto:``) e âncoras puras (``#secção``)
são ignorados. Um caminho com âncora, ``ficheiro.md#secção``, é validado só
pela parte do ficheiro — a âncora não é verificada.

Uso:
    python scripts/verificar_referencias.py
    python scripts/verificar_referencias.py --verboso
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Extensões cujos ficheiros são varridos à procura de links Markdown locais.
EXTENSAO_MARKDOWN = ".md"

# Pastas de código Python cujas strings são varridas à procura de caminhos
# de documentação (padrão "docs/..." ou "*.md").
PASTAS_CODIGO = ("cct/", "scripts/")

# Link Markdown: [texto](destino)
PADRAO_LINK_MARKDOWN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Caminho de documentação citado em código Python: começa sempre por
# "docs/" (por exemplo numa mensagem do doctor a apontar para um guia).
# Um nome de ficheiro ".md" isolado, sem "docs/", não chega a ser
# considerado — é demasiado provável que seja um ficheiro gerado
# dinamicamente (ex. "RESUMO.md" escrito por um script de inventário) e não
# uma referência documental real.
PADRAO_CAMINHO_DOC = re.compile(r"docs/[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*\.md")


def listar_ficheiros_versionados(raiz: Path) -> list[str]:
    """Devolve os caminhos (relativos à raiz, com "/") dos ficheiros versionados."""
    resultado = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=raiz, capture_output=True, check=True)
    bruto = resultado.stdout.decode("utf-8")
    return [caminho for caminho in bruto.split("\0") if caminho]


def _e_url_ou_ancora_pura(destino: str) -> bool:
    if destino.startswith(("http://", "https://", "mailto:")):
        return True
    if destino.startswith("#"):
        return True
    return False


def _existe_sensivel_a_caixa(base: Path, partes: list[str]) -> tuple[bool, bool]:
    """Verifica se ``base/partes...`` existe, sensível à caixa.

    Devolve (existe_insensivel, existe_sensivel). Se o primeiro for False, o
    caminho não existe de todo, seja qual for a caixa. Se for True mas o
    segundo for False, existe com outra combinação de maiúsculas/minúsculas.
    """
    cursor = base
    for parte in partes:
        if parte in ("", "."):
            continue
        if parte == "..":
            cursor = cursor.parent
            continue
        try:
            nomes = os.listdir(cursor)
        except OSError:
            return False, False
        if parte in nomes:
            cursor = cursor / parte
            continue
        # existe com outra caixa?
        correspondencias = [n for n in nomes if n.lower() == parte.lower()]
        if correspondencias:
            cursor = cursor / correspondencias[0]
            return True, False
        return False, False
    return True, True


def _resolver_destino(destino_ficheiro: str, base: Path, raiz: Path) -> Path:
    if destino_ficheiro.startswith("/"):
        return raiz
    return base


def verificar_links_markdown(caminhos: list[str], raiz: Path) -> tuple[list[str], list[str]]:
    """Verifica os links Markdown locais dos ficheiros .md versionados.

    Devolve (quebrados, caixa_errada), cada um como lista de mensagens
    "ficheiro:linha: destino".
    """
    quebrados: list[str] = []
    caixa_errada: list[str] = []
    for caminho in caminhos:
        if not caminho.endswith(EXTENSAO_MARKDOWN):
            continue
        ficheiro_absoluto = raiz / caminho
        try:
            texto = ficheiro_absoluto.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for numero_linha, linha in enumerate(texto.splitlines(), 1):
            for correspondencia in PADRAO_LINK_MARKDOWN.finditer(linha):
                destino = correspondencia.group(1).strip()
                if not destino or _e_url_ou_ancora_pura(destino):
                    continue
                destino_ficheiro = destino.split("#", 1)[0]
                if not destino_ficheiro:
                    continue  # só âncora, ex. "ficheiro.md#" com parte vazia
                base = _resolver_destino(
                    destino_ficheiro, ficheiro_absoluto.parent, raiz)
                partes = destino_ficheiro.lstrip("/").split("/")
                existe_ci, existe_cs = _existe_sensivel_a_caixa(base, partes)
                if not existe_ci:
                    quebrados.append(f"{caminho}:{numero_linha}: {destino}")
                elif not existe_cs:
                    caixa_errada.append(f"{caminho}:{numero_linha}: {destino}")
    return quebrados, caixa_errada


def verificar_caminhos_em_codigo(caminhos: list[str], raiz: Path) -> tuple[list[str], list[str]]:
    """Verifica caminhos de documentação citados em strings de código Python.

    Só considera ficheiros sob PASTAS_CODIGO. Devolve (quebrados, caixa_errada).
    """
    quebrados: list[str] = []
    caixa_errada: list[str] = []
    for caminho in caminhos:
        if not caminho.endswith(".py"):
            continue
        if not any(caminho.startswith(pasta) for pasta in PASTAS_CODIGO):
            continue
        ficheiro_absoluto = raiz / caminho
        try:
            texto = ficheiro_absoluto.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for numero_linha, linha in enumerate(texto.splitlines(), 1):
            for correspondencia in PADRAO_CAMINHO_DOC.finditer(linha):
                destino = correspondencia.group(0)
                # só nos interessam caminhos que pareçam apontar para
                # documentação dentro do repositório (têm pelo menos uma
                # barra, ou vivem sob docs/) — evita falsos positivos como
                # nomes de módulos Python terminados em coincidência.
                partes = destino.split("/")
                existe_ci, existe_cs = _existe_sensivel_a_caixa(raiz, partes)
                if not existe_ci:
                    quebrados.append(f"{caminho}:{numero_linha}: {destino}")
                elif not existe_cs:
                    caixa_errada.append(f"{caminho}:{numero_linha}: {destino}")
    return quebrados, caixa_errada


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verboso", action="store_true",
        help="mostra também as verificações que passaram")
    args = parser.parse_args()

    raiz = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, check=True, text=True).stdout.strip())
    caminhos = listar_ficheiros_versionados(raiz)

    links_quebrados, links_caixa_errada = verificar_links_markdown(caminhos, raiz)
    codigo_quebrados, codigo_caixa_errada = verificar_caminhos_em_codigo(caminhos, raiz)

    total_problemas = 0

    def reportar(titulo: str, quebrados: list[str], caixa_errada: list[str]) -> None:
        nonlocal total_problemas
        if not quebrados and not caixa_errada:
            if args.verboso:
                print(f"OK — {titulo}")
            return
        print(f"FALHOU — {titulo}:")
        for problema in quebrados:
            print(f"  - {problema}: destino não existe")
            total_problemas += 1
        for problema in caixa_errada:
            print(f"  - {problema}: destino existe com outra maiúsculas/minúsculas "
                  "(passa em macOS/Windows, falha em Linux)")
            total_problemas += 1

    reportar("Links Markdown locais", links_quebrados, links_caixa_errada)
    reportar("Caminhos de documentação em código Python",
              codigo_quebrados, codigo_caixa_errada)

    if total_problemas:
        print(f"\n{total_problemas} referência(s) quebrada(s) encontrada(s).")
        return 1
    print("OK — nenhuma referência documental local quebrada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
