"""Localiza convenções individuais dentro de um número do BTE.

A amostra de referência identifica documentos como "25_PR_016_BTE_04_EMARP_SINTAP":
o número do BTE (04) dá o ficheiro (bte4_2025.pdf) e os tokens das partes
(EMARP, SINTAP) permitem encontrar a convenção certa dentro do número.

O token depois do ano (aqui "PR") identifica a família documental — "PR" para
convenções, mas cct.nomeacao usa também "PE"/"AV"/"AA" para portarias de
extensão, avisos e acordos de adesão (ver TOKEN_FAMILIA em cct/nomeacao.py).
RE_DOC_ID aceita qualquer sigla de duas letras maiúsculas nessa posição — não
lista as famílias uma a uma, para não ter de ser revisto sempre que
cct.nomeacao ganhar uma família nova.

Desde a adoção da convenção de nomes do RNC (ADR-0016) há um segundo esquema,
com o ano por extenso, o âmbito, o número sequencial do BTE, o tipo tal como
vem do índice e o código IRCT:

    2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2

`interpretar_doc_id` lê os dois e devolve sempre a mesma coisa — (ano de dois
dígitos, número do BTE, tokens das partes) — para que nada a jusante tenha de
saber em que esquema o corpus foi nomeado. Um corpus pode ter os dois à mistura:
os nomes já atribuídos não se alteram (ver docs/rnc/README.md §5).
"""
import re
import unicodedata
from pathlib import Path

RE_INICIO_CONVENCAO = re.compile(
    r"^(Contrato coletivo|Acordo coletivo|Acordo de empresa|Acordo de adesão)"
    r"\s+(entre|celebrado)", re.MULTILINE)

RE_DOC_ID = re.compile(r"^(\d{2})_[A-Z]{2}_\d+_BTE_(\d+)_(.+?)(?:_TXT)?$")

# Esquema RNC: {ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}
# O tipo vem do índice do BTE e pode ter variantes com hífen (CCT-ALT,
# AE-ALT-RECT); o código IRCT são dígitos; as siglas vêm separadas por hífen e
# podem terminar em "+N" quando há mais outorgantes do que os que cabem no nome.
RE_DOC_ID_RNC = re.compile(
    r"^(\d{4})_(?P<ambito>[A-Z]{3})_(?P<seq>\d+)_(?P<tipo>[A-Z][A-Z-]*)"
    r"_(?P<cod>\d+)_BTE_(\d+)_(.+?)(?:_TXT)?$")


def _sem_acentos(s) -> str:
    """Remove marcas de acentuação (NFD → descarta categoria 'Mn').

    Implementação partilhada — cct/nomeacao.py e cct/recolha.py importam
    daqui em vez de reimplementar, para não terem três versões da mesma
    normalização a poderem divergir silenciosamente (ver PR #35, achado nº9).
    """
    return "".join(c for c in unicodedata.normalize("NFD", str(s or ""))
                   if unicodedata.category(c) != "Mn")


def _colapsar(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _sem_acentos(s).lower())


def _subtokens(token: str) -> list[str]:
    """Divide tokens camel-case da referência: 'AguasRibatejo' → [aguas, ribatejo]."""
    partes = re.findall(r"[A-ZÀ-Ý]+(?![a-z])|[A-ZÀ-Ý][a-zà-ÿ]+|[a-zà-ÿ]+|\d+", token)
    return [_colapsar(p) for p in partes if len(p) > 1]


def interpretar_doc_id(doc_id: str) -> tuple[int, int, list[str]]:
    """Devolve (ano_2dig, nº BTE, subtokens das partes).

    Aceita os dois esquemas de nome. O ano vem sempre com dois dígitos, mesmo
    quando o nome o traz por extenso, porque é assim que o resto do pipeline o
    compara — mudar isso obrigaria a rever o cruzamento com as variáveis do
    MaxQDA, que é o que esta função existe para não partir.
    """
    doc_id = doc_id.strip()
    m = RE_DOC_ID.match(doc_id)
    if m:
        ano, bte, partes = int(m.group(1)), int(m.group(2)), m.group(3)
    else:
        m = RE_DOC_ID_RNC.match(doc_id)
        if not m:
            raise ValueError(f"doc_id não reconhecido: {doc_id}")
        ano, bte, partes = int(m.group(1)) % 100, int(m.group(6)), m.group(7)
    tokens = []
    for t in re.split(r"[_-]", partes):
        tokens.extend(_subtokens(re.sub(r"\+\d+$", "", t)))
    return ano, bte, tokens


def interpretar_nome_rnc(doc_id: str) -> dict | None:
    """Metadados que o esquema RNC leva no nome, ou None se for outro esquema.

    Serve para não ter de abrir o catálogo quando só se quer saber o âmbito ou o
    código IRCT de um ficheiro que se tem à frente. O catálogo continua a ser a
    fonte de verdade — isto é uma conveniência, não uma segunda fonte.
    """
    m = RE_DOC_ID_RNC.match(doc_id.strip())
    if not m:
        return None
    return {"ano": int(m.group(1)), "ambito": m.group("ambito"),
            "seq": int(m.group("seq")), "tipo": m.group("tipo"),
            "cod_irct": m.group("cod"), "num_bte": int(m.group(6)),
            "siglas": [s for s in re.sub(r"\+\d+$", "", m.group(7)).split("-") if s],
            "outros_outorgantes": int(re.search(r"\+(\d+)$", m.group(7)).group(1))
            if re.search(r"\+(\d+)$", m.group(7)) else 0}


def listar_convencoes(pdf_path: Path) -> list[dict]:
    """Devolve [{titulo, pag_ini, pag_fim}] para cada convenção do número (0-based, fim exclusivo)."""
    import pdfplumber

    inicios = []  # (pagina, titulo)
    with pdfplumber.open(pdf_path) as pdf:
        n_pags = len(pdf.pages)
        for i, pag in enumerate(pdf.pages):
            t = pag.extract_text() or ""
            for m in RE_INICIO_CONVENCAO.finditer(t):
                titulo = t[m.start():m.start() + 300].split("\n")
                # título pode ocupar 2-3 linhas
                titulo = " ".join(l.strip() for l in titulo[:3])
                inicios.append((i, titulo))
    convencoes = []
    for j, (pag, titulo) in enumerate(inicios):
        fim = inicios[j + 1][0] if j + 1 < len(inicios) else n_pags
        # a convenção seguinte pode começar na mesma página
        convencoes.append({"titulo": titulo, "pag_ini": pag,
                           "pag_fim": max(fim, pag + 1)})
    return convencoes


def encontrar_convencao(pdf_path: Path, doc_id: str,
                        minimo: float = 0.5) -> dict | None:
    """Escolhe a convenção do número cujo título melhor cobre os tokens do doc_id."""
    _ano, _bte, tokens = interpretar_doc_id(doc_id)
    if not tokens:
        return None
    melhores = []
    for conv in listar_convencoes(pdf_path):
        titulo_norm = _colapsar(conv["titulo"])
        acertos = sum(1 for t in tokens if t and t in titulo_norm)
        melhores.append((acertos / len(tokens), conv))
    if not melhores:
        return None
    pontuacao, conv = max(melhores, key=lambda x: x[0])
    if pontuacao < minimo:
        return None
    return {**conv, "pontuacao": pontuacao}


def caminho_bte(pasta_bte: Path, doc_id: str) -> Path:
    ano2, bte, _ = interpretar_doc_id(doc_id)
    ano = 2000 + ano2
    return pasta_bte / f"bte_{ano}" / f"bte{bte}_{ano}.pdf"
