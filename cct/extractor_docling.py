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
# item de lista que já traz marcador próprio no texto ("1- …", "a) …",
# "-Executar …" — este último dava "- -Executar" com a bala do docling)
RE_MARCADOR_PROPRIO = re.compile(
    r"^(?:\d+\s*[-–—.)]|[a-zà-ú]\)|[ivxl]+\)|[-–—•·])")

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


def celulas_da_linha(linha, indice_linha: int = 0) -> list[str]:
    """Uma célula por span, a partir de uma linha da grelha do docling.

    A grelha repete a mesma célula em todas as posições que o span
    abrange: nas colunas de um colspan ("Competência | Competência |
    Competência") e nas linhas de um rowspan. Uma célula só é emitida na
    sua posição inicial, dada por start_col_offset_idx e
    start_row_offset_idx em conjunto.

    A continuação de um colspan é omitida; a continuação de um rowspan sai
    como célula vazia, para as colunas à direita não deslizarem para a
    esquerda no texto separado por " | ". Garante-se que nenhuma célula
    se perde e que nenhuma sai repetida; NÃO se garante que todas as
    linhas tenham o mesmo número de células — quando duas linhas têm
    colspans diferentes, emitem contagens diferentes, o que é inerente a
    "uma célula por span".

    Células genuinamente iguais em posições distintas (ex.: "n.a." numa
    tabela salarial) mantêm-se todas — o que as distingue de um span é
    começarem cada uma na sua própria posição.
    """
    saida = []
    for indice, celula in enumerate(linha):
        if celula is None:
            saida.append("")
            continue
        if getattr(celula, "start_col_offset_idx", indice) != indice:
            continue  # continuação horizontal: já emitida nesta linha
        if getattr(celula, "start_row_offset_idx", indice_linha) != indice_linha:
            saida.append("")  # continuação vertical: emitida numa linha acima
            continue
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
    for indice_linha, linha in enumerate(grelha):
        celulas = celulas_da_linha(linha, indice_linha)
        if any(celulas):
            linhas.append(" | ".join(celulas))
    return linhas


# origem das coordenadas do docling: o CoordOrigin dele é um enum de
# strings, por isso comparamos pelo nome e não importamos docling_core —
# assim a ordenação (e os seus testes) não arrasta a dependência opcional
ORIGEM_INFERIOR = "BOTTOMLEFT"


def distancia_ao_topo(bbox, altura_pagina: float) -> float:
    """Topo do item medido a partir do topo da página (origem indiferente).

    Com origem no canto inferior esquerdo (o que o docling usa nos PDF),
    `t` cresce para cima e tem de ser invertido; com origem no canto
    superior já é a distância ao topo.
    """
    origem = getattr(bbox, "coord_origin", None)
    nome = getattr(origem, "name", origem)
    if nome == ORIGEM_INFERIOR:
        return altura_pagina - bbox.t
    return bbox.t


def _duas_colunas(caixas, largura: float) -> bool:
    """Página em duas colunas? (BTE antigos; os de 2025 são coluna única)"""
    if len(caixas) < 8:
        return False
    meio, tol = largura / 2, largura * 0.02
    atravessam = sum(1 for b in caixas if b.l < meio - tol and b.r > meio + tol)
    esquerda = sum(1 for b in caixas if b.r <= meio + tol)
    direita = sum(1 for b in caixas if b.l >= meio - tol)
    return (atravessam / len(caixas) < 0.05
            and esquerda / len(caixas) > 0.25 and direita / len(caixas) > 0.25)


def ordenar_por_leitura(itens: list) -> list:
    """Ordena (item, pagina, bbox) pela ordem de leitura da página.

    O docling emite por vezes blocos fora de sítio — na LAGOSemFORMA o
    conteúdo da cláusula 9.ª aparecia antes do próprio cabeçalho, e a
    cláusula ficava vazia. A geometria é fiável, por isso é ela que manda:
    página, coluna (quando existem duas) e distância ao topo. Itens sem
    geometria herdam a posição do anterior, ficando onde estavam.
    """
    paginas = {}
    for indice, (_item, pagina, bbox, _altura, _largura) in enumerate(itens):
        if bbox is not None:
            paginas.setdefault(pagina, []).append(bbox)
    colunado = {}
    for pagina, caixas in paginas.items():
        largura = next(l for (_i, p, _b, _a, l) in itens if p == pagina)
        colunado[pagina] = _duas_colunas(caixas, largura)

    chaves, ultima = [], (0, 0, 0.0)
    for indice, (_item, pagina, bbox, altura, largura) in enumerate(itens):
        if bbox is None:
            chaves.append((*ultima, indice))
            continue
        coluna = 0
        if colunado.get(pagina) and bbox.l >= largura / 2 - largura * 0.02:
            coluna = 1
        ultima = (pagina, coluna, distancia_ao_topo(bbox, altura))
        chaves.append((*ultima, indice))
    return [itens[i] for i in sorted(range(len(itens)), key=lambda i: chaves[i])]


def _itens_ordenados(documento):
    """Itens do documento pela ordem de leitura geométrica."""
    recolhidos = []
    for item, _nivel in documento.iterate_items():
        pagina, bbox, altura, largura = 0, None, 0.0, 0.0
        prov = getattr(item, "prov", None)
        if prov:
            pagina = prov[0].page_no
            bbox = prov[0].bbox
            pag = documento.pages.get(pagina)
            if pag is not None and pag.size is not None:
                altura, largura = pag.size.height, pag.size.width
        recolhidos.append((item, pagina, bbox, altura, largura))
    return [i[0] for i in ordenar_por_leitura(recolhidos)]


def documento_para_texto(documento) -> str:
    """DoclingDocument → texto plano que o estruturar consome.

    Percorre os itens pela ordem de leitura geométrica: imagens ficam de
    fora, as tabelas saem entre sentinelas MARCA_TABELA_* e o resto sai
    como texto limpo, sem sintaxe de Markdown pelo meio.
    """
    from docling_core.types.doc.document import (
        ListItem, PictureItem, TableItem, TextItem)

    linhas: list[str] = []
    for item in _itens_ordenados(documento):
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
    # sem o pós-processador docling-hierarchical-pdf: rebenta com
    # page_range e a hierarquia que infere não acrescenta nada — quem
    # reconhece capítulos e cláusulas é o estruturar, e a ordem de
    # leitura vem da geometria (ordenar_por_leitura)
    return _obter_conversor().convert(str(pdf_path), **kwargs)


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
