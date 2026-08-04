"""CLI do pipeline CCT: fases comunicam por ficheiros.

Uso:
  python -m cct.cli adaptar  --input output_v2.txt --out-dir docs/
  python -m cct.cli codificar --docs-dir docs/ --codebook codebooks/x.yaml --out-dir anotacoes/
  python -m cct.cli exportar --docs-dir docs/ --anotacoes-dir anotacoes/ --out projeto.qdpx
"""
import argparse
import json
from pathlib import Path

import yaml

from .adapter_v2 import adaptar_v2
from .extractor import extrair_pdf
from .lexical import codificar
from .qdpx import exportar_qdpx
from .schemas import validar_doc, validar_anotacoes


def cmd_adaptar(args):
    conteudo = Path(args.input).read_text(encoding="utf-8")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    docs = adaptar_v2(conteudo)
    if args.apenas:
        docs = [(d, t) for d, t in docs if d["doc_id"] in args.apenas]
    for doc, texto in docs:
        validar_doc(doc)
        (out / f"{doc['doc_id']}.doc.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        (out / f"{doc['doc_id']}.txt").write_text(texto, encoding="utf-8")
        print(f"OK  {doc['doc_id']}: {len(doc['nos'])} nós, {len(texto)} chars")
    print(f"{len(docs)} documento(s) em {out}")


def cmd_extrair(args):
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paginas = tuple(args.paginas) if args.paginas else None
    doc, texto = extrair_pdf(Path(args.pdf), paginas=paginas,
                             doc_id=args.doc_id, subtipo=args.subtipo)
    validar_doc(doc)
    (out / f"{doc['doc_id']}.doc.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / f"{doc['doc_id']}.txt").write_text(texto, encoding="utf-8")
    n_cl = sum(1 for n in doc["nos"] if n["tipo"] == "clausula")
    print(f"OK  {doc['doc_id']}: {len(doc['nos'])} nós ({n_cl} cláusulas), {len(texto)} chars")


def cmd_codificar(args):
    codebook = yaml.safe_load(Path(args.codebook).read_text(encoding="utf-8"))
    docs_dir, out = Path(args.docs_dir), Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for doc_path in sorted(docs_dir.glob("*.doc.json")):
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        texto = (docs_dir / f"{doc['doc_id']}.txt").read_text(encoding="utf-8")
        anot = codificar(doc, texto, codebook)
        validar_anotacoes(anot)
        (out / f"{doc['doc_id']}.anotacoes.json").write_text(
            json.dumps(anot, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"OK  {doc['doc_id']}: {len(anot['anotacoes'])} anotações")


def cmd_exportar(args):
    docs_dir, anot_dir = Path(args.docs_dir), Path(args.anotacoes_dir)
    itens = []
    for doc_path in sorted(docs_dir.glob("*.doc.json")):
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        texto = (docs_dir / f"{doc['doc_id']}.txt").read_text(encoding="utf-8")
        anot_path = anot_dir / f"{doc['doc_id']}.anotacoes.json"
        anot = (json.loads(anot_path.read_text(encoding="utf-8"))
                if anot_path.exists()
                else {"versao_schema": "0.1", "doc_id": doc["doc_id"], "anotacoes": []})
        itens.append((doc, texto, anot))
    destino = exportar_qdpx(itens, Path(args.out), nome_projeto=args.nome)
    total = sum(len(a["anotacoes"]) for _, _, a in itens)
    print(f"QDPX escrito em {destino} ({len(itens)} documento(s), {total} codificações)")


def main():
    p = argparse.ArgumentParser(prog="cct")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("adaptar", help="output V2 → doc.json + doc.txt")
    pa.add_argument("--input", required=True)
    pa.add_argument("--out-dir", required=True)
    pa.add_argument("--apenas", nargs="*", help="processar só estes doc_id")
    pa.set_defaults(func=cmd_adaptar)

    px = sub.add_parser("extrair", help="PDF do BTE → doc.json + doc.txt")
    px.add_argument("--pdf", required=True)
    px.add_argument("--paginas", nargs=2, type=int,
                    help="intervalo 0-based, fim exclusivo (ex.: 15 49)")
    px.add_argument("--doc-id")
    px.add_argument("--subtipo", default="desconhecido")
    px.add_argument("--out-dir", required=True)
    px.set_defaults(func=cmd_extrair)

    pc = sub.add_parser("codificar", help="doc.json + codebook YAML → anotacoes.json")
    pc.add_argument("--docs-dir", required=True)
    pc.add_argument("--codebook", required=True)
    pc.add_argument("--out-dir", required=True)
    pc.set_defaults(func=cmd_codificar)

    pe = sub.add_parser("exportar", help="docs + anotações → .qdpx")
    pe.add_argument("--docs-dir", required=True)
    pe.add_argument("--anotacoes-dir", required=True)
    pe.add_argument("--out", required=True)
    pe.add_argument("--nome", default="CRL CCT")
    pe.set_defaults(func=cmd_exportar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
