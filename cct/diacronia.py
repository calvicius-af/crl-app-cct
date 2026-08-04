"""Comparador diacrónico de versões de convenções (Fase 5, N4).

Implementa o classificador do CRL para o relatório anual: cada cláusula da
versão nova é classificada como "=" (igual à anterior), "alteracao", ou
"nova"; as cláusulas da versão antiga sem correspondência ficam "removida".

Alinhamento em duas passagens:
1. pelo número da cláusula/artigo (o caso comum);
2. as não emparelhadas, por semelhança de conteúdo (recupera renumerações).
"""
import difflib
import re
import unicodedata

LIMIAR_IGUAL = 0.995
LIMIAR_RENUMERACAO = 0.75
# um match pelo número só é aceite se o conteúdo for minimamente parecido;
# senão trata-se de renumeração (outra cláusula ocupa aquele número)
LIMIAR_MESMO_NUMERO = 0.5

RE_NUMERO = re.compile(r"(cl[aá]usula|artigo)\s+(\d+)", re.IGNORECASE)


def _norm(t: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFD", t)
                if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t.lower()).strip()


def _chave_numero(no: dict) -> str | None:
    m = RE_NUMERO.search(no["rotulo"])
    return f"{m.group(1).lower()[:2]}{int(m.group(2))}" if m else None


def _titulo(no: dict) -> str:
    partes = no["rotulo"].split(" - ", 1)
    return _norm(partes[1]) if len(partes) > 1 else ""


def _corpo(no: dict, texto: str) -> str:
    """Texto da cláusula sem a linha do rótulo (títulos mudam sem ser alteração)."""
    trecho = texto[no["char_start"]:no["char_end"]]
    linhas = trecho.split("\n", 1)
    return linhas[1] if len(linhas) > 1 else linhas[0]


def _semelhanca(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _diff(a: str, b: str, contexto: int = 0) -> str:
    linhas = list(difflib.unified_diff(
        a.strip().split("\n"), b.strip().split("\n"),
        fromfile="anterior", tofile="nova", lineterm="", n=contexto))
    return "\n".join(linhas[2:])  # sem cabeçalhos ---/+++


def comparar_versoes(doc_antigo: dict, texto_antigo: str,
                     doc_novo: dict, texto_novo: str) -> dict:
    def clausulas(doc):
        todas = [n for n in doc["nos"]
                 if n["tipo"] in ("clausula", "artigo") and n.get("folha")]
        # nas publicações com texto consolidado, cada cláusula aparece duas
        # vezes (alterações, muitas vezes só com "…", e republicação);
        # a comparação usa apenas a republicação — o texto integral final
        cons = [n for n in todas if n.get("origem") == "consolidado"]
        return cons if len(cons) >= len(todas) * 0.5 else todas

    antigas = clausulas(doc_antigo)
    novas = clausulas(doc_novo)
    antigas_por_chave: dict[str, list[dict]] = {}
    for n in antigas:
        ch = _chave_numero(n)
        if ch:
            antigas_por_chave.setdefault(ch, []).append(n)

    usadas_antigas: set[str] = set()
    resultados = []

    def classificar(no_novo, no_antigo, renumerada=False):
        corpo_n = _corpo(no_novo, texto_novo)
        corpo_a = _corpo(no_antigo, texto_antigo)
        sem = _semelhanca(corpo_a, corpo_n)
        classificacao = "=" if sem >= LIMIAR_IGUAL else "alteracao"
        resultados.append({
            "rotulo_novo": no_novo["rotulo"],
            "rotulo_antigo": no_antigo["rotulo"],
            "classificacao": classificacao,
            "semelhanca": round(sem, 3),
            "renumerada": renumerada,
            "diff": "" if classificacao == "=" else _diff(corpo_a, corpo_n),
        })
        usadas_antigas.add(no_antigo["id"])

    # 1.ª passagem: pelo número, mas só se o conteúdo corroborar
    pendentes_novas = []
    for no in novas:
        ch = _chave_numero(no)
        candidatos = [a for a in antigas_por_chave.get(ch, [])
                      if a["id"] not in usadas_antigas] if ch else []
        if candidatos:
            cand = candidatos[0]
            sem = _semelhanca(_corpo(cand, texto_antigo), _corpo(no, texto_novo))
            # mesmo número corrobora-se pelo conteúdo OU pelo título
            # (cláusulas muito reescritas mantêm número e título — ex.
            # "Direito a férias" 2009→2025 com semelhança 0.45)
            titulos_iguais = (_titulo(no) and
                              _semelhanca(_titulo(no), _titulo(cand)) >= 0.8)
            if sem >= LIMIAR_MESMO_NUMERO or titulos_iguais:
                classificar(no, cand)
                continue
        pendentes_novas.append(no)

    # 2.ª passagem: renumerações, por semelhança de conteúdo
    restantes_antigas = [a for a in antigas if a["id"] not in usadas_antigas]
    for no in pendentes_novas:
        corpo_n = _corpo(no, texto_novo)
        melhor, melhor_sem = None, 0.0
        for a in restantes_antigas:
            if a["id"] in usadas_antigas:
                continue
            sem = _semelhanca(_corpo(a, texto_antigo), corpo_n)
            if sem > melhor_sem:
                melhor, melhor_sem = a, sem
        if melhor is not None and melhor_sem >= LIMIAR_RENUMERACAO:
            classificar(no, melhor, renumerada=True)
        else:
            resultados.append({
                "rotulo_novo": no["rotulo"], "rotulo_antigo": None,
                "classificacao": "nova", "semelhanca": 0.0,
                "renumerada": False,
                "diff": _corpo(no, texto_novo).strip()[:600],
            })

    for a in antigas:
        if a["id"] not in usadas_antigas:
            resultados.append({
                "rotulo_novo": None, "rotulo_antigo": a["rotulo"],
                "classificacao": "removida", "semelhanca": 0.0,
                "renumerada": False,
                "diff": _corpo(a, texto_antigo).strip()[:600],
            })

    resumo: dict[str, int] = {}
    for r in resultados:
        resumo[r["classificacao"]] = resumo.get(r["classificacao"], 0) + 1
    return {"clausulas": resultados, "resumo": resumo,
            "doc_antigo": doc_antigo["doc_id"], "doc_novo": doc_novo["doc_id"]}


def novidades_do_consolidado(resultado: dict, doc_novo: dict) -> set[str]:
    """Ids dos nós do texto consolidado com novidade face à versão anterior.

    Regra do CRL (memo 6): as cláusulas do consolidado só entram na análise
    quando a comparação diacrónica mostra alteração ou novidade; as "="
    ficam na faixa CONSOLIDADO.
    """
    rotulos_novidade = {r["rotulo_novo"] for r in resultado["clausulas"]
                        if r["classificacao"] in ("alteracao", "nova")
                        and r["rotulo_novo"]}
    return {n["id"] for n in doc_novo["nos"]
            if n["tipo"] in ("clausula", "artigo")
            and n.get("folha")
            and n.get("origem") == "consolidado"
            and n["rotulo"] in rotulos_novidade}


def exportar_comparacao_xlsx(resultado: dict, destino) -> None:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Comparação"
    ws.append(["Classificação", "Cláusula (nova)", "Cláusula (anterior)",
               "Semelhança", "Renumerada", "Diferenças"])
    ordem = {"nova": 0, "alteracao": 1, "removida": 2, "=": 3}
    for r in sorted(resultado["clausulas"],
                    key=lambda x: (ordem[x["classificacao"]], x["rotulo_novo"] or "")):
        ws.append([r["classificacao"], r["rotulo_novo"] or "",
                   r["rotulo_antigo"] or "", r["semelhanca"],
                   "sim" if r["renumerada"] else "",
                   r["diff"][:8000]])
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    res = wb.create_sheet("Resumo")
    res.append(["Documento novo", resultado["doc_novo"]])
    res.append(["Documento anterior", resultado["doc_antigo"]])
    for k, v in sorted(resultado["resumo"].items()):
        res.append([k, v])
    wb.save(destino)
