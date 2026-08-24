"""Prova mínima do ISSUE-0003: richTextPath com DOCX num QDPX.

Gera um QDPX de UM documento com duas representações da mesma fonte:
o TXT plano (âncora das seleções, como sempre) e um DOCX com uma tabela
verdadeira (richTextPath). Três codificações marcam os pontos críticos:

  PROVA>ANTES  — frase antes da tabela (controlo: tem de estar sempre certa)
  PROVA>CELULA — o valor "907,53" dentro da tabela
  PROVA>DEPOIS — frase imediatamente a seguir à tabela (o teste decisivo:
                 se o MaxQDA recalcular offsets a partir do DOCX, é esta
                 âncora que desliza)

Verificação no MaxQDA após importar: se o documento aparecer com a tabela
formatada E os três segmentos codificados caírem exatamente nas frases
com os nomes SEGMENTO-*, a via DOCX é viável.

Uso: .venv/bin/python scripts/prova_richtext_qdpx.py [destino.qdpx]
"""
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

NS = "urn:QDA-XML:project:1.0"

PARAGRAFOS_ANTES = [
    "PROVA DE CONCEITO — richTextPath com DOCX (ISSUE-0003).",
    "Parágrafo de controlo. SEGMENTO-ANTES: esta frase deve aparecer "
    "codificada do primeiro P ao ponto final.",
    "Tabela salarial de teste:",
]
TABELA = [
    ["Níveis", "Escalão 1", "Escalão 2"],
    ["1", "1 234,56", "1 345,67"],
    ["2", "907,53", "998,42"],
]
PARAGRAFOS_DEPOIS = [
    "SEGMENTO-DEPOIS: se esta frase aparecer codificada por inteiro, a "
    "âncora sobreviveu à tabela e a via DOCX é viável.",
    "Último parágrafo de fecho do documento de prova.",
]


def texto_plano() -> str:
    linhas = list(PARAGRAFOS_ANTES)
    linhas += [" | ".join(r) for r in TABELA]
    linhas += PARAGRAFOS_DEPOIS
    return "\n".join(linhas) + "\n"


def docx_bytes() -> bytes:
    """DOCX mínimo (WordprocessingML à mão) com os parágrafos e a tabela."""
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    def par(txt: str) -> str:
        return f'<w:p><w:r><w:t xml:space="preserve">{escape(txt)}</w:t></w:r></w:p>'

    borda = ('<w:tcBorders>'
             + "".join(f'<w:{l} w:val="single" w:sz="4" w:color="000000"/>'
                       for l in ("top", "left", "bottom", "right"))
             + '</w:tcBorders>')
    linhas_tbl = "".join(
        "<w:tr>" + "".join(
            f'<w:tc><w:tcPr>{borda}</w:tcPr>{par(c)}</w:tc>' for c in row)
        + "</w:tr>"
        for row in TABELA)
    corpo = ("".join(par(p) for p in PARAGRAFOS_ANTES)
             + '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/></w:tblPr>'
             + '<w:tblGrid>' + '<w:gridCol/>' * len(TABELA[0]) + '</w:tblGrid>'
             + linhas_tbl + "</w:tbl>"
             + "".join(par(p) for p in PARAGRAFOS_DEPOIS))
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="{W}"><w:body>{corpo}'
                f'<w:sectPr/></w:body></w:document>')
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType='
        '"application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>')
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>')

    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document)
    return buf.getvalue()


def main():
    destino = Path(sys.argv[1] if len(sys.argv) > 1
                   else "results/prova_richtext/prova_richtext.qdpx")
    destino.parent.mkdir(parents=True, exist_ok=True)

    texto = texto_plano()
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ET.register_namespace("", NS)

    projeto = ET.Element(f"{{{NS}}}Project", {
        "name": "PROVA richtext DOCX (ISSUE-0003)",
        "creationDateTime": agora, "modifiedDateTime": agora,
    })
    user_guid = str(uuid.uuid4())
    users = ET.SubElement(projeto, f"{{{NS}}}Users")
    ET.SubElement(users, f"{{{NS}}}User",
                  {"guid": user_guid, "id": "CCT", "name": "Pipeline CCT"})

    codebook = ET.SubElement(projeto, f"{{{NS}}}CodeBook")
    codes = ET.SubElement(codebook, f"{{{NS}}}Codes")
    pai = ET.SubElement(codes, f"{{{NS}}}Code", {
        "guid": str(uuid.uuid4()), "name": "PROVA", "isCodable": "true"})
    guids = {}
    for nome in ("ANTES", "CELULA", "DEPOIS"):
        g = str(uuid.uuid4())
        ET.SubElement(pai, f"{{{NS}}}Code",
                      {"guid": g, "name": nome, "isCodable": "true"})
        guids[nome] = g

    src_guid = str(uuid.uuid4())
    sources = ET.SubElement(projeto, f"{{{NS}}}Sources")
    src = ET.SubElement(sources, f"{{{NS}}}TextSource", {
        "guid": src_guid,
        "name": "prova_richtext",
        "plainTextPath": f"internal://{src_guid}.txt",
        "richTextPath": f"internal://{src_guid}.docx",
        "creatingUser": user_guid, "creationDateTime": agora,
        "modifyingUser": user_guid, "modifiedDateTime": agora,
    })

    def marcar(codigo: str, trecho: str):
        ini = texto.index(trecho)
        sel = ET.SubElement(src, f"{{{NS}}}PlainTextSelection", {
            "guid": str(uuid.uuid4()), "name": "",
            "startPosition": str(ini), "endPosition": str(ini + len(trecho)),
            "creatingUser": user_guid, "creationDateTime": agora,
            "modifyingUser": user_guid, "modifiedDateTime": agora,
        })
        coding = ET.SubElement(sel, f"{{{NS}}}Coding", {
            "guid": str(uuid.uuid4()),
            "creatingUser": user_guid, "creationDateTime": agora,
        })
        ET.SubElement(coding, f"{{{NS}}}CodeRef", {"targetGUID": guids[codigo]})

    marcar("ANTES", PARAGRAFOS_ANTES[1])
    marcar("CELULA", "907,53")
    marcar("DEPOIS", PARAGRAFOS_DEPOIS[0])

    xml_bytes = ET.tostring(projeto, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.qde", xml_bytes)
        zf.writestr(f"Sources/{src_guid}.txt", texto.encode("utf-8"))
        zf.writestr(f"Sources/{src_guid}.docx", docx_bytes())
    print(f"→ {destino}")
    print("No MaxQDA: importar; verificar (1) tabela formatada, "
          "(2) ANTES/CELULA/DEPOIS ancorados nas frases SEGMENTO-*.")


if __name__ == "__main__":
    main()
