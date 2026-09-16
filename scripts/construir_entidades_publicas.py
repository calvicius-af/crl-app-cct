#!/usr/bin/env python3
"""Constrói o vocabulário de entidades do sector institucional das Administrações Públicas.

Entrada: o PDF que o INE publica anualmente com as entidades que integram o
setor S.13 nos termos do SEC 2010.

    python scripts/construir_entidades_publicas.py \\
        1_fontes/externas/Entidades_S13_2025.pdf --ano 2025

Saída: `vocabularios/entidades_administracao_publica.csv`.

**Leia isto antes de usar o ficheiro.** A lista do INE responde a uma pergunta
que não é a do RNC. O INE classifica por *contas nacionais*: uma entidade está
em S.13 se for produtor não mercantil, o que se decide pelo teste dos 50% de
cobertura dos custos por receitas de mercado. O RNC classifica por *regime
laboral*: APU são as entidades cujos trabalhadores estão sob a LTFP e cujos IRCT
são depositados na DGAEP, e não publicados no BTE.

Os dois critérios não coincidem, e a diferença é perigosa nos dois sentidos:

* o **Metropolitano de Lisboa, E.P.E.**, a **RTP, S.A.** e as **Infraestruturas
  de Portugal, S.A.** estão em S.13 — mas os seus trabalhadores estão sob o
  Código do Trabalho e os seus acordos de empresa saem no BTE. Para o RNC são
  SPE, e são processáveis. Classificá-los como APU retirava-os do pipeline;
* a **CP**, a **Carris**, a **EPAL** e as **Águas de Portugal** **não** estão em
  S.13, porque passam o teste de mercado. A ausência da lista não diz nada sobre
  o âmbito.

Daí as duas colunas de sinal deste ficheiro, e daí o `sinal` nunca ser tratado
como decisão: é uma proposta que sai sempre marcada para revisão humana.

Ver docs/rnc/README.md §5.2-bis e ADR-0019.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

RE_SUBSETOR = re.compile(r"^S\.(\d+[AM]?)\s*[–-]\s*(.+)$")
RE_RODAPE = re.compile(r"^\d+\s+de\s+\d+$")

# Formas jurídicas empresariais. Uma entidade de S.13 que as tenha é, quase
# sempre, uma empresa pública reclassificada em contas nacionais — e é
# precisamente o caso em que a lista do INE **não** serve para decidir o âmbito
# do RNC. Ver o aviso no topo deste ficheiro.
RE_FORMA_EMPRESARIAL = re.compile(
    r"\b(E\.?\s?P\.?\s?E\.?|E\.?\s?M\.?(\s?T\.?)?|E\.?\s?I\.?\s?M\.?"
    r"|S\.?\s?A\.?|SGPS|Unipessoal|L\.?da\.?|Lda|Limitada)\b")

# Subsectores que são administração pública em sentido estrito. Uma entidade
# destes, sem forma jurídica empresarial, é um sinal forte de APU.
SUBSETORES_ADMINISTRACAO = {
    "S.13111": "Administração Central — Estado",
    "S.13112": "Serviços e Fundos Autónomos da Administração Central",
    "S.13113": "Instituições Sem Fim Lucrativo da Administração Central",
    "S.131311": "Órgãos dos Governos Regionais",
    "S.131311A": "Órgãos do Governo Regional dos Açores",
    "S.131311M": "Órgãos do Governo Regional da Madeira",
    "S.131312": "Serviços e Fundos Autónomos da Administração Regional",
    "S.131312A": "Serviços e Fundos Autónomos da Administração Regional dos Açores",
    "S.131312M": "Serviços e Fundos Autónomos da Administração Regional da Madeira",
    "S.131322": "Municípios",
    "S.131323": "Freguesias",
    "S.131324": "Serviços e Fundos Autónomos da Administração Local",
    "S.131325": "Instituições Sem Fim Lucrativo da Administração Local",
    "S.1314": "Fundos de Segurança Social",
}

SINAL_APU = "APU"
SINAL_REVER = "SPE_PROVAVEL"


def ler_pdf(caminho: Path) -> list[dict]:
    """Uma entrada por entidade, com o subsector em que o INE a coloca."""
    import pdfplumber

    entidades: list[dict] = []
    subsetor = subsetor_nome = ""
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            for linha in (pagina.extract_text() or "").split("\n"):
                linha = linha.strip()
                if not linha or RE_RODAPE.match(linha):
                    continue
                cabecalho = RE_SUBSETOR.match(linha)
                if cabecalho:
                    subsetor = "S." + cabecalho.group(1)
                    subsetor_nome = cabecalho.group(2).strip()
                    continue
                if not subsetor or subsetor not in SUBSETORES_ADMINISTRACAO:
                    continue
                empresarial = bool(RE_FORMA_EMPRESARIAL.search(linha))
                entidades.append({
                    "nome": linha,
                    "subsetor": subsetor,
                    "subsetor_nome": subsetor_nome or
                    SUBSETORES_ADMINISTRACAO[subsetor],
                    # É aqui que a distinção que importa fica registada: uma
                    # entidade com forma empresarial em S.13 é uma empresa
                    # pública reclassificada, não administração pública. Para o
                    # RNC é candidata a SPE — processável — e nunca a APU.
                    "sinal": SINAL_REVER if empresarial else SINAL_APU,
                    "forma_empresarial": "sim" if empresarial else "nao",
                })
    return entidades


def construir(pdf: Path, saida: Path, ano: str) -> dict:
    entidades = ler_pdf(pdf)
    if not entidades:
        raise SystemExit(f"Nenhuma entidade lida de {pdf.name} — confirmar que é "
                         "a lista do sector institucional das Administrações "
                         "Públicas publicada pelo INE")
    vistos: dict[str, dict] = {}
    for e in entidades:
        vistos.setdefault(e["nome"].lower(), {**e, "fonte": f"INE S.13 {ano}",
                                              "ano": ano})
    linhas = sorted(vistos.values(), key=lambda e: (e["subsetor"], e["nome"]))
    saida.parent.mkdir(parents=True, exist_ok=True)
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["nome", "sinal", "subsetor",
                                          "subsetor_nome", "forma_empresarial",
                                          "fonte", "ano"],
                           delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)
    return {
        "entidades": len(linhas),
        "sinal_APU": sum(1 for e in linhas if e["sinal"] == SINAL_APU),
        "sinal_SPE_PROVAVEL": sum(1 for e in linhas if e["sinal"] == SINAL_REVER),
        "subsetores": len({e["subsetor"] for e in linhas}),
    }


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="construir_entidades_publicas",
        description="Lê a lista do INE das entidades do sector S.13.")
    p.add_argument("pdf", help="PDF publicado pelo INE")
    p.add_argument("--ano", required=True, help="ano a que a lista respeita")
    p.add_argument("--saida", default=str(RAIZ / "vocabularios"
                                          / "entidades_administracao_publica.csv"))
    args = p.parse_args(argv)

    resumo = construir(Path(args.pdf), Path(args.saida), args.ano)
    print("== Entidades do sector institucional das Administrações Públicas")
    for k, v in resumo.items():
        print(f"  {k.replace('_', ' ')}: {v}")
    print("  AVISO: o sinal é uma proposta, nunca uma decisão. Uma entidade com")
    print("         forma empresarial em S.13 é candidata a SPE, não a APU —")
    print("         ver o cabeçalho deste script e ADR-0019.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
