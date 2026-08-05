#!/usr/bin/env python3
"""Anonimiza nomes de signatários nos artefactos de exemplo publicados.

Os PDFs originais não são alterados por este utilitário: não devem ser
versionados na edição pública. As substituições preservam o comprimento do
nome, para manter válidos os offsets do .doc.json e do projeto QDPX.

Uso:
    python scripts/anonimizar_exemplos.py
    python scripts/anonimizar_exemplos.py --check
"""
import argparse
import copy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


RAIZ = Path(__file__).resolve().parent.parent
EXEMPLOS = RAIZ / "examples"
NOMES = (
    "Deborah Cristina Santos Barbosa",
    "Cecília Patrícia Quintas",
    "Afonso Manuel de Almeida Figueiredo",
    "António Francisco Gonçalves Soares Baião",
    "Frederico Válter Resende de Oliveira Batista",
    "António Alexandre Delgado",
)


def _substituir(texto: str) -> str:
    for indice, nome in enumerate(NOMES, 1):
        rotulo = f"[SIGNATÁRIO {indice:02d}]"
        # O preenchimento é deliberado: char_start/char_end continuam corretos.
        anonimo = rotulo + " " * (len(nome) - len(rotulo))
        texto = texto.replace(nome, anonimo)
    return texto


def _tem_nome(texto: str) -> bool:
    return any(nome in texto for nome in NOMES)


def _processar_texto(caminho: Path, verificar: bool) -> int:
    texto = caminho.read_text(encoding="utf-8")
    if verificar:
        return int(_tem_nome(texto))
    caminho.write_text(_substituir(texto), encoding="utf-8")
    return 0


def _processar_zip(caminho: Path, verificar: bool) -> int:
    with ZipFile(caminho) as origem:
        membros = [(info, origem.read(info.filename)) for info in origem.infolist()]
    encontrados = 0
    atualizados = []
    for info, conteudo in membros:
        if info.filename.endswith((".txt", ".xml")):
            texto = conteudo.decode("utf-8")
            encontrados += int(_tem_nome(texto))
            if not verificar:
                conteudo = _substituir(texto).encode("utf-8")
        atualizados.append((info, conteudo))
    if verificar:
        return encontrados
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    with ZipFile(temporario, "w", ZIP_DEFLATED) as destino:
        for info, conteudo in atualizados:
            destino.writestr(copy.copy(info), conteudo)
    temporario.replace(caminho)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true",
                   help="falha se encontrar um nome de signatário conhecido")
    args = p.parse_args()
    encontrados = 0
    for caminho in EXEMPLOS.rglob("*"):
        if caminho.suffix in {".txt", ".json"}:
            encontrados += _processar_texto(caminho, args.check)
        elif caminho.suffix in {".qdpx", ".xlsx"}:
            encontrados += _processar_zip(caminho, args.check)
    if args.check and encontrados:
        print(f"ERRO: {encontrados} artefacto(s) ainda contêm nomes de signatários.")
        return 1
    print("OK — exemplos sem nomes de signatários conhecidos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
