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

from cct import siglas as mod_siglas             # noqa: E402
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


def sigla_base(denominacao: str, acronimo: str) -> tuple[str, str]:
    """A sigla antes de desambiguar. Devolve `(sigla, origem)`.

    `origem` é `registo` (o acrónimo consta do registo da DGERT), `derivada`
    (extraída da denominação por um padrão fiável) ou `recurso` (inventada pelo
    script). A desambiguação de duplicados é feita depois, em `cct/siglas.py`,
    sobre o conjunto todo — não se pode decidir caso a caso.
    """
    limpo = _limpar_sigla(acronimo or "")
    if limpo and limpo.upper() not in SIGLAS_RECUSADAS and 2 <= len(limpo) <= 20:
        return limpo, "registo"
    # a denominação costuma trazer a sigla a seguir a um travessão ou entre parênteses
    from cct.nomeacao import sigla as derivar
    s, aviso = derivar(denominacao)
    if s and not aviso and s.upper() not in SIGLAS_RECUSADAS:
        return s, "derivada"
    return _camel(denominacao), "recurso"


def siglas_fixadas(caminho: Path) -> dict[str, str]:
    """As siglas já atribuídas → `{(linhagem, sigla_base): sigla}`.

    Uma sigla atribuída não se reatribui, pela mesma razão por que um nome de
    ficheiro não muda: o que já foi escrito com ela deixaria de corresponder.
    """
    if not caminho.exists():
        return {}
    fixadas: dict[tuple[str, str], str] = {}
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            lin = mod_siglas.linhagem(linha.get("codigo_dgert", ""))
            base = linha.get("sigla_base") or linha.get("sigla", "")
            if lin and base and linha.get("sigla"):
                fixadas.setdefault((lin, base), linha["sigla"])
    return fixadas


def construir(xlsx: Path, saida: Path, *, reatribuir: bool = False) -> dict:
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
            s, origem = sigla_base(denominacao, r.get("Acrónimo", ""))
            organizacoes.append({
                "codigo_dgert": r.get("Código Identificador da Organização", ""),
                "denominacao": denominacao,
                "sigla": s,
                "sigla_base": s,
                "origem_sigla": origem,
                "tipo": r.get("Tipo de Organização", ""),
                "lado": lado,
                "concelho": (r.get("Concelho da Sede", "") or "").strip(),
                "distrito": (r.get("Distrito da Sede", "") or "").strip(),
                "estado_registo": r.get("Ativa ou Extinta", ""),
                "primeira_atividade": r.get("Data da Primeira Atividade Registada", ""),
                "ultima_atividade": r.get("Data da Última Atividade Registada", ""),
            })

    # Desambiguação. Tem de ser feita sobre o conjunto todo e por regra: duas
    # pessoas a decidirem caso a caso produzem duas siglas para o mesmo
    # sindicato, e a série parte-se. Ver cct/siglas.py e ADR-0017.
    fixadas = {} if reatribuir else siglas_fixadas(saida / "siglas_organizacoes.csv")
    resolvidas = mod_siglas.atribuir(organizacoes, fixadas)
    # Conta-se por reivindicação e não por linha: uma organização que mudou de
    # nome seis vezes tem seis linhas e uma só sigla, e contá-la seis vezes
    # daria a impressão de que a regra mexeu em muito mais do que mexeu.
    desambiguadas = sum(1 for (_lin, base), final in resolvidas.items()
                        if final != base)
    for o in organizacoes:
        chave = (mod_siglas.linhagem(o["codigo_dgert"]), o["sigla_base"])
        nova = resolvidas.get(chave, o["sigla"])
        if nova != o["sigla_base"]:
            o["origem_sigla"] += "+desambiguada"
        o["sigla"] = nova

    organizacoes.sort(key=lambda o: (o["lado"], _sem_acentos(o["denominacao"]).upper()))
    _escrever(saida / "siglas_organizacoes.csv", organizacoes)
    resumo["organizacoes"] = len(organizacoes)
    resumo["sigla_do_registo"] = sum(1 for o in organizacoes
                                     if o["origem_sigla"].startswith("registo"))
    resumo["siglas_desambiguadas"] = desambiguadas
    resumo["siglas_fixadas_do_anterior"] = len(fixadas)

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
        raizes = {mod_siglas.linhagem(o["codigo_dgert"]) for o in grupo}
        if len(raizes) > 1:
            ambiguas.append({
                "sigla": s,
                "n_organizacoes": len(grupo),
                "n_linhagens": len(raizes),
                "denominacoes": " | ".join(o["denominacao"] for o in grupo),
                "resolucao": "",
            })
    _escrever(saida / "siglas_ambiguas.csv", ambiguas)
    resumo["siglas_distintas"] = len(por_sigla)
    resumo["siglas_ambiguas"] = len(ambiguas)
    if ambiguas:
        # Não é um aviso: é uma falha. A regra da escada só termina em
        # candidatos livres, pelo que um duplicado aqui significa que a regra
        # tem um defeito — e um duplicado silencioso produz dois ficheiros
        # diferentes com o mesmo nome.
        raise SystemExit(
            f"ERRO — {len(ambiguas)} sigla(s) ainda duplicada(s) depois da "
            f"desambiguação: {', '.join(a['sigla'] for a in ambiguas[:5])}. "
            "É um defeito da regra em cct/siglas.py, não dos dados.")

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
    p.add_argument("--reatribuir", action="store_true",
                   help="ignora as siglas já atribuídas e recalcula tudo. "
                        "Muda siglas em uso — usar só quando se sabe que "
                        "nenhum ficheiro foi ainda nomeado com elas.")
    args = p.parse_args(argv)

    resumo = construir(Path(args.export), Path(args.saida),
                       reatribuir=args.reatribuir)
    print("== Vocabulários construídos")
    for k, v in resumo.items():
        print(f"  {k.replace('_', ' ')}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
