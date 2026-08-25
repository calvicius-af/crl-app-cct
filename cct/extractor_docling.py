"""Extrator alternativo: docling → limpeza APP_CCT → doc.json.

Substitui apenas a camada de extração de texto (pdfplumber); a
estruturação hierárquica é a mesma do extrator clássico (estruturar),
pelo que o doc.json e o texto final têm o formato habitual do pipeline.

O texto é montado a partir dos itens do DoclingDocument (não do
Markdown): os cabeçalhos chegam como texto simples — sem os `#` que o
Markdown acrescenta e que sobreviviam à limpeza quando o nível passava
de 6 — e as tabelas são lidas da grelha estruturada, o que permite
emitir uma célula por span em vez das repetições que o Markdown cria
para cada coluna abrangida por um colspan (ISSUE-0003, pontos 1 e 2).

Custo: ~1-1,7 s/página em CPU e download único dos modelos na primeira
corrida — o extrator clássico continua a ser a via rápida.
"""
import re
from pathlib import Path

from .extractor import MARCA_TABELA_FIM, MARCA_TABELA_INI, estruturar

# mobiliário do BTE que aparece no corpo da página
RE_BTE_CABECALHO = re.compile(r"^Boletim do Trabalho e Emprego\b")
RE_BTE_DATA = re.compile(r"^\d{1,2}\s+(?:de\s+)?[a-zç]+\s+(?:de\s+)?\d{4}$")
# hífen de translineação que sobrou com espaço: "profis -sional"
RE_HIFEN_SOLTO = re.compile(r"([a-zà-ú]) -([a-zà-ú])")
# item de lista que já traz marcador próprio no texto ("1- …", "a) …")
RE_MARCADOR_PROPRIO = re.compile(r"^(?:\d+\s*[-–—.)]|[a-zà-ú]\)|[ivxl]+\))")

_conversor = None


def limpar_texto_item(texto: str) -> str | None:
    """Normaliza o texto de um item; devolve None se for para descartar.

    Descarta mobiliário do BTE (cabeçalho corrido, data da edição,
    número de página solto) e repara a translineação que o docling deixa
    com espaço antes do hífen.
    """
    texto = (texto or "").replace("\n", " ").replace("\t", " ")
    texto = re.sub(r"\s{2,}", " ", texto).strip()
    if not texto:
        return None
    if (RE_BTE_CABECALHO.match(texto) or RE_BTE_DATA.match(texto)
            or re.fullmatch(r"\d+", texto)):
        return None
    return RE_HIFEN_SOLTO.sub(r"\1\2", texto)


def celulas_sem_colspan(linha) -> list[str]:
    """Uma célula por span, a partir de uma linha da grelha do docling.

    A grelha repete a mesma célula em cada coluna que um colspan abrange
    ("Competência | Competência | Competência"); só a primeira conta,
    identificada por start_col_offset_idx. Células genuinamente repetidas
    em colunas distintas (ex.: "n.a." numa tabela salarial) mantêm-se.
    """
    saida = []
    for indice, celula in enumerate(linha):
        if celula is None:
            saida.append("")
            continue
        if getattr(celula, "start_col_offset_idx", indice) != indice:
            continue  # continuação de um colspan já emitido
        texto = (getattr(celula, "text", "") or "").replace("\n", " ").strip()
        saida.append(re.sub(r"\s{2,}", " ", texto))
    return saida


def _linhas_de_tabela(tabela) -> list[str]:
    """Tabela do docling → linhas 'célula | célula' (formato do pipeline)."""
    try:
        grelha = tabela.data.grid
    except AttributeError:
        return []
    linhas = []
    for linha in grelha:
        celulas = celulas_sem_colspan(linha)
        if any(celulas):
            linhas.append(" | ".join(celulas))
    return linhas


def documento_para_texto(documento) -> str:
    """DoclingDocument → texto plano que o estruturar consome.

    Percorre os itens pela ordem de leitura: imagens ficam de fora, as
    tabelas saem entre sentinelas MARCA_TABELA_* e o resto sai como
    texto limpo, sem sintaxe de Markdown pelo meio.
    """
    from docling_core.types.doc.document import (
        ListItem, PictureItem, TableItem, TextItem)

    linhas: list[str] = []
    for item, _nivel in documento.iterate_items():
        if isinstance(item, PictureItem):
            continue
        if isinstance(item, TableItem):
            corpo = _linhas_de_tabela(item)
            if corpo:
                linhas.append(MARCA_TABELA_INI)
                linhas.extend(corpo)
                linhas.append(MARCA_TABELA_FIM)
            continue
        if not isinstance(item, TextItem):
            continue
        texto = limpar_texto_item(item.text)
        if texto is None:
            continue
        if isinstance(item, ListItem) and not RE_MARCADOR_PROPRIO.match(texto):
            texto = f"- {texto}"
        linhas.append(texto)
    return "\n".join(linhas) + "\n"


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
    texto = documento_para_texto(resultado.document)
    if not texto.strip():
        raise ValueError(f"Sem texto extraível em {pdf_path} — PDF digitalizado?")
    return estruturar(texto, doc_id or pdf_path.stem, subtipo=subtipo)
