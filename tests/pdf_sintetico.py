"""PDF mínimos, escritos à mão, para testar os extratores de ponta a ponta.

Os PDF do BTE não estão no repositório. Sem eles, os testes do extrator
trabalhavam sobre texto já extraído, e um defeito na passagem PDF → texto (a
ordem de leitura, o mobiliário, a remoção de linhas) só aparecia na estação.
Estes PDF são pequenos, mas passam pelo pdfplumber e pelo PDFium como um PDF
real: cada linha tem uma posição na página.

Só usa a fonte Helvetica com a codificação WinAnsi, que cobre os acentos do
português. Não serve para tabelas com grelha nem para texto rodado.
"""
from pathlib import Path

LARGURA, ALTURA = 595, 842          # A4, em pontos


def _escapar(texto: str) -> bytes:
    bruto = texto.encode("cp1252")
    return (bruto.replace(b"\\", b"\\\\").replace(b"(", b"\\(")
            .replace(b")", b"\\)"))


def _conteudo(linhas: list[tuple[float, float, str]]) -> bytes:
    partes = [b"BT /F1 10 Tf"]
    for x, y, texto in linhas:
        partes.append(b"1 0 0 1 %.1f %.1f Tm (" % (x, y) + _escapar(texto) + b") Tj")
    partes.append(b"ET")
    return b"\n".join(partes)


def escrever_pdf(destino: Path, paginas: list[list[tuple[float, float, str]]]) -> Path:
    """Escreve um PDF; cada página é uma lista de (x, y, texto), y a contar de baixo."""
    objetos: list[bytes] = []

    def novo(corpo: bytes) -> int:
        objetos.append(corpo)
        return len(objetos)

    catalogo = novo(b"")                     # preenchidos no fim
    arvore = novo(b"")
    fonte = novo(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                 b"/Encoding /WinAnsiEncoding >>")
    folhas = []
    for linhas in paginas:
        conteudo = _conteudo(linhas)
        fluxo = novo(b"<< /Length %d >>\nstream\n" % len(conteudo) + conteudo
                     + b"\nendstream")
        folhas.append(novo(
            b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] "
            b"/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
            % (arvore, LARGURA, ALTURA, fonte, fluxo)))
    objetos[catalogo - 1] = b"<< /Type /Catalog /Pages %d 0 R >>" % arvore
    objetos[arvore - 1] = (b"<< /Type /Pages /Kids [%s] /Count %d >>"
                           % (b" ".join(b"%d 0 R" % f for f in folhas), len(folhas)))

    saida = bytearray(b"%PDF-1.4\n")
    posicoes = []
    for n, corpo in enumerate(objetos, 1):
        posicoes.append(len(saida))
        saida += b"%d 0 obj\n" % n + corpo + b"\nendobj\n"
    xref = len(saida)
    saida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    saida += b"".join(b"%010d 00000 n \n" % p for p in posicoes)
    saida += (b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
              % (len(objetos) + 1, catalogo, xref))
    Path(destino).write_bytes(bytes(saida))
    return Path(destino)


def pagina_bte(numero: int, corpo: list[str], bte: int = 31) -> list[tuple[float, float, str]]:
    """Página com o mobiliário do BTE: cabeçalho no topo, rodapé no fundo."""
    linhas = [(72, 800, f"Boletim do Trabalho e Emprego, n.º {bte}, 22/8/2026")]
    y = 760.0
    for texto in corpo:
        linhas.append((72, y, texto))
        y -= 14
    linhas.append((72, 40, f"BTE {bte} | {numero}"))
    return linhas
