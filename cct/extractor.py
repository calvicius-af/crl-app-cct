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

RE_CAPITULO = re.compile(r"^(?:CAP[IÍ]TULO|T[IÍ]TULO)\s+([IVXLCD]+|\d+)\b(.*)$")
RE_SECCAO = re.compile(r"^SEC[ÇC][AÃ]O\s+([IVXLCD]+|\d+)\b(.*)$", re.IGNORECASE)
RE_ANEXO = re.compile(r"^ANEXO\s+([IVXLCD]+|\d+)?\b(.*)$")
RE_CLAUSULA = re.compile(
    r"^Cl[aá]usula\s+(\d+\.?[ªº]?(?:-[A-Z])?|[a-zçã]+)\s*(.*)$", re.IGNORECASE)
RE_ARTIGO = re.compile(r"^Artigo\s+(\d+\.?[ºª]?|[a-zçã]+)\s*(.*)$", re.IGNORECASE)

_RE_HEADINGS = [
    ("capitulo", RE_CAPITULO),
    ("seccao", RE_SECCAO),
    ("anexo", RE_ANEXO),
    ("clausula", RE_CLAUSULA),
    ("artigo", RE_ARTIGO),
]

# marcadores que justificam manter a quebra de linha antes deles
RE_MARCADOR = re.compile(
    r"^(?:\d+\s*[-–—.)]|[a-z]\)|[ivxl]+\)|[-–—•§]\s|"
    r"Cl[aá]usula\s|Artigo\s|CAP[IÍ]TULO\s|SEC[ÇC][AÃ]O\s|ANEXO\b|NOTA\b)",
    re.IGNORECASE)
RE_PONTUACAO_FORTE = re.compile(r"[.!?:;]\s*$")
RE_RODAPE_BTE = re.compile(r"^BTE\s+\d+\s*\|\s*\d+$")
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
        # linha curta imediatamente após cabeçalho = título ("Âmbito")
        e_titulo = (_e_cabecalho(anterior) and atual
                    and len(atual) <= 60
                    and not RE_PONTUACAO_FORTE.search(atual)
                    and not _e_cabecalho(atual)
                    and not RE_MARCADOR.match(atual))
        # memo 4 (06/07): "…alíneas a),\nb) e c) do número…" é continuação,
        # não uma alínea nova — junta-se apesar do marcador
        continuacao_alinea = (RE_ALINEA_CONTINUACAO.match(atual)
                              and anterior.endswith(","))
        manter = (
            not atual
            or RE_PONTUACAO_FORTE.search(anterior)
            or _e_cabecalho(anterior)
            or _e_cabecalho(atual)
            or (RE_MARCADOR.match(atual) and not continuacao_alinea)
            or anterior.isupper()
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
    """Linha curta que serve de título a um cabeçalho (ex.: "Âmbito")."""
    linha = linha.strip()
    return (0 < len(linha) <= 90
            and not _e_cabecalho(linha)
            and not RE_MARCADOR.match(linha))


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
    linhas = [l for l in juntar_linhas(texto).split("\n")
              if l.strip() and l not in (MARCA_TABELA_INI, MARCA_TABELA_FIM)]

    # 1.ª passagem: identificar cabeçalhos e fundir títulos na mesma linha
    eventos: list[tuple[str | None, str]] = []  # (tipo_cabecalho | None, linha)
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        tipo_encontrado = None
        rotulo = linha
        for tipo, rx in _RE_HEADINGS:
            m = rx.match(linha)
            if not m:
                continue
            tipo_encontrado = tipo
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
            rotulo = _normalizar_rotulo(tipo, m, titulo_extra)
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


RE_PARAGRAFO = re.compile(r"^(?:\d+\s*[-–—.)]|[a-z]\)|[ivxl]+\)|[-–—•§]\s)")


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


def _duas_colunas(pag) -> float | None:
    """Devolve o x da goteira se a página estiver em duas colunas (BTE antigo).

    Heurística: poucas palavras atravessam a faixa central e ambas as
    metades têm texto substancial.
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
            and esquerda / total > 0.25 and direita / total > 0.25):
        return meio
    return None


def _extrair_pagina(pag) -> str:
    """Extrai uma página intercalando bandas de texto e tabelas na ordem de leitura.

    O BTE é de coluna única: fatiamos a página em bandas horizontais entre
    as tabelas detetadas; o texto de cada banda sai com extract_text e as
    tabelas saem estruturadas entre sentinelas MARCA_TABELA_*.
    """
    goteira = _duas_colunas(pag)
    if goteira is not None:
        esq = pag.crop((pag.bbox[0], pag.bbox[1], goteira, pag.bbox[3]))
        dir_ = pag.crop((goteira, pag.bbox[1], pag.bbox[2], pag.bbox[3]))
        return "\n".join(t for t in (_extrair_pagina(esq), _extrair_pagina(dir_))
                         if t.strip())

    tabelas = sorted(pag.find_tables(), key=lambda t: t.bbox[1])
    if not tabelas:
        return pag.extract_text() or ""

    partes = []
    topo = pag.bbox[1]
    for tab in tabelas:
        x0, t0, x1, t1 = tab.bbox
        if t0 > topo:
            banda = pag.crop((pag.bbox[0], topo, pag.bbox[2], t0))
            txt = banda.extract_text() or ""
            if txt.strip():
                partes.append(txt)
        dados = tab.extract()
        if dados:
            corpo = _formatar_tabela(dados)
            if corpo:
                partes.append(f"{MARCA_TABELA_INI}\n{corpo}\n{MARCA_TABELA_FIM}")
        topo = max(topo, t1)
    if topo < pag.bbox[3]:
        banda = pag.crop((pag.bbox[0], topo, pag.bbox[2], pag.bbox[3]))
        txt = banda.extract_text() or ""
        if txt.strip():
            partes.append(txt)
    return "\n".join(partes)


def _remover_cabecalhos_rodapes(paginas: list[str]) -> list[str]:
    """Remove linhas repetidas em ≥30% das páginas e números de página soltos."""
    contagem = Counter()
    for pag in paginas:
        for linha in set(l.strip() for l in pag.split("\n") if l.strip()):
            contagem[linha] += 1
    limiar = max(2, int(len(paginas) * 0.3))
    repetidas = {l for l, c in contagem.items() if c >= limiar}
    limpas = []
    for pag in paginas:
        linhas = [l for l in pag.split("\n")
                  if l.strip() not in repetidas
                  and not re.fullmatch(r"\d+", l.strip())
                  and not RE_RODAPE_BTE.match(l.strip())]
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
