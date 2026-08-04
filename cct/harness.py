"""Harness de avaliação: anotações do pipeline vs gabarito manual.

Dois níveis (plano, Fase 2):
- documento: o par (doc_id, código) previsto existe no gabarito?
- segmento: além do par certo, o texto do nó anotado sobrepõe-se ao
  segmento do gabarito? (comparação por contenção de texto normalizado,
  porque os offsets do MaxQDA e do pipeline não são diretamente comparáveis)

`previstos`: [{doc_id, codigo, texto}] — texto = conteúdo do nó anotado.
`gabarito`:  [{doc_id, codigo, segmento}].
"""
import re
from collections import defaultdict


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower()).strip()


def _sobrepoe(texto_no: str, segmento: str) -> bool:
    a, b = _norm(texto_no), _norm(segmento)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    # sobreposição parcial: um trecho inicial/central do mais curto no mais longo
    curto, longo = (a, b) if len(a) <= len(b) else (b, a)
    janela = curto[: max(40, len(curto) // 3)]
    return janela in longo


def avaliar(previstos: list[dict], gabarito: list[dict]) -> dict:
    pares_gab = defaultdict(list)   # (doc, codigo) -> [segmentos]
    for g in gabarito:
        pares_gab[(g["doc_id"], g["codigo"])].append(g["segmento"])

    pares_prev = defaultdict(list)  # (doc, codigo) -> [textos]
    for p in previstos:
        pares_prev[(p["doc_id"], p["codigo"])].append(p.get("texto", ""))

    codigos = {c for _, c in pares_gab} | {c for _, c in pares_prev}
    por_codigo = {}
    tot = {"vp": 0, "fp": 0, "fn": 0, "vp_segmento": 0}

    for cod in sorted(codigos):
        gab_docs = {d for (d, c) in pares_gab if c == cod}
        prev_docs = {d for (d, c) in pares_prev if c == cod}
        vp = len(gab_docs & prev_docs)
        fp = len(prev_docs - gab_docs)
        fn = len(gab_docs - prev_docs)

        vp_seg = 0
        for doc in gab_docs & prev_docs:
            segmentos = pares_gab[(doc, cod)]
            textos = pares_prev[(doc, cod)]
            if any(_sobrepoe(t, s) for t in textos for s in segmentos):
                vp_seg += 1

        precisao = vp / (vp + fp) if (vp + fp) else None
        cobertura = vp / (vp + fn) if (vp + fn) else None
        f1 = (2 * precisao * cobertura / (precisao + cobertura)
              if precisao and cobertura else 0.0)
        por_codigo[cod] = {
            "vp": vp, "fp": fp, "fn": fn, "vp_segmento": vp_seg,
            "precisao": precisao, "cobertura": cobertura, "f1": f1,
            "n_gabarito": len(gab_docs),
        }
        tot["vp"] += vp
        tot["fp"] += fp
        tot["fn"] += fn
        tot["vp_segmento"] += vp_seg

    tot["precisao"] = tot["vp"] / (tot["vp"] + tot["fp"]) if (tot["vp"] + tot["fp"]) else None
    tot["cobertura"] = tot["vp"] / (tot["vp"] + tot["fn"]) if (tot["vp"] + tot["fn"]) else None
    return {"por_codigo": por_codigo, "global": tot}


def relatorio(m: dict) -> str:
    linhas = [f"{'código':<12} {'n_gab':>5} {'VP':>4} {'FP':>4} {'FN':>4} "
              f"{'VPseg':>5} {'prec':>6} {'cob':>6} {'F1':>6}"]
    for cod, r in m["por_codigo"].items():
        fmt = lambda v: f"{v:.2f}" if isinstance(v, float) else ("--" if v is None else str(v))
        linhas.append(f"{cod:<12} {r['n_gabarito']:>5} {r['vp']:>4} {r['fp']:>4} "
                      f"{r['fn']:>4} {r['vp_segmento']:>5} {fmt(r['precisao']):>6} "
                      f"{fmt(r['cobertura']):>6} {fmt(r['f1']):>6}")
    g = m["global"]
    fmtg = lambda v: f"{v:.2f}" if v is not None else "--"
    linhas.append(f"{'GLOBAL':<12} {'':>5} {g['vp']:>4} {g['fp']:>4} {g['fn']:>4} "
                  f"{g['vp_segmento']:>5} {fmtg(g['precisao']):>6} {fmtg(g['cobertura']):>6}")
    return "\n".join(linhas)
