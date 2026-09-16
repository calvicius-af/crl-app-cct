#!/usr/bin/env python3
"""Constrói os vocabulários controlados a partir do registo da DGERT.

Entrada: o `data-export_AAAA-MM-DD-HH_MM_SS.xlsx` que a DGERT publica com o
registo de organizações sindicais e de empregadores, a negociação coletiva, os
pré-avisos de greve, os estatutos e as eleições.

Saída, em `vocabularios/`:

    siglas_organizacoes.csv   uma linha por organização, com a sigla canónica
    actos_negociacao.csv      identidade plurianual de cada convenção
    siglas_ambiguas.csv       as siglas usadas por organizações diferentes

Corre offline e é repetível: a mesma entrada dá sempre a mesma saída, o que
permite versionar os CSV e ver num `git diff` o que mudou de um export para o
seguinte.

    python scripts/construir_vocabularios.py data-export.xlsx

Ver docs/rnc/README.md §8.
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from cct.localizador import _sem_acentos          # noqa: E402
from cct.nomeacao import _camel, _limpar_sigla    # noqa: E402

FOLHAS = {
    "sindicais": "Organizações sindicais",
    "empregadores": "Organizações de empregadores",
    "negociacao": "Negociação coletiva",
}

# Siglas que o registo traz mas que não identificam ninguém: são fragmentos de
# outra sigla, ou palavras comuns. Ficam de fora da tabela canónica para não
# produzirem nomes de ficheiro errados.
SIGLAS_RECUSADAS = {"IN", "PT", "SUL", "NORTE", "CGTP", "UGT", "SA", "LDA"}


def _ler(ws) -> list[dict]:
    linhas = ws.iter_rows(values_only=True)
    cab = [str(c or "").strip() for c in next(linhas)]
    saida = []
    for linha in linhas:
        item = {cab[i]: (str(v).strip() if v is not None else "")
                for i, v in enumerate(linha) if i < len(cab)}
        if any(item.values()):
            saida.append(item)
    return saida


def sigla_canonica(denominacao: str, acronimo: str) -> tuple[str, str]:
    """Devolve `(sigla, origem)` — `registo`, `derivada` ou `recurso`."""
    limpo = _limpar_sigla(acronimo or "")
    if limpo and limpo.upper() not in SIGLAS_RECUSADAS and 2 <= len(limpo) <= 20:
        return limpo, "registo"
    # a denominação costuma trazer a sigla a seguir a um travessão ou entre parênteses
    from cct.nomeacao import sigla as derivar
    s, aviso = derivar(denominacao)
    if s and not aviso and s.upper() not in SIGLAS_RECUSADAS:
        return s, "derivada"
    return _camel(denominacao), "recurso"


def construir(xlsx: Path, saida: Path) -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    em_falta = [n for n in FOLHAS.values() if n not in wb.sheetnames]
    if em_falta:
        raise SystemExit(f"Folhas em falta em {xlsx.name}: {', '.join(em_falta)}")

    saida.mkdir(parents=True, exist_ok=True)
    resumo: dict[str, int] = {}

    # ------------------------------------------------ siglas_organizacoes.csv
    organizacoes = []
    for lado, folha in (("trabalhadores", FOLHAS["sindicais"]),
                        ("empregadores", FOLHAS["empregadores"])):
        for r in _ler(wb[folha]):
            denominacao = r.get("Denominação da Organização", "")
            if not denominacao:
                continue
            s, origem = sigla_canonica(denominacao, r.get("Acrónimo", ""))
            organizacoes.append({
                "codigo_dgert": r.get("Código Identificador da Organização", ""),
                "denominacao": denominacao,
                "sigla": s,
                "origem_sigla": origem,
                "tipo": r.get("Tipo de Organização", ""),
                "lado": lado,
                "estado_registo": r.get("Ativa ou Extinta", ""),
                "primeira_atividade": r.get("Data da Primeira Atividade Registada", ""),
                "ultima_atividade": r.get("Data da Última Atividade Registada", ""),
            })
    organizacoes.sort(key=lambda o: (o["lado"], _sem_acentos(o["denominacao"]).upper()))
    _escrever(saida / "siglas_organizacoes.csv", organizacoes)
    resumo["organizacoes"] = len(organizacoes)
    resumo["sigla_do_registo"] = sum(1 for o in organizacoes
                                     if o["origem_sigla"] == "registo")

    # ------------------------------------------------------ siglas_ambiguas.csv
    #
    # Uma sigla partilhada por organizações *diferentes* é um problema para
    # nomear ficheiros. Uma sigla partilhada por gerações sucessivas da mesma
    # organização não é: o SITESE mudou de nome seis vezes e continua a ser o
    # SITESE. Distinguem-se pela raiz do código DGERT ("1.402.1" → "1.402").
    por_sigla: dict[str, list[dict]] = defaultdict(list)
    for o in organizacoes:
        por_sigla[o["sigla"].upper()].append(o)
    ambiguas = []
    for s, grupo in sorted(por_sigla.items()):
        raizes = {".".join(o["codigo_dgert"].split(".")[:2]) for o in grupo}
        if len(raizes) > 1:
            ambiguas.append({
                "sigla": s,
                "n_organizacoes": len(grupo),
                "n_linhagens": len(raizes),
                "denominacoes": " | ".join(o["denominacao"] for o in grupo),
                "resolucao": "",          # preenchido pela equipa
            })
    _escrever(saida / "siglas_ambiguas.csv", ambiguas)
    resumo["siglas_distintas"] = len(por_sigla)
    resumo["siglas_ambiguas"] = len(ambiguas)

    # ----------------------------------------------------- actos_negociacao.csv
    #
    # É esta folha que prova que o código IRCT é estável entre revisões: o
    # «Identificador do Acto de Negociação» acompanha a mesma convenção ao longo
    # dos anos, e é ele que o BTE publica como COD: (IRCT) com um dígito de
    # família à frente. Ver docs/rnc/README.md §5.3.
    actos: dict[str, dict] = {}
    for r in _ler(wb[FOLHAS["negociacao"]]):
        acto = r.get("Identificador do Acto de Negociação", "")
        if not acto:
            continue
        ano = r.get("Ano", "")
        registo = actos.setdefault(acto, {
            "acto": acto, "nome": r.get("Nome Acto", ""),
            "tipo": r.get("Tipo Acto", ""), "ambito_geografico":
            r.get("Âmbito Geográfico", ""),
            "primeiro_ano": ano, "ultimo_ano": ano,
            "n_publicacoes": 0, "organizacoes": set(),
        })
        registo["n_publicacoes"] += 1
        if ano:
            registo["primeiro_ano"] = min(registo["primeiro_ano"] or ano, ano)
            registo["ultimo_ano"] = max(registo["ultimo_ano"] or ano, ano)
        if r.get("Código Identificador da Organização"):
            registo["organizacoes"].add(r["Código Identificador da Organização"])
    linhas_actos = []
    for a in sorted(actos.values(), key=lambda x: int(x["acto"]) if x["acto"].isdigit()
                    else 0):
        # Guardam-se os códigos da DGERT e não as denominações: os códigos
        # ligam a `siglas_organizacoes.csv`, que já tem os nomes, e poupam
        # ~1 MB de nomes repetidos milhares de vezes dentro do repositório.
        linhas_actos.append({**{k: v for k, v in a.items() if k != "organizacoes"},
                             "n_organizacoes": len(a["organizacoes"]),
                             "codigos_organizacoes": " ".join(
                                 sorted(a["organizacoes"]))})
    _escrever(saida / "actos_negociacao.csv", linhas_actos)
    resumo["actos"] = len(linhas_actos)
    resumo["actos_plurianuais"] = sum(1 for a in linhas_actos
                                      if a["primeiro_ano"] != a["ultimo_ano"])
    wb.close()
    return resumo


def _escrever(caminho: Path, linhas: list[dict]) -> None:
    if not linhas:
        caminho.write_text("", encoding="utf-8")
        return
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()), delimiter=";",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="construir_vocabularios",
        description="Constrói os vocabulários controlados do registo da DGERT.")
    p.add_argument("export", help="data-export_….xlsx da DGERT")
    p.add_argument("--saida", default=str(RAIZ / "vocabularios"))
    args = p.parse_args(argv)

    resumo = construir(Path(args.export), Path(args.saida))
    print("== Vocabulários construídos")
    for k, v in resumo.items():
        print(f"  {k.replace('_', ' ')}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
