"""CLI da comparação diacrónica: duas versões de uma convenção → XLSX.

Uso:
  python -m cct.comparar --antigo ACIP_FESAHT_2009.pdf \
      --novo 3_BTE_2_ACIP_FESAHT.pdf --out comparacao_ACIP.xlsx

  # ou escolha automática do par dentro de uma pasta de versões:
  python -m cct.comparar --pasta data/raw/textos_consolidados/NORQUIFAR_FIEQUIMETAL \
      --out results/benchmarks/tema-4.08/comparacoes/NORQUIFAR.xlsx
"""
import argparse
import re
from pathlib import Path

from .extractor import extrair_pdf
from .diacronia import comparar_versoes, exportar_comparacao_xlsx


def _ano(nome: str) -> int | None:
    if re.match(r"^\d{1,2}_BTE_", nome):
        return 2025  # numeração PR de 2025 ("3_BTE_2_…")
    m = re.match(r"^(\d{2})_[A-Z]{2}_\d+_BTE_\d+_", nome)
    if m:
        return 2000 + int(m.group(1))  # esquema da aquisição automática (cct.nomeacao):
                                       # "26_PR_003_BTE_31_…", "26_PE_001_BTE_31_…"
    m = re.match(r"^(\d{2})\d{3}_", nome)
    if m:
        return 2000 + int(m.group(1))  # "25146_", "24122_", "19000_"
    m = re.match(r"^(20\d{2})", nome)
    if m:
        return int(m.group(1))
    return None


def escolher_par(candidatos: list[tuple[str, int]]) -> tuple[str, str, list[str]]:
    """Escolhe (novo, antigo, avisos) numa pasta de versões.

    novo = versão de 2025 com mais texto; antigo = o texto COMPLETO
    anterior mais recente (as revisões parciais não servem de base de
    comparação — foi o principal ponto de dor do lote de 07/07).
    """
    avisos: list[str] = []
    max_len = max(n for _, n in candidatos)
    completo = lambda n: n >= max_len * 0.5

    de_2025 = [(nome, n) for nome, n in candidatos if _ano(nome) == 2025]
    if not de_2025:
        raise ValueError("nenhum candidato de 2025 identificável na pasta")
    novo, n_novo = max(de_2025, key=lambda x: x[1])
    if not completo(n_novo):
        avisos.append(f"a versão nova ({novo}) parece parcial "
                      f"({n_novo} caracteres) — confirmar o par")

    anteriores = [(nome, n) for nome, n in candidatos if nome != novo]
    completos = [(nome, n) for nome, n in anteriores if completo(n)]
    if not completos:
        completos = anteriores
        avisos.append("nenhum texto completo anterior — a usar o maior disponível")
    antigo, _ = max(completos, key=lambda x: (_ano(x[0]) or -1, x[1]))
    return novo, antigo, avisos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--antigo")
    p.add_argument("--novo")
    p.add_argument("--pasta", help="pasta com as versões — escolhe o par automaticamente")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    # subtipo consolidado por omissão: ativa a deteção da republicação
    # (na comparação interessa sempre o texto integral final de cada versão)
    st = "revisao_parcial_com_consolidado"

    if args.pasta:
        pdfs = [f for f in sorted(Path(args.pasta).glob("*.pdf"))
                if not re.match(r"(?i)^(comparei|diferencas)", f.name)]
        extraidos = {}
        for f in pdfs:
            extraidos[f.name] = extrair_pdf(f, doc_id=f.stem, subtipo=st)
        nome_novo, nome_antigo, avisos = escolher_par(
            [(nome, len(t)) for nome, (_, t) in extraidos.items()])
        for a in avisos:
            print(f"⚠ {a}")
        print(f"par escolhido: {nome_antigo} → {nome_novo}")
        doc_a, txt_a = extraidos[nome_antigo]
        doc_n, txt_n = extraidos[nome_novo]
    elif args.antigo and args.novo:
        doc_a, txt_a = extrair_pdf(Path(args.antigo), doc_id=Path(args.antigo).stem, subtipo=st)
        doc_n, txt_n = extrair_pdf(Path(args.novo), doc_id=Path(args.novo).stem, subtipo=st)
    else:
        p.error("usa --pasta OU (--antigo e --novo)")
    if len(txt_a) < len(txt_n) * 0.25:
        print(f"⚠ A versão antiga tem só {len(txt_a)} caracteres — parece uma "
              "revisão parcial, não um texto integral. Para a comparação "
              "diacrónica usa o último texto completo (consolidado ou revisão "
              "global) como versão anterior.")
    r = comparar_versoes(doc_a, txt_a, doc_n, txt_n)
    exportar_comparacao_xlsx(r, Path(args.out))
    print(f"{r['doc_antigo']} → {r['doc_novo']}")
    for k in ("=", "alteracao", "nova", "removida"):
        print(f"  {k:<10} {r['resumo'].get(k, 0)}")
    renum = sum(1 for c in r["clausulas"] if c["renumerada"])
    if renum:
        print(f"  (renumeradas emparelhadas por conteúdo: {renum})")
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
