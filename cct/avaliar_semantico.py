"""Fase 4: mede o ganho da camada semântica local sobre a baseline lexical.

Corre lexical + semântica num LLM local OpenAI-compatível (por exemplo, LM
Studio) nas convenções da amostra de referência e compara as métricas com e sem a camada
semântica. As chamadas são cacheadas em data/interim/cache_llm_<modelo>.
Custo controlado por --max-lotes por documento.

Uso:
  .venv/bin/python -m cct.avaliar_semantico \
      --xlsx data/raw/maxqda/4_08_ParaClaudeAppCCT.xlsx --pdfs data/raw/bte/bte_2025 \
      --codebook codebooks/4_08_protecao_dados.yaml \
      --out results/metricas/semantico_4_08 [--apenas-fn] [--max-lotes 4]
"""
import argparse
import json
from pathlib import Path

import yaml

from .extractor import extrair_pdf
from .lexical import codificar
from .semantico import codificar_semantico, backend_lmstudio
from .referencia import carregar_referencia
from .harness import avaliar, relatorio


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", required=True)
    p.add_argument("--pdfs", required=True)
    p.add_argument("--codebook", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-lotes", type=int, default=4,
                   help="máx. de chamadas ao modelo local por documento")
    p.add_argument("--apenas-fn", action="store_true",
                   help="só documentos onde a baseline lexical falhou algum código")
    p.add_argument("--modelo", default="google/gemma-4-e2b")
    p.add_argument("--base-url", default="http://127.0.0.1:1234",
                   help="URL do servidor local (só localhost/loopback)")
    args = p.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    codebook = yaml.safe_load(Path(args.codebook).read_text(encoding="utf-8"))
    referencia = carregar_referencia(Path(args.xlsx))
    docs = sorted({r["doc_id"] for r in referencia})

    previstos_lex, previstos_tot = [], []
    for i, doc_id in enumerate(docs, 1):
        nome = doc_id.removesuffix("_TXT")
        pdf = Path(args.pdfs) / f"{nome}.pdf"
        if not pdf.exists():
            continue
        doc, texto = extrair_pdf(pdf, doc_id=doc_id)
        lex = codificar(doc, texto, codebook)
        nos = {n["id"]: n for n in doc["nos"]}

        def registar(dest, anot):
            for a in anot["anotacoes"]:
                if a["codigo"].startswith("Estrutura/"):
                    continue
                n = nos[a["no_id"]]
                dest.append({"doc_id": doc_id, "codigo": a["codigo"],
                             "texto": texto[n["char_start"]:n["char_end"]],
                             "metodo": a["metodo"]})

        registar(previstos_lex, lex)
        registar(previstos_tot, lex)

        pares_lex = {(doc_id, a["codigo"]) for a in lex["anotacoes"]}
        pares_ref = {(g["doc_id"], g["codigo"]) for g in referencia if g["doc_id"] == doc_id}
        if args.apenas_fn and pares_ref <= pares_lex:
            print(f"[{i}/{len(docs)}] {nome}: lexical completo, sem LLM")
            continue

        anotados = {a["no_id"] for a in lex["anotacoes"]}
        backend = lambda pr: backend_lmstudio(pr, modelo=args.modelo,
                                               base_url=args.base_url)
        sem = codificar_semantico(
            doc, texto, codebook,
            backend=backend,
            nos_ja_anotados=anotados,
            cache_dir=Path("data/interim") / f"cache_llm_{args.modelo}".replace("/", "_"),
            max_lotes=args.max_lotes,
            max_chars=6000)
        registar(previstos_tot, sem)
        aviso = f" ({len(sem['falhas'])} lotes falhados)" if sem.get("falhas") else ""
        print(f"[{i}/{len(docs)}] {nome}: +{len(sem['anotacoes'])} anotações LLM{aviso}")
        for f in sem.get("falhas", []):
            print(f"    ⚠ {f}")

    m_lex = avaliar(previstos_lex, referencia)
    m_tot = avaliar(previstos_tot, referencia)
    (out / "metricas_lexical.json").write_text(json.dumps(m_lex, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "metricas_com_llm.json").write_text(json.dumps(m_tot, ensure_ascii=False, indent=1), encoding="utf-8")
    rel = ("== BASELINE LEXICAL ==\n" + relatorio(m_lex)
           + "\n\n== LEXICAL + SEMÂNTICA (LLM) ==\n" + relatorio(m_tot))
    (out / "relatorio.txt").write_text(rel, encoding="utf-8")
    print("\n" + rel)


if __name__ == "__main__":
    main()
