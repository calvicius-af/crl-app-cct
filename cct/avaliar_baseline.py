"""Baseline lexical do tema 4.08 medida contra a amostra de referência manual (Fase 2).

Para cada convenção da amostra de referência: extrai o PDF individual (data/raw/bte/bte_2025/),
codifica com o codebook YAML e compara com a codificação manual.

Uso:
  python -m cct.avaliar_baseline --xlsx data/raw/maxqda/4_08_ParaClaudeAppCCT.xlsx \
      --pdfs data/raw/bte/bte_2025 --codebook codebooks/4_08_protecao_dados.yaml \
      --out results/metricas/baseline_4_08
"""
import argparse
import json
from pathlib import Path

import yaml

from .extractor import extrair_pdf
from .lexical import codificar
from .referencia import carregar_referencia
from .harness import avaliar, relatorio


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", required=True)
    p.add_argument("--pdfs", required=True)
    p.add_argument("--codebook", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    codebook = yaml.safe_load(Path(args.codebook).read_text(encoding="utf-8"))
    referencia = carregar_referencia(Path(args.xlsx))
    docs = sorted({r["doc_id"] for r in referencia})

    previstos = []
    falhas = []
    for i, doc_id in enumerate(docs, 1):
        nome = doc_id.removesuffix("_TXT")
        pdf = Path(args.pdfs) / f"{nome}.pdf"
        if not pdf.exists():
            falhas.append((doc_id, "PDF não encontrado"))
            continue
        try:
            doc, texto = extrair_pdf(pdf, doc_id=doc_id)
            anot = codificar(doc, texto, codebook)
            nos = {n["id"]: n for n in doc["nos"]}
            for a in anot["anotacoes"]:
                if a["codigo"].startswith("Estrutura/"):
                    continue  # códigos estruturais não são temáticos
                n = nos[a["no_id"]]
                previstos.append({
                    "doc_id": doc_id,
                    "codigo": a["codigo"],
                    "texto": texto[n["char_start"]:n["char_end"]],
                    "confianca": a["confianca"],
                })
            print(f"[{i}/{len(docs)}] {nome}: {len(anot['anotacoes'])} anotações")
        except Exception as e:
            falhas.append((doc_id, str(e)))
            print(f"[{i}/{len(docs)}] {nome}: ERRO {e}")

    m = avaliar(previstos, referencia)
    (out / "previstos.json").write_text(
        json.dumps(previstos, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "metricas.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    rel = relatorio(m)
    if falhas:
        rel += "\n\nFALHAS:\n" + "\n".join(f"  {d}: {e}" for d, e in falhas)
    (out / "relatorio.txt").write_text(rel, encoding="utf-8")
    print("\n" + rel)


if __name__ == "__main__":
    main()
