"""Número canónico de uma cláusula ou artigo, a partir do rótulo.

O extrator reconhece a numeração em algarismos («Cláusula 12.ª»), por extenso
(«Cláusula décima segunda»), com letra de inserção («Cláusula 16.ª-A»), única
(«Artigo único») e por posição («Cláusula prévia»). O rótulo fica sempre como
está no documento; esta função dá-lhe uma chave estável para comparar versões:

    Cláusula 12.ª - Horário            → cl12
    CLÁUSULA DÉCIMA SEGUNDA - Horário   → cl12
    Cláusula 16.ª-A - Férias            → cl16A
    Artigo único - Âmbito               → arunico
    Cláusula prévia - Âmbito da revisão → clprevia

A letra de inserção faz parte da chave: a 16.ª-A é uma cláusula nova, inserida
por uma revisão, e não a 16.ª. Sem ela, as duas disputavam o mesmo número na
comparação diacrónica (ISSUE-0001, issue #28).
"""
import re
import unicodedata

# Radicais dos ordinais, do maior valor para o menor, para que «nonagésima»
# não seja lida como «nona» nem «setuagésima» como «sétima».
_ORDINAIS = (
    ("centesim", 100), ("nonagesim", 90), ("octogesim", 80),
    ("septuagesim", 70), ("setuagesim", 70), ("sexagesim", 60),
    ("quinquagesim", 50), ("quadragesim", 40), ("trigesim", 30),
    ("vigesim", 20), ("decim", 10),
    ("primeir", 1), ("segund", 2), ("terceir", 3), ("quart", 4),
    ("quint", 5), ("sext", 6), ("setim", 7), ("oitav", 8), ("non", 9),
)

_RE_ROTULO = re.compile(r"^\s*(clausula|artigo)\s+(.+?)\s*(?:\s-\s.*)?$")
_RE_ALGARISMOS = re.compile(r"^(\d+)\s*\.?\s*[ªº]?(?:\s*-\s*([a-z]))?\b")
_RE_PALAVRA = re.compile(r"[a-z]+")


def _sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def ordinal_por_extenso(texto: str) -> int | None:
    """«décima segunda» → 12; `None` se não for um ordinal por extenso.

    Aceita as formas simples e compostas até 199, em ordem decrescente
    («vigésima primeira», nunca «primeira vigésima»), no masculino e no
    feminino. Uma palavra que não seja ordinal invalida o todo: «Cláusula
    geral e transitória» não tem número.
    """
    palavras = _RE_PALAVRA.findall(_sem_acentos(texto.lower()))
    if not palavras:
        return None
    valores = []
    for palavra in palavras:
        radical = palavra[:-1] if palavra[-1:] in ("a", "o") else palavra
        valor = next((v for r, v in _ORDINAIS if radical == r), None)
        if valor is None:
            return None
        valores.append(valor)
    if any(a <= b for a, b in zip(valores, valores[1:])):
        return None             # «primeira décima» não é um número
    return sum(valores)


def chave_numero(rotulo: str) -> str | None:
    """Chave canónica da cláusula ou artigo (`cl12`, `cl16A`, `arunico`)."""
    m = _RE_ROTULO.match(_sem_acentos(rotulo or "").lower())
    if not m:
        return None
    tipo, numeracao = m.group(1)[:2], m.group(2)
    algarismos = _RE_ALGARISMOS.match(numeracao)
    if algarismos:
        return f"{tipo}{int(algarismos.group(1))}{(algarismos.group(2) or '').upper()}"
    if re.match(r"^unic[oa]\b", numeracao):
        return f"{tipo}unico"
    if re.match(r"^(previ[oa]|preliminar)\b", numeracao):
        return f"{tipo}previa"
    # por extenso: no máximo três palavras (o extrator aceita duas; «centésima
    # vigésima primeira» cabe), e só se todas forem ordinais
    palavras = numeracao.split()
    for n in (3, 2, 1):
        valor = ordinal_por_extenso(" ".join(palavras[:n]))
        if valor is not None:
            return f"{tipo}{valor}"
    return None
