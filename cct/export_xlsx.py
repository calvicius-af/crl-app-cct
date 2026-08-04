"""Exportador XLSX para as peritas (que não têm MaxQDA).

Uma linha por anotação, com o contexto que pediram para o relatório:
segmento, cláusula onde está, cadeia de contexto (capítulo/secção/anexo),
documento e confiança/método para triagem. Formato pronto para tabelas
dinâmicas — os mesmos dados do QDPX, sem trabalho adicional.
"""
from pathlib import Path


def _cadeia_contexto(no: dict, por_id: dict) -> tuple[str, str]:
    """Devolve (rótulo da cláusula, contexto acima da cláusula)."""
    clausula = ""
    acima = []
    atual = no
    while atual is not None:
        if atual["tipo"] in ("clausula", "artigo"):
            clausula = atual["rotulo"]
        elif atual["tipo"] in ("capitulo", "seccao", "anexo"):
            acima.append(atual["rotulo"])
        atual = por_id.get(atual.get("pai"))
    if no["tipo"] in ("preambulo", "bloco"):
        clausula = no["rotulo"]
    return clausula, " > ".join(reversed(acima))


def exportar_xlsx(itens: list[tuple[dict, str, dict]], destino: Path,
                  variaveis: list[dict] | None = None) -> Path:
    """`variaveis`: registos de cct.variaveis.carregar_variaveis (opcional);
    quando presentes, cada linha leva os metadados do documento do MaxQDA."""
    import openpyxl
    from .variaveis import procurar

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Segmentos"
    cab = ["Código", "Nível", "Segmento", "Cláusula", "Contexto",
           "Documento", "Subtipo", "Tipo", "CAE", "Entidade patronal",
           "Entidade sindical", "Âmbito", "Nº BTE",
           "Confiança", "Método", "Evidência"]
    ws.append(cab)

    for doc, texto, anot in itens:
        por_id = {n["id"]: n for n in doc["nos"]}
        v = procurar(variaveis, doc["doc_id"]) if variaveis else None
        subtipo = (v or {}).get("subtipo") or doc.get("subtipo", "")
        for a in anot["anotacoes"]:
            no = por_id[a["no_id"]]
            clausula, contexto = _cadeia_contexto(no, por_id)
            segmento = texto[a["char_start"]:a["char_end"]].strip()
            ws.append([
                a["codigo"],
                a.get("nivel", "clausula"),
                segmento[:2000],
                clausula,
                contexto,
                doc["doc_id"],
                subtipo,
                (v or {}).get("tipo_conv", ""),
                (v or {}).get("cae", ""),
                (v or {}).get("entidade_patronal", ""),
                (v or {}).get("entidade_sindical", ""),
                (v or {}).get("ambito_geografico", ""),
                (v or {}).get("num_bte", ""),
                a["confianca"],
                a["metodo"],
                a.get("evidencia", ""),
            ])

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    destino = Path(destino)
    wb.save(destino)
    return destino
