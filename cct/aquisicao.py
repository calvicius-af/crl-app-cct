"""Aquisição do corpus: recolha do BTE + nomeação, numa só corrida.

As duas fases continuam a ser autónomas (ADR-0004) — este módulo é só o
encadeamento normal, e o que a app gráfica lança. Escreve um relatório único.

Uso:
  python -m cct.aquisicao --indices data/raw/indices                       # simulação
  python -m cct.aquisicao --indices data/raw/indices --confirmar-rede --aplicar
"""
import argparse
import os
import sys
import time
from pathlib import Path

from . import nomeacao, recolha
from .proveniencia import agora_utc, construir_manifesto, escrever_manifesto
from .recolha import (DESTINO_OMISSAO, FAMILIAS_POR_OMISSAO, INDICES_OMISSAO,
                      REGISTO_OMISSAO, RAIZ, Registo)


def _indices(caminho: Path) -> list[Path]:
    ficheiros = sorted(caminho.glob("*.xlsx")) if caminho.is_dir() else [caminho]
    return [f for f in ficheiros if not f.name.startswith("~$")]


def main(argv=None):
    inicio_utc = agora_utc()
    p = argparse.ArgumentParser(
        prog="cct.aquisicao",
        description="Recolhe os documentos do BTE e renomeia-os para o pipeline. "
                    "Sem --confirmar-rede e --aplicar, apenas simula.")
    p.add_argument("--indices", default=str(INDICES_OMISSAO))
    p.add_argument("--interim", default=str(DESTINO_OMISSAO),
                   help="onde ficam os PDFs com o nome de origem")
    p.add_argument("--destino", default=str(nomeacao.DESTINO_OMISSAO),
                   help="pasta data/raw/bte, onde ficam os PDFs já nomeados")
    p.add_argument("--registo", default=str(REGISTO_OMISSAO))
    p.add_argument("--siglas", help="CSV opcional 'nome;sigla'")
    p.add_argument("--familias", default=",".join(FAMILIAS_POR_OMISSAO))
    p.add_argument("--confirmar-rede", action="store_true")
    p.add_argument("--aplicar", action="store_true")
    p.add_argument("--aceitar-heuristicas", action="store_true",
                   help="escreve mesmo os documentos com sigla derivada por "
                        "heurística, sem esperar por confirmação humana")
    p.add_argument("--pausa", type=float, default=1.0)
    p.add_argument("--limite", type=int)
    p.add_argument("--relatorio", default=str(RAIZ / "results" / "aquisicao"))
    args = p.parse_args(argv)

    indices = _indices(Path(args.indices))
    if not indices:
        raise SystemExit(f"Sem ficheiros-índice em {args.indices} "
                         "(ver docs/dados/README.md §Índices do BTE)")

    familias = tuple(f.strip() for f in args.familias.split(",") if f.strip())
    rede = args.confirmar_rede or os.environ.get("CCT_RECOLHA_REDE") == "1"
    registo = Registo.carregar(Path(args.registo))

    print(f"Índices: {', '.join(i.name for i in indices)}")
    r1 = recolha.recolher(indices, Path(args.interim), registo, rede=rede,
                          familias=familias, pausa=args.pausa, limite=args.limite)
    texto1 = recolha.texto_resumo(r1, rede=rede)
    print(texto1)

    tabela = nomeacao.carregar_siglas(Path(args.siglas)) if args.siglas else None
    r2 = nomeacao.nomear(registo, Path(args.destino), aplicar=args.aplicar,
                         tabela=tabela, familias=familias,
                         aceitar_heuristicas=args.aceitar_heuristicas)
    texto2 = nomeacao.texto_resumo(r2, aplicar=args.aplicar)
    print(texto2)

    pasta = Path(args.relatorio)
    pasta.mkdir(parents=True, exist_ok=True)
    destino_rel = pasta / f"relatorio_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    destino_rel.write_text(
        "\n".join([f"Aquisição do BTE — {time.strftime('%Y-%m-%d %H:%M:%S')}",
                   f"Índices: {', '.join(i.name for i in indices)}",
                   f"Rede: {'autorizada' if rede else 'desligada'} · "
                   f"Escrita: {'sim' if args.aplicar else 'simulação'}",
                   "", texto1, "", texto2, "",
                   "Nomes atribuídos:",
                   *(f"  {c} → {n}" for c, n in r2["nomes"])]) + "\n",
        encoding="utf-8")
    print(f"\n→ {destino_rel}")

    problemas = r1["problemas"] + r2["problemas"]
    parametros = {chave: valor for chave, valor in vars(args).items()}
    comando = ["python", "-m", "cct.aquisicao", *(argv if argv is not None else sys.argv[1:])]
    manifesto = construir_manifesto(
        raiz=RAIZ, inicio_utc=inicio_utc, parametros=parametros,
        entradas=indices, saidas=[destino_rel, Path(args.registo)],
        resumo={"documentos_no_indice": r1["documentos"],
               "descarregados": r1["por_estado"].get("descarregado", 0),
               "nomeados": r2["por_estado"].get("nomeado", 0),
               "por_confirmar": r2["por_estado"].get("por_confirmar", 0)},
        problemas=problemas, comando=comando)
    caminho_manifesto = pasta / "manifest.json"
    escrever_manifesto(caminho_manifesto, manifesto)
    print(f"→ {caminho_manifesto}")

    if not rede or not args.aplicar:
        print("Corrida de simulação. Para executar: "
              "--confirmar-rede --aplicar")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
