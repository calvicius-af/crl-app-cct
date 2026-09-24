"""Extrator Fase 1: PDF do BTE → doc.json + texto plano.

Evolui o preprocessador V2 com as correções pedidas no gate da Fase 0:
- junção de linhas que não pára em maiúsculas (só pontuação forte ou
  marcadores estruturais justificam manter a quebra);
- rótulo de cláusula/capítulo fundido com o título numa só linha;
- hierarquia capítulo/secção/cláusula/anexo/artigo com nós-pai.

O texto final é uma sequência de "folhas" contíguas (preâmbulo, cabeçalhos
de capítulo/secção/anexo, cláusulas, artigos) cuja concatenação reconstrói
o texto na íntegra (propriedade zero-perda).
"""
import re
from collections import Counter
from pathlib import Path

from .mobiliario import e_mobiliario

RE_CAPITULO = re.compile(r"^(?:CAP[IÍ]TULO|T[IÍ]TULO)\s+([IVXLCD]+|\d+)\b(.*)$")
RE_SECCAO = re.compile(r"^SEC[ÇC][AÃ]O\s+([IVXLCD]+|\d+)\b(.*)$", re.IGNORECASE)
RE_ANEXO = re.compile(r"^ANEXO\s+([IVXLCD]+|\d+)?\b(.*)$")
# numeração por extenso: só designadores a sério. Qualquer palavra servia
# antes, o que transformava o título do CAPÍTULO XV do AguasNorte
# ("Cláusula geral e transitória") numa cláusula vazia — mas restringir só
# a ordinais deixava cair "Artigo único"/"Cláusula única", que é redação
# corrente quando o instrumento tem um só artigo (EMARP 2025, anexo I)
_ORDINAL = (r"(?:primeir|segund|terceir|quart|quint|sext|s[eé]tim|oitav|non"
            r"|d[eé]cim|vig[eé]sim|trig[eé]sim|quadrag[eé]sim|quinquag[eé]sim"
            r"|sexag[eé]sim|sept?uag[eé]sim|octog[eé]sim|nonag[eé]sim"
            r"|cent[eé]sim)[oa]")
_UNICO = r"[úu]nic[oa]"
# designadores de posição, em vez de número: nas revisões parciais o BTE abre
# com "Cláusula prévia Âmbito de revisão", que fixa o que a revisão altera.
# Lista fechada, pela mesma razão que levou a restringir os ordinais: com
# "qualquer palavra" a seguir, o título do CAPÍTULO XV do AguasNorte
# ("Cláusula geral e transitória") voltava a virar uma cláusula vazia.
# O guarda final exige fim de linha ou uma maiúscula a seguir (o título da
# cláusula): sem ele, "previa" sem acento é a forma verbal de "prever" e uma
# linha de prosa passaria a cabeçalho. O (?-i:…) é preciso porque o grupo da
# numeração é aplicado dentro de (?i:…), que tornaria [A-ZÀ-Ú] inútil
_DESIGNADOR = r"(?:pr[ée]vi[oa]|preliminar)(?=\s*$|\s+(?-i:[A-ZÀ-Ú«(]))"
# "12.ª", "16.ª-A", "décima segunda", "único", "prévia"
_NUMERACAO = (rf"\d+\.?[ªº]?(?:-[A-Z])?|{_UNICO}|{_DESIGNADOR}"
              rf"|{_ORDINAL}(?:\s+{_ORDINAL})?")
# a palavra-chave tem de vir capitalizada: no BTE os cabeçalhos são
# "Cláusula 1.ª" ou "CLÁUSULA 1.ª", nunca minúsculos. Com IGNORECASE, uma
# remissão partida pelo PDF ("… nos termos do\nartigo 253.º do Código do
# Trabalho…") virava um nó falso que roubava o corpo à cláusula real —
# 4 casos nos 6 documentos de 2025, um deles com 3746 caracteres.
# A numeração continua indiferente a maiúsculas (grupo com (?i:…)).
RE_CLAUSULA = re.compile(
    rf"^(?:Cl[aá]usula|CL[AÁ]USULA)\s+((?i:{_NUMERACAO}))\s*(.*)$")
RE_ARTIGO = re.compile(
    rf"^(?:Artigo|ARTIGO)\s+((?i:{_NUMERACAO}))\s*(.*)$")

_RE_HEADINGS = [
    ("capitulo", RE_CAPITULO),
    ("seccao", RE_SECCAO),
    ("anexo", RE_ANEXO),
    ("clausula", RE_CLAUSULA),
    ("artigo", RE_ARTIGO),
]

# marcadores que justificam manter a quebra de linha antes deles
_MARCADOR_LISTA = r"\d+\s*[-–—.)]|[a-z]\)|[ivxl]+\)|[-–—•§]\s?"
# "Declaração" (ISSUE-0015, ponto 3): quando uma parte assina em representação
# de outras, o PDF traz uma declaração própria a identificá-las — sem isto,
# cola-se ao nome do signatário anterior, como se fosse o mesmo bloco
_MARCADOR_ESTRUTURAL = (r"Cl[aá]usula\s|Artigo\s|CAP[IÍ]TULO\s|SEC[ÇC][AÃ]O\s"
                        r"|ANEXO\b|NOTA\b|Declara[çc][ãa]o\b")
RE_MARCADOR = re.compile(
    rf"^(?:{_MARCADOR_LISTA}|{_MARCADOR_ESTRUTURAL})", re.IGNORECASE)
# só os de lista: uma linha que comece por "Cláusula" mas não seja um
# cabeçalho a sério ainda pode ser o título do cabeçalho anterior
RE_MARCADOR_LISTA = re.compile(rf"^(?:{_MARCADOR_LISTA})", re.IGNORECASE)
# pontuação forte, tolerando o fecho de parêntesis/aspas que a segue:
# "(Valores em euros.)" termina a frase tanto como "Valores em euros."
RE_PONTUACAO_FORTE = re.compile(r"""[.!?:;][)\]»”"']*\s*$""")
# ordinal separado do número pelo PDF: "Artigo 1. º", "12. º ano"
RE_ORDINAL_SEPARADO = re.compile(r"(\d)\s*\.\s+([ºª])")
# número de parágrafo que perdeu o separador: "3São considerados…" (o PDF
# tem "3- São"); exige maiúscula a seguir para não tocar em "12.º" ou "2025".
# A maiúscula sozinha basta — não se exige uma minúscula a seguir a ela, para
# apanhar também siglas/palavras de uma letra coladas ao número (ISSUE-0016,
# ponto 7: "3A EMEM deve…", em que "A" fica isolado antes do espaço)
RE_NUMERO_SEM_SEPARADOR = re.compile(r"(?m)^(\d+(?:\.\d+)?)(?=[A-ZÀ-Ú])")
# fim do bloco de título de uma convenção: o BTE fecha-o sempre com o
# subtipo oficial, e o que vier a seguir já é o corpo do documento
RE_FIM_TITULO_CONVENCAO = re.compile(
    r"(?:revis[ãa]o\s+(?:global|parcial)"
    r"|altera[çc][ãa]o\s+salarial(?:\s+e\s+outras)?"
    r"|(?:e\s+)?texto\s+consolidado"
    r"|acordo\s+de\s+ades[ãa]o"
    r"|1\.?[ªa]\s+conven[çc][ãa]o)\s*$", re.IGNORECASE)
# o bloco de título vive no cabeçalho do documento; a regra acima só lá
# se aplica, para não partir frases do corpo que acabem nas mesmas palavras
LINHAS_DO_CABECALHO = 20
# continuação de enumeração de alíneas partida pelo PDF: "b) e c) do número…"
# (minúscula ou conjunção após o parêntesis — uma alínea real começa por maiúscula)
RE_ALINEA_CONTINUACAO = re.compile(r"^[a-z]\)\s+(?:e\b|ou\b|[a-zà-ú])")
RE_ASSINATURA = re.compile(r"^(Pel[ao]s?\s|Depositado em\b|Pel['´]\s?)", re.IGNORECASE)
# data de outorga por extenso: "Lisboa, 12 de maio de 2025."
RE_DATA_OUTORGA = re.compile(
    r"^[A-ZÀ-Ú][\wà-ÿ\s]*,\s+\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}\s*\.?\s*$")
RE_MARCA_CONSOLIDADO = re.compile(r"^Texto consolidado\b")
RE_PREAMBULO_LINHA = re.compile(r"^Pre[âa]mbulo\s*$", re.IGNORECASE)

# sentinelas internas que delimitam tabelas durante a normalização
MARCA_TABELA_INI = "\x02TABELA"
MARCA_TABELA_FIM = "\x03TABELA"
# Fronteira entre as duas colunas de uma página. Só existe entre a extração da
# página e a remoção do mobiliário, que a usa para saber onde começa e acaba
# cada coluna, e a retira. Nunca chega ao texto final.
MARCA_COLUNA = "\x04COLUNA"


def _e_cabecalho(linha: str) -> bool:
    return (any(rx.match(linha) for _, rx in _RE_HEADINGS)
            or bool(RE_PREAMBULO_LINHA.match(linha)))


def juntar_linhas(texto: str) -> str:
    """Une quebras de linha a meio de frase.

    Mantém a quebra apenas quando a linha atual termina em pontuação forte,
    a linha atual ou a seguinte é um cabeçalho estrutural, ou a seguinte
    começa com marcador de lista/número. Ao contrário do V2, uma maiúscula
    no início da linha seguinte NÃO impede a junção (feedback do gate F0).
    """
    linhas = texto.split("\n")
    resultado: list[str] = []
    protegidas: set[int] = set()  # linhas de título — não recebem junções
    em_tabela = False
    for linha in linhas:
        atual = linha.rstrip()
        if atual == MARCA_TABELA_INI:
            em_tabela = True
            resultado.append(atual)
            continue
        if atual == MARCA_TABELA_FIM:
            em_tabela = False
            resultado.append(atual)
            continue
        if em_tabela:
            resultado.append(atual)
            continue
        if not resultado or not resultado[-1] or resultado[-1] == MARCA_TABELA_FIM:
            resultado.append(atual)
            continue
        anterior = resultado[-1]
        # linha curta imediatamente após cabeçalho = título ("Âmbito").
        # O limite é 90, o mesmo de `_titulo_candidato` (ISSUE-0017): um
        # limite mais apertado aqui, sem razão para ser diferente, fundia
        # títulos legítimos com o corpo só por terem mais de 60 caracteres
        # ("Organização de serviços de segurança, higiene e saúde no
        # trabalho", com 65, virava início da Cláusula 68.ª sem título).
        # A vírgula final continua a excluir: um título não deixa a frase a
        # meio, ao contrário do início de um parágrafo de corpo (memo 23:
        # "Cumpre … qualquer organização,\npressupõe respostas coletivas.")
        e_titulo = (_e_cabecalho(anterior) and atual
                    and len(atual) <= 90
                    and not atual.endswith(",")
                    and not RE_PONTUACAO_FORTE.search(atual)
                    and not _e_cabecalho(atual)
                    and not RE_MARCADOR.match(atual))
        # memo 4 (06/07): "…alíneas a),\nb) e c) do número…" é continuação,
        # não uma alínea nova — junta-se apesar do marcador
        continuacao_alinea = (RE_ALINEA_CONTINUACAO.match(atual)
                              and anterior.endswith(","))
        # bloco de título da convenção: "… - Revisão global" fecha o
        # título, o que vier a seguir é o preâmbulo (memo 21/23)
        fim_do_titulo = (len(resultado) <= LINHAS_DO_CABECALHO
                         and RE_FIM_TITULO_CONVENCAO.search(anterior))
        manter = (
            not atual
            or RE_PONTUACAO_FORTE.search(anterior)
            or _e_cabecalho(anterior)
            or _e_cabecalho(atual)
            or (RE_MARCADOR.match(atual) and not continuacao_alinea)
            or anterior.isupper()
            or fim_do_titulo
            or (len(resultado) - 1) in protegidas
        )
        if manter:
            resultado.append(atual)
            if e_titulo:
                protegidas.add(len(resultado) - 1)
        else:
            resultado[-1] = anterior + " " + atual.strip()
    return "\n".join(resultado)


def _titulo_candidato(linha: str) -> bool:
    """Linha curta que serve de título a um cabeçalho (ex.: "Âmbito").

    Uma data de outorga nunca é título (ISSUE-0018): quando a tabela de um
    anexo não produz conteúdo, o cabeçalho ("ANEXO III") fica seguido, sem
    nada entre os dois, pela data que assina o documento ("Maia, 14 de
    julho de 2026.") — sem este guarda, essa data virava o título do anexo.
    """
    linha = linha.strip()
    return (0 < len(linha) <= 90
            and not _e_cabecalho(linha)
            and not RE_MARCADOR_LISTA.match(linha)
            and not RE_DATA_OUTORGA.match(linha))


def _normalizar_rotulo(tipo: str, m: re.Match, titulo_extra: str | None) -> str:
    linha = m.group(0).strip()
    resto = (m.group(2) if m.lastindex and m.lastindex >= 2 else "") or ""
    resto = resto.strip(" -–—:")
    if resto:
        base = linha.split(resto)[0].strip(" -–—:")
        rotulo = f"{base} - {resto}"
    elif titulo_extra:
        rotulo = f"{linha.strip(' -–—:')} - {titulo_extra.strip()}"
    else:
        rotulo = linha
    return rotulo


def estruturar(texto: str, doc_id: str, subtipo: str = "desconhecido") -> tuple[dict, str]:
    """Constrói doc.json a partir do texto normalizado."""
    # "Artigo 1. º" → "Artigo 1.º": o espaço a mais partia o rótulo em
    # duas metades ("Artigo 1. - º") e escondia o ordinal no corpo
    texto = RE_ORDINAL_SEPARADO.sub(r"\1.\2", texto)
    # "3São considerados…" → "3- São considerados…" (repõe o que o PDF tem)
    texto = RE_NUMERO_SEM_SEPARADOR.sub(r"\1- ", texto)
    linhas = [l for l in juntar_linhas(texto).split("\n")
              if l.strip() and l not in (MARCA_TABELA_INI, MARCA_TABELA_FIM)]

    # 1.ª passagem: identificar cabeçalhos e fundir títulos na mesma linha
    eventos: list[tuple[str | None, str]] = []  # (tipo_cabecalho | None, linha)
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        tipo_encontrado = None
        rotulo = linha
        for tipo_cabecalho, rx in _RE_HEADINGS:
            m = rx.match(linha)
            if not m:
                continue
            tipo_encontrado = tipo_cabecalho
            resto = (m.group(2) if m.lastindex and m.lastindex >= 2 else "") or ""
            titulo_extra = None
            if not resto.strip(" -–—:"):
                # título na(s) linha(s) seguinte(s)?
                j = i + 1
                while j < len(linhas) and not linhas[j].strip():
                    j += 1
                if j < len(linhas) and _titulo_candidato(linhas[j]):
                    titulo_extra = linhas[j].strip()
                    i = j  # consome a linha do título
            rotulo = _normalizar_rotulo(tipo_cabecalho, m, titulo_extra)
            break
        eventos.append((tipo_encontrado, rotulo if tipo_encontrado else linhas[i]))
        i += 1

    # 2.ª passagem: montar texto final e nós com offsets
    nos: list[dict] = []
    partes: list[str] = []
    pos = 0
    contexto = {"capitulo": None, "seccao": None, "anexo": None}
    no_aberto: dict | None = None

    def emitir(segmento: str):
        nonlocal pos
        partes.append(segmento)
        pos += len(segmento)

    def fechar_no():
        nonlocal no_aberto
        if no_aberto is not None:
            no_aberto["char_end"] = pos
            nos.append(no_aberto)
            no_aberto = None

    em_consolidado = False

    def abrir_no(tipo: str, rotulo: str, pai: str | None):
        nonlocal no_aberto
        fechar_no()
        no_aberto = {
            "id": f"n{len(nos)}",
            "tipo": tipo,
            "rotulo": rotulo,
            "char_start": pos,
            "char_end": pos,
            "pai": pai,
            "origem": "consolidado" if em_consolidado else "novo",
            "folha": True,
        }

    abrir_no("preambulo", "PREÂMBULO", None)
    for tipo, linha in eventos:
        if tipo is None:
            # marca explícita de republicação: vale em qualquer subtipo
            # (memo 19 — o GENERALI é revisão global com texto consolidado)
            if not em_consolidado and RE_MARCA_CONSOLIDADO.match(linha.strip()):
                em_consolidado = True
                abrir_no("bloco", "TEXTO CONSOLIDADO", None)
            emitir(linha + "\n")
            continue
        if tipo in ("capitulo", "seccao", "anexo"):
            # padrão ACIP: sem marca explícita, a republicação começa no
            # primeiro capítulo/título depois dos artigos de alteração
            ha_artigo = (any(n["tipo"] == "artigo" for n in nos)
                         or (no_aberto is not None and no_aberto["tipo"] == "artigo"))
            if (not em_consolidado
                    and subtipo in ("revisao_parcial_com_consolidado",
                                    "texto_consolidado")
                    and tipo == "capitulo"
                    and ha_artigo):
                em_consolidado = True
            if tipo == "capitulo":
                contexto.update(capitulo=None, seccao=None, anexo=None)
                pai = None
            elif tipo == "seccao":
                contexto["seccao"] = None
                pai = contexto["capitulo"] or contexto["anexo"]
            else:
                contexto.update(capitulo=None, seccao=None, anexo=None)
                pai = None
            abrir_no(tipo, linha, pai)
            emitir(linha + "\n")
            fechar_no()
            contexto[tipo] = nos[-1]["id"]
            # nó "bloco" absorve conteúdo até ao próximo cabeçalho
            # (ex.: anexos sem cláusulas/artigos — não pode ficar órfão)
            abrir_no("bloco", f"Corpo de {linha}", nos[-1]["id"])
        else:  # clausula | artigo
            pai = (contexto["seccao"] or contexto["anexo"]
                   or contexto["capitulo"])
            abrir_no(tipo, linha, pai)
            emitir(linha + "\n")
    fechar_no()

    # descartar preâmbulo vazio
    nos = [n for n in nos if n["char_end"] > n["char_start"]]

    texto_final = "".join(partes)
    _destacar_assinaturas(nos, texto_final)
    nos.extend(_subsegmentar_paragrafos(nos, texto_final))
    doc = {
        "versao_schema": "0.1",
        "doc_id": doc_id,
        "tipo": "CCT",
        "subtipo": subtipo,
        "nos": nos,
    }
    return doc, texto_final


def _e_linha_assinatura(linha: str) -> bool:
    linha = linha.strip()
    # "Pela Generali Seguros, SA:" — curto ou terminado em dois pontos,
    # para não confundir com prosa que comece por "Pelo presente acordo…"
    return bool(RE_ASSINATURA.match(linha)) and (linha.endswith(":") or len(linha) < 60)


def _inicio_assinaturas(linhas: list[str]) -> int | None:
    """Índice da linha onde começa o bloco de assinaturas, se existir.

    Padrões (memos 20/24-28 de 06/07): data por extenso seguida de
    "Pela/Pelo/Pelas/Pelos …" nas linhas seguintes, ou diretamente as
    linhas "Pel…" (nalgumas convenções a data vem depois das assinaturas).
    """
    for i, linha in enumerate(linhas):
        l = linha.strip()
        if _e_linha_assinatura(l):
            return i
        if RE_DATA_OUTORGA.match(l) and any(
                _e_linha_assinatura(s.strip()) for s in linhas[i + 1:i + 5]):
            return i
    return None


def _destacar_assinaturas(nos: list[dict], texto: str) -> None:
    """Separa blocos de assinaturas em qualquer ponto do documento.

    As assinaturas aparecem no fim, mas também a meio — entre as alterações
    e o texto consolidado (memo 20). Ficam em nós próprios ASSINATURAS,
    fora dos segmentos temáticos.
    """
    for no in list(nos):
        if no["tipo"] not in ("clausula", "artigo", "bloco", "preambulo"):
            continue
        if no["rotulo"] in ("ASSINATURAS", "TEXTO CONSOLIDADO"):
            continue
        linhas = texto[no["char_start"]:no["char_end"]].split("\n")
        idx = _inicio_assinaturas(linhas)
        if idx is None or idx == 0:
            continue
        inicio_ass = no["char_start"] + sum(len(l) + 1 for l in linhas[:idx])
        if inicio_ass >= no["char_end"]:
            continue
        fim = no["char_end"]
        no["char_end"] = inicio_ass
        nos.append({
            "id": f"n{len(nos)}ass",
            "tipo": "bloco",
            "rotulo": "ASSINATURAS",
            "char_start": inicio_ass,
            "char_end": fim,
            "pai": None,
            "origem": no.get("origem", "novo"),
            "folha": True,
        })
    # manter a ordem de leitura (a propriedade zero-perda percorre as folhas)
    nos.sort(key=lambda n: (n["char_start"], n["char_end"]))


RE_PARAGRAFO = re.compile(r"^(?:\d+\s*[-–—.)]|[a-z]\)|[ivxl]+\)|[-–—•§]\s?)")


def _subsegmentar_paragrafos(nos: list[dict], texto: str) -> list[dict]:
    """Cria nós 'paragrafo' (números/alíneas) dentro de cláusulas e artigos.

    Convenção do CRL para 2025: a cláusula inteira recebe o código _identif;
    os números/alíneas recebem os subcódigos. Estes nós não são folhas
    (a propriedade zero-perda continua medida sobre as folhas).
    """
    novos = []
    for no in nos:
        if no["tipo"] not in ("clausula", "artigo"):
            continue
        corpo = texto[no["char_start"]:no["char_end"]]
        pos_linha = no["char_start"]
        atual: dict | None = None
        seq = 0
        for linha in corpo.split("\n"):
            if RE_PARAGRAFO.match(linha.strip()):
                if atual is not None:
                    atual["char_end"] = pos_linha
                    novos.append(atual)
                seq += 1
                atual = {
                    "id": f"{no['id']}p{seq}",
                    "tipo": "paragrafo",
                    "rotulo": linha.strip()[:60],
                    "char_start": pos_linha,
                    "char_end": pos_linha,
                    "pai": no["id"],
                    "origem": no.get("origem", "novo"),
                    "folha": False,
                }
            pos_linha += len(linha) + 1
        if atual is not None:
            atual["char_end"] = min(pos_linha, no["char_end"])
            novos.append(atual)
    return novos


# ---------- PDF ----------

def _formatar_tabela(linhas_tabela: list[list[str | None]]) -> str:
    """Converte uma tabela do pdfplumber em linhas 'célula | célula | célula'.

    A informação tabular deve manter estrutura analisável (pedido do CRL);
    células vazias ficam em branco mas as colunas mantêm a posição.
    """
    linhas = []
    for row in linhas_tabela:
        celulas = [(c or "").replace("\n", " ").strip() for c in row]
        if any(celulas):
            linhas.append(" | ".join(celulas))
    return "\n".join(linhas)


# ---------- texto rodado (ISSUE-0020, #42) ----------
#
# Tabelas e escalas desenhadas a 90º numa página que não declara rotação: o
# pdfplumber, por omissão, lê cada palavra ao contrário («sagloF»). Desde a
# 0.11 sabe lê-las no sentido certo (`char_dir_rotated`); falta agrupar as
# palavras em linhas e pôr as tabelas de pé. Só se ativa numa página com texto
# rodado suficiente: as outras seguem o caminho de sempre.
MIN_CARACTERES_RODADOS = 10


def _sentido_rodado(obj) -> str | None:
    """«btt» (lê-se de baixo para cima), «ttb» (de cima para baixo) ou None."""
    a, b, c, d = obj["matrix"][:4]
    if abs(a) > 0.1 or abs(d) > 0.1:
        return None
    return "btt" if b > 0 else "ttb"


def _sentido_da_pagina(pag) -> str | None:
    sentidos = Counter(
        s for c in pag.chars
        if not c.get("upright", True) and c["text"].strip()
        and (s := _sentido_rodado(c)))
    if sum(sentidos.values()) < MIN_CARACTERES_RODADOS:
        return None
    return sentidos.most_common(1)[0][0]


def _opcoes(sentido: str) -> dict:
    # btt: as linhas seguem da esquerda para a direita; ttb: da direita para a esquerda
    return {"char_dir_rotated": sentido,
            "line_dir_rotated": "ltr" if sentido == "btt" else "rtl"}


def _linhas_rodadas(area, sentido: str) -> str:
    """O texto rodado de uma área, uma linha por linha do documento."""
    palavras = [w for w in area.extract_words(**_opcoes(sentido))
                if not w.get("upright", True)]
    palavras.sort(key=lambda w: w["x0"], reverse=sentido == "ttb")
    linhas: list[list[dict]] = []
    for w in palavras:
        if linhas and abs(linhas[-1][0]["x0"] - w["x0"]) <= 2:
            linhas[-1].append(w)
        else:
            linhas.append([w])
    return "\n".join(
        " ".join(w["text"] for w in sorted(
            linha, key=lambda w: w["top"], reverse=sentido == "btt"))
        for linha in linhas)


def _texto(area, sentido: str | None) -> str:
    """O texto de uma área: direito como sempre, e o rodado à parte, no fim."""
    if sentido is None:
        return area.extract_text() or ""
    direito = area.filter(lambda o: o.get("object_type") != "char"
                          or o.get("upright", True)).extract_text() or ""
    return "\n".join(t for t in (direito, _linhas_rodadas(area, sentido)) if t.strip())


def _dados_tabela(tab, sentido: str | None) -> list:
    """As células da tabela; uma tabela rodada é posta de pé.

    Rodada no sentido «btt», o cabeçalho está à esquerda da página e a
    primeira coluna em baixo; no sentido «ttb», à direita e em cima.
    """
    if sentido is None:
        return tab.extract()
    x0, t0, x1, t1 = tab.bbox
    dentro = [c for c in tab.page.chars
              if x0 <= c["x0"] <= x1 and t0 <= c["top"] <= t1 and c["text"].strip()]
    if sum(1 for c in dentro if not c.get("upright", True)) * 2 < len(dentro):
        return tab.extract()
    # célula a célula, com o mesmo agrupamento do texto rodado: o
    # extract_text do pdfplumber põe cada palavra rodada na sua linha e, no
    # sentido «btt», pela ordem inversa («355,48 1»)
    celulas = [[None if cel is None else
                _linhas_rodadas(tab.page.crop(cel), sentido).replace("\n", " ")
                for cel in linha.cells] for linha in tab.rows]
    if not celulas:
        return celulas
    n_linhas, n_colunas = len(celulas), max(len(r) for r in celulas)
    celulas = [r + [None] * (n_colunas - len(r)) for r in celulas]
    if sentido == "btt":
        return [[celulas[n_linhas - 1 - j][i] for j in range(n_linhas)]
                for i in range(n_colunas)]
    return [[celulas[j][n_colunas - 1 - i] for j in range(n_linhas)]
            for i in range(n_colunas)]


def _grelha_atravessa(pag, meio: float) -> bool:
    """Há traços de tabela a cruzar a goteira no corpo da página?

    Uma tabela com a coluna do meio vazia parece uma página em duas colunas
    (377, «Enquadramento das profissões»; 384 e 385, grelhas largas): cortá-la
    ao meio separava as colunas e partia os títulos centrados («ANEX» | «O II»).
    Os traços do cabeçalho e do rodapé (10% de cima e de baixo) não contam.
    """
    topo, fundo = pag.bbox[1], pag.bbox[3]
    margem = (fundo - topo) * 0.1
    cruzam = sum(1 for e in pag.horizontal_edges
                 if e["x0"] < meio - 10 and e["x1"] > meio + 10
                 and topo + margem < e["top"] < fundo - margem)
    return cruzam >= 2


def _duas_colunas(pag) -> float | None:
    """Devolve o x da goteira se a página estiver em duas colunas (BTE antigo).

    Heurística: poucas palavras atravessam a faixa central, ambas as
    metades têm texto substancial e nenhuma grelha de tabela cruza o meio.
    """
    palavras = pag.extract_words()
    if len(palavras) < 40:
        return None
    meio = (pag.bbox[0] + pag.bbox[2]) / 2
    atravessam = sum(1 for w in palavras if w["x0"] < meio - 5 < meio + 5 < w["x1"])
    esquerda = sum(1 for w in palavras if w["x1"] <= meio)
    direita = sum(1 for w in palavras if w["x0"] >= meio)
    total = len(palavras)
    if (atravessam / total < 0.02
            and esquerda / total > 0.25 and direita / total > 0.25
            and not _grelha_atravessa(pag, meio)):
        return meio
    return None


def _extrair_pagina(pag) -> str:
    """Extrai uma página intercalando bandas de texto e tabelas na ordem de leitura.

    O BTE é de coluna única: fatiamos a página em bandas horizontais entre
    as tabelas detetadas; o texto de cada banda sai com extract_text e as
    tabelas saem estruturadas entre sentinelas MARCA_TABELA_*. Uma página com
    texto rodado a 90º não se corta em colunas e lê-se no sentido certo.
    """
    sentido = _sentido_da_pagina(pag)
    goteira = None if sentido else _duas_colunas(pag)
    if goteira is not None:
        esq = pag.crop((pag.bbox[0], pag.bbox[1], goteira, pag.bbox[3]))
        dir_ = pag.crop((goteira, pag.bbox[1], pag.bbox[2], pag.bbox[3]))
        return f"\n{MARCA_COLUNA}\n".join(
            t for t in (_extrair_pagina(esq), _extrair_pagina(dir_)) if t.strip())

    tabelas = sorted(pag.find_tables(), key=lambda t: t.bbox[1])
    if not tabelas:
        return _texto(pag, sentido)

    partes = []
    topo = pag.bbox[1]
    for tab in tabelas:
        x0, t0, x1, t1 = tab.bbox
        if t0 > topo:
            banda = pag.crop((pag.bbox[0], topo, pag.bbox[2], t0))
            txt = _texto(banda, sentido)
            if txt.strip():
                partes.append(txt)
        dados = _dados_tabela(tab, sentido)
        if dados:
            corpo = _formatar_tabela(dados)
            if corpo:
                partes.append(f"{MARCA_TABELA_INI}\n{corpo}\n{MARCA_TABELA_FIM}")
        topo = max(topo, t1)
    if topo < pag.bbox[3]:
        banda = pag.crop((pag.bbox[0], topo, pag.bbox[2], pag.bbox[3]))
        txt = _texto(banda, sentido)
        if txt.strip():
            partes.append(txt)
    return "\n".join(partes)


# Linhas no topo e no fundo de cada página (ou coluna) onde o BTE põe o seu
# mobiliário: cabeçalho com o número do boletim, número da página, rodapé.
ZONA_MOBILIARIO = 3


def _segmentos(pagina: str) -> list[list[str]]:
    """As colunas de uma página, sem a marca que as separa."""
    segmentos: list[list[str]] = [[]]
    for linha in pagina.split("\n"):
        if linha.strip() == MARCA_COLUNA:
            segmentos.append([])
        else:
            segmentos[-1].append(linha)
    return segmentos


def _texto_fora_de_tabela(linhas: list[str]) -> list[int]:
    """Índices das linhas não vazias, fora das tabelas e das suas marcas."""
    fora = []
    em_tabela = False
    for i, linha in enumerate(linhas):
        limpa = linha.strip()
        if limpa == MARCA_TABELA_INI:
            em_tabela = True
        elif limpa == MARCA_TABELA_FIM:
            em_tabela = False
        elif limpa and not em_tabela:
            fora.append(i)
    return fora


def _nas_margens(linhas: list[str]) -> set[int]:
    """Índices das linhas de texto no topo ou no fundo de uma coluna.

    As linhas de tabela contam para a posição, mas nunca são mobiliário: um
    rodapé depois de uma tabela no fim da página está na margem; uma linha
    entre duas tabelas a meio da página não está.
    """
    cheias = [i for i, l in enumerate(linhas) if l.strip()]
    # numa página curta, três linhas de cada lado eram a página inteira, e
    # uma frase do corpo repetida entre páginas curtas desaparecia
    zona = max(1, min(ZONA_MOBILIARIO, len(cheias) // 4))
    margens = set(cheias[:zona] + cheias[-zona:])
    return margens.intersection(_texto_fora_de_tabela(linhas))


def _remover_cabecalhos_rodapes(paginas: list[str]) -> list[str]:
    """Remove o mobiliário do BTE sem tocar no corpo nem nas tabelas.

    Mobiliário é o que se repete no topo ou no fundo das páginas: uma linha
    de texto que aparece nas margens de pelo menos 30% das páginas, um
    número de página sozinho nas margens, ou uma linha inteira de cabeçalho,
    data ou rodapé do BTE em qualquer sítio (`cct/mobiliario.py`). A posição conta: antes, qualquer linha repetida em 30%
    das páginas desaparecia, incluindo frases legítimas do corpo (issue #47).
    """
    colunas = [_segmentos(pag) for pag in paginas]
    contagem: Counter[str] = Counter()
    for segmentos in colunas:
        contagem.update({seg[i].strip() for seg in segmentos for i in _nas_margens(seg)})
    limiar = max(2, int(len(paginas) * 0.3))
    repetidas = {l for l, c in contagem.items() if c >= limiar}
    limpas = []
    for segmentos in colunas:
        linhas = []
        for seg in segmentos:
            margens = _nas_margens(seg)
            texto = set(_texto_fora_de_tabela(seg))
            for i, linha in enumerate(seg):
                limpa = linha.strip()
                # cabeçalho, data e rodapé do BTE em linha própria, em
                # qualquer sítio: nas páginas de 2026 nem sempre se repetem
                # o bastante para a regra das margens os apanhar (os
                # CARRISTUR têm três páginas e o cabeçalho só na primeira)
                if i in texto and e_mobiliario(limpa):
                    continue
                if i in margens and (limpa in repetidas or re.fullmatch(r"\d+", limpa)):
                    continue
                linhas.append(linha)
        limpas.append("\n".join(linhas))
    return limpas


def extrair_pdf(pdf_path: Path, paginas: tuple[int, int] | None = None,
                doc_id: str | None = None,
                subtipo: str = "desconhecido") -> tuple[dict, str]:
    """Extrai uma convenção de um PDF do BTE (intervalo de páginas 0-based, fim exclusivo)."""
    import pdfplumber

    pdf_path = Path(pdf_path)
    textos = []
    with pdfplumber.open(pdf_path) as pdf:
        pags = pdf.pages if paginas is None else pdf.pages[paginas[0]:paginas[1]]
        for pag in pags:
            t = _extrair_pagina(pag)
            if t.strip():
                textos.append(t)
    if not textos:
        raise ValueError(f"Sem texto extraível em {pdf_path} — PDF digitalizado?")

    textos = _remover_cabecalhos_rodapes(textos)
    bruto = "\n".join(textos)
    bruto = re.sub(r"-\n(?=[a-zà-ú])", "", bruto)          # des-hifenização
    bruto = re.sub(r"[ \t]+\n", "\n", bruto)               # espaços finais
    bruto = re.sub(r"\n{3,}", "\n\n", bruto)

    return estruturar(bruto, doc_id or pdf_path.stem, subtipo=subtipo)
