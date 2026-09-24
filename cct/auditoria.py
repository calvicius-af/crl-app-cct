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


# uma tabela de remunerações genuína não é quase 2× mais alta do que larga;
# quando é, o mais provável é estar rodada 90º no PDF (ISSUE-0020) — o
# pdfplumber não deteta a rotação e lê o texto invertido, carácter a
# carácter, sem se queixar
LIMIAR_PROPORCAO_RODADA = 2.0


def _aviso_tabela_rodada(pagina: int, bbox: tuple[float, float, float, float]
                         ) -> str | None:
    """Aviso para uma tabela cuja bbox (x0, top, x1, bottom) sugere rotação."""
    x0, top, x1, bottom = bbox
    largura, altura = x1 - x0, bottom - top
    if largura > 0 and altura > LIMIAR_PROPORCAO_RODADA * largura:
        return (f"p{pagina}: tabela com {largura:.0f}×{altura:.0f} pt "
                f"(muito mais alta do que larga) — provavelmente rodada "
                f"90º; o pdfplumber lê-a invertida, usar --extrator docling")
    return None


def tabelas_rodadas_pdfplumber(pdf_path: Path) -> list[str]:
    """Tabelas cuja bbox sugere rotação 90º, por página (auditor, não segundo extrator).

    O docling lê estas tabelas na orientação correta (verificado nos quatro
    documentos CARRISTUR do BTE 31/2026); o pdfplumber não deteta a rotação
    e emite o texto invertido como se fosse conteúdo válido. Isto não
    corrige a leitura — só avisa, para quem vir a tabela invertida no QDPX
    saber que a causa é conhecida e que `--extrator docling` a lê bem.
    """
    import pdfplumber

    avisos = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, pag in enumerate(pdf.pages, 1):
            for tab in pag.find_tables():
                aviso = _aviso_tabela_rodada(i, tab.bbox)
                if aviso:
                    avisos.append(aviso)
    return avisos


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


def _descendentes(no: dict, nos: list[dict]) -> list[dict]:
    filhos = [n for n in nos if n.get("pai") == no["id"]]
    return [d for f in filhos for d in (f, *_descendentes(f, nos))]


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
    nos = doc.get("nos", [])
    for no in nos:
        if no.get("tipo") != "anexo":
            continue
        rotulo = no.get("rotulo", "")
        if not _RE_ANEXO_TABELA.search(rotulo):
            continue
        # O estruturar fecha o nó do anexo no cabeçalho e põe o corpo num
        # nó filho («Corpo de ANEXO III…»). O corpo do anexo são os dois:
        # olhar só para o cabeçalho dava «fora do nó» para tabelas que estão
        # no sítio certo (issue #83).
        bruto = "".join(texto[n["char_start"]:n["char_end"]]
                        for n in [no, *_descendentes(no, nos)])
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
