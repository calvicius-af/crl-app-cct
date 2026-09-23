"""Atribuição de siglas sem duplicados, por regra e não por decisão de cada pessoa.

O problema. Das organizações do registo da DGERT, mais de uma centena partilha a
mesma sigla com outra organização genuinamente diferente. Alguém tem de decidir
quem fica com a sigla curta e como se chamam as outras — e se cada pessoa
decidir à sua maneira, o mesmo sindicato aparece como `SNM` num ficheiro e como
`SNMot` noutro, e a série parte-se.

A regra. Uma escada de candidatos, percorrida por ordem até encontrar um que
esteja livre. É determinística: a mesma entrada dá sempre a mesma saída,
independentemente de quem corre o script e por que ordem.

    1. SIGLA                         SNM
    2. SIGLA + palavra distintiva    SNMotoristas
    3. SIGLA + concelho da sede      SNMLisboa
    4. SIGLA + 2.ª palavra
    5. SIGLA + código DGERT          SNM14023      ← garantidamente único

A escada só é percorrida quando há mesmo conflito. Uma sigla que só uma
organização usa fica como está — o script não corrige o registo da DGERT, só
resolve duplicados. Quem fica com o degrau 1 não é quem chegou primeiro ao
script: é a **linhagem com o código DGERT mais baixo**, que é a mais antiga no
registo. Não depende da ordem de processamento, e por isso não muda de uma
corrida para a outra.

E, acima de tudo isto, **uma sigla já atribuída não se reatribui**: o construtor
lê o vocabulário anterior e fixa o que lá está, pela mesma razão por que um nome
de ficheiro não muda depois de atribuído.

Linhagens e gerações. O SITESE mudou de nome seis vezes e continua a ser o
SITESE: gerações da mesma organização partilham a sigla, e não são conflito. A
linhagem lê-se dos dois primeiros componentes do código DGERT (`1.402.1` e
`1.402.3` são a mesma; `1.402.1` e `5.10.0` não são).

Ver docs/rnc/README.md §5.5-b e ADR-0017.
"""
import re

from .localizador import _sem_acentos
from .nomeacao import (FORMA_JURIDICA, GENERICOS, LIGACOES, MAX_SIGLA, _camel,
                       _limpar_sigla)

# Palavras que aparecem em quase todas as denominações de um mesmo ramo e que,
# por isso, distinguem pouco. Não são excluídas — são **despreferidas**: usam-se
# só quando não há outra palavra disponível. É o que faz com que a Associação
# Comercial de Espinho fique `ACEEspinho` e não `ACEComercial`.
QUALIFICADORES_FRACOS = {
    "comercial", "comerciais", "industrial", "industriais", "empresarial",
    "empresariais", "empresas", "empresa", "servicos", "servico", "regional",
    "regionais", "distrital", "distritais", "concelhia", "concelhias",
    "geral", "gerais", "norte", "sul", "centro", "outros", "outras",
    "concelhos", "concelho", "regiao", "zona", "area", "sector", "setor",
    "actividade", "atividade", "actividades", "atividades", "democratico",
    "democratica", "independente", "independentes", "livre", "livres",
}


def linhagem(codigo_dgert: str) -> str:
    """`1.402.1` → `1.402`. Gerações da mesma organização partilham a linhagem."""
    partes = str(codigo_dgert or "").split(".")
    return ".".join(partes[:2]) if len(partes) >= 2 else (partes[0] if partes else "")


def _ordem(codigo_dgert: str) -> tuple:
    """Chave de ordenação numérica do código DGERT, para «o mais antigo ganha»."""
    return tuple(int(p) if p.isdigit() else 0
                 for p in str(codigo_dgert or "0").split("."))


def palavras_distintivas(denominacao: str) -> list[str]:
    """As palavras da denominação que servem para distinguir, por preferência.

    Descarta ligações e formas jurídicas, e põe no fim — sem as remover — as que
    aparecem em meio ramo de actividade. A ordem do resultado é a ordem em que a
    escada as vai experimentar.
    """
    fortes: list[str] = []
    fracas: list[str] = []
    for bruto in re.split(r"[^\wÀ-ÿ]+", _sem_acentos(denominacao or "")):
        if len(bruto) < 3:
            continue
        baixo = bruto.lower()
        if baixo in LIGACOES or baixo in FORMA_JURIDICA or baixo in GENERICOS:
            continue
        # Sempre capitalizada, seja qual for a caixa da origem: o registo da
        # DGERT está todo em maiúsculas, e `SNMOTORISTAS` lê-se pior do que
        # `SNMotoristas`. O que importa é ser sempre a mesma coisa.
        palavra = bruto.capitalize()
        (fracas if baixo in QUALIFICADORES_FRACOS else fortes).append(palavra)
    vistos: dict[str, None] = {}
    for p in fortes + fracas:
        vistos.setdefault(p, None)
    return list(vistos)


# Quando `base + sufixo` não cabe, encurta-se a **base**, não o sufixo: o sufixo
# é a parte que distingue, e cortá-lo devolvia `COMERCIALCONCELHOeir` — que já
# não diz Oeiras nem se distingue de Oliveira. Guardam-se pelo menos estes
# caracteres de cada lado, e só se corta o sufixo se nem assim couber.
MIN_BASE = 6
MAX_SUFIXO = 12

# A sobreposição (`SNM` + `Motoristas` → `SNMotoristas`) só se aplica a bases
# curtas, que são as siglas a sério. Numa base longa — as que o `_camel()`
# fabrica para quem não tem acrónimo no registo — comia o princípio da palavra
# que distingue: `COMERCIALCONCELHO` + `Oeiras` dava `COMERCIALCONCELeiras`,
# que já não diz Oeiras e não se distingue de Oliveira.
MAX_BASE_SOBREPOSICAO = 8
MAX_SOBREPOSICAO = 3


def _juntar(base: str, sufixo: str) -> str:
    """`SNM` + `Motoristas` → `SNMotoristas`, dentro do limite do MaxQDA.

    Se a base já termina com o princípio do sufixo, não se repete a sobreposição:
    é o que transforma `SNM` + `Motoristas` em `SNMotoristas` e não em
    `SNMMotoristas`. A sobreposição é procurada da mais longa para a mais curta,
    e só conta quando é o **fim** da base a coincidir com o **princípio** do
    sufixo.
    """
    base = _limpar_sigla(base)
    sufixo = _limpar_sigla(sufixo)
    if not sufixo:
        return base[:MAX_SIGLA]
    if len(base) <= MAX_BASE_SOBREPOSICAO:
        for n in range(min(MAX_SOBREPOSICAO, len(base), len(sufixo) - 1), 0, -1):
            if base[-n:].upper() == sufixo[:n].upper():
                sufixo = sufixo[n:]
                break
    sufixo = sufixo[:MAX_SUFIXO]
    if len(base) + len(sufixo) > MAX_SIGLA:
        base = base[:max(MIN_BASE, MAX_SIGLA - len(sufixo))]
    return (base + sufixo)[:MAX_SIGLA]


def candidatos(base: str, denominacao: str, concelho: str = "",
               codigo_dgert: str = "") -> list[str]:
    """A escada de candidatos, por ordem. O último é sempre único."""
    base = _limpar_sigla(base) or _camel(denominacao)
    escada = [base[:MAX_SIGLA]]
    palavras = palavras_distintivas(denominacao)
    if palavras:
        escada.append(_juntar(base, palavras[0]))
    if concelho:
        escada.append(_juntar(base, _limpar_sigla(
            _sem_acentos(concelho).strip().capitalize())))
    if len(palavras) > 1:
        escada.append(_juntar(base, palavras[0] + palavras[1]))
    codigo = re.sub(r"\D", "", str(codigo_dgert or ""))
    escada.append((base[:MAX_SIGLA - len(codigo)] + codigo)[:MAX_SIGLA] if codigo
                  else base[:MAX_SIGLA])
    # Sem duplicados e sem vazios, preservando a ordem.
    return [c for c in dict.fromkeys(escada) if c]


def atribuir(organizacoes: list[dict],
             fixadas: dict[tuple[str, str], str] | None = None
             ) -> dict[tuple[str, str], str]:
    """Resolve os duplicados → `{(linhagem, sigla_base): sigla_final}`.

    `organizacoes` são dicionários com `codigo_dgert`, `denominacao`,
    `sigla_base` e, opcionalmente, `concelho` e `ultima_atividade`. `fixadas`
    são atribuições anteriores, com a mesma chave, que não se mexem.

    **Só se mexe no que colide.** Uma sigla que só uma linhagem usa fica como
    está, mesmo que a organização tenha mudado de nome pelo caminho: o registo
    da DGERT diz que aquela geração se chamava A.A.N.P. e não cabe a este
    script corrigi-lo. O que não se tolera é a mesma sigla em duas linhagens
    diferentes — aí a mais antiga fica com ela e as outras sobem a escada.

    A unicidade é verificada sem distinguir maiúsculas de minúsculas:
    `SNMotoristas` e `SNMOTORISTAS` são o mesmo ficheiro no Windows e no macOS,
    e dois documentos com o mesmo nome perdem-se um ao outro.
    """
    fixadas = dict(fixadas or {})

    # Uma reivindicação é um par (linhagem, sigla que essa linhagem pediu).
    # Duas gerações da mesma organização com o mesmo acrónimo são uma só
    # reivindicação; com acrónimos diferentes são duas, e ambas podem viver.
    reivindicacoes: dict[tuple[str, str], list[dict]] = {}
    for o in organizacoes:
        chave = (linhagem(o["codigo_dgert"]), _limpar_sigla(o.get("sigla_base", ""))
                 or _camel(o["denominacao"]))
        reivindicacoes.setdefault(chave, []).append(o)

    # Dentro de uma reivindicação manda a geração com atividade mais recente:
    # é a que melhor descreve a organização, e é dela que sai a escada.
    representante = {
        chave: max(grupo, key=lambda o: (str(o.get("ultima_atividade") or ""),
                                         _ordem(o["codigo_dgert"])))
        for chave, grupo in reivindicacoes.items()}

    # Quantas linhagens distintas pedem cada sigla. Uma só → não há conflito.
    linhagens_por_sigla: dict[str, set[str]] = {}
    for lin, base in reivindicacoes:
        linhagens_por_sigla.setdefault(base.upper(), set()).add(lin)

    atribuidas: dict[tuple[str, str], str] = {}
    usadas: dict[str, tuple[str, str]] = {}

    def reservar(chave, sigla):
        atribuidas[chave] = sigla
        usadas[sigla.upper()] = chave

    for chave, sigla in fixadas.items():
        if chave in reivindicacoes and sigla and sigla.upper() not in usadas:
            reservar(chave, sigla)

    # Primeiro as que não colidem: ficam com o que pediram, sem alteração.
    for chave in reivindicacoes:
        if chave in atribuidas:
            continue
        base = chave[1]
        if len(linhagens_por_sigla[base.upper()]) == 1 and base.upper() not in usadas:
            reservar(chave, base[:MAX_SIGLA])

    # Depois as que colidem, da linhagem mais antiga para a mais recente: é o
    # que faz com que o resultado não dependa da ordem de chegada.
    for chave in sorted((c for c in reivindicacoes if c not in atribuidas),
                        key=lambda c: (_ordem(c[0]), c[1])):
        o = representante[chave]
        for candidato in candidatos(chave[1], o["denominacao"],
                                    o.get("concelho", ""), o["codigo_dgert"]):
            if candidato.upper() not in usadas:
                reservar(chave, candidato)
                break
        else:                       # a escada acabou sem candidato livre
            n, base = 2, chave[1][:MAX_SIGLA - 2]
            while f"{base}{n}".upper() in usadas:
                n += 1
            reservar(chave, f"{base}{n}")
    return atribuidas
