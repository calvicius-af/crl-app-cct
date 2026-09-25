"""Limites dos PDF que entram na extração, verificados antes de a começar (#25).

Um PDF é um input complexo, e o que custa caro tem de falhar cedo e com uma
mensagem que diga o que fazer: um ficheiro corrompido, protegido por
palavra-passe, grande de mais ou com páginas a mais. Verifica-se com o PDFium,
que abre o ficheiro sem o interpretar todo, antes de qualquer extrator (o
pdfplumber ou o docling, que carrega modelos e pode demorar minutos).

Os limites mudam-se pelo ambiente, sem mexer no código:
`CCT_MAX_PAGINAS` (por omissão 500) e `CCT_MAX_MB` (por omissão 100). Uma
convenção do BTE tem poucas dezenas de páginas; o maior PDF do corpus de 2025
tem 67 páginas e 1,6 MB.
"""
from __future__ import annotations

import os
from pathlib import Path

MAX_PAGINAS = 500
MAX_MB = 100.0


class PDFRecusado(ValueError):
    """O PDF não entra na extração; a mensagem diz porquê e o que fazer."""


def _limite(nome: str, omissao: float) -> float:
    valor = os.environ.get(nome)
    try:
        return float(valor) if valor else omissao
    except ValueError:
        raise PDFRecusado(f"{nome}={valor!r} não é um número") from None


def verificar_pdf(caminho: Path) -> int:
    """Abre o PDF com o PDFium e devolve o número de páginas, ou recusa-o."""
    import pypdfium2 as pdfium

    caminho = Path(caminho)
    max_mb = _limite("CCT_MAX_MB", MAX_MB)
    max_paginas = int(_limite("CCT_MAX_PAGINAS", MAX_PAGINAS))
    tamanho = caminho.stat().st_size / (1024 * 1024)
    if tamanho > max_mb:
        raise PDFRecusado(
            f"{caminho.name}: {tamanho:.1f} MB, acima do limite de {max_mb:g} MB. "
            "Uma convenção do BTE não chega a isto: confirmar que é o PDF certo, "
            "ou subir CCT_MAX_MB")
    try:
        documento = pdfium.PdfDocument(str(caminho))
    except pdfium.PdfiumError as e:
        if "password" in str(e).lower():
            raise PDFRecusado(
                f"{caminho.name}: o PDF está protegido por palavra-passe. Obter a "
                "versão pública do BTE, que não é protegida") from None
        raise PDFRecusado(
            f"{caminho.name}: o PDF está corrompido ou não é um PDF ({e}). "
            "Descarregar de novo do BTE") from None
    try:
        paginas = len(documento)
    finally:
        documento.close()
    if paginas > max_paginas:
        raise PDFRecusado(
            f"{caminho.name}: {paginas} páginas, acima do limite de {max_paginas}. "
            "Uma convenção do BTE não chega a isto: confirmar que é uma convenção e "
            "não o boletim inteiro, ou subir CCT_MAX_PAGINAS")
    return paginas
