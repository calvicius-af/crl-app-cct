"""Corrida completa de um tema sobre uma pasta de convenções.

Extração → codificação lexical (+ semântica opcional) → triagem calibrada
→ QDPX (MaxQDA) + XLSX (peritas). O comando único da operação normal.

Uso mínimo:
  python -m cct.pipeline_tema --pdfs data/raw/bte/bte_2026 \
      --codebook codebooks/4_08_protecao_dados.yaml --out results/2026_4_08
"""
import argparse
import json
from pathlib import Path

import yaml

from .extractor import extrair_pdf
from .lexical import codificar
from .qdpx import exportar_qdpx
from .export_xlsx import exportar_xlsx
from .triagem import codigos_auto, triar
from .schemas import validar_doc, validar_anotacoes


def _novidades_via_versoes(pasta_versoes: Path, pdf: Path, doc: dict,
                           texto: str, problemas: list) -> set[str] | None:
    """Encontra a subpasta de versões da convenção e devolve as novidades
    do consolidado (cláusulas alteradas/novas face à versão anterior)."""
    import re
    from .localizador import _colapsar
    from .diacronia import comparar_versoes, novidades_do_consolidado

    alvo = _colapsar(pdf.stem)
    pasta = None
    for d in sorted(pasta_versoes.iterdir()):
        if d.is_dir() and _colapsar(d.name) and _colapsar(d.name) in alvo:
            pasta = d
            break
    if pasta is None:
        problemas.append(f"{pdf.stem}: sem pasta de versões correspondente "
                         "— consolidado fica todo na faixa CONSOLIDADO")
        return None
    from .comparar import _ano
    versoes = [f for f in sorted(pasta.glob("*.pdf"))
               if not re.match(r"(?i)^(comparei|diferencas)", f.name)
               and _ano(f.name) != 2025]  # o próprio 2025 não é "anterior"
    if not versoes:
        problemas.append(f"{pdf.stem}: pasta {pasta.name} sem versões anteriores")
        return None
    extraidas = {f.name: extrair_pdf(f, doc_id=f.stem,
                                     subtipo="revisao_parcial_com_consolidado")
                 for f in versoes}
    # versão anterior = o texto COMPLETO mais recente (parciais não servem)
    completas = {n: (d, t) for n, (d, t) in extraidas.items()
                 if len(t) >= len(texto) * 0.5} or extraidas
    nome_antigo = max(completas, key=lambda n: (_ano(n) or -1, len(completas[n][1])))
    doc_a, txt_a = extraidas[nome_antigo]
    r = comparar_versoes(doc_a, txt_a, doc, texto)
    nov = novidades_do_consolidado(r, doc)
    print(f"    diacronia vs {nome_antigo}: {r['resumo']} → {len(nov)} novidades no consolidado")
    return nov


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdfs", required=True, help="pasta com PDFs individuais de convenções")
    p.add_argument("--codebook", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--variaveis", help="VariaveisDocumento*.xlsx do MaxQDA (subtipo, CAE, …)")
    p.add_argument("--master", help="codebook .qdc do MaxQDA (nomes/cores/descrições)")
    p.add_argument("--metricas", help="metricas.json de avaliar_baseline (calibra AUTO/REVER)")
    p.add_argument("--pasta-versoes",
                   help="pasta com subpastas de versões anteriores (estrutura "
                        "data/raw/textos_consolidados) — promove novidades do consolidado")
    p.add_argument("--extrator", choices=("pdfplumber", "docling"),
                   default="pdfplumber",
                   help="docling recupera tabelas de anexos e layouts difíceis "
                        "(mais lento; requer 'pip install docling')")
    p.add_argument("--semantica", action="store_true",
                   help="ativa a camada LLM (LM Studio) nas cláusulas não resolvidas")
    p.add_argument("--modelo", default="google/gemma-4-e2b")
    p.add_argument("--base-url", default="http://127.0.0.1:1234")
    p.add_argument("--max-lotes", type=int, default=4)
    p.add_argument("--nome", default="CRL CCT pré-codificado")
    args = p.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    codebook = yaml.safe_load(Path(args.codebook).read_text(encoding="utf-8"))

    variaveis = None
    if args.variaveis:
        from .variaveis import carregar_variaveis
        variaveis = carregar_variaveis(Path(args.variaveis))
    master = None
    if args.master:
        from .qdc import carregar_qdc
        master = carregar_qdc(Path(args.master))
    aptos = set()
    if args.metricas:
        aptos = codigos_auto(json.loads(Path(args.metricas).read_text(encoding="utf-8")))

    pdfs = sorted(Path(args.pdfs).glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"Sem PDFs em {args.pdfs}")

    extrair = extrair_pdf
    if args.extrator == "docling":
        from .extractor_docling import extrair_pdf_docling
        extrair = extrair_pdf_docling

    itens, problemas = [], []
    for i, pdf in enumerate(pdfs, 1):
        try:
            v = None
            if variaveis:
                from .variaveis import procurar
                v = procurar(variaveis, pdf.stem)
            doc, texto = extrair(pdf, doc_id=pdf.stem,
                                 subtipo=(v or {}).get("subtipo", "desconhecido"))
            validar_doc(doc)
            anot = codificar(doc, texto, codebook)
            if args.semantica:
                from .semantico import codificar_semantico, backend_lmstudio
                anotados = {a["no_id"] for a in anot["anotacoes"]}
                sem = codificar_semantico(
                    doc, texto, codebook,
                    backend=lambda pr: backend_lmstudio(pr, modelo=args.modelo,
                                                        base_url=args.base_url),
                    nos_ja_anotados=anotados,
                    cache_dir=out / "cache_llm",
                    max_lotes=args.max_lotes, max_chars=6000)
                anot["anotacoes"].extend(sem["anotacoes"])
                for f in sem.get("falhas", []):
                    problemas.append(f"{pdf.stem}: LLM {f}")
            validar_anotacoes({**anot, "anotacoes": [
                {k: v for k, v in a.items()} for a in anot["anotacoes"]]})
            novidades = None
            if args.pasta_versoes and any(
                    n.get("origem") == "consolidado" for n in doc["nos"]):
                novidades = _novidades_via_versoes(
                    Path(args.pasta_versoes), pdf, doc, texto, problemas)
            itens.append((doc, texto, triar(anot, aptos, doc=doc,
                                            novidades=novidades)))
            n_cl = sum(1 for n in doc["nos"] if n["tipo"] == "clausula")
            print(f"[{i}/{len(pdfs)}] {pdf.stem}: {n_cl} cláusulas, "
                  f"{len(anot['anotacoes'])} anotações")
        except Exception as e:
            problemas.append(f"{pdf.stem}: {e}")
            print(f"[{i}/{len(pdfs)}] {pdf.stem}: ERRO {e}")

    exportar_qdpx(itens, out / "projeto.qdpx", nome_projeto=args.nome, master=master)
    exportar_xlsx(itens, out / "sugestoes_peritas.xlsx", variaveis=variaveis)

    relatorio = [f"Convenções processadas: {len(itens)}/{len(pdfs)}"]
    if problemas:
        relatorio.append("\nPROBLEMAS:")
        relatorio.extend(f"  {p}" for p in problemas)
    (out / "relatorio.txt").write_text("\n".join(relatorio), encoding="utf-8")
    print(f"\n{relatorio[0]}")
    print(f"→ {out/'projeto.qdpx'}\n→ {out/'sugestoes_peritas.xlsx'}")
    if problemas:
        print(f"⚠ {len(problemas)} problemas — ver {out/'relatorio.txt'}")


if __name__ == "__main__":
    main()
