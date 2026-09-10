"""Nomeação dos documentos recolhidos, no esquema que o pipeline sabe ler.

Segunda fase da aquisição (a primeira é `cct/recolha.py`). Corre inteiramente
offline e pode repetir-se à vontade: lê o registo, atribui a cada documento um
ordinal estável, deriva as siglas dos outorgantes e copia o PDF para

    data/raw/bte/bte_2026/26_PR_003_BTE_31_ACRAL_CESP.pdf          convenções
    data/raw/bte/bte_2026/extensoes/26_PE_001_BTE_31_….pdf         portarias e avisos

O nome não é decorativo: o `cct/localizador.py` lê dele o ano, o número do BTE e
os tokens das partes; o `cct/comparar.py` deduz o ano; e o cruzamento com as
variáveis do MaxQDA é feito pelos primeiros caracteres. Ver docs/dados/README.md.

Uso:
  python -m cct.nomeacao --destino data/raw/bte             # simulação
  python -m cct.nomeacao --destino data/raw/bte --aplicar
"""
import argparse
import re
import shutil
import time
from pathlib import Path

from .localizador import _sem_acentos
from .recolha import (INTERVALO_PERSISTENCIA, RAIZ, REGISTO_OMISSAO, Registo,
                      sha256_ficheiro)

DESTINO_OMISSAO = RAIZ / "data" / "raw" / "bte"

TOKEN_FAMILIA = {"convencao": "PR", "extensao": "PE",
                 "aviso": "AV", "adesao": "AA"}
SUBPASTA_FAMILIA = {"convencao": "", "extensao": "extensoes",
                    "aviso": "extensoes", "adesao": "extensoes"}

ESTADOS_COM_FICHEIRO = {"descarregado", "ja_existente", "inalterado"}

MAX_NOME = 63          # limite de nome de documento do MaxQDA (RF-21)
MAX_SIGLA = 20

# Palavras que não entram numa sigla derivada por recurso.
LIGACOES = {"de", "do", "da", "dos", "das", "e", "em", "a", "o", "as", "os",
            "no", "na", "nos", "nas", "para", "com", "ao", "aos", "à", "às"}
FORMA_JURIDICA = {"sa", "s", "lda", "ldª", "l", "da", "unipessoal", "crl",
                  "sarl", "sgps", "inc", "sucursal", "limitada",
                  "sociedade", "em", "ea", "eim", "ldas"}

# Palavras que quase todas as organizações têm no nome e que, por isso, não
# distinguem ninguém. Só são descartadas se sobrar alguma coisa depois.
GENERICOS = {"sindicato", "sindicatos", "sindical", "sindicais", "associacao",
             "associacoes", "federacao", "confederacao", "uniao", "nacional",
             "nacionais", "trabalhadores", "trabalhadoras", "profissionais",
             "portugues", "portuguesa", "portugueses", "portugal"}

RE_PARENTESES = re.compile(r"\(([^)]{2,30})\)")
RE_FIM_APOS_TRACO = re.compile(r"[-–—]\s*([^-–—,;()]{2,30})\s*$")
RE_INICIO_ANTES_TRACO = re.compile(r"^\s*([^-–—,;()]{2,30}?)\s*[-–—]\s")
RE_ENTRE_TRACOS = re.compile(r"[-–—]\s*([^-–—,;()]{2,30}?)\s*(?=[-–—]|$)")
RE_PARTES_TITULO = re.compile(
    r"\bentre\s+(?:a|o|as|os)?\s*(?P<a>.+?)\s+e\s+(?:a|o|as|os)\s+(?P<b>.+?)\s*$",
    re.IGNORECASE | re.DOTALL)


def _e_sigla(token: str) -> bool:
    """'ACRAL' e 'AEVP' sim; 'Sindicato' e 'L.da' não."""
    limpo = re.sub(r"[^A-Za-z0-9]", "", _sem_acentos(token))
    if len(limpo) < 2 or len(limpo) > MAX_SIGLA:
        return False
    letras = [c for c in limpo if c.isalpha()]
    return bool(letras) and all(c.isupper() for c in letras)


def _limpar_sigla(token: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", _sem_acentos(token))


def _camel(nome: str, max_chars: int = MAX_SIGLA) -> str:
    """Recurso quando não há sigla: 'Águas do Norte' → 'AguasNorte'.

    Descarta ligações e formas jurídicas e, se ainda assim sobrar alguma coisa,
    também as palavras genéricas: 'Sindicato Nacional dos Motoristas' vale
    'Motoristas', não 'SindicatoNacional'.
    """
    uteis = []
    for bruto in re.split(r"[^\wÀ-ÿ]+", _sem_acentos(nome)):
        baixo = bruto.lower()
        if not bruto or len(bruto) < 2:
            continue
        if baixo in LIGACOES or baixo in FORMA_JURIDICA:
            continue
        uteis.append(bruto if bruto.isupper() else bruto.capitalize())
    distintivas = [p for p in uteis if p.lower() not in GENERICOS]
    palavras = (distintivas or uteis)[:4]
    saida = ""
    for p in palavras:
        if len(saida) + len(p) > max_chars and saida:
            break
        saida += p
    return saida[:max_chars] or "SemNome"


def sigla(nome: str, tabela: dict[str, str] | None = None) -> tuple[str, str | None]:
    """Sigla de um outorgante. Devolve (sigla, aviso) — aviso quando é derivada."""
    nome = (nome or "").strip(" .;,")
    if not nome:
        return "", "outorgante vazio"
    if tabela:
        chave = _sem_acentos(nome).lower()
        if chave in tabela:
            return tabela[chave], None
        for k, v in tabela.items():                    # correspondência parcial
            if k and k in chave:
                return v, None
    for regex in (RE_PARENTESES, RE_FIM_APOS_TRACO, RE_INICIO_ANTES_TRACO,
                  RE_ENTRE_TRACOS):
        for m in regex.finditer(nome):
            if _e_sigla(m.group(1)):
                return _limpar_sigla(m.group(1)), None
    return _camel(nome), f"sigla derivada de «{nome[:60]}» — confirmar"


def e_sindical(nome: str) -> bool:
    """Sindical é quem tem 'sindic' no nome.

    Classifica corretamente a CNIS (Confederação Nacional das Instituições de
    Solidariedade) como patronal e a FNSTFPS (Federação Nacional dos Sindicatos
    dos Trabalhadores…) como sindical.
    """
    return "sindic" in _sem_acentos(nome).lower()


def _partes_do_titulo(titulo: str) -> list[str]:
    """'Contrato coletivo entre a X e o Y' → ['X', 'Y'] (para as retificações)."""
    m = RE_PARTES_TITULO.search(re.sub(r"\s+", " ", titulo or ""))
    if not m:
        return []
    partes = []
    for lado in (m.group("a"), m.group("b")):
        lado = re.split(r"\s+e\s+outr[ao]s?\b", lado, flags=re.IGNORECASE)[0]
        partes.append(lado.strip(" .,;"))
    return [p for p in partes if p]


def separar_outorgantes(outorgantes: str, titulo: str = "") -> tuple[list[str], list[str]]:
    """Divide os outorgantes em (patronais, sindicais)."""
    nomes = [n.strip() for n in re.split(r"[;\n]", outorgantes or "") if n.strip()]
    if not nomes:
        nomes = _partes_do_titulo(titulo)
    patronais = [n for n in nomes if not e_sindical(n)]
    sindicais = [n for n in nomes if e_sindical(n)]
    return patronais, sindicais


def nome_documento(entrada: dict, ordinal: int,
                   tabela: dict[str, str] | None = None) -> tuple[str, list[str]]:
    """Compõe o nome (sem extensão) e devolve os avisos que exigem confirmação."""
    avisos: list[str] = []
    ano = int(entrada.get("ano") or 0)
    num_bte = int(entrada.get("num_bte") or 0)
    fam = entrada.get("familia") or "convencao"
    patronais, sindicais = separar_outorgantes(entrada.get("outorgantes", ""),
                                               entrada.get("titulo", ""))
    lados = []
    for lista, rotulo in ((patronais, "patronal"), (sindicais, "sindical")):
        if not lista:
            avisos.append(f"sem outorgante do lado {rotulo}")
            continue
        s, aviso = sigla(lista[0], tabela)
        if aviso:
            avisos.append(aviso)
        if len(lista) > 1:
            avisos.append(f"{len(lista)} outorgantes do lado {rotulo} "
                          "— o nome usa o primeiro")
        if s:
            lados.append(s)
    if not lados:
        lados = [_camel(entrada.get("titulo", ""))]
        avisos.append("nome derivado do título — confirmar")

    prefixo = (f"{ano % 100:02d}_{TOKEN_FAMILIA.get(fam, 'PR')}_{ordinal:03d}"
               f"_BTE_{num_bte:02d}")
    nome = prefixo + "".join("_" + l for l in lados)
    if len(nome) > MAX_NOME:                       # encurta as siglas, não o prefixo
        folga = MAX_NOME - len(prefixo) - len(lados)
        por_lado = max(4, folga // len(lados))
        nome = prefixo + "".join("_" + l[:por_lado] for l in lados)
        avisos.append("nome encurtado para caber em 63 caracteres")
    return nome, avisos


def atribuir_ordinais(registo: Registo, familias=("convencao", "extensao",
                                                  "aviso", "adesao")) -> int:
    """Numera os documentos por ano e família, por ordem de (nº BTE, posição).

    Um ordinal já atribuído nunca é recalculado — é o que mantém a continuidade
    com a numeração de 2025 e com o trabalho já feito sobre esses nomes.
    """
    novos = 0
    entradas = [e for e in registo.entradas.values()
                if e.get("familia") in familias
                and (e.get("descarga") or {}).get("estado") in ESTADOS_COM_FICHEIRO]
    grupos: dict[tuple, list[dict]] = {}
    for e in entradas:
        grupos.setdefault((e.get("ano"), e.get("familia")), []).append(e)
    for (_ano, _fam), grupo in grupos.items():
        usados = {(e.get("nomeacao") or {}).get("ordinal")
                  for e in grupo if (e.get("nomeacao") or {}).get("ordinal")}
        proximo = max(usados) + 1 if usados else 1
        por_atribuir = [e for e in grupo
                        if not (e.get("nomeacao") or {}).get("ordinal")]
        por_atribuir.sort(key=lambda e: (e.get("num_bte") or 0,
                                         e.get("posicao") or 0, e["chave"]))
        for e in por_atribuir:
            e.setdefault("nomeacao", {})["ordinal"] = proximo
            proximo += 1
            novos += 1
    return novos


def carregar_siglas(caminho: Path) -> dict[str, str]:
    """Tabela opcional de siglas fixadas pela equipa: 'nome;sigla' por linha."""
    import csv

    tabela: dict[str, str] = {}
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for linha in csv.reader(f, delimiter=";"):
            if len(linha) < 2 or not linha[0].strip():
                continue
            if _sem_acentos(linha[0]).strip().lower() in ("nome", "nome_completo"):
                continue
            tabela[_sem_acentos(linha[0]).strip().lower()] = \
                _limpar_sigla(linha[1])[:MAX_SIGLA]
    return tabela


def nomear(registo: Registo, destino: Path, *, aplicar: bool = False,
           tabela: dict[str, str] | None = None,
           familias=("convencao", "extensao", "aviso", "adesao"),
           aceitar_heuristicas: bool = False) -> dict:
    """Atribui nomes e, com `aplicar=True`, copia os PDFs para o destino.

    Um documento cujo nome tenha avisos de `nome_documento()` (sigla
    derivada por heurística, outorgante em falta, nome do título, nome
    encurtado) fica em estado `por_confirmar` e **não é escrito**, mesmo com
    `aplicar=True` — a confirmação humana que a spec promete tem de acontecer
    antes de o ficheiro existir e o ordinal ficar permanente, não depois.
    `aceitar_heuristicas=True` desliga esta proteção, para quem decide
    conscientemente aceitar o risco (ex.: uma corrida em lote já revista).
    """
    resumo = {"ordinais_novos": atribuir_ordinais(registo, familias),
              "por_estado": {}, "avisos": [], "problemas": [], "nomes": []}

    def contar(estado):
        resumo["por_estado"][estado] = resumo["por_estado"].get(estado, 0) + 1

    entradas = [e for e in registo.entradas.values()
                if e.get("familia") in familias
                and (e.get("descarga") or {}).get("estado") in ESTADOS_COM_FICHEIRO]
    entradas.sort(key=lambda e: (e.get("ano") or 0, e.get("num_bte") or 0,
                                 (e.get("nomeacao") or {}).get("ordinal") or 0))
    vistos: dict[tuple, list[str]] = {}
    escritos = 0

    try:
        for e in entradas:
            nomeacao = e.setdefault("nomeacao", {})
            origem = Path((e.get("descarga") or {}).get("caminho", ""))
            if not origem.exists():
                resumo["problemas"].append(f"{e['chave']}: PDF recolhido não encontrado "
                                           f"({origem})")
                contar("sem_origem")
                continue
            nome, avisos = nome_documento(e, nomeacao["ordinal"], tabela)
            avisos_heuristica = list(avisos)   # antes do aviso de par repetido, abaixo —
                                               # esse é informativo, não indica nome errado
            partes = "_".join(nome.split("_")[5:])
            vistos.setdefault((e.get("ano"), partes), []).append(nome)
            if len(vistos[(e.get("ano"), partes)]) > 1:
                avisos.append("outro documento do mesmo par de outorgantes neste ano: "
                              + ", ".join(vistos[(e.get("ano"), partes)][:-1]))
            subpasta = SUBPASTA_FAMILIA.get(e["familia"], "")
            pasta = destino / f"bte_{e['ano']}" / subpasta if subpasta \
                else destino / f"bte_{e['ano']}"
            alvo = pasta / f"{nome}.pdf"
            nomeacao.update({"doc_id": nome, "caminho": str(alvo), "avisos": avisos})
            resumo["nomes"].append((e["chave"], nome))
            resumo["avisos"].extend(f"{nome}: {a}" for a in avisos)

            if alvo.exists():
                if sha256_ficheiro(alvo) == (e.get("descarga") or {}).get("sha256"):
                    nomeacao["estado"] = "ja_existente"
                    contar("ja_existente")
                else:
                    nomeacao["estado"] = "conflito"
                    resumo["problemas"].append(
                        f"{nome}: já existe um ficheiro diferente no destino — não foi escrito")
                    contar("conflito")
                continue

            if avisos_heuristica and not aceitar_heuristicas:
                nomeacao["estado"] = "por_confirmar"
                contar("por_confirmar")
                continue

            if not aplicar:
                nomeacao["estado"] = "por_nomear"
                contar("por_nomear")
                continue

            pasta.mkdir(parents=True, exist_ok=True)
            temp = alvo.with_suffix(".pdf.part")
            shutil.copyfile(origem, temp)
            temp.replace(alvo)
            nomeacao.update({"estado": "nomeado",
                             "data": time.strftime("%Y-%m-%dT%H:%M:%S")})
            contar("nomeado")
            escritos += 1
            if escritos % INTERVALO_PERSISTENCIA == 0:
                registo.guardar()
    finally:
        registo.guardar()
    return resumo


def texto_resumo(resumo: dict, *, aplicar: bool) -> str:
    linhas = ["== Nomeação"]
    linhas.append(f"  ordinais novos atribuídos: {resumo['ordinais_novos']}")
    for estado, n in sorted(resumo["por_estado"].items()):
        linhas.append(f"    {estado}: {n}")
    if not aplicar and resumo["por_estado"].get("por_nomear"):
        linhas.append("  (simulação — repetir com --aplicar para escrever)")
    if resumo["por_estado"].get("por_confirmar"):
        linhas.append("  (siglas por confirmar — corrigir com --siglas, ou aceitar "
                      "conscientemente o risco com --aceitar-heuristicas)")
    if resumo["avisos"]:
        linhas.append(f"  a confirmar ({len(resumo['avisos'])}):")
        linhas.extend(f"    {a}" for a in resumo["avisos"])
    if resumo["problemas"]:
        linhas.append("  PROBLEMAS:")
        linhas.extend(f"    {p}" for p in resumo["problemas"])
    return "\n".join(linhas)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="cct.nomeacao",
        description="Renomeia os documentos recolhidos para o esquema do pipeline.")
    p.add_argument("--registo", default=str(REGISTO_OMISSAO))
    p.add_argument("--destino", default=str(DESTINO_OMISSAO))
    p.add_argument("--siglas", help="CSV opcional 'nome;sigla' com siglas fixadas")
    p.add_argument("--familias", default="convencao,extensao,aviso,adesao")
    p.add_argument("--aplicar", action="store_true",
                   help="escreve mesmo (por omissão só simula)")
    p.add_argument("--aceitar-heuristicas", action="store_true",
                   help="escreve mesmo os documentos com sigla derivada por "
                        "heurística, sem esperar por confirmação humana "
                        "(--siglas) — usar com critério")
    args = p.parse_args(argv)

    registo = Registo.carregar(Path(args.registo))
    if not registo.entradas:
        raise SystemExit(f"Registo vazio ({args.registo}) — correr primeiro "
                         "python -m cct.recolha")
    tabela = carregar_siglas(Path(args.siglas)) if args.siglas else None
    resumo = nomear(registo, Path(args.destino), aplicar=args.aplicar,
                    tabela=tabela,
                    familias=tuple(f.strip() for f in args.familias.split(",") if f.strip()),
                    aceitar_heuristicas=args.aceitar_heuristicas)
    print(texto_resumo(resumo, aplicar=args.aplicar))
    return 1 if resumo["problemas"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
