"""Triagem AUTO/REVER (Fase 3): calibrada com a precisão medida na amostra de referência.

Uma anotação vai para a faixa AUTO quando o seu código tem precisão medida
≥ limiar (por omissão 0.85) numa amostra de referência com pelo menos `n_minimo` documentos;
todas as restantes vão para REVER. No MaxQDA os códigos aparecem prefixados
(AUTO/…, REVER/…), permitindo rever só o que precisa de olhos humanos.
"""
LIMIAR_AUTO = 0.85
N_MINIMO = 2


def codigos_auto(metricas: dict, limiar: float = LIMIAR_AUTO,
                 n_minimo: int = N_MINIMO) -> set[str]:
    aptos = set()
    for cod, r in metricas.get("por_codigo", {}).items():
        p = r.get("precisao")
        if p is not None and p >= limiar and r.get("n_referencia", 0) >= n_minimo:
            aptos.add(cod)
    return aptos


def triar(anotacoes: dict, aptos: set[str], doc: dict | None = None,
          novidades: set[str] | None = None) -> dict:
    """Devolve novas anotações com o código prefixado por faixa.

    - Estrutura/…: sem prefixo (não é codificação temática);
    - nós com origem "consolidado": faixa CONSOLIDADO — exceto quando a
      comparação diacrónica os marca como novidade (`novidades`: ids de
      cláusulas alteradas/novas), caso em que sobem para AUTO/REVER;
    - restantes: AUTO se o código tem precisão calibrada, senão REVER.
    """
    nos_por_id = {n["id"]: n for n in doc["nos"]} if doc else {}
    novidades = novidades or set()

    def clausula_de(no_id: str) -> str:
        """Resolve anotações de parágrafo para a cláusula-mãe."""
        no = nos_por_id.get(no_id)
        if no and no["tipo"] == "paragrafo" and no.get("pai"):
            return no["pai"]
        return no_id

    novas = []
    for a in anotacoes["anotacoes"]:
        if a["codigo"].startswith("Estrutura/"):
            novas.append(a)
            continue
        no = nos_por_id.get(a["no_id"])
        em_consolidado = bool(no) and no.get("origem") == "consolidado"
        if em_consolidado and clausula_de(a["no_id"]) not in novidades:
            faixa = "CONSOLIDADO"
        else:
            faixa = "AUTO" if a["codigo"] in aptos else "REVER"
        novas.append({**a, "codigo": f"{faixa}/{a['codigo']}"})
    return {**anotacoes, "anotacoes": novas}
