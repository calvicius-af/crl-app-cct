"""Adaptador do output do preprocessador V2 (#TEXT/#CODE/#ENDCODE) para doc.json.

Produz, por documento, um par (doc, texto):
- texto: o texto plano contínuo (será a fonte no QDPX);
- doc: dicionário conforme DOC_SCHEMA, com offsets char_start/char_end
  sobre esse texto. Os nós cobrem o texto na totalidade (zero perda).
"""
import re

RE_TEXT = re.compile(r"^#TEXT\s+(.+)$")
RE_CODE = re.compile(r"^#CODE\s+(.+)$")

_TIPO_POR_PREFIXO = [
    ("PREÂMBULO", "preambulo"),
    ("PREAMBULO", "preambulo"),
    ("Cláusula", "clausula"),
    ("Clausula", "clausula"),
    ("Artigo", "artigo"),
    ("Capítulo", "capitulo"),
    ("Secção", "seccao"),
    ("Anexo", "anexo"),
]


def _tipo_do_rotulo(rotulo: str) -> str:
    # rótulos do V2 podem vir como "Artigo\Artigo 1.º - ..."
    base = rotulo.split("\\")[-1].strip()
    for prefixo, tipo in _TIPO_POR_PREFIXO:
        if base.startswith(prefixo) or rotulo.startswith(prefixo):
            return tipo
    return "bloco"


def adaptar_v2(conteudo: str) -> list[tuple[dict, str]]:
    """Converte o ficheiro completo do V2 (pode conter vários #TEXT)."""
    docs = []
    doc_id = None
    blocos: list[tuple[str, list[str]]] = []
    rotulo_atual = None
    linhas_atuais: list[str] = []

    def fechar_doc():
        if doc_id is not None:
            docs.append(_construir_doc(doc_id, blocos))

    for linha in conteudo.splitlines():
        m = RE_TEXT.match(linha)
        if m:
            fechar_doc()
            doc_id, blocos = m.group(1).strip(), []
            continue
        m = RE_CODE.match(linha)
        if m:
            rotulo_atual, linhas_atuais = m.group(1).strip(), []
            continue
        if linha.strip() == "#ENDCODE":
            if rotulo_atual is not None:
                blocos.append((rotulo_atual, linhas_atuais))
            rotulo_atual = None
            continue
        if rotulo_atual is not None:
            linhas_atuais.append(linha)
    fechar_doc()
    return docs


def _construir_doc(doc_id: str, blocos: list[tuple[str, list[str]]]) -> tuple[dict, str]:
    partes = []
    nos = []
    pos = 0
    for i, (rotulo, linhas) in enumerate(blocos):
        segmento = "\n".join(linhas).strip("\n") + "\n"
        base = rotulo.split("\\")[-1].strip()
        nos.append({
            "id": f"n{i}",
            "tipo": _tipo_do_rotulo(rotulo),
            "rotulo": base,
            "char_start": pos,
            "char_end": pos + len(segmento),
            "pai": None,
            "origem": "novo",
        })
        partes.append(segmento)
        pos += len(segmento)

    texto = "".join(partes)
    doc = {
        "versao_schema": "0.1",
        "doc_id": doc_id,
        "tipo": "CCT",
        "subtipo": "desconhecido",
        "nos": nos,
    }
    return doc, texto
