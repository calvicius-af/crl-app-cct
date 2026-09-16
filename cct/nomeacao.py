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

from . import ambito as mod_ambito
from .localizador import _sem_acentos
from .recolha import (INTERVALO_PERSISTENCIA, RAIZ, REGISTO_OMISSAO, Registo,
                      sha256_ficheiro)

DESTINO_OMISSAO = RAIZ / "data" / "raw" / "bte"

# Os dois esquemas de nome que convivem no corpus. Ver ADR-0016.
#
#   pipeline  26_PR_003_BTE_31_ACRAL_CESP            o de 2025, ainda em uso
#   rnc       2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2
#
# O `rnc` é o do documento de gestão documental do Relatório da Negociação
# Coletiva, com um acrescento: o `_BTE_{NN}`, que o esquema publicado não tinha.
# Custa sete caracteres e é o que permite voltar do ficheiro ao boletim sem
# consultar o catálogo — e é o que `cct/localizador.py` e `cct/comparar.py`
# leem para emparelhar versões. Ver docs/rnc/README.md §5.1.
ESQUEMAS = ("pipeline", "rnc")
ESQUEMA_OMISSAO = "pipeline"

MAX_SIGLAS_RNC = 3     # as restantes ficam em "+N"

TOKEN_FAMILIA = {"convencao": "PR", "extensao": "PE",
                 "aviso": "AV", "adesao": "AA"}

# Esquema de 2025: tudo o que não é convenção ia para uma só pasta `extensoes/`,
# cujo único objetivo era ficar fora do `glob("*.pdf")` do pipeline.
SUBPASTA_FAMILIA = {"convencao": "", "extensao": "extensoes",
                    "aviso": "extensoes", "adesao": "extensoes"}

# Esquema RNC: cada família tem a sua pasta, e dentro dela o âmbito. Uma
# portaria de extensão e um acordo de adesão referem-se a uma convenção
# concreta, mas são actos de natureza diferente — a portaria é do Governo, a
# adesão é de uma parte — e nenhum dos dois tem o articulado que a codificação
# temática pressupõe. Juntá-los às convenções faria com que fossem codificados
# como se fossem uma, e isso não dá erro: dá números errados.
#
#   1_fontes/irct/convencoes/PRI/    ← o pipeline lê daqui
#   1_fontes/irct/extensoes/PRI/
#   1_fontes/irct/adesoes/PRI/
#   1_fontes/irct/avisos/PRI/
#
# Ver docs/rnc/README.md §5.7 e ADR-0018.
PASTA_FAMILIA = {"convencao": "convencoes", "extensao": "extensoes",
                 "adesao": "adesoes", "aviso": "avisos"}
PASTA_FAMILIA_DESCONHECIDA = "por_classificar"

# As famílias que o pipeline temático sabe processar. É a convenção e o que a
# substitui; tudo o resto é contexto, não corpus.
FAMILIAS_PROCESSAVEIS = frozenset({"convencao"})

ESTADOS_COM_FICHEIRO = {"descarregado", "ja_existente", "inalterado"}

MAX_NOME = 63          # limite de nome de documento do MaxQDA (RF-21)
MAX_SIGLA = 20
MIN_CHAVE_PARCIAL = 12   # ver a nota em sigla(), sobre correspondência parcial

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
        # Correspondência parcial, para apanhar as variações de pontuação e os
        # «e outros» que o índice acrescenta. Só com chaves longas, e ganha a
        # mais longa: com uma tabela de milhares de entradas, uma chave curta
        # encaixa por acaso dentro de meio registo e atribui a sigla errada em
        # silêncio — que é precisamente o erro que a tabela existe para evitar.
        melhor = max((k for k in tabela
                      if len(k) >= MIN_CHAVE_PARCIAL and k in chave),
                     key=len, default=None)
        if melhor:
            return tabela[melhor], None
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


def sequencial_bte(entrada: dict) -> int | None:
    """O «377» de `ID: 377/2026` — a posição do documento na série anual do BTE.

    É o que o esquema RNC usa como número sequencial, em vez do ordinal interno
    da aplicação: é o número pelo qual o documento é citado no próprio boletim e
    nas cadeias de alteração (`CCT-ALT.20250708.321/2025`), pelo que é o único
    que permite ligar um ficheiro ao que o índice diz sobre ele.
    """
    bruto = str(entrada.get("id_dgert") or "").strip()
    m = re.match(r"^\s*(\d+)\s*/\s*(\d{4})\s*$", bruto)
    if m:
        return int(m.group(1))
    return int(m.group(0)) if (m := re.match(r"^\d+$", bruto)) else None


def tipo_normalizado(tipo: str) -> str:
    """`CCT-ALT-RECT` a partir do que vier no índice; `SEMTIPO` se vier vazio."""
    limpo = re.sub(r"[^A-Z0-9-]", "", _sem_acentos(tipo or "").upper())
    limpo = re.sub(r"-{2,}", "-", limpo).strip("-")
    return limpo or "SEMTIPO"


def siglas_outorgantes(entrada: dict, tabela: dict[str, str] | None = None,
                       maximo: int = MAX_SIGLAS_RNC) -> tuple[list[str], int, list[str]]:
    """Siglas dos outorgantes, pela ordem do índice, e quantos ficaram de fora.

    O índice do BTE lista o lado patronal primeiro, o que dá a ordem natural
    «empregador-sindicatos» que a equipa usa para procurar. Ao contrário do
    esquema antigo, não se escolhe um de cada lado: levam-se os primeiros
    `maximo` e conta-se o resto.
    """
    avisos: list[str] = []
    nomes = [n.strip() for n in re.split(r"[;\n]", entrada.get("outorgantes") or "")
             if n.strip()]
    if not nomes:
        nomes = _partes_do_titulo(entrada.get("titulo", ""))
        if nomes:
            avisos.append("outorgantes lidos do título — confirmar")
    if not nomes:
        return [], 0, avisos + ["sem outorgantes no índice nem no título"]
    escolhidas: list[str] = []
    for nome in nomes[:maximo]:
        s, aviso = sigla(nome, tabela)
        if aviso:
            avisos.append(aviso)
        if s:
            escolhidas.append(s)
    return escolhidas, max(0, len(nomes) - len(escolhidas)), avisos


def _nome_rnc(entrada: dict, ordinal: int, tabela: dict[str, str] | None,
              vocabulario_ambito: dict[str, str] | None) -> tuple[str, list[str]]:
    """{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}"""
    avisos: list[str] = []
    ano = int(entrada.get("ano") or 0)
    num_bte = int(entrada.get("num_bte") or 0)

    seq = sequencial_bte(entrada)
    if seq is None:
        seq = ordinal
        avisos.append("sem «ID: nnn/aaaa» no índice — usado o ordinal interno "
                      f"({ordinal}); o número não corresponde ao do boletim")

    tipo = tipo_normalizado(entrada.get("tipo"))
    if tipo == "SEMTIPO":
        avisos.append("tipo de documento vazio no índice — confirmar")

    cod = re.sub(r"\D", "", str(entrada.get("cod_irct") or ""))
    if not cod:
        cod = "0"
        avisos.append("sem COD: (IRCT) no índice — a série da convenção fica "
                      "por identificar")

    patronais, _sindicais = separar_outorgantes(entrada.get("outorgantes", ""),
                                                entrada.get("titulo", ""))
    amb, origem, aviso_amb = mod_ambito.classificar(
        patronais[0] if patronais else entrada.get("titulo", ""),
        entrada.get("tipo", ""), vocabulario_ambito)
    if aviso_amb:
        avisos.append(aviso_amb)
    entrada.setdefault("nomeacao", {}).update({"ambito": amb,
                                               "ambito_origem": origem})

    siglas, restantes, avisos_siglas = siglas_outorgantes(entrada, tabela)
    avisos.extend(avisos_siglas)
    if not siglas:
        siglas = [_camel(entrada.get("titulo", ""))]
        avisos.append("nome derivado do título — confirmar")

    prefixo = f"{ano:04d}_{amb}_{seq:03d}_{tipo}_{cod}_BTE_{num_bte:02d}_"
    cauda = f"+{restantes}" if restantes else ""
    nome = prefixo + "-".join(siglas) + cauda
    if len(nome) > MAX_NOME:            # encurta as siglas, nunca o prefixo
        folga = MAX_NOME - len(prefixo) - len(cauda) - (len(siglas) - 1)
        por_sigla = max(3, folga // len(siglas))
        nome = prefixo + "-".join(s[:por_sigla] for s in siglas) + cauda
        avisos.append(f"nome encurtado para caber em {MAX_NOME} caracteres")
    return nome[:MAX_NOME], avisos


def nome_documento(entrada: dict, ordinal: int,
                   tabela: dict[str, str] | None = None, *,
                   esquema: str = ESQUEMA_OMISSAO,
                   vocabulario_ambito: dict[str, str] | None = None
                   ) -> tuple[str, list[str]]:
    """Compõe o nome (sem extensão) e devolve os avisos que exigem confirmação."""
    if esquema not in ESQUEMAS:
        raise ValueError(f"esquema de nome desconhecido: {esquema!r} "
                         f"(conhecidos: {', '.join(ESQUEMAS)})")
    if esquema == "rnc":
        return _nome_rnc(entrada, ordinal, tabela, vocabulario_ambito)
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


COLUNAS_NOME = ("nome", "nome_completo", "denominacao",
                "denominacao_da_organizacao", "organizacao")
COLUNAS_SIGLA = ("sigla", "acronimo", "sigla_canonica")
COLUNA_ORIGEM = "origem_sigla"

# Uma sigla que o próprio `_camel()` inventou não é uma sigla confirmada: dá
# «Motoristas» onde a equipa escreveria «SNM». Se entrasse na tabela, calava o
# aviso de «confirmar» e transformava um palpite num facto. Fica no ficheiro,
# para se ver o que falta, mas não é carregada — promove-se editando a coluna
# `origem_sigla` para `equipa` depois de alguém a ter visto.
ORIGENS_IGNORADAS = frozenset({"recurso"})


def carregar_siglas(caminho: Path) -> dict[str, str]:
    """Tabela de siglas fixadas pela equipa → {nome normalizado: sigla}.

    Aceita dois formatos, para que a mesma bandeira `--siglas` sirva tanto a
    lista curta que alguém escreve à mão como o `vocabularios/
    siglas_organizacoes.csv` gerado do registo da DGERT:

    * **sem cabeçalho** — `nome;sigla`, as duas primeiras colunas;
    * **com cabeçalho** — as colunas são encontradas pelo nome (`denominacao`
      e `sigla`, entre outros), seja qual for a ordem em que venham.

    Separador `;`, UTF-8 com ou sem BOM. Linhas incompletas são saltadas em
    silêncio; um ficheiro cujo cabeçalho não tenha nenhuma coluna reconhecível
    é tratado como sendo do formato sem cabeçalho.
    """
    import csv

    tabela: dict[str, str] = {}
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        linhas = [l for l in csv.reader(f, delimiter=";") if l and l[0].strip()]
    if not linhas:
        return tabela

    i_nome, i_sigla = 0, 1
    cabecalho = [re.sub(r"[^a-z0-9]+", "_", _sem_acentos(c).strip().lower()).strip("_")
                 for c in linhas[0]]
    tem_cabecalho = any(c in COLUNAS_NOME for c in cabecalho)
    if tem_cabecalho:
        i_nome = next(i for i, c in enumerate(cabecalho) if c in COLUNAS_NOME)
        candidatos = [i for i, c in enumerate(cabecalho) if c in COLUNAS_SIGLA]
        if not candidatos:
            return tabela
        i_sigla = candidatos[0]
        linhas = linhas[1:]
    i_origem = (cabecalho.index(COLUNA_ORIGEM)
                if tem_cabecalho and COLUNA_ORIGEM in cabecalho else None)

    for linha in linhas:
        if max(i_nome, i_sigla) >= len(linha):
            continue
        # A origem pode vir composta (`recurso+desambiguada`): compara-se a
        # parte antes do `+`, que é de onde a sigla saiu. Comparar a cadeia
        # inteira deixava passar exatamente as siglas que isto existe para
        # travar — e sem dar erro nenhum.
        if (i_origem is not None and i_origem < len(linha)
                and linha[i_origem].strip().lower().split("+")[0]
                in ORIGENS_IGNORADAS):
            continue
        nome = _sem_acentos(linha[i_nome]).strip().lower()
        valor = _limpar_sigla(linha[i_sigla])[:MAX_SIGLA]
        if not nome or not valor:
            continue
        if not tem_cabecalho and nome in COLUNAS_NOME:
            continue                       # cabeçalho não declarado
        tabela.setdefault(nome, valor)
    return tabela


def nomear(registo: Registo, destino: Path, *, aplicar: bool = False,
           tabela: dict[str, str] | None = None,
           familias=("convencao", "extensao", "aviso", "adesao"),
           aceitar_heuristicas: bool = False,
           esquema: str = ESQUEMA_OMISSAO,
           vocabulario_ambito: dict[str, str] | None = None) -> dict:
    """Atribui nomes e, com `aplicar=True`, copia os PDFs para o destino.

    Um documento cujo nome tenha avisos de `nome_documento()` (sigla
    derivada por heurística, outorgante em falta, nome do título, nome
    encurtado) fica em estado `por_confirmar` e **não é escrito**, mesmo com
    `aplicar=True` — a confirmação humana que a spec promete tem de acontecer
    antes de o ficheiro existir e o ordinal ficar permanente, não depois.
    `aceitar_heuristicas=True` desliga esta proteção, para quem decide
    conscientemente aceitar o risco (ex.: uma corrida em lote já revista).

    Com `esquema="rnc"` os ficheiros são arrumados em subpastas por âmbito
    (`PRI/`, `SPE/`, `APU/`), para que «não conseguimos processar isto» deixe de
    ser uma nota num documento e passe a ser a estrutura das pastas.
    """
    if esquema not in ESQUEMAS:
        raise ValueError(f"esquema de nome desconhecido: {esquema!r} "
                         f"(conhecidos: {', '.join(ESQUEMAS)})")
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
            nome, avisos = nome_documento(e, nomeacao["ordinal"], tabela,
                                          esquema=esquema,
                                          vocabulario_ambito=vocabulario_ambito)
            nomeacao = e["nomeacao"]      # _nome_rnc pode ter registado o âmbito
            avisos_heuristica = list(avisos)   # antes do aviso de par repetido, abaixo —
                                               # esse é informativo, não indica nome errado
            partes = "_".join(nome.split("_")[5 if esquema == "pipeline" else 7:])
            vistos.setdefault((e.get("ano"), partes), []).append(nome)
            if len(vistos[(e.get("ano"), partes)]) > 1:
                avisos.append("outro documento do mesmo par de outorgantes neste ano: "
                              + ", ".join(vistos[(e.get("ano"), partes)][:-1]))
            if esquema == "rnc":
                pasta = (destino / f"bte_{e['ano']}"
                         / PASTA_FAMILIA.get(e.get("familia"),
                                             PASTA_FAMILIA_DESCONHECIDA)
                         / nomeacao.get("ambito", mod_ambito.OMISSAO))
            else:
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
    p.add_argument("--siglas", action="append", default=[],
                   help="CSV de siglas fixadas ('nome;sigla', ou o "
                        "vocabularios/siglas_organizacoes.csv). Repetível: em "
                        "caso de conflito ganha o primeiro ficheiro indicado.")
    p.add_argument("--esquema", choices=ESQUEMAS, default=ESQUEMA_OMISSAO,
                   help="esquema de nome: 'pipeline' (o de 2025) ou 'rnc' "
                        "(o da gestão documental do RNC)")
    p.add_argument("--ambitos", help="CSV 'nome;ambito' de empregadores com "
                                     "âmbito conhecido (só com --esquema rnc)")
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
    tabela: dict[str, str] = {}
    for caminho in args.siglas:
        for nome, s in carregar_siglas(Path(caminho)).items():
            tabela.setdefault(nome, s)      # o primeiro ficheiro ganha
    voc_ambito = (mod_ambito.carregar_vocabulario(Path(args.ambitos))
                  if args.ambitos else mod_ambito.carregar_vocabulario())
    resumo = nomear(registo, Path(args.destino), aplicar=args.aplicar,
                    tabela=tabela or None,
                    familias=tuple(f.strip() for f in args.familias.split(",") if f.strip()),
                    aceitar_heuristicas=args.aceitar_heuristicas,
                    esquema=args.esquema, vocabulario_ambito=voc_ambito)
    print(texto_resumo(resumo, aplicar=args.aplicar))
    return 1 if resumo["problemas"] else 0


if __name__ == "__main__":
    raise SystemExit(main())


def familia_do_nome(nome: str) -> str | None:
    """A família documental que um nome de ficheiro declara, ou `None`.

    Lê os dois esquemas: o token da família no esquema de 2025
    (`26_PE_001_BTE_31_…` → `extensao`) e o tipo do BTE no esquema RNC
    (`2026_PRI_401_PE_…` → `extensao`). Serve para que quem consome uma pasta
    de PDF possa recusar o que não devia lá estar, em vez de o processar.
    """
    from .localizador import RE_DOC_ID, interpretar_nome_rnc
    from .recolha import familia

    meta = interpretar_nome_rnc(nome)
    if meta:
        return familia(meta["tipo"])
    m = RE_DOC_ID.match(nome.strip())
    if not m:
        return None
    token = nome.split("_")[1]
    for fam, tok in TOKEN_FAMILIA.items():
        if tok == token:
            return fam
    return None
