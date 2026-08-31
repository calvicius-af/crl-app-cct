"""Localiza convenções individuais dentro de um número do BTE.

A amostra de referência identifica documentos como "25_PR_016_BTE_04_EMARP_SINTAP":
o número do BTE (04) dá o ficheiro (bte4_2025.pdf) e os tokens das partes
(EMARP, SINTAP) permitem encontrar a convenção certa dentro do número.
"""
import re
import unicodedata
from pathlib import Path

RE_INICIO_CONVENCAO = re.compile(
    r"^(Contrato coletivo|Acordo coletivo|Acordo de empresa|Acordo de adesão)"
    r"\s+(entre|celebrado)", re.MULTILINE)

RE_DOC_ID = re.compile(r"^(\d{2})_PR_\d+_BTE_(\d+)_(.+?)(?:_TXT)?$")


def _sem_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def _colapsar(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _sem_acentos(s).lower())


def _subtokens(token: str) -> list[str]:
    """Divide tokens camel-case da referência: 'AguasRibatejo' → [aguas, ribatejo]."""
    partes = re.findall(r"[A-ZÀ-Ý]+(?![a-z])|[A-ZÀ-Ý][a-zà-ÿ]+|[a-zà-ÿ]+|\d+", token)
    return [_colapsar(p) for p in partes if len(p) > 1]


def interpretar_doc_id(doc_id: str) -> tuple[int, int, list[str]]:
    """Devolve (ano_2dig, nº BTE, subtokens das partes)."""
    m = RE_DOC_ID.match(doc_id.strip())
    if not m:
        raise ValueError(f"doc_id não reconhecido: {doc_id}")
    ano, bte, partes = int(m.group(1)), int(m.group(2)), m.group(3)
    tokens = []
    for t in partes.split("_"):
        tokens.extend(_subtokens(t))
    return ano, bte, tokens


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
