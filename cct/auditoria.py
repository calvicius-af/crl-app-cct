"""Auditoria cruzada de tabelas: o que um extrator vê e o outro não.

Uma tabela perdida na extração é hoje indistinguível de uma página sem
tabelas: o pdfplumber cai silenciosamente em `extract_text()` quando o
`find_tables()` não deteta nada, e nenhum relatório dá conta. Como as
tabelas de remuneração são precisamente o que o MaxQDA precisa de ver
completo (mapas salariais dos anexos), a divergência entre extratores é
o canário mais barato que existe: cada um apanha tabelas que o outro
deixa escapar — o docling nas grelhas estruturadas sem bordos, o
pdfplumber nas tabelas de linhas fechadas.

Os avisos daqui são avisos, não erros: um documento sem anexos pode
legitimamente não ter tabelas nenhumas. O que é irracional é um
extrator ver tabelas onde o outro não vê nada — ou um anexo de
remuneração sem uma única linha de tabela.
"""
import re
from pathlib import Path


def contar_tabelas_pdfplumber(pdf_path: Path) -> int:
    """Tabelas que o pdfplumber deteta no PDF (soma por página).

    Corre só o `find_tables()` — a parte barata. Não extrai texto, não
    estruturar: é um auditor, não um segundo extrator.
    """
    import pdfplumber

    total = 0
    with pdfplumber.open(pdf_path) as pdf:
        for pag in pdf.pages:
            total += len(pag.find_tables())
    return total


def contar_blocos_tabela(texto: str) -> int:
    """Blocos de tabela que sobreviveram no texto extraído.

    Conta as sequências de ≥2 linhas consecutivas com " | " — o mesmo
    critério de bloco que o `qdpx.pontos_de_espacamento` usa para isolar
    tabelas no MaxQDA. Linhas isoladas com " | " (prosa com barra) não
    contam.
    """
    blocos, consecutivas = 0, 0
    for linha in texto.split("\n"):
        if " | " in linha:
            consecutivas += 1
            if consecutivas == 2:       # só a 2.ª linha confirma o bloco
                blocos += 1
        else:
            consecutivas = 0
    return blocos


def contar_tabelas_docling(pdf_path: Path) -> int:
    """Tabelas que o docling deteta (itens TableItem com grelha)."""
    from .extractor_docling import _converter

    resultado = _converter(pdf_path, None)
    n = 0
    for item, _nivel in resultado.document.iterate_items():
        data = getattr(item, "data", None)
        if getattr(data, "grid", None):
            n += 1
    return n


def divergencias(n_pdfplumber: int, n_texto: int, n_docling: int | None = None
                 ) -> list[str]:
    """Avisos de divergência entre as contagens dos extratores.

    `n_pdfplumber` — o que o pdfplumber deteta (auditor);
    `n_texto` — o que sobreviveu no texto extraído (blocos " | ");
    `n_docling` — o que o docling deteta (opcional, quando instalado).

    As três vistas raramente coincidem ao exacto: uma tabela do pdfplumber
    pode colidir com duas do docling na mesma página, e uma tabela
    detetada pode não sobreviver ao `estruturar` se todas as células forem
    vazias. O aviso dispara quando um lado vê tabelas e o outro não vê
    nada — o padrão de perda silenciosa.
    """
    avisos = []
    if n_pdfplumber and not n_texto:
        avisos.append(
            f"pdfplumber deteta {n_pdfplumber} tabela(s) mas o texto "
            f"extraído não tem nenhum bloco de tabela — possível perda "
            f"na extração")
    if n_docling is not None and n_docling and not n_texto:
        avisos.append(
            f"docling deteta {n_docling} tabela(s) mas o texto extraído "
            f"não tem nenhum bloco de tabela — possível perda na extração")
    if (n_docling is not None and not n_docling and n_pdfplumber):
        # docling a não ver o que o pdfplumber vê é menos grave (o texto
        # pode ter vindo do pdfplumber), mas regista-se: pode ser tabela
        # sem grelha estruturada, que o docling não representa
        avisos.append(
            f"pdfplumber deteta {n_pdfplumber} tabela(s) que o docling não "
            f"representa (tabelas sem grelha?)")
    return avisos


# termos de anexo que na prática carregam tabelas (mapas de remuneração)
_RE_ANEXO_TABELA = re.compile(
    r"remunera|sal[áa]ri|venciment|mapa|escal[ãa]o|carreir|n[íi]vel",
    re.IGNORECASE)


def tabelas_esperadas(doc: dict, texto: str) -> list[str]:
    """Anexos que pela natureza deviam ter tabela e não têm nenhuma.

    Um anexo cujo rótulo menciona remuneração/salários/mapa/escalões sem
    uma única linha de tabela no seu corpo é quase sempre uma tabela
    perdida — o caso exato das tabelas de remuneração que motivaram esta
    auditoria. Distinguem-se dois casos, com mensagens diferentes:

    * tabela **perdida** — o documento inteiro não tem linhas de tabela;
    * tabela **fora do nó** — o documento tem tabelas, mas caíram fora
      do corpo do anexo (o estruturar fecha o anexo no cabeçalho e as
      linhas de grelha ficam órfãs a seguir). No MaxQDA chegam, mas não
      ficam ancoradas ao anexo a que pertencem.

    Aviso conservador: só anexos, só quando o rótulo o diz.
    """
    avisos = []
    doc_tem_tabelas = " | " in texto
    for no in doc.get("nos", []):
        if no.get("tipo") != "anexo" or not no.get("folha", True):
            continue
        rotulo = no.get("rotulo", "")
        if not _RE_ANEXO_TABELA.search(rotulo):
            continue
        bruto = texto[no["char_start"]:no["char_end"]]
        if " | " not in bruto:
            if doc_tem_tabelas:
                avisos.append(
                    f"{rotulo}: anexo de remuneração/mapa com a tabela fora "
                    f"do corpo do nó — as linhas existem no documento mas "
                    f"não ficaram ancoradas ao anexo (ordem de leitura)")
            else:
                avisos.append(
                    f"{rotulo}: anexo de remuneração/mapa sem nenhuma tabela "
                    f"no documento — tabela perdida na extração?")
    return avisos
