"""Recolha dos documentos do BTE a partir dos ficheiros-índice da DGERT.

É a **única** fase da aplicação que toca na rede, e está desligada por omissão:
sem `--confirmar-rede` (ou `CCT_RECOLHA_REDE=1`) simula a corrida e diz o que
faria. Só descarrega URLs vindos do índice, e só de anfitriões da lista abaixo —
ver ADR-0014.

Entrada:  data/raw/indices/BTE31_2026.xlsx   (índice fornecido por número do BTE)
Saída:    data/interim/recolha/2026/31/00260057.pdf   (nome de origem, imutável)
Registo:  data/registo/registo_bte.jsonl     (uma linha JSON por documento)

Uso:
  python -m cct.recolha --indices data/raw/indices                  # simulação
  python -m cct.recolha --indices data/raw/indices --confirmar-rede
"""
import argparse
import hashlib
import json
import os
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parent.parent

# Anfitriões públicos do Boletim do Trabalho e Emprego. O antigo bte.gep.msess.gov.pt
# redireciona hoje para bte.dgcp.mtsss.gov.pt; ambos ficam permitidos.
HOSTS_PERMITIDOS = frozenset({
    "bte.dgcp.mtsss.gov.pt",
    "bte.gep.msess.gov.pt",
    "bte.gep.mtsss.gov.pt",
})

USER_AGENT = "AppCCT/0.6 (Centro de Relacoes Laborais; recolha do BTE)"
TIMEOUT = 60
MAX_BYTES = 200 * 1024 * 1024
TENTATIVAS = 3

# Vocabulário de tipos da DGERT → família. A comparação é feita pelo prefixo do
# tipo normalizado, para apanhar as variantes (-ALT, -RECT, -ALT-RECT).
PREFIXOS_FAMILIA = [
    ("CCT", "convencao"), ("ACTV", "convencao"), ("ACT", "convencao"),
    ("AE", "convencao"),
    ("PE", "extensao"), ("PCT", "extensao"), ("PRT", "extensao"),
    ("AVISO", "aviso"), ("AV", "aviso"),
    ("AA", "adesao"),
]
FAMILIAS_POR_OMISSAO = ("convencao", "extensao", "aviso")

REGISTO_OMISSAO = RAIZ / "data" / "registo" / "registo_bte.jsonl"
DESTINO_OMISSAO = RAIZ / "data" / "interim" / "recolha"
INDICES_OMISSAO = RAIZ / "data" / "raw" / "indices"


# ---------------------------------------------------------------- utilitários

def _norm(s) -> str:
    """Minúsculas, sem acentos e sem pontuação — para comparar cabeçalhos."""
    s = "".join(c for c in unicodedata.normalize("NFD", str(s or ""))
                if unicodedata.category(c) != "Mn")
    return "".join(c for c in s.lower() if c.isalnum())


def familia(tipo: str) -> str | None:
    """Família documental de um tipo da DGERT ('CCT-ALT' → 'convencao')."""
    t = _norm(tipo).upper()
    if not t:
        return None
    for prefixo, fam in PREFIXOS_FAMILIA:
        if t.startswith(prefixo):
            return fam
    return None


def sha256_ficheiro(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ------------------------------------------------------------ leitura do índice

COLUNAS = {
    "ano": ["ano"],
    "id_dgert": ["id"],
    "titulo": ["titulododocumento"],
    "tipo": ["tipodedocumento"],
    "volume": ["nvolumedoboletim", "novolumedoboletim"],
    "num_bte": ["ndoboletim", "nodoboletim"],
    "data_bte": ["datadoboletim"],
    "data_distribuicao": ["datadedistribuicaodoboletim"],
    "pagina": ["paginanaversaoescrita"],
    "cae": ["cae"],
    "cod_irct": ["codirct"],
    "sectores": ["sectoresdeactividade", "setoresdeatividade"],
    "outorgantes": ["outorgantes"],
    "altera": ["docsalteradosporeste"],
    "alterado_por": ["docsquealteramestes", "docsquealteramestee", "docsquealterameste"],
    "url": ["linkparaodocumentocriado", "linkparaodocumento"],
    "ficheiro": ["paginacriado"],
}


def _mapa_colunas(cabecalho: list) -> dict[str, list[int]]:
    """Nome interno → índices das colunas do índice (há cabeçalhos repetidos)."""
    normalizado = [_norm(c) for c in cabecalho]
    mapa: dict[str, list[int]] = {}
    for campo, nomes in COLUNAS.items():
        mapa[campo] = [i for i, n in enumerate(normalizado) if n in nomes]
    return mapa


def ler_indice(xlsx: Path) -> list[dict]:
    """Lê um ficheiro-índice do BTE e devolve um item por documento.

    Tolerante à ordem das colunas e a cabeçalhos repetidos (o índice de 2026 tem
    'TIPO DE DOCUMENTO:' duas vezes, a segunda vazia).
    """
    import openpyxl

    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    itens: list[dict] = []
    for ws in wb.worksheets:
        linhas = ws.iter_rows(values_only=True)
        try:
            cabecalho = list(next(linhas))
        except StopIteration:
            continue
        mapa = _mapa_colunas(cabecalho)
        if not mapa["titulo"] and not mapa["url"]:
            continue  # folha que não é um índice do BTE
        for posicao, linha in enumerate(linhas, 1):
            item = {}
            for campo, indices in mapa.items():
                valor = ""
                for i in indices:
                    if i < len(linha) and linha[i] not in (None, ""):
                        valor = str(linha[i]).strip()
                        break
                item[campo] = valor
            if not (item["titulo"] or item["url"]):
                continue
            item["indice"] = xlsx.name
            item["folha"] = ws.title
            item["posicao"] = posicao
            item["familia"] = familia(item["tipo"])
            _completar(item)
            itens.append(item)
    wb.close()
    return itens


def _completar(item: dict) -> None:
    """Deriva ano, número do BTE, ficheiro de origem, URL e chave."""
    item["ano"] = _inteiro(item.get("ano"))
    item["num_bte"] = _inteiro(item.get("num_bte"))
    url = (item.get("url") or "").strip()
    ficheiro = (item.get("ficheiro") or "").strip()
    if url:
        ficheiro = ficheiro or Path(urlparse(url).path).name
        partes = [p for p in urlparse(url).path.split("/") if p]
        if item["ano"] is None and len(partes) >= 3:
            item["ano"] = _inteiro(partes[-3])
        if item["num_bte"] is None and len(partes) >= 2:
            item["num_bte"] = _inteiro(partes[-2])
    elif ficheiro and item["ano"] and item["num_bte"]:
        url = (f"https://bte.dgcp.mtsss.gov.pt/documentos/"
               f"{item['ano']}/{item['num_bte']}/{ficheiro}")
    item["url"] = url
    item["ficheiro"] = ficheiro
    item["chave"] = chave(item)


def _inteiro(v) -> int | None:
    try:
        return int(str(v).strip().split(".")[0])
    except (TypeError, ValueError):
        return None


def chave(item: dict) -> str:
    """Identidade estável de um documento: ano/número do BTE/ficheiro de origem."""
    base = Path(item.get("ficheiro") or "").stem or _norm(item.get("id_dgert")) \
        or _norm(item.get("titulo"))[:40]
    return f"{item.get('ano')}/{item.get('num_bte')}/{base}"


# ------------------------------------------------------------------- registo

class Registo:
    """Registo persistente dos documentos: proveniência, descarga e nomeação.

    Ficheiro JSONL, uma linha por documento, reescrito de forma atómica. Vive em
    `data/registo/` — fora de `data/interim/`, que é descartável — porque perder
    o registo perde os ordinais já atribuídos.
    """

    def __init__(self, caminho: Path, entradas: dict[str, dict] | None = None):
        self.caminho = Path(caminho)
        self.entradas: dict[str, dict] = entradas or {}

    @classmethod
    def carregar(cls, caminho: Path) -> "Registo":
        caminho = Path(caminho)
        entradas: dict[str, dict] = {}
        if caminho.exists():
            for linha in caminho.read_text(encoding="utf-8").splitlines():
                linha = linha.strip()
                if not linha:
                    continue
                e = json.loads(linha)
                entradas[e["chave"]] = e          # última linha ganha
        return cls(caminho, entradas)

    def guardar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temp = self.caminho.with_suffix(self.caminho.suffix + ".part")
        with open(temp, "w", encoding="utf-8", newline="\n") as f:
            for chave_ in sorted(self.entradas):
                f.write(json.dumps(self.entradas[chave_], ensure_ascii=False) + "\n")
        os.replace(temp, self.caminho)

    def get(self, chave_: str) -> dict | None:
        return self.entradas.get(chave_)

    def actualizar(self, item: dict, **campos) -> dict:
        entrada = self.entradas.setdefault(item["chave"], {"chave": item["chave"]})
        for c in ("ano", "num_bte", "volume", "id_dgert", "tipo", "familia",
                  "cod_irct", "cae", "titulo", "outorgantes", "sectores",
                  "url", "ficheiro", "indice", "posicao", "data_bte",
                  "data_distribuicao", "altera", "alterado_por"):
            if item.get(c) not in (None, ""):
                entrada[c] = item[c]
        entrada.update(campos)
        return entrada

    def por_familia(self, ano: int, fam: str) -> list[dict]:
        return [e for e in self.entradas.values()
                if e.get("ano") == ano and e.get("familia") == fam]


# ---------------------------------------------------------------------- rede

@dataclass
class Resposta:
    estado: int
    cabecalhos: dict = field(default_factory=dict)
    corpo: bytes = b""


class ErroRede(Exception):
    pass


def validar_url(url: str) -> str:
    """Recusa tudo o que não seja https para um anfitrião do BTE."""
    p = urlparse(url)
    if p.scheme != "https":
        raise ErroRede(f"esquema recusado ({p.scheme or 'nenhum'}): só https — {url}")
    if (p.hostname or "").lower() not in HOSTS_PERMITIDOS:
        raise ErroRede(f"anfitrião fora da lista permitida: {p.hostname}")
    return url


class _RedireccionamentoVerificado(urllib.request.HTTPRedirectHandler):
    """Revalida o anfitrião a cada redirecionamento (o antigo host redireciona)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validar_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def abridor_urllib(url: str, cabecalhos: dict | None = None) -> Resposta:
    """Transporte real. Injetável: os testes passam outra função em `abridor=`."""
    validar_url(url)
    pedido = urllib.request.Request(url, method="GET")
    pedido.add_header("User-Agent", USER_AGENT)
    for k, v in (cabecalhos or {}).items():
        pedido.add_header(k, v)
    # ProxyHandler por omissão: respeita HTTPS_PROXY das estações do CRL.
    opener = urllib.request.build_opener(_RedireccionamentoVerificado)
    try:
        with opener.open(pedido, timeout=TIMEOUT) as r:
            corpo = r.read(MAX_BYTES + 1)
            if len(corpo) > MAX_BYTES:
                raise ErroRede(f"resposta acima de {MAX_BYTES} bytes")
            return Resposta(r.status, dict(r.headers), corpo)
    except urllib.error.HTTPError as e:
        return Resposta(e.code, dict(e.headers or {}), b"")
    except OSError as e:                               # timeout, DNS, TLS
        raise ErroRede(str(e)) from e


# ------------------------------------------------------------------- descarga

def _escrever_atomico(destino: Path, dados: bytes) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    temp = destino.with_suffix(destino.suffix + ".part")
    temp.write_bytes(dados)
    os.replace(temp, destino)


def descarregar_item(item: dict, destino_raiz: Path, registo: Registo, *,
                     abridor=None) -> dict:
    """Descarrega um documento, se ainda não estiver cá. Devolve a entrada do registo.

    Estados possíveis: `ja_existente`, `inalterado`, `descarregado`, `falhado`.
    """
    abridor = abridor or abridor_urllib
    anterior = registo.get(item["chave"]) or {}
    descarga = dict(anterior.get("descarga") or {})
    caminho = destino_raiz / str(item["ano"]) / str(item["num_bte"]) / item["ficheiro"]

    if descarga.get("sha256") and caminho.exists():
        if sha256_ficheiro(caminho) == descarga["sha256"]:
            return registo.actualizar(item, descarga={**descarga,
                                                      "estado": "ja_existente"})

    cabecalhos = {}
    if descarga.get("etag"):
        cabecalhos["If-None-Match"] = descarga["etag"]
    if descarga.get("last_modified"):
        cabecalhos["If-Modified-Since"] = descarga["last_modified"]
    if not caminho.exists():
        cabecalhos = {}          # o ficheiro desapareceu: pedir a cópia inteira

    erro = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = abridor(item["url"], cabecalhos)
        except ErroRede as e:
            erro = str(e)
            if "anfitrião" in erro or "esquema" in erro:
                break                                   # não vale a pena repetir
            time.sleep(min(2 ** tentativa, 8))
            continue
        if resposta.estado == 304:
            return registo.actualizar(item, descarga={**descarga,
                                                      "estado": "inalterado"})
        if resposta.estado == 200:
            if not resposta.corpo.startswith(b"%PDF"):
                erro = "a resposta não é um PDF"
                break
            _escrever_atomico(caminho, resposta.corpo)
            cab = {k.lower(): v for k, v in resposta.cabecalhos.items()}
            return registo.actualizar(item, descarga={
                "estado": "descarregado",
                "data": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "bytes": len(resposta.corpo),
                "sha256": hashlib.sha256(resposta.corpo).hexdigest(),
                "etag": cab.get("etag", ""),
                "last_modified": cab.get("last-modified", ""),
                "caminho": str(caminho),
            })
        erro = f"HTTP {resposta.estado}"
        if 400 <= resposta.estado < 500:
            break
        time.sleep(min(2 ** tentativa, 8))

    return registo.actualizar(item, descarga={**descarga, "estado": "falhado",
                                              "erro": erro or "sem resposta"})


def recolher(indices: list[Path], destino: Path, registo: Registo, *,
             rede: bool = False, familias: tuple[str, ...] = FAMILIAS_POR_OMISSAO,
             abridor=None, pausa: float = 1.0,
             limite: int | None = None) -> dict:
    """Percorre os índices e descarrega o que ainda não está cá.

    Com `rede=False` (omissão) não é aberta nenhuma ligação: os documentos em
    falta ficam com estado `por_descarregar`.
    """
    abridor = abridor or abridor_urllib
    resumo = {"indices": [], "por_estado": {}, "tipos_desconhecidos": {},
              "problemas": [], "documentos": 0}
    pedidos = 0

    def contar(estado):
        resumo["por_estado"][estado] = resumo["por_estado"].get(estado, 0) + 1

    for indice in indices:
        itens = ler_indice(indice)
        resumo["indices"].append({"ficheiro": indice.name, "linhas": len(itens)})
        for item in itens:
            resumo["documentos"] += 1
            if item["familia"] is None:
                tipo = item.get("tipo") or "(sem tipo)"
                resumo["tipos_desconhecidos"][tipo] = \
                    resumo["tipos_desconhecidos"].get(tipo, 0) + 1
                registo.actualizar(item, descarga={"estado": "ignorado",
                                                   "motivo": f"tipo desconhecido: {tipo}"})
                contar("ignorado")
                continue
            if item["familia"] not in familias:
                registo.actualizar(item, descarga={
                    "estado": "ignorado",
                    "motivo": f"família fora do âmbito: {item['familia']}"})
                contar("ignorado")
                continue
            if not item["url"]:
                resumo["problemas"].append(
                    f"{item['chave']}: sem ligação para o documento")
                registo.actualizar(item, descarga={"estado": "falhado",
                                                   "erro": "sem URL"})
                contar("falhado")
                continue

            anterior = (registo.get(item["chave"]) or {}).get("descarga") or {}
            caminho_ant = Path(anterior.get("caminho", ""))
            if anterior.get("sha256") and caminho_ant.exists() and \
                    sha256_ficheiro(caminho_ant) == anterior["sha256"]:
                registo.actualizar(item, descarga={**anterior,
                                                   "estado": "ja_existente"})
                contar("ja_existente")
                continue

            if not rede:
                registo.actualizar(item, descarga={**anterior,
                                                   "estado": "por_descarregar"})
                contar("por_descarregar")
                continue

            if limite is not None and pedidos >= limite:
                registo.actualizar(item, descarga={**anterior,
                                                   "estado": "por_descarregar"})
                contar("por_descarregar")
                continue

            if pedidos and pausa:
                time.sleep(pausa)
            pedidos += 1
            entrada = descarregar_item(item, destino, registo, abridor=abridor)
            estado = entrada["descarga"]["estado"]
            contar(estado)
            if estado == "falhado":
                resumo["problemas"].append(
                    f"{item['chave']}: {entrada['descarga'].get('erro')}")

    registo.guardar()
    resumo["pedidos_de_rede"] = pedidos
    return resumo


def texto_resumo(resumo: dict, *, rede: bool) -> str:
    linhas = ["== Recolha do BTE"]
    for i in resumo["indices"]:
        linhas.append(f"  índice {i['ficheiro']}: {i['linhas']} documento(s)")
    linhas.append(f"  documentos no total: {resumo['documentos']}")
    for estado, n in sorted(resumo["por_estado"].items()):
        linhas.append(f"    {estado}: {n}")
    linhas.append(f"  pedidos de rede: {resumo['pedidos_de_rede']}"
                  + ("" if rede else "  (rede desligada — simulação)"))
    if resumo["tipos_desconhecidos"]:
        linhas.append("  tipos que a tabela não conhece (não descarregados):")
        for tipo, n in sorted(resumo["tipos_desconhecidos"].items()):
            linhas.append(f"    {tipo}: {n}")
    if resumo["problemas"]:
        linhas.append("  PROBLEMAS:")
        linhas.extend(f"    {p}" for p in resumo["problemas"])
    return "\n".join(linhas)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="cct.recolha",
        description="Descarrega os documentos do BTE a partir dos ficheiros-índice. "
                    "A rede está desligada por omissão.")
    p.add_argument("--indices", default=str(INDICES_OMISSAO),
                   help="pasta com os .xlsx dos índices, ou um ficheiro")
    p.add_argument("--destino", default=str(DESTINO_OMISSAO))
    p.add_argument("--registo", default=str(REGISTO_OMISSAO))
    p.add_argument("--familias", default=",".join(FAMILIAS_POR_OMISSAO),
                   help="famílias a descarregar (convencao,extensao,aviso,adesao)")
    p.add_argument("--confirmar-rede", action="store_true",
                   help="autoriza os pedidos de rede nesta corrida")
    p.add_argument("--pausa", type=float, default=1.0,
                   help="segundos entre pedidos (por civilidade com o servidor)")
    p.add_argument("--limite", type=int, help="máximo de descargas nesta corrida")
    args = p.parse_args(argv)

    caminho_indices = Path(args.indices)
    if caminho_indices.is_dir():
        indices = sorted(caminho_indices.glob("*.xlsx"))
    else:
        indices = [caminho_indices]
    indices = [i for i in indices if not i.name.startswith("~$")]
    if not indices:
        raise SystemExit(f"Sem ficheiros-índice em {args.indices} "
                         "(ver docs/dados/README.md)")

    rede = args.confirmar_rede or os.environ.get("CCT_RECOLHA_REDE") == "1"
    registo = Registo.carregar(Path(args.registo))
    resumo = recolher(indices, Path(args.destino), registo, rede=rede,
                      familias=tuple(f.strip() for f in args.familias.split(",") if f.strip()),
                      pausa=args.pausa, limite=args.limite)
    print(texto_resumo(resumo, rede=rede))
    if not rede and resumo["por_estado"].get("por_descarregar"):
        print("\nPara descarregar mesmo: repetir com --confirmar-rede")
    return 1 if resumo["problemas"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
