"""Desempenho dos extratores: medida reproduzível, referência e orçamento (#26).

Mede, sobre os PDF do corpus de regressão, o que custa extrair: o arranque
(importar o extrator), a extração a frio (a primeira, com as caches vazias) e
a quente (a mesma, logo a seguir), os segundos por página e a memória máxima
(RSS). Cada PDF corre num subprocesso próprio, para que a memória e o arranque
de um não contem no seguinte.

    python -m cct.desempenho medir [--pdfs data/corpus] [--extrator pdfplumber]
    python -m cct.desempenho medir --atualizar      # grava a referência deste ambiente
    python -m cct.desempenho medir --comparar       # falha acima da tolerância

O tempo depende da máquina: a referência guarda-se por ambiente (sistema,
arquitetura, Python), com o hardware e as versões identificados. `--comparar`
falha (código 1) quando os segundos por página ou a memória passam a
referência deste ambiente mais a tolerância (15%), ou o orçamento absoluto do
extrator. Sem referência para o ambiente, diz como a criar e não falha.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REFERENCIA = RAIZ / "tests" / "desempenho" / "referencia.json"
PASTA_CORPUS = RAIZ / "data" / "corpus"
RESULTADOS = RAIZ / "results" / "desempenho"
TOLERANCIA = 0.15
# o que se compara, e em que sentido: menos é melhor em todas
METRICAS = ("s_por_pagina", "rss_max_mb")


def _rss_max_mb() -> float:
    """A memória máxima deste processo, em MB (o Linux dá KB, o macOS bytes)."""
    import resource
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return pico / (1024 * 1024) if sys.platform == "darwin" else pico / 1024


def _medir_um(pdf: Path, extrator: str) -> dict:
    """Corre dentro do subprocesso: arranque, extração a frio e a quente."""
    t0 = time.perf_counter()
    if extrator == "docling":
        from .extractor_docling import extrair_pdf_docling as extrair
    else:
        from .extractor import extrair_pdf as extrair
    import pdfplumber
    arranque = time.perf_counter() - t0
    with pdfplumber.open(pdf) as documento:
        paginas = len(documento.pages)
    t1 = time.perf_counter()
    doc, _texto = extrair(pdf, doc_id=pdf.stem)
    frio = time.perf_counter() - t1
    t2 = time.perf_counter()
    extrair(pdf, doc_id=pdf.stem)
    quente = time.perf_counter() - t2
    return {"documento": pdf.stem, "paginas": paginas, "arranque_s": round(arranque, 3),
            "frio_s": round(frio, 3), "quente_s": round(quente, 3),
            "rss_max_mb": round(_rss_max_mb(), 1), "nos": len(doc["nos"])}


def medir_documento(pdf: Path, extrator: str) -> dict:
    """Um PDF num subprocesso novo: nada do anterior conta."""
    r = subprocess.run(
        [sys.executable, "-m", "cct.desempenho", "_um", str(pdf), extrator],
        capture_output=True, text=True, encoding="utf-8", cwd=RAIZ,
        env={**os.environ, "PYTHONUTF8": "1"})
    if r.returncode != 0:
        raise RuntimeError(f"{pdf.name}: {r.stderr.strip().splitlines()[-1:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def ambiente() -> dict:
    """O hardware e o software em que se mediu."""
    from importlib.metadata import PackageNotFoundError, version
    versoes = {}
    for pacote in ("pdfplumber", "pdfminer.six", "pypdfium2", "docling"):
        try:
            versoes[pacote] = version(pacote)
        except PackageNotFoundError:
            pass
    commit = ""
    try:
        from .proveniencia import estado_git
        commit = (estado_git(RAIZ) or {}).get("commit", "")
    except Exception:
        pass
    return {"chave": chave_ambiente(), "sistema": platform.platform(),
            "maquina": platform.machine(), "processador": platform.processor(),
            "cpus": os.cpu_count(), "python": platform.python_version(),
            "versoes": versoes, "commit": commit}


def chave_ambiente() -> str:
    """Sistema, arquitetura e Python: as medidas só se comparam dentro de uma."""
    return f"{sys.platform}-{platform.machine()}-py{sys.version_info[0]}.{sys.version_info[1]}"


def agregar(documentos: list[dict]) -> dict:
    """Os números da corrida: tempo por página a quente e a frio, memória máxima."""
    paginas = sum(d["paginas"] for d in documentos)
    return {
        "documentos": len(documentos), "paginas": paginas,
        "s_por_pagina": round(sum(d["quente_s"] for d in documentos) / paginas, 4),
        "s_por_pagina_frio": round(sum(d["frio_s"] for d in documentos) / paginas, 4),
        "arranque_s": round(statistics.median(d["arranque_s"] for d in documentos), 3),
        "total_s": round(sum(d["arranque_s"] + d["frio_s"] for d in documentos), 1),
        "rss_max_mb": max(d["rss_max_mb"] for d in documentos),
    }


def comparar(atual: dict, referencia: dict | None, orcamento: dict | None,
             tolerancia: float = TOLERANCIA) -> list[str]:
    """Regressões: acima da referência mais a tolerância, ou do orçamento absoluto."""
    problemas = []
    for chave in METRICAS:
        agora = atual[chave]
        if referencia and chave in referencia and agora > referencia[chave] * (1 + tolerancia):
            problemas.append(f"{chave} subiu de {referencia[chave]} para {agora} "
                             f"(mais de {tolerancia:.0%} acima da referência)")
        if orcamento and chave in orcamento and agora > orcamento[chave]:
            problemas.append(f"{chave} = {agora} passa o orçamento de {orcamento[chave]}")
    return problemas


def _carregar(caminho: Path) -> dict:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {"tolerancia": TOLERANCIA, "orcamento": {}, "ambientes": {}}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["_um"]:
        print(json.dumps(_medir_um(Path(argv[1]), argv[2]), ensure_ascii=False))
        return 0
    p = argparse.ArgumentParser(prog="python -m cct.desempenho")
    sub = p.add_subparsers(dest="comando", required=True)
    m = sub.add_parser("medir", help="mede os PDF e escreve results/desempenho/")
    m.add_argument("--pdfs", type=Path, default=PASTA_CORPUS)
    m.add_argument("--extrator", choices=("pdfplumber", "docling"), default="pdfplumber")
    m.add_argument("--referencia", type=Path, default=REFERENCIA)
    m.add_argument("--atualizar", action="store_true",
                   help="grava estas medidas como referência deste ambiente")
    m.add_argument("--comparar", action="store_true",
                   help="sai com 1 se passar a referência + tolerância ou o orçamento")
    args = p.parse_args(argv)

    pdfs = sorted(args.pdfs.glob("*.pdf"))
    if not pdfs:
        print(f"Sem PDF em {args.pdfs}. Obter o corpus: python -m cct.corpus obter --rede")
        return 1
    documentos = []
    for pdf in pdfs:
        d = medir_documento(pdf, args.extrator)
        documentos.append(d)
        print(f"  {d['documento'][:55]:55} {d['paginas']:3} p  frio {d['frio_s']:6.2f} s  "
              f"quente {d['quente_s']:6.2f} s  {d['rss_max_mb']:7.1f} MB")
    atual = agregar(documentos)
    amb = ambiente()
    resultado = {"ambiente": amb, "extrator": args.extrator, "agregado": atual,
                 "documentos": documentos}
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    saida = RESULTADOS / f"{amb['chave']}-{args.extrator}.json"
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{amb['chave']} ({args.extrator}): {atual['s_por_pagina']} s/página a quente, "
          f"{atual['s_por_pagina_frio']} a frio, arranque {atual['arranque_s']} s, "
          f"{atual['rss_max_mb']} MB no máximo → {saida}")

    ref = _carregar(args.referencia)
    if args.atualizar:
        ref.setdefault("ambientes", {}).setdefault(amb["chave"], {})[args.extrator] = {
            "agregado": atual, "ambiente": amb}
        args.referencia.parent.mkdir(parents=True, exist_ok=True)
        args.referencia.write_text(json.dumps(ref, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
        print(f"Referência atualizada: {args.referencia} (fazer commit)")
        return 0
    if args.comparar:
        do_ambiente = ref.get("ambientes", {}).get(amb["chave"], {}).get(args.extrator)
        orcamento = ref.get("orcamento", {}).get(args.extrator)
        problemas = comparar(atual, (do_ambiente or {}).get("agregado"), orcamento,
                             ref.get("tolerancia", TOLERANCIA))
        if do_ambiente is None:
            print(f"Sem referência para {amb['chave']} ({args.extrator}): só se verifica o "
                  "orçamento. Para a criar: python -m cct.desempenho medir --atualizar")
        for problema in problemas:
            print(f"REGRESSÃO: {problema}")
        return 1 if problemas else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
