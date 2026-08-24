"""Extrator alternativo: docling → limpeza APP_CCT → doc.json.

Substitui apenas a camada de extração de texto (pdfplumber); a
estruturação hierárquica é a mesma do extrator clássico (estruturar),
pelo que o doc.json e o texto final têm o formato habitual do pipeline.

O docling resolve os problemas assinalados no QA de MaxQDA de 2026-08:
tabelas de anexos recuperadas (TableFormer), cláusulas com cabeçalho
próprio, tabela salarial separada das assinaturas. O pós-processador
docling-hierarchical-pdf (opcional) afina os níveis dos cabeçalhos antes
da exportação para Markdown.

Custo: ~1-1,7 s/página em CPU e download único dos modelos na primeira
corrida — o extrator clássico continua a ser a via rápida.
"""
import html
import re
from pathlib import Path

from .extractor import MARCA_TABELA_FIM, MARCA_TABELA_INI, estruturar

# mobiliário do BTE que o docling ainda deixa passar no corpo do texto
RE_BTE_CABECALHO = re.compile(r"^Boletim do Trabalho e Emprego\b")
RE_BTE_DATA = re.compile(r"^\d{1,2}\s+(?:de\s+)?[a-zç]+\s+(?:de\s+)?\d{4}$")
RE_IMAGEM = re.compile(r"^<!--\s*image\s*-->$")
RE_HEADING_MD = re.compile(r"^#{1,6}\s+")
RE_SEPARADOR_TABELA = re.compile(r"^\|[\s:|-]+\|$")
# hífen de translineação que sobrou com espaço: "profis -sional"
RE_HIFEN_SOLTO = re.compile(r"([a-zà-ú]) -([a-zà-ú])")
# item de lista markdown cujo conteúdo já traz marcador próprio ("- 1- …", "- a) …")
RE_LISTA_COM_MARCADOR = re.compile(r"^-\s+(?=\d+\s*[-–—.)]|[a-zà-ú]\)|[ivxl]+\))")

_conversor = None


def _linha_tabela(linha: str) -> bool:
    return linha.startswith("|") and linha.endswith("|") and linha.count("|") >= 2


def _celulas(linha: str) -> str:
    return " | ".join(c.strip() for c in linha[1:-1].split("|"))


def markdown_para_texto(md: str) -> str:
    """Converte o Markdown do docling no texto plano que estruturar espera.

    Remove mobiliário do BTE e placeholders de imagem, dissolve os
    cabeçalhos markdown (a hierarquia é reconstruída por estruturar),
    repara a translineação residual e reescreve as tabelas no formato
    'célula | célula' entre sentinelas, como o extrator clássico.
    """
    md = html.unescape(md)
    md = re.sub(r"\\([_*\[\]#`~])", r"\1", md)  # escapes do markdown

    saida: list[str] = []
    em_tabela = False
    for linha in md.split("\n"):
        linha = linha.replace("\t", " ").rstrip()
        limpa = linha.strip()
        if (RE_IMAGEM.match(limpa) or RE_BTE_CABECALHO.match(limpa)
                or RE_BTE_DATA.match(limpa) or re.fullmatch(r"\d+", limpa)):
            continue
        if _linha_tabela(limpa):
            if RE_SEPARADOR_TABELA.match(limpa):
                continue
            if not em_tabela:
                saida.append(MARCA_TABELA_INI)
                em_tabela = True
            saida.append(_celulas(limpa))
            continue
        if em_tabela:
            saida.append(MARCA_TABELA_FIM)
            em_tabela = False
        linha = RE_HEADING_MD.sub("", linha)
        linha = RE_LISTA_COM_MARCADOR.sub("", linha)
        linha = RE_HIFEN_SOLTO.sub(r"\1\2", linha)
        saida.append(linha)
    if em_tabela:
        saida.append(MARCA_TABELA_FIM)

    texto = "\n".join(saida)
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip() + "\n"


def _obter_conversor():
    global _conversor
    if _conversor is None:
        from docling.document_converter import DocumentConverter
        _conversor = DocumentConverter()
    return _conversor


def _converter(pdf_path: Path, paginas: tuple[int, int] | None):
    kwargs = {}
    if paginas is not None:  # 0-based fim-exclusivo → 1-based inclusivo
        kwargs["page_range"] = (paginas[0] + 1, paginas[1])
    resultado = _obter_conversor().convert(str(pdf_path), **kwargs)
    try:
        from hierarchical.postprocessor import ResultPostprocessor
        ResultPostprocessor(resultado, source=pdf_path).process()
    except Exception:
        pass  # hierarquia refinada é um extra; sem ela o estruturar resolve
    return resultado


def extrair_pdf_docling(pdf_path: Path, paginas: tuple[int, int] | None = None,
                        doc_id: str | None = None,
                        subtipo: str = "desconhecido") -> tuple[dict, str]:
    """Extrai uma convenção com docling (mesma assinatura de extrair_pdf)."""
    pdf_path = Path(pdf_path)
    resultado = _converter(pdf_path, paginas)
    md = resultado.document.export_to_markdown()
    texto = markdown_para_texto(md)
    if not texto.strip():
        raise ValueError(f"Sem texto extraível em {pdf_path} — PDF digitalizado?")
    return estruturar(texto, doc_id or pdf_path.stem, subtipo=subtipo)
