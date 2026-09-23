"""O catálogo IRCT — uma linha por documento, gerada a partir dos índices do BTE.

É a fonte de verdade da gestão documental do RNC. Se a pasta e o catálogo
discordarem, o catálogo está certo e a pasta está por arrumar.

Ao contrário de uma lista mantida à mão, este ficheiro **regera-se**: correr
outra vez sobre os mesmos índices dá exatamente o mesmo CSV. O que a equipa
escreve (`temas_atribuidos`, `tecnico`, `data_validacao`, `perita`,
`observacoes`) é preservado entre corridas, procurado pelo `nome_canonico`.

    python -m cct.catalogo --indices data/raw/indices \\
        --saida 0_gestao/catalogo/catalogo_irct_2026.csv

Ver docs/rnc/README.md §7.
"""
import argparse
import csv
import re
from pathlib import Path

from . import ambito as mod_ambito
from .nomeacao import (ESQUEMA_2025, FAMILIAS_COM_AMBITO,
                       FAMILIAS_PROCESSAVEIS, FAMILIAS_SO_METADADO,
                       PASTA_FAMILIA, PASTA_FAMILIA_DESCONHECIDA, RE_ALTERA,
                       NomeRNCInvalido, carregar_siglas, nome_documento,
                       resolver_convencoes_base, separar_outorgantes,
                       sequencial_bte, tipo_normalizado)
from .recolha import INDICES_OMISSAO, familia, ler_indice

# Colunas produzidas pelo script. A ordem é a do documento de gestão documental.
COLUNAS_AUTOMATICAS = [
    "nome_canonico", "ficheiro_destino", "ficheiro_origem", "ano", "seq_anual",
    "tipo_documento", "familia", "processavel", "ambito", "ambito_origem",
    "cod_irct", "acto_negociacao", "cod_irct_base", "cod_irct_base_adicionais",
    "portaria_dr", "bte_numero", "bte_data",
    "pagina_inicio", "pagina_fim",
    "n_outorgantes", "outorgantes", "relacao", "relacao_alvo",
    "avisos_projeto", "altera_estruturado", "altera_por_resolver",
    "vide_em_vigor", "materias_detectadas", "sectores_a_classificar",
    "url_fonte", "titulo", "estado", "avisos",
]

# Colunas preenchidas pela equipa ao longo do ciclo. O script cria-as vazias e
# nunca lhes toca depois — é o que permite regerar o catálogo sem perder
# trabalho humano.
COLUNAS_EQUIPA = ["temas_atribuidos", "tecnico", "data_validacao", "perita",
                  "observacoes"]

COLUNAS = COLUNAS_AUTOMATICAS + COLUNAS_EQUIPA

# `CCT-ALT.20250708.321/2025` → tipo, data, sequencial/ano do documento
# alterado. O padrão vive em cct/nomeacao.py, que também o usa para ligar uma
# portaria à convenção de base.

# `00260057.pdf` → páginas 26 a 57. O nome de origem do BTE codifica o
# intervalo de páginas em dois blocos de quatro dígitos.
RE_PAGINAS = re.compile(r"^(\d{4})(\d{4})$")

# A coluna SECTOR(ES) DE ACTIVIDADE: do índice mistura dois vocabulários: os
# sectores de atividade a que a convenção se aplica e as matérias que ela
# regula. Não separar isto contamina qualquer análise sectorial.
#
# A lista abaixo reconhece *matérias* — o que sobra é tratado como sector
# candidato e vai para `sectores_a_classificar`, para decisão humana. É
# deliberadamente uma lista de matérias e não de sectores: as matérias são um
# conjunto pequeno e fechado (são as do livro de códigos), enquanto os sectores
# são abertos e mudam com a CAE. Ver docs/rnc/README.md §7-b.
MATERIAS = (
    "remuneracoes", "retribuicao", "subsidio", "abono", "premio",
    "ajudas de custo", "diuturnidades", "anuidades",
    "horario", "tempo de trabalho", "duracao do trabalho", "trabalho suplementar",
    "trabalho nocturno", "trabalho noturno", "turnos", "banco de horas",
    "descanso", "ferias", "feriados", "faltas", "licencas",
    "teletrabalho", "trabalho a distancia", "desconexao",
    "parentalidade", "maternidade", "paternidade",
    "formacao profissional", "estagio profissional", "aprendizagem",
    "carreira", "promocao profissional", "categoria profissional",
    "categorias profissionais", "definicao de funcoes", "descricao de funcoes",
    "progressao", "avaliacao de desempenho", "polivalencia",
    "seguranca e saude", "higiene e seguranca", "medicina no trabalho",
    "seguro de saude", "seguro de acidentes", "seguro de vida",
    "acidentes de trabalho",
    "disciplina", "cessacao do contrato", "periodo experimental",
    "mobilidade", "deslocacoes", "transferencia",
    "igualdade", "nao discriminacao", "assedio", "protecao de dados",
    "videovigilancia", "direitos de personalidade",
    "greve", "actividade sindical", "atividade sindical", "delegados sindicais",
    "comissao de trabalhadores", "quotizacao",
    "reforma", "pensoes", "complemento de reforma",
    "seguranca social", "accao social", "acao social",
)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", mod_ambito._normalizar(s))


def separar_sectores(bruto: str) -> tuple[list[str], list[str]]:
    """Divide a coluna dos sectores em `(materias, sectores_a_classificar)`.

    Nada é descartado: cada item cai num dos dois lados. O que o script não
    reconhece como matéria fica marcado para classificação humana — não é
    silenciosamente assumido como sector, porque assumir era o problema.
    """
    materias, sectores = [], []
    for item in (p.strip(" .;") for p in re.split(r"[;\n]", bruto or "")):
        if not item:
            continue
        n = _norm(item)
        if any(m in n for m in MATERIAS):
            materias.append(item)
        else:
            sectores.append(item)
    return list(dict.fromkeys(materias)), list(dict.fromkeys(sectores))


def separar_alteracoes(bruto: str) -> tuple[list[dict], list[str]]:
    """Divide a cadeia de alterações em `(estruturado, por_resolver)`."""
    estruturado, resto = [], []
    for item in (p.strip() for p in re.split(r"[;\n]", bruto or "")):
        if not item:
            continue
        m = RE_ALTERA.match(item)
        if m:
            estruturado.append(m.groupdict())
        else:
            resto.append(item)
    return estruturado, resto


# Que relação um documento tem com a convenção a que se refere. A cadeia de
# alterações do índice tem o mesmo formato nos quatro casos — o que muda é o que
# a relação significa, e isso não se lê da coluna: lê-se do tipo do documento.
#
#   altera   uma revisão da própria convenção (CCT-ALT, AE-ALT, …)
#   estende  uma portaria alarga o âmbito de uma convenção a terceiros
#   adere    uma parte adere a uma convenção de que não era outorgante
#   refere   um aviso menciona a convenção, sem produzir efeito sobre ela
#
# Sem isto, uma leitura do catálogo conta uma portaria de extensão como se fosse
# uma revisão da convenção — e a série de revisões passa a ter documentos que
# nunca alteraram uma vírgula do articulado.
RELACAO_POR_FAMILIA = {"convencao": "altera", "extensao": "estende",
                       "adesao": "adere", "aviso": "refere"}


def relacao(fam: str, estruturado: list[dict], por_resolver: list[str]) -> tuple[str, str]:
    """`(tipo de relação, documento-alvo)` — vazios quando não há relação."""
    if not estruturado and not por_resolver:
        return "", ""
    alvos = [f"{a['tipo']}.{a['data']}.{a['seq']}/{a['ano']}" for a in estruturado]
    return RELACAO_POR_FAMILIA.get(fam or "", "refere"), "; ".join(alvos)


def paginas(ficheiro_origem: str) -> tuple[int | None, int | None]:
    """`00260057.pdf` → (26, 57). `(None, None)` quando o nome não o diz."""
    m = RE_PAGINAS.match(Path(ficheiro_origem or "").stem)
    if not m:
        return None, None
    ini, fim = int(m.group(1)), int(m.group(2))
    return (ini, fim) if 0 < ini <= fim else (None, None)


# Dígitos de família do `COD: (IRCT)` **observados e verificados** por
# cruzamento do BTE 31/2026 com o registo da DGERT. Não é a tabela de famílias
# da DGCP (ex-GEP), que não está publicada — é a lista do que se confirmou.
#
#   2  contrato coletivo de trabalho     27251 → acto 7251
#   4  acordo de empresa                 47252 → acto 7252
#
# O dígito dos acordos coletivos de trabalho, das portarias de extensão, dos
# acordos de adesão e das decisões arbitrais **está por determinar**: nenhum
# aparece no único boletim verificado. Enquanto não estiver, um código que
# comece por outro dígito é devolvido inteiro — prefere-se não ter a ligação ao
# registo a ter uma ligação errada. Ver docs/rnc/README.md §5.3 e §10, tarefa 5.
FAMILIAS_COD_IRCT = {"2": "contrato coletivo de trabalho",
                     "4": "acordo de empresa"}


def acto_negociacao(cod_irct: str) -> str:
    """Do `COD: (IRCT)` para o identificador de acto de negociação da DGERT.

    O código que o BTE publica é o identificador do acto de negociação da DGERT
    com um dígito de família à frente. É esse identificador que é estável entre
    revisões da mesma convenção, ao longo dos anos — a verificação está no §5.3
    do README do RNC.

    Devolve `""` quando não consegue derivar o acto: um código de cinco
    algarismos cujo primeiro dígito não é nenhum dos verificados fica sem
    tradução, e a coluna `cod_irct` do catálogo guarda na mesma o código
    completo. Uma coluna vazia é um facto; um acto errado é uma junção errada
    com o registo da DGERT, e essas não se notam.
    """
    cod = re.sub(r"\D", "", str(cod_irct or ""))
    if len(cod) == 5:
        return cod[1:] if cod[0] in FAMILIAS_COD_IRCT else ""
    return cod


def _colunas_base(item: dict, fam: str, nomeado: dict) -> dict:
    """`cod_irct_base`, `cod_irct_base_adicionais` e `portaria_dr` (ADR-0022).

    `cod_irct_base` é o código que vai no nome — numa convenção, o seu. Numa
    portaria que estenda várias convenções, os outros códigos ficam em
    `cod_irct_base_adicionais`, pela ordem da cadeia do índice, separados por
    `; `, sem sobrecarregar o campo singular.
    """
    if fam == "convencao":
        base = re.sub(r"\D", "", str(item.get("cod_irct") or ""))
        return {"cod_irct_base": base, "cod_irct_base_adicionais": "",
                "portaria_dr": ""}
    codigos = [c for c in re.split(r"[;\s]+", str(item.get("cod_irct_base") or "")) if c]
    return {"cod_irct_base": codigos[0] if codigos else "",
            "cod_irct_base_adicionais": "; ".join(codigos[1:]),
            "portaria_dr": (nomeado.get("nomeacao") or {}).get("portaria_dr", "")}


def linhas(itens: list[dict], *, tabela_siglas: dict[str, str] | None = None,
           vocabulario_ambito: dict[str, str] | None = None,
           esquema: str = "rnc") -> list[dict]:
    """Uma linha de catálogo por item de índice, já com o nome canónico."""
    saida = []
    itens = [dict(i) for i in itens]      # a resolução da base escreve nos itens
    if esquema == "rnc":
        resolver_convencoes_base(itens)
    for posicao, item in enumerate(sorted(
            itens, key=lambda i: (i.get("ano") or 0, i.get("num_bte") or 0,
                                  sequencial_bte(i) or 0, i.get("posicao") or 0)), 1):
        copia = dict(item)
        try:
            nome, avisos = nome_documento(copia, posicao, tabela_siglas,
                                          esquema=esquema,
                                          vocabulario_ambito=vocabulario_ambito)
        except NomeRNCInvalido as exc:
            # A linha fica no catálogo — o documento existe —, mas sem nome
            # canónico: nenhum nome se atribui sem os campos estruturais.
            nome, avisos = "", [f"{exc} — nome por atribuir"]
        patronais, sindicais = separar_outorgantes(item.get("outorgantes", ""),
                                                   item.get("titulo", ""))
        materias, sectores = separar_sectores(item.get("sectores", ""))
        estruturado, por_resolver = separar_alteracoes(item.get("altera", ""))
        amb, amb_origem, _ = mod_ambito.classificar_com_ine(
            patronais[0] if patronais else item.get("titulo", ""),
            item.get("tipo", ""), vocabulario_ambito)
        p_ini, p_fim = paginas(item.get("ficheiro", ""))
        fam = item.get("familia") or familia(item.get("tipo", "")) or ""
        if not nome:
            destino = ""
        elif fam in FAMILIAS_SO_METADADO:
            # Um aviso de projeto de portaria não tem ficheiro próprio: o que
            # interessa dele — que houve projeto, e quando — vai para a coluna
            # `avisos_projeto` da portaria que se lhe seguir. A linha de
            # catálogo fica, porque o aviso existiu e apagá-lo era perder um
            # facto; o que não fica é o PDF.
            destino = ""
        else:
            pasta = PASTA_FAMILIA.get(fam, PASTA_FAMILIA_DESCONHECIDA)
            if fam in FAMILIAS_COM_AMBITO:
                pasta = f"{pasta}/{amb}"
            destino = f"1_fontes/irct/{pasta}/{nome}.pdf"
        # Processável é quem passa nas duas peneiras: a família certa (uma
        # portaria não tem articulado para codificar) e o âmbito que a aplicação
        # sabe ler (a Administração Pública ainda não).
        processavel = (fam in FAMILIAS_PROCESSAVEIS and mod_ambito.processavel(amb))
        rel, rel_alvo = relacao(fam, estruturado, por_resolver)
        saida.append({
            "nome_canonico": nome,
            "ficheiro_destino": destino,
            "ficheiro_origem": item.get("ficheiro", ""),
            "ano": item.get("ano") or "",
            "seq_anual": sequencial_bte(item) or "",
            "tipo_documento": tipo_normalizado(item.get("tipo")),
            "familia": fam,
            "processavel": "sim" if processavel else "nao",
            "ambito": amb,
            "ambito_origem": amb_origem,
            "cod_irct": item.get("cod_irct", ""),
            "acto_negociacao": acto_negociacao(item.get("cod_irct", "")),
            **_colunas_base(item, fam, copia),
            "bte_numero": item.get("num_bte") or "",
            "bte_data": (item.get("data_bte") or "")[:10],
            "pagina_inicio": p_ini if p_ini is not None else "",
            "pagina_fim": p_fim if p_fim is not None else "",
            "n_outorgantes": len(patronais) + len(sindicais),
            "outorgantes": "; ".join(patronais + sindicais),
            "relacao": rel,
            "relacao_alvo": rel_alvo,
            "avisos_projeto": "",        # preenchido em ligar_avisos()

            "altera_estruturado": "; ".join(
                f"{a['tipo']}.{a['data']}.{a['seq']}/{a['ano']}" for a in estruturado),
            "altera_por_resolver": "; ".join(por_resolver),
            "vide_em_vigor": item.get("em_vigor", ""),
            "materias_detectadas": "; ".join(materias),
            "sectores_a_classificar": "; ".join(sectores),
            "url_fonte": item.get("url", ""),
            "titulo": item.get("titulo", ""),
            "estado": ("metadado" if fam in FAMILIAS_SO_METADADO
                       else "por_confirmar" if not nome
                       else "recolhido" if processavel else "nao_processavel"),
            "avisos": " | ".join(avisos),
            **{c: "" for c in COLUNAS_EQUIPA},
        })
    return saida


def ligar_avisos(linhas_catalogo: list[dict]) -> list[dict]:
    """Passa os avisos de projeto para a coluna da portaria correspondente.

    Um aviso de projeto de portaria de extensão e a portaria que dele resulta
    apontam para a mesma convenção. É por aí que se ligam: mesmo `relacao_alvo`,
    e o aviso tem de ser anterior. Quando a portaria ainda não saiu, o aviso
    fica sem destino — é um facto sobre o ano, não um erro, e a linha do aviso
    mantém-se no catálogo para o registar.
    """
    avisos: dict[str, list[dict]] = {}
    for l in linhas_catalogo:
        if l.get("familia") in FAMILIAS_SO_METADADO and l.get("relacao_alvo"):
            avisos.setdefault(l["relacao_alvo"], []).append(l)
    if not avisos:
        return linhas_catalogo
    for l in linhas_catalogo:
        if l.get("familia") != "extensao":
            continue
        candidatos = avisos.get(l.get("relacao_alvo", ""), [])
        anteriores = [a for a in candidatos
                      if str(a.get("bte_data", "")) <= str(l.get("bte_data", ""))]
        l["avisos_projeto"] = "; ".join(
            f"{a['seq_anual']}/{a['ano']} ({a['bte_data']})" for a in anteriores)
    return linhas_catalogo


# Identidade de um documento entre regenerações: só campos que vêm do índice
# do BTE, nunca campos que a aplicação deriva (nome, siglas, âmbito, avisos),
# para que uma tabela de siglas nova ou uma migração de nomes não separem uma
# linha do trabalho que a equipa lá pôs. O ficheiro de origem sozinho não
# serve: o BTE numera os PDF por páginas (`00010004.pdf`) e o nome repete-se
# de boletim para boletim.
COLUNAS_IDENTIDADE = ("ano", "seq_anual", "bte_numero", "tipo_documento",
                      "ficheiro_origem", "url_fonte", "titulo")

# Estados que a aplicação escreve sozinha. Outro estado foi posto pela equipa.
ESTADOS_AUTOMATICOS = frozenset({"", "recolhido", "nao_processavel",
                                 "por_confirmar", "metadado"})

AVISO_ORFA = "já não consta dos índices lidos — verificar"
AVISO_REPETIDO = ("documento repetido no catálogo anterior ou nos índices — "
                  "colunas da equipa não repostas, verificar à mão")
# Avisos que a própria fusão escreve. São recalculados em cada corrida, para
# que um aviso que deixou de se aplicar não fique para sempre na linha.
AVISOS_DA_FUSAO = frozenset({AVISO_ORFA, AVISO_REPETIDO})


def _identidade(linha: dict) -> tuple | None:
    chave = tuple(str(linha.get(c) or "").strip() for c in COLUNAS_IDENTIDADE)
    return chave if any(chave) else None


def _nome(linha: dict) -> str | None:
    return (linha.get("nome_canonico") or "").strip() or None


def _avisar(linha: dict, aviso: str | None) -> None:
    """Tira os avisos da fusão de corridas anteriores e põe o atual, uma vez."""
    avisos = [a.strip() for a in (linha.get("avisos") or "").split(";")
              if a.strip() and a.strip() not in AVISOS_DA_FUSAO]
    if aviso:
        avisos.insert(0, aviso)
    linha["avisos"] = "; ".join(avisos)


def _tem_trabalho_da_equipa(linha: dict) -> bool:
    return (any((linha.get(c) or "").strip() for c in COLUNAS_EQUIPA)
            or (linha.get("estado") or "") not in ESTADOS_AUTOMATICOS)


def carregar_correspondencia(caminho: Path) -> dict[str, str]:
    """`nome_anterior;nome_novo;…` (de `cct.nomeacao --migrar`) → {antigo: novo}."""
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return {l["nome_anterior"]: l["nome_novo"]
                for l in csv.DictReader(f, delimiter=";")
                if l.get("nome_anterior") and l.get("nome_novo")}


def fundir(novas: list[dict], anterior: Path | None,
           correspondencia: dict[str, str] | None = None) -> list[dict]:
    """Repõe as colunas da equipa a partir de um catálogo anterior.

    Garante quatro propriedades, verificadas em `tests/test_esquema_adr0022.py`
    sobre centenas de cenários gerados ao acaso:

    1. **idempotência** — regenerar com os mesmos índices dá o mesmo ficheiro;
    2. **nada do trabalho da equipa se perde nem se duplica**;
    3. **o trabalho da equipa só é reposto no documento a que pertence**;
    4. **um documento que desaparece dos índices fica no catálogo**, assinalado.

    O algoritmo, por esta ordem:

    1. **Cópias.** Uma linha antiga sem trabalho da equipa, cujo documento
       (`COLUNAS_IDENTIDADE`) está nos índices atuais, é a cópia que a corrida
       anterior gerou: a linha nova substitui-a, e ela é posta de parte antes
       de qualquer decisão. É isto que torna a fusão idempotente — a corrida
       seguinte vê exatamente as mesmas linhas antigas que a anterior.
    2. **Identidade.** As restantes linhas antigas casam com as novas pelo
       documento. Uma para uma: as colunas da equipa passam para a nova. Mais do
       que uma de algum dos lados: não se escolhe às cegas; nada é reposto, e
       as antigas ficam, uma vez cada, assinaladas.
    3. **Nome.** O que sobrar casa pelo `nome_canonico`, com as mesmas regras e
       sem descartar nada. Apanha um título corrigido pela DGERT e, com
       `correspondencia`, a migração de nomes do ADR-0022.
    4. **Órfãs.** O que ainda sobrar do catálogo anterior é documento que
       desapareceu dos índices e fica, com aviso.

    Um documento repetido nos índices é sempre assinalado, haja ou não
    catálogo anterior.
    """
    contagem: dict = {}
    for l in novas:
        contagem[_identidade(l)] = contagem.get(_identidade(l), 0) + 1
    for l in novas:
        if _identidade(l) is not None and contagem[_identidade(l)] > 1:
            _avisar(l, AVISO_REPETIDO)
    if not anterior or not Path(anterior).exists():
        return novas
    correspondencia = correspondencia or {}
    with open(anterior, encoding="utf-8-sig", newline="") as f:
        antigas = list(csv.DictReader(f, delimiter=";"))
    for l in antigas:
        if l.get("nome_canonico") in correspondencia:
            l["nome_canonico"] = correspondencia[l["nome_canonico"]]

    # 1. cópias da corrida anterior
    identidades_novas = {k for k in contagem if k is not None}
    antigas_livres = {i for i, l in enumerate(antigas)
                      if _tem_trabalho_da_equipa(l)
                      or _identidade(l) not in identidades_novas}
    novas_livres = set(range(len(novas)))
    repetidas: list[int] = []                 # antigas mantidas por ambiguidade

    # 2. e 3. casar por identidade, depois por nome
    for chave_de in (_identidade, _nome):
        grupos_novas: dict = {}
        for i in sorted(novas_livres):
            if (k := chave_de(novas[i])) is not None:
                grupos_novas.setdefault(k, []).append(i)
        grupos_antigas: dict = {}
        for i in sorted(antigas_livres):
            if (k := chave_de(antigas[i])) is not None:
                grupos_antigas.setdefault(k, []).append(i)
        for k, ias in grupos_antigas.items():
            ins = grupos_novas.get(k)
            if not ins:
                continue
            if len(ins) == 1 and len(ias) == 1:
                nova, velha = novas[ins[0]], antigas[ias[0]]
                for c in COLUNAS_EQUIPA:
                    if velha.get(c):
                        nova[c] = velha[c]
                if (velha.get("estado") or "") not in ESTADOS_AUTOMATICOS:
                    nova["estado"] = velha["estado"]
            else:
                for i in ins:
                    _avisar(novas[i], AVISO_REPETIDO)
                repetidas.extend(ias)
            novas_livres.difference_update(ins)
            antigas_livres.difference_update(ias)

    # 4. o que sobra do catálogo anterior
    saida = list(novas)
    for i in sorted(repetidas):
        linha = {c: antigas[i].get(c, "") for c in COLUNAS}
        _avisar(linha, AVISO_REPETIDO)
        saida.append(linha)
    for i in sorted(antigas_livres):
        linha = {c: antigas[i].get(c, "") for c in COLUNAS}
        _avisar(linha, AVISO_ORFA)
        saida.append(linha)
    return saida


def escrever(linhas_catalogo: list[dict], saida: Path) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS, delimiter=";",
                           extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(linhas_catalogo)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="cct.catalogo",
        description="Gera o catálogo IRCT a partir dos índices do BTE.")
    p.add_argument("--indices", default=str(INDICES_OMISSAO),
                   help="pasta com os .xlsx de índice, ou um ficheiro")
    p.add_argument("--saida", required=True, help="CSV do catálogo a escrever")
    p.add_argument("--siglas", action="append", default=[],
                   help="CSV de siglas fixadas; repetível, o primeiro ganha")
    p.add_argument("--ambitos", help="CSV 'nome;ambito' de empregadores")
    p.add_argument("--esquema", default="rnc", choices=("rnc", ESQUEMA_2025))
    p.add_argument("--correspondencia",
                   help="CSV nome_anterior;nome_novo escrito por "
                        "`cct.nomeacao --migrar`: as colunas da equipa do catálogo "
                        "anterior passam para o nome novo (SPEC-0004, passo 4)")
    args = p.parse_args(argv)

    origem = Path(args.indices)
    ficheiros = sorted(origem.glob("*.xlsx")) if origem.is_dir() else [origem]
    if not ficheiros:
        raise SystemExit(f"Sem índices em {origem}")

    itens: list[dict] = []
    for f in ficheiros:
        itens.extend(ler_indice(f))
    if not itens:
        raise SystemExit("Os índices não têm nenhuma linha reconhecível — "
                         "confirmar que são índices do BTE")

    tabela: dict[str, str] = {}
    for caminho in args.siglas:
        for nome, s in carregar_siglas(Path(caminho)).items():
            tabela.setdefault(nome, s)
    voc = (mod_ambito.carregar_vocabulario(Path(args.ambitos)) if args.ambitos
           else mod_ambito.carregar_vocabulario())

    saida = Path(args.saida)
    correspondencia = (carregar_correspondencia(Path(args.correspondencia))
                       if args.correspondencia else None)
    catalogo = fundir(ligar_avisos(
        linhas(itens, tabela_siglas=tabela or None, vocabulario_ambito=voc,
               esquema=args.esquema)), saida, correspondencia)
    escrever(catalogo, saida)

    print(f"== Catálogo: {len(catalogo)} documentos → {saida}")
    por_familia: dict[str, int] = {}
    por_ambito: dict[str, int] = {}
    for l in catalogo:
        por_familia[l["familia"] or "por_classificar"] = \
            por_familia.get(l["familia"] or "por_classificar", 0) + 1
        por_ambito[l["ambito"]] = por_ambito.get(l["ambito"], 0) + 1
    print("  por família:")
    for f, n in sorted(por_familia.items()):
        print(f"    {f}: {n}" + ("" if f in FAMILIAS_PROCESSAVEIS
                                 else "   (não entra no pipeline temático)"))
    print("  por âmbito:")
    for a, n in sorted(por_ambito.items()):
        print(f"    {a}: {n}" + ("" if mod_ambito.processavel(a)
                                 else "   (não processável)"))
    print(f"  processáveis: {sum(1 for l in catalogo if l['processavel'] == 'sim')}")
    com_aviso = [l for l in catalogo if l["avisos"]]
    por_classificar = [l for l in catalogo if l["sectores_a_classificar"]]
    print(f"    com avisos: {len(com_aviso)}")
    print(f"    com sectores por classificar: {len(por_classificar)}")
    nomes = [l["nome_canonico"] for l in catalogo if l["nome_canonico"]]
    colisoes = {n for n in nomes if nomes.count(n) > 1}
    sem_nome = sum(1 for l in catalogo if not l["nome_canonico"])
    if sem_nome:
        print(f"    sem nome canónico (por confirmar): {sem_nome}")
    if colisoes:
        print("    COLISÕES DE NOME: " + ", ".join(sorted(colisoes)))
    return 1 if colisoes else 0


if __name__ == "__main__":
    raise SystemExit(main())
