"""Exportador QDPX (REFI-QDA 1.5) mínimo.

Gera o project.qde diretamente (ElementTree) e empacota com as fontes
em Sources/{guid}.txt. Regras críticas para o MaxQDA:
- texto fonte em UTF-8, sem BOM, quebras de linha LF;
- offsets das PlainTextSelection contados sobre esse texto plano.
"""
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

NS = "urn:QDA-XML:project:1.0"

_RE_NUMERICO = re.compile(r"^\d+(?:\.\d+)+$")


def _caminho(codigo: str) -> list[str]:
    """Expande um código na sua cadeia hierárquica para a árvore do MaxQDA.

    "REVER/4.08.4.1" → ["REVER", "4.08", "4.08.4", "4.08.4.1"]
    (os segmentos "/" são níveis explícitos; ids numéricos expandem-se
    pela sua ancestralidade, permitindo a organização natural em árvore)
    """
    caminho = []
    for parte in codigo.split("/"):
        parte = parte.strip()
        if _RE_NUMERICO.match(parte):
            segmentos = parte.split(".")
            for i in range(2, len(segmentos) + 1):
                caminho.append(".".join(segmentos[:i]))
        else:
            caminho.append(parte)
    # remover duplicados consecutivos preservando a ordem
    unicos = []
    for c in caminho:
        if not unicos or unicos[-1] != c:
            unicos.append(c)
    return unicos


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_NS_GUID = uuid.uuid5(uuid.NAMESPACE_URL, "crl-cct-pipeline")


def _guid_deterministico(caminho: tuple) -> str:
    """GUID estável derivado do caminho do código — exports sucessivos
    produzem sempre os mesmos GUIDs, mantendo os outputs compatíveis."""
    return str(uuid.uuid5(_NS_GUID, "/".join(caminho)))


def exportar_qdpx(itens: list[tuple[dict, str, dict]], destino: Path,
                  nome_projeto: str = "CRL CCT",
                  nome_utilizador: str = "Pipeline CCT",
                  master: dict[str, dict] | None = None) -> Path:
    """itens: lista de (doc, texto, anotacoes). Escreve o .qdpx em destino.

    `master`: registos do codebook .qdc do MaxQDA (cct.qdc.carregar_qdc);
    quando um segmento de código existe no master, reutiliza o seu GUID,
    nome de exibição, cor e descrição."""
    destino = Path(destino)
    ET.register_namespace("", NS)
    agora = _agora()

    projeto = ET.Element(f"{{{NS}}}Project", {
        "name": nome_projeto,
        "creationDateTime": agora,
        "modifiedDateTime": agora,
    })

    user_guid = str(uuid.uuid4())
    users = ET.SubElement(projeto, f"{{{NS}}}Users")
    ET.SubElement(users, f"{{{NS}}}User",
                  {"guid": user_guid, "id": "CCT", "name": nome_utilizador})

    # CodeBook em árvore: cada código expande a sua cadeia hierárquica
    # (REVER > 4.08 > 4.08.4 > 4.08.4.1) para organização natural no MaxQDA
    codebook = ET.SubElement(projeto, f"{{{NS}}}CodeBook")
    codes_el = ET.SubElement(codebook, f"{{{NS}}}Codes")
    elemento_por_caminho: dict[tuple, ET.Element] = {}
    guid_por_codigo: dict[str, str] = {}

    def garantir_codigo(codigo: str) -> str:
        from .qdc import procurar_codigo
        caminho = _caminho(codigo)
        pai_el = codes_el
        for i in range(1, len(caminho) + 1):
            chave = tuple(caminho[:i])
            if chave not in elemento_por_caminho:
                segmento = caminho[i - 1]
                reg = procurar_codigo(master, segmento) if master else None
                # GUID sempre determinístico por caminho: o mesmo código pode
                # existir em várias faixas (AUTO/REVER/CONSOLIDADO) e GUIDs
                # duplicados num projeto são inválidos; do master reutilizam-se
                # nome, cor e descrição
                attrs = {
                    "guid": _guid_deterministico(chave),
                    "name": (reg or {}).get("nome") or segmento,
                    "isCodable": "true",
                }
                if reg and reg.get("cor"):
                    attrs["color"] = reg["cor"]
                el = ET.SubElement(pai_el, f"{{{NS}}}Code", attrs)
                if reg and reg.get("descricao"):
                    d = ET.SubElement(el, f"{{{NS}}}Description")
                    d.text = reg["descricao"]
                elemento_por_caminho[chave] = el
            pai_el = elemento_por_caminho[chave]
        return pai_el.get("guid")

    for _doc, _texto, anot in itens:
        for a in anot["anotacoes"]:
            if a["codigo"] not in guid_por_codigo:
                guid_por_codigo[a["codigo"]] = garantir_codigo(a["codigo"])

    sources_el = ET.SubElement(projeto, f"{{{NS}}}Sources")
    fontes: list[tuple[str, str]] = []  # (guid, texto)
    for doc, texto, anot in itens:
        src_guid = str(uuid.uuid4())
        fontes.append((src_guid, texto))
        src = ET.SubElement(sources_el, f"{{{NS}}}TextSource", {
            "guid": src_guid,
            "name": doc["doc_id"],
            "plainTextPath": f"internal://{src_guid}.txt",
            "creatingUser": user_guid,
            "creationDateTime": agora,
            "modifyingUser": user_guid,
            "modifiedDateTime": agora,
        })
        for a in anot["anotacoes"]:
            sel = ET.SubElement(src, f"{{{NS}}}PlainTextSelection", {
                "guid": str(uuid.uuid4()),
                "name": "",
                "startPosition": str(a["char_start"]),
                "endPosition": str(a["char_end"]),
                "creatingUser": user_guid,
                "creationDateTime": agora,
                "modifyingUser": user_guid,
                "modifiedDateTime": agora,
            })
            desc = ET.SubElement(sel, f"{{{NS}}}Description")
            desc.text = (f"método={a['metodo']}; confiança={a['confianca']:.2f}; "
                         f"evidência={a.get('evidencia', '')}")
            coding = ET.SubElement(sel, f"{{{NS}}}Coding", {
                "guid": str(uuid.uuid4()),
                "creatingUser": user_guid,
                "creationDateTime": agora,
            })
            ET.SubElement(coding, f"{{{NS}}}CodeRef",
                          {"targetGUID": guid_por_codigo[a["codigo"]]})

    xml_bytes = ET.tostring(projeto, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.qde", xml_bytes)
        for guid, texto in fontes:
            zf.writestr(f"Sources/{guid}.txt",
                        texto.replace("\r\n", "\n").encode("utf-8"))
    return destino
