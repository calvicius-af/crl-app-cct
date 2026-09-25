"""Corpus de regressão: PDF reais do BTE, medidos antes e depois de cada alteração.

Os testes do extrator trabalhavam sobre texto escrito à mão ou PDF sintéticos;
as regressões só apareciam na estação, dias depois. O corpus fixa um conjunto de
PDF reais, identificados pelo SHA-256, e guarda no repositório as métricas de
cada um (completude, ordem, mobiliário, estrutura). Uma alteração ao extrator
mede-se contra essa referência: se algum documento piorar, o comando falha e
diz qual e em quê.

Os PDF não são versionados (ADR-0013): o manifesto guarda o hash e, quando se
conhece, o URL no BTE. O texto extraído também não: a referência só tem números.

    python -m cct.corpus obter --pasta data/raw/bte/bte_2026 [--registo …] [--rede]
    python -m cct.corpus medir [--extrator docling] [--atualizar]

`obter` junta os PDF em data/corpus/, verificando o hash: primeiro nas pastas
indicadas, depois no BTE (só com --rede). Com --registo, acrescenta ao manifesto
os URL que o registo da recolha conhece. `medir` escreve results/corpus/
comparacao.md e sai com 1 se houver regressões.

Os dois comandos são estritos: falham se faltar qualquer PDF do manifesto ou,
no `medir`, qualquer documento na referência. `--permitir-ausentes` aceita um
corpus parcial, para leitura offline; o CI nunca o usa.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .completude import Medida, diagnostico, medir_pdf
from .numeracao import chave_numero
from .qdpx import verificar_offsets

RAIZ = Path(__file__).resolve().parent.parent
MANIFESTO = RAIZ / "tests" / "corpus" / "manifesto.json"
REFERENCIA = RAIZ / "tests" / "corpus" / "referencia.json"
PASTA = RAIZ / "data" / "corpus"
RESULTADOS = RAIZ / "results" / "corpus"

# métrica → (sentido, tolerância). «+» maior é melhor; «-» menor é melhor;
# «=» qualquer mudança tem de ser confirmada por uma pessoa (a contagem de
# cláusulas não é melhor nem pior por si: é outra).
METRICAS = {
    "cobertura": ("+", 0.0005),
    "ordem": ("+", 0.002),
    "a_mais": ("-", 0),
    "invertidas": ("-", 0),
    "mobiliario": ("-", 0),
    "linhas_longas": ("-", 0),
    "saltos_numeracao": ("-", 0),
    "avisos_sanidade": ("-", 0),
    # seleções do QDPX que não recortam o texto do nó (issue #84)
    "offsets_qdpx": ("-", 0),
    "clausulas": ("=", 0),
    "anexos": ("=", 0),
    "linhas_tabela": ("=", 0),
}


def carregar(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}


def gravar(caminho: Path, dados: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # LF também em Windows: estes ficheiros vão para o repositório
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8", newline="\n")


# ---------- obter ----------

def _sha256(caminho: Path) -> str:
    from .recolha import sha256_ficheiro
    return sha256_ficheiro(caminho)


def obter(manifesto: dict, pastas: list[Path], destino: Path, *,
          rede: bool = False, abridor=None) -> dict[str, str]:
    """Junta os PDF do corpus em `destino`. Devolve nome → estado."""
    destino.mkdir(parents=True, exist_ok=True)
    candidatos: dict[int, list[Path]] = {}
    for pasta in pastas:
        for pdf in pasta.rglob("*.pdf"):
            candidatos.setdefault(pdf.stat().st_size, []).append(pdf)

    estados = {}
    for doc in manifesto.get("documentos", []):
        alvo = destino / f"{doc['nome']}.pdf"
        if alvo.exists() and _sha256(alvo) == doc["sha256"]:
            estados[doc["nome"]] = "já presente"
            continue
        origem = next((p for p in candidatos.get(doc.get("bytes", -1), [])
                       if _sha256(p) == doc["sha256"]), None)
        if origem is None:
            # o tamanho pode faltar no manifesto: procurar em todos
            origem = next((p for ps in candidatos.values() for p in ps
                           if "bytes" not in doc and _sha256(p) == doc["sha256"]), None)
        if origem is not None:
            shutil.copyfile(origem, alvo)
            estados[doc["nome"]] = f"copiado de {origem}"
            continue
        if rede and doc.get("url"):
            estados[doc["nome"]] = _descarregar(doc, alvo, abridor)
            continue
        estados[doc["nome"]] = ("em falta: sem URL no manifesto" if not doc.get("url")
                                else "em falta: usar --rede para descarregar")
    return estados


def _descarregar(doc: dict, alvo: Path, abridor=None) -> str:
    import hashlib

    from .recolha import ErroRede, abridor_urllib
    try:
        resposta = (abridor or abridor_urllib)(doc["url"], None)
    except ErroRede as e:
        return f"em falta: {e}"
    if resposta.estado != 200:
        return f"em falta: HTTP {resposta.estado}"
    if hashlib.sha256(resposta.corpo).hexdigest() != doc["sha256"]:
        return "em falta: o BTE devolveu um ficheiro diferente (hash não confere)"
    alvo.write_bytes(resposta.corpo)
    return "descarregado"


def urls_do_registo(manifesto: dict, registo: Path) -> int:
    """Acrescenta ao manifesto os URL que o registo da recolha associa ao hash."""
    por_hash = {}
    for linha in registo.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        try:
            entrada = json.loads(linha)
        except ValueError:
            continue
        sha = (entrada.get("descarga") or {}).get("sha256")
        if sha and entrada.get("url"):
            por_hash[sha] = entrada["url"]
    novos = 0
    for doc in manifesto.get("documentos", []):
        if not doc.get("url") and doc["sha256"] in por_hash:
            doc["url"] = por_hash[doc["sha256"]]
            novos += 1
    return novos


# ---------- medir ----------

def metricas(doc: dict, texto: str, m: Medida, avisos: list[str]) -> dict:
    """Os números que se guardam na referência: nada de texto (ADR-0013)."""
    clausulas = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    numeros = []
    for n in clausulas:
        chave = chave_numero(n.get("rotulo", "")) or ""
        digitos = "".join(c for c in chave if c.isdigit())
        if digitos and chave == f"cl{digitos}":
            numeros.append(int(digitos))
    saltos = sum(1 for a, b in zip(numeros, numeros[1:]) if b != a + 1)
    return {
        "cobertura": round(m.cobertura, 4),
        "ordem": round(m.ordem, 4),
        "a_mais": sum(m.a_mais.values()),
        "invertidas": len(m.invertidas),
        "mobiliario": len(m.residuos),
        "linhas_longas": len(m.linhas_longas),
        "saltos_numeracao": saltos,
        "avisos_sanidade": len(avisos),
        "offsets_qdpx": len(verificar_offsets(doc, texto)),
        "clausulas": len(clausulas),
        "anexos": sum(1 for n in doc["nos"] if n["tipo"] == "anexo"),
        "linhas_tabela": sum(1 for l in texto.split("\n") if " | " in l),
    }


def comparar(atual: dict, referencia: dict) -> list[str]:
    """Diferenças que contam como regressão, em português corrente."""
    problemas = []
    for chave, (sentido, tolerancia) in METRICAS.items():
        if chave not in referencia or chave not in atual:
            continue
        antes, agora = referencia[chave], atual[chave]
        if sentido == "+" and agora < antes - tolerancia:
            problemas.append(f"{chave} desceu de {antes} para {agora}")
        elif sentido == "-" and agora > antes + tolerancia:
            problemas.append(f"{chave} subiu de {antes} para {agora}")
        elif sentido == "=" and agora != antes:
            problemas.append(f"{chave} mudou de {antes} para {agora} (confirmar)")
    return problemas


def melhorias(atual: dict, referencia: dict) -> list[str]:
    saida = []
    for chave, (sentido, tolerancia) in METRICAS.items():
        if chave not in referencia or chave not in atual:
            continue
        antes, agora = referencia[chave], atual[chave]
        if (sentido == "+" and agora > antes + tolerancia) or \
                (sentido == "-" and agora < antes - tolerancia):
            saida.append(f"{chave}: {antes} → {agora}")
    return saida


def medir_corpus(manifesto: dict, pasta: Path, extrator: str = "pdfplumber"):
    """Extrai e mede cada PDF presente. Devolve (resultados, medidas, ausentes)."""
    from .auditoria import paginas_com_imagem
    from .sanidade import verificar
    if extrator == "docling":
        from .extractor_docling import extrair_pdf_docling as extrair
    else:
        from .extractor import extrair_pdf as extrair
    resultados, medidas, ausentes = {}, [], []
    for doc_m in manifesto.get("documentos", []):
        pdf = pasta / f"{doc_m['nome']}.pdf"
        if not pdf.exists():
            ausentes.append(doc_m["nome"])
            continue
        try:
            doc, texto = extrair(pdf, doc_id=doc_m["nome"],
                                 subtipo=doc_m.get("subtipo", "desconhecido"))
        except Exception as e:
            resultados[doc_m["nome"]] = {"erro": f"{type(e).__name__}: {e}"}
            continue
        m = medir_pdf(doc_m["nome"], pdf, texto)
        medidas.append(m)
        avisos = verificar(doc, texto, m.palavras_referencia, paginas_com_imagem(pdf))
        resultados[doc_m["nome"]] = metricas(doc, texto, m, avisos)
    return resultados, medidas, ausentes


def relatorio(resultados: dict, referencia: dict, ausentes: list[str],
              extrator: str) -> tuple[str, int]:
    """Markdown da comparação e número de documentos com regressão."""
    linhas = [f"# Corpus de regressão ({extrator})", "",
              "| Documento | Estado | Diferenças |", "|---|---|---|"]
    regressoes = 0
    for nome, atual in resultados.items():
        ref = referencia.get(nome)
        if "erro" in atual:
            regressoes += 1
            linhas.append(f"| {nome} | ERRO | {atual['erro']} |")
        elif ref is None:
            linhas.append(f"| {nome} | sem referência | correr com --atualizar |")
        elif (problemas := comparar(atual, ref)):
            regressoes += 1
            linhas.append(f"| {nome} | REGRESSÃO | {'; '.join(problemas)} |")
        else:
            ganhos = melhorias(atual, ref)
            linhas.append(f"| {nome} | {'melhorou' if ganhos else 'igual'} "
                          f"| {'; '.join(ganhos)} |")
    for nome in ausentes:
        linhas.append(f"| {nome} | PDF em falta | correr `python -m cct.corpus obter` |")
    linhas += ["", f"Documentos medidos: {len(resultados)}. Com regressão: {regressoes}. "
               f"PDF em falta: {len(ausentes)}.", ""]
    return "\n".join(linhas), regressoes


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="acao", required=True)
    o = sub.add_parser("obter", help="juntar os PDF do corpus em data/corpus")
    o.add_argument("--pasta", action="append", default=[],
                   help="pasta onde procurar os PDF (repetível)")
    o.add_argument("--registo", help="registo_bte.jsonl, para acrescentar URL ao manifesto")
    o.add_argument("--rede", action="store_true", help="descarregar do BTE o que faltar")
    m = sub.add_parser("medir", help="medir e comparar com a referência")
    m.add_argument("--extrator", choices=("pdfplumber", "docling"), default="pdfplumber")
    m.add_argument("--atualizar", action="store_true",
                   help="gravar as métricas atuais como nova referência")
    for s in (o, m):
        s.add_argument("--manifesto", default=str(MANIFESTO))
        s.add_argument("--corpus", default=str(PASTA))
        s.add_argument("--permitir-ausentes", action="store_true",
                       help="não falhar por faltarem PDF ou referências (leitura "
                            "parcial offline; nunca no CI)")
    m.add_argument("--referencia", default=str(REFERENCIA))
    m.add_argument("--saida", default=str(RESULTADOS))
    args = p.parse_args(argv)

    manifesto = carregar(Path(args.manifesto))
    if args.acao == "obter":
        if args.registo:
            novos = urls_do_registo(manifesto, Path(args.registo))
            if novos:
                gravar(Path(args.manifesto), manifesto)
                print(f"URL acrescentados ao manifesto: {novos} (fazer commit de "
                      f"{args.manifesto})")
        estados = obter(manifesto, [Path(x) for x in args.pasta], Path(args.corpus),
                        rede=args.rede)
        for nome, estado in estados.items():
            print(f"  {nome}: {estado}")
        faltam = sum(1 for e in estados.values() if e.startswith("em falta"))
        print(f"Corpus: {len(estados) - faltam}/{len(estados)} PDF em {args.corpus}")
        if faltam and not args.permitir_ausentes:
            print(f"FALHA: faltam {faltam} PDF do corpus. Um corpus incompleto não "
                  "garante nada sobre os documentos que faltam.")
            return 1
        return 0

    resultados, medidas, ausentes = medir_corpus(manifesto, Path(args.corpus), args.extrator)
    if not resultados:
        print("Nenhum PDF do corpus presente: correr primeiro `python -m cct.corpus obter`.")
        return 2
    referencia_toda = carregar(Path(args.referencia))
    referencia = referencia_toda.get(args.extrator, {})
    texto, regressoes = relatorio(resultados, referencia, ausentes, args.extrator)
    sem_referencia = [n for n, r in resultados.items()
                      if "erro" not in r and n not in referencia]
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "comparacao.md").write_text(
        texto + "\n" + diagnostico(medidas), encoding="utf-8", newline="\n")
    print(texto)
    print(f"→ {saida / 'comparacao.md'}")
    if args.atualizar:
        referencia_toda[args.extrator] = {
            **referencia, **{n: r for n, r in resultados.items() if "erro" not in r}}
        gravar(Path(args.referencia), referencia_toda)
        print(f"Referência atualizada: {args.referencia} (fazer commit)")
        sem_referencia = []
    # Modo estrito, o do CI: o corpus só garante alguma coisa se os documentos
    # todos forem medidos contra a referência. Um PDF que falta, ou sem
    # referência, é uma falha, e não uma linha no relatório que ninguém lê.
    incompleto = []
    if ausentes:
        incompleto.append(f"{len(ausentes)} PDF em falta")
    if sem_referencia:
        incompleto.append(f"{len(sem_referencia)} documento(s) sem referência")
    if incompleto and not args.permitir_ausentes:
        print(f"FALHA: corpus incompleto ({'; '.join(incompleto)}).")
        return 1
    if args.atualizar:
        return 0
    return 1 if regressoes else 0


if __name__ == "__main__":
    sys.exit(main())
