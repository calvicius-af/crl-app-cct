"""Codificação lexical com granularidade cláusula/parágrafo (Fase 3).

Convenção do CRL (dados 2025):
- nivel="clausula": marca a cláusula inteira (código _identif) — permite
  quantificar cláusulas por tema;
- nivel="paragrafo": marca o número/alínea onde o termo ocorre.

Condições opcionais por código (aplicadas ao texto da cláusula inteira):
- condicoes.requer_algum: pelo menos um destes termos tem de estar presente;
- condicoes.excluir: se algum destes termos ocorre (e nenhum requer_algum
  compensa), o código não é atribuído — trava falsos positivos de termos
  genéricos (ex.: "quota sindical" em cláusulas de pagamento, não de dados).
"""


def _contem(trecho_lower: str, termos: list[str]) -> list[str]:
    return [t for t in termos if t.lower() in trecho_lower]


def _passa_condicoes(codigo: dict, trecho_lower: str) -> bool:
    cond = codigo.get("condicoes") or {}
    requer = cond.get("requer_algum")
    if requer and not _contem(trecho_lower, requer):
        return False
    excluir = cond.get("excluir")
    if excluir and _contem(trecho_lower, excluir):
        return False
    return True


def codificar(doc: dict, texto: str, codebook: dict) -> dict:
    anotacoes = []
    texto_lower = texto.lower()
    paragrafos_por_pai: dict[str, list[dict]] = {}
    for n in doc["nos"]:
        if n["tipo"] == "paragrafo":
            paragrafos_por_pai.setdefault(n["pai"], []).append(n)

    eixos = codebook.get("eixos", [])
    eixos_emitidos: set[tuple[str, str]] = set()

    def emitir_eixo(no: dict, codigo_id: str, confianca: float, evidencia: str):
        """Eixo-pai cobre a cláusula inteira (memo 1 de 06/07)."""
        for eixo in eixos:
            if codigo_id.startswith(eixo + ".") and (no["id"], eixo) not in eixos_emitidos:
                eixos_emitidos.add((no["id"], eixo))
                anotacoes.append({
                    "no_id": no["id"],
                    "char_start": no["char_start"],
                    "char_end": no["char_end"],
                    "codigo": eixo,
                    "confianca": confianca,
                    "metodo": "lexical",
                    "nivel": "clausula",
                    "evidencia": evidencia,
                })

    for no in doc["nos"]:
        if no["tipo"] == "paragrafo":
            continue
        # estrutura: preâmbulo e assinaturas ficam fora da codificação temática
        # (memos 2/5 de 06/07), mas recebem código estrutural próprio
        if no["tipo"] == "preambulo" or no["rotulo"] == "ASSINATURAS":
            nome = "Preâmbulo" if no["tipo"] == "preambulo" else "Assinaturas"
            anotacoes.append({
                "no_id": no["id"],
                "char_start": no["char_start"],
                "char_end": no["char_end"],
                "codigo": f"Estrutura/{nome}",
                "confianca": 1.0,
                "metodo": "contexto",
                "nivel": "clausula",
                "evidencia": "",
            })
            continue
        trecho = texto_lower[no["char_start"]:no["char_end"]]
        for codigo in codebook.get("codigos", []):
            encontrados = _contem(trecho, codigo.get("termos", []))
            if not encontrados or not _passa_condicoes(codigo, trecho):
                continue
            confianca = min(0.9, 0.6 + 0.1 * (len(encontrados) - 1))
            emitir_eixo(no, codigo["id"], confianca, encontrados[0])
            # subcódigo ao nível do número/alínea onde o termo ocorre;
            # só cai para a cláusula inteira quando não há parágrafos com match
            matches_par = []
            for par in paragrafos_por_pai.get(no["id"], []):
                trecho_par = texto_lower[par["char_start"]:par["char_end"]]
                enc_par = _contem(trecho_par, codigo.get("termos", []))
                if enc_par:
                    matches_par.append((par, enc_par[0]))
            if matches_par:
                for par, evid in matches_par:
                    anotacoes.append({
                        "no_id": par["id"],
                        "char_start": par["char_start"],
                        "char_end": par["char_end"],
                        "codigo": codigo["id"],
                        "confianca": confianca,
                        "metodo": "lexical",
                        "nivel": "paragrafo",
                        "evidencia": evid,
                    })
            else:
                anotacoes.append({
                    "no_id": no["id"],
                    "char_start": no["char_start"],
                    "char_end": no["char_end"],
                    "codigo": codigo["id"],
                    "confianca": confianca,
                    "metodo": "lexical",
                    "nivel": "clausula",
                    "evidencia": encontrados[0],
                })
    # zona consolidada: um único segmento estrutural a cobrir a região
    # (prática CRL 2025 — sinalizar o texto republicado enquanto tal)
    consolidados = [n for n in doc["nos"]
                    if n.get("folha") and n.get("origem") == "consolidado"]
    if consolidados:
        anotacoes.append({
            "no_id": consolidados[0]["id"],
            "char_start": min(n["char_start"] for n in consolidados),
            "char_end": max(n["char_end"] for n in consolidados),
            "codigo": "Estrutura/Texto Consolidado",
            "confianca": 1.0,
            "metodo": "contexto",
            "nivel": "clausula",
            "evidencia": "",
        })
    return {
        "versao_schema": "0.1",
        "doc_id": doc["doc_id"],
        "anotacoes": anotacoes,
    }
