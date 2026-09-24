"""Corrida completa de um tema sobre uma pasta de convenções.

Extração → codificação lexical (+ semântica opcional) → triagem calibrada
→ QDPX (MaxQDA) + XLSX (peritas). O comando único da operação normal.

Uso mínimo:
  python -m cct.pipeline_tema --pdfs data/raw/bte/bte_2026 \
      --codebook codebooks/4_08_protecao_dados.yaml --out results/runs/2026/2026_4_08
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

from .completude import (diagnostico, invertidas_pela_forma, medir_pdf,
                         ultima_aquisicao)
from .extractor import extrair_pdf
from .lexical import codificar
from .nomeacao import FAMILIAS_PROCESSAVEIS, familia_do_nome
from .qdpx import exportar_qdpx
from .export_xlsx import exportar_xlsx
from .triagem import codigos_auto, triar
from .localizador import interpretar_nome_rnc
from .sanidade import RE_RETIFICACAO
from .sanidade import verificar as verificar_sanidade
from .schemas import validar_doc, validar_anotacoes
from .proveniencia import agora_utc, construir_manifesto, escrever_manifesto

# âmbitos processáveis do esquema RNC (ADR-0021) — APU fica de fora: a
# aplicação recolhe-o mas ainda não o processa (docs/rnc/README.md §4.3)
_AMBITOS_PROCESSAVEIS = ("PRI", "SPE")

# Um nome que nenhum esquema reconhece mas que traz o tipo de uma portaria ou de
# uma adesão como campo próprio. É o caso das PE renomeadas à mão antes do
# ADR-0022 (`2026_001_BTE_01_PE_0452_ADCP_SETAAB`): `familia_do_nome` não as lê,
# e sem isto passavam pela recusa como se fossem convenções.
_TOKENS_NAO_CONVENCAO = {"PE": "extensao?", "PCT": "extensao?",
                         "PRT": "extensao?", "AA": "adesao?"}


def _familia_suspeita(nome: str) -> str | None:
    """Família provável de um nome fora dos esquemas conhecidos, ou `None`."""
    for token in nome.split("_"):
        if token in _TOKENS_NAO_CONVENCAO:
            return _TOKENS_NAO_CONVENCAO[token]
    return None


def _pdfs_da_pasta(pasta: Path) -> list[Path]:
    """PDFs de convenções na pasta do ano, em `convencoes` ou no âmbito.

    O esquema RNC arruma os PDFs em `convencoes/{PRI,SPE,APU}/`, não direto
    na pasta do ano (`bte_2026/`) — mas apontar `--pdfs` para essa pasta,
    como o guia de operação sempre ensinou, continua a funcionar: procura-se
    primeiro direto (esquema de 2025, ou já a pasta de âmbito), e só depois
    nas subpastas de âmbito processável.
    """
    diretos = sorted(pasta.glob("*.pdf"))
    if diretos:
        return diretos
    # `--pdfs .../convencoes` é um ponto de entrada normal: não procurar
    # `convencoes/convencoes` quando a pasta indicada já é essa.
    convencoes = pasta if pasta.name.lower() == "convencoes" else pasta / "convencoes"
    if not convencoes.is_dir():
        return []
    achados: list[Path] = []
    for ambito in _AMBITOS_PROCESSAVEIS:
        achados.extend((convencoes / ambito).glob("*.pdf"))
    return sorted(achados)


def _novidades_via_versoes(pasta_versoes: Path, pdf: Path, doc: dict,
                           texto: str, problemas: list) -> set[str] | None:
    """Encontra a subpasta de versões da convenção e devolve as novidades
    do consolidado (cláusulas alteradas/novas face à versão anterior)."""
    import re
    from .localizador import _colapsar
    from .diacronia import comparar_versoes, novidades_do_consolidado

    alvo = _colapsar(pdf.stem)
    pasta = None
    for d in sorted(pasta_versoes.iterdir()):
        if d.is_dir() and _colapsar(d.name) and _colapsar(d.name) in alvo:
            pasta = d
            break
    if pasta is None:
        problemas.append(f"{pdf.stem}: sem pasta de versões correspondente "
                         "— consolidado fica todo na faixa CONSOLIDADO")
        return None
    from .comparar import _ano
    versoes = [f for f in sorted(pasta.glob("*.pdf"))
               if not re.match(r"(?i)^(comparei|diferencas)", f.name)
               and _ano(f.name) != 2025]  # o próprio 2025 não é "anterior"
    if not versoes:
        problemas.append(f"{pdf.stem}: pasta {pasta.name} sem versões anteriores")
        return None
    extraidas = {f.name: extrair_pdf(f, doc_id=f.stem,
                                     subtipo="revisao_parcial_com_consolidado")
                 for f in versoes}
    # versão anterior = o texto COMPLETO mais recente (parciais não servem)
    completas = {n: (d, t) for n, (d, t) in extraidas.items()
                 if len(t) >= len(texto) * 0.5} or extraidas
    nome_antigo = max(completas, key=lambda n: (_ano(n) or -1, len(completas[n][1])))
    doc_a, txt_a = extraidas[nome_antigo]
    r = comparar_versoes(doc_a, txt_a, doc, texto)
    nov = novidades_do_consolidado(r, doc)
    print(f"    diacronia vs {nome_antigo}: {r['resumo']} → {len(nov)} novidades no consolidado")
    return nov


def main():
    inicio_utc = agora_utc()
    p = argparse.ArgumentParser()
    p.add_argument("--pdfs", required=True,
                   help="pasta com PDFs individuais de convenções — a pasta "
                        "do ano (bte_2026), convencoes, PRI ou SPE")
    p.add_argument("--codebook", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--variaveis", help="VariaveisDocumento*.xlsx do MaxQDA (subtipo, CAE, …)")
    p.add_argument("--master", help="codebook .qdc do MaxQDA (nomes/cores/descrições)")
    p.add_argument("--metricas", help="metricas.json de avaliar_baseline (calibra AUTO/REVER)")
    p.add_argument("--pasta-versoes",
                   help="pasta com subpastas de versões anteriores (estrutura "
                        "data/raw/textos_consolidados) — promove novidades do consolidado")
    p.add_argument("--extrator", choices=("pdfplumber", "docling"),
                   default="pdfplumber",
                   help="docling recupera tabelas de anexos e layouts difíceis "
                        "(mais lento; requer 'pip install docling')")
    p.add_argument("--semantica", action="store_true",
                   help="ativa a camada LLM (LM Studio) nas cláusulas não resolvidas")
    p.add_argument("--modelo", default="google/gemma-4-e2b")
    p.add_argument("--base-url", default="http://127.0.0.1:1234")
    p.add_argument("--max-lotes", type=int, default=4)
    p.add_argument("--nome", default="CRL CCT pré-codificado")
    args = p.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    codebook = yaml.safe_load(Path(args.codebook).read_text(encoding="utf-8"))

    variaveis = None
    if args.variaveis:
        from .variaveis import carregar_variaveis
        variaveis = carregar_variaveis(Path(args.variaveis))
    master = None
    if args.master:
        from .qdc import carregar_qdc
        master = carregar_qdc(Path(args.master))
    aptos = set()
    if args.metricas:
        aptos = codigos_auto(json.loads(Path(args.metricas).read_text(encoding="utf-8")))

    pdfs = _pdfs_da_pasta(Path(args.pdfs))
    if not pdfs:
        raise SystemExit(
            f"Sem PDFs em {args.pdfs} (procurado direto e nas subpastas "
            f"PRI/SPE de convencoes). Confirma o caminho e a presença "
            "dos ficheiros .pdf")

    # Uma portaria de extensão ou um acordo de adesão não têm o articulado que a
    # codificação temática pressupõe. Se um deles entrar aqui, não dá erro: dá
    # números errados, que só se descobrem muito mais tarde — ou nunca. Por
    # isso recusa-se à entrada, em vez de se avisar e continuar.
    intrusos = []
    for f in pdfs:
        fam = familia_do_nome(f.stem)
        if fam is None:
            fam = _familia_suspeita(f.stem)
        if fam and fam not in FAMILIAS_PROCESSAVEIS:
            intrusos.append((f, fam))
    if intrusos:
        linhas = "\n".join(f"    {f.name}  ({fam})" for f, fam in intrusos[:10])
        raise SystemExit(
            f"{len(intrusos)} ficheiro(s) em {args.pdfs} não são convenções:\n"
            f"{linhas}\n"
            "  Estes documentos referem-se a uma convenção mas não são uma, e\n"
            "  codificá-los como se fossem contamina as contagens por cláusula.\n"
            "  Apontar --pdfs para a pasta das convenções "
            "(1_fontes/irct/convencoes/PRI).\n"
            "  Uma família com «?» vem de um nome fora dos esquemas conhecidos:\n"
            "  voltar a nomeá-lo com python -m cct.nomeacao (ADR-0022).")

    entradas = [*pdfs, Path(args.codebook)]
    for opcional in (args.variaveis, args.master, args.metricas):
        if opcional:
            entradas.append(Path(opcional))
    if args.pasta_versoes:
        entradas.extend(sorted(Path(args.pasta_versoes).rglob("*.pdf")))
    parametros = {chave: valor for chave, valor in vars(args).items()}
    parametros["argv"] = sys.argv[1:]
    comando = ["python", "-m", "cct.pipeline_tema", *sys.argv[1:]]
    raiz = Path(__file__).resolve().parent.parent
    manifesto_inicial = construir_manifesto(
        raiz=raiz,
        inicio_utc=inicio_utc,
        parametros=parametros,
        entradas=entradas,
        saidas=[],
        resumo={"documentos_encontrados": len(pdfs)},
        problemas=[],
        status="running",
        comando=comando,
    )
    escrever_manifesto(out / "manifest.json", manifesto_inicial)

    extrair = extrair_pdf
    if args.extrator == "docling":
        from .extractor_docling import extrair_pdf_docling
        extrair = extrair_pdf_docling

    # o subtipo pode vir das variáveis MaxQDA ou, em sua falta, do registo
    # BTE — é o que diz se um documento é uma retificação (AE-ALT-RECT),
    # e isso desliga o controlo da nota de depósito. O tipo do registo
    # (código IRCT) traduz-se no subtipo do schema; o que não encaixa
    # fica "desconhecido" e o tipo original viaja no doc para a sanidade.
    tipo_do_registo: dict[str, str] = {}
    REGISTO_OMISSAO = Path(__file__).resolve().parent.parent / "data" / "registo" / "registo_bte.jsonl"
    if REGISTO_OMISSAO.exists():
        import json as _json
        for _linha in REGISTO_OMISSAO.read_text(encoding="utf-8").splitlines():
            if not _linha.strip():
                continue
            try:
                _e = _json.loads(_linha)
                _doc = (_e.get("nomeacao") or {}).get("doc_id")
                if _doc and _e.get("tipo"):
                    tipo_do_registo.setdefault(_doc, _e["tipo"])
            except ValueError:
                continue

    def _subtipo_do(doc_id: str, das_variaveis: str | None) -> tuple[str, str]:
        """Subtipo do schema; o tipo IRCT viaja no doc como 'tipo_registo'.

        O tipo vem do registo da recolha e, sem ele, do próprio nome: os
        esquemas RNC (ADR-0016 e ADR-0022) trazem-no. Sem isto, correr o
        pipeline numa máquina sem o registo tratava uma retificação como
        convenção e dava-a como truncada (ISSUE-0014).
        """
        tipo = tipo_do_registo.get(doc_id, "")
        if not tipo:
            meta = interpretar_nome_rnc(doc_id)
            tipo = (meta or {}).get("tipo") or ""
        if das_variaveis:
            return das_variaveis, tipo
        if RE_RETIFICACAO.search(tipo):
            return "retificacao", tipo
        return "desconhecido", tipo

    itens, problemas = [], []
    medidas = []
    for i, pdf in enumerate(pdfs, 1):
        try:
            v = None
            if variaveis:
                from .variaveis import procurar
                v = procurar(variaveis, pdf.stem)
            subtipo, tipo_registo = _subtipo_do(pdf.stem, (v or {}).get("subtipo"))
            doc, texto = extrair(pdf, doc_id=pdf.stem, subtipo=subtipo)
            doc["tipo_registo"] = tipo_registo  # fora do schema: meta para sanidade
            # completude contra uma leitura independente do PDF: nunca
            # rebenta, e o resultado vai para o diagnostico.md
            medidas.append(medir_pdf(pdf.stem, pdf, texto))
            validar_doc(doc)
            for aviso in verificar_sanidade(doc, texto):
                problemas.append(f"{pdf.stem}: {aviso}")
            # auditoria cruzada de tabelas: o que um extrator vê e o outro
            # não — a perda silenciosa que motivou o guardião (2026-09-17).
            # O canário de anexos sem tabela já vem na sanidade.
            # A auditoria é OPCIONAL e nunca pode custar o documento: com
            # --extrator docling, o docling pode ter extraído bem um PDF
            # que o auditor pdfplumber não consegue abrir — uma falha aqui
            # é um aviso, não a exclusão do resultado válido do QDPX.
            try:
                from .auditoria import (contar_blocos_tabela,
                                       contar_tabelas_pdfplumber, divergencias)
                n_texto = contar_blocos_tabela(texto)
                n_pp = contar_tabelas_pdfplumber(pdf)
                for aviso in divergencias(n_pp, n_texto):
                    problemas.append(f"{pdf.stem}: [auditoria] {aviso}")
            except Exception as e:
                problemas.append(
                    f"{pdf.stem}: [auditoria] não foi possível verificar "
                    f"as tabelas ({e}) — documento mantido")
            # tabelas rodadas 90º (ISSUE-0020): o extrator lê hoje o texto
            # rodado no sentido certo; o aviso só se dá quando o texto ainda
            # traz palavras invertidas, sinal de uma rotação não reconhecida.
            # Sem essa condição, dizia que estava errado o que já estava certo.
            if args.extrator != "docling" and invertidas_pela_forma(texto):
                try:
                    from .auditoria import tabelas_rodadas_pdfplumber
                    for aviso in tabelas_rodadas_pdfplumber(pdf):
                        problemas.append(f"{pdf.stem}: [auditoria] {aviso}")
                except Exception as e:
                    problemas.append(
                        f"{pdf.stem}: [auditoria] não foi possível verificar "
                        f"tabelas rodadas ({e}) — documento mantido")
            anot = codificar(doc, texto, codebook)
            if args.semantica:
                from .semantico import codificar_semantico, backend_lmstudio
                anotados = {a["no_id"] for a in anot["anotacoes"]}
                sem = codificar_semantico(
                    doc, texto, codebook,
                    backend=lambda pr: backend_lmstudio(pr, modelo=args.modelo,
                                                        base_url=args.base_url),
                    nos_ja_anotados=anotados,
                    cache_dir=out / "cache_llm",
                    max_lotes=args.max_lotes, max_chars=6000)
                anot["anotacoes"].extend(sem["anotacoes"])
                for f in sem.get("falhas", []):
                    problemas.append(f"{pdf.stem}: LLM {f}")
            validar_anotacoes({**anot, "anotacoes": [
                {k: v for k, v in a.items()} for a in anot["anotacoes"]]})
            novidades = None
            if args.pasta_versoes and any(
                    n.get("origem") == "consolidado" for n in doc["nos"]):
                novidades = _novidades_via_versoes(
                    Path(args.pasta_versoes), pdf, doc, texto, problemas)
            itens.append((doc, texto, triar(anot, aptos, doc=doc,
                                            novidades=novidades)))
            n_cl = sum(1 for n in doc["nos"] if n["tipo"] == "clausula")
            print(f"[{i}/{len(pdfs)}] {pdf.stem}: {n_cl} cláusulas, "
                  f"{len(anot['anotacoes'])} anotações")
        except Exception as e:
            problemas.append(f"{pdf.stem}: {e}")
            print(f"[{i}/{len(pdfs)}] {pdf.stem}: ERRO {e}")

    exportar_qdpx(itens, out / "projeto.qdpx", nome_projeto=args.nome, master=master)
    exportar_xlsx(itens, out / "sugestoes_peritas.xlsx", variaveis=variaveis)

    relatorio = [f"Convenções processadas: {len(itens)}/{len(pdfs)}"]
    if problemas:
        relatorio.append("\nPROBLEMAS:")
        relatorio.extend(f"  {p}" for p in problemas)
    (out / "relatorio.txt").write_text("\n".join(relatorio), encoding="utf-8")
    saidas = [out / "projeto.qdpx", out / "sugestoes_peritas.xlsx",
              out / "relatorio.txt", out / "diagnostico.md"]
    resumo = {
        "documentos_encontrados": len(pdfs),
        "documentos_processados": len(itens),
        "clausulas": sum(
            1 for doc, _texto, _anot in itens
            for no in doc["nos"] if no["tipo"] == "clausula"),
        "anotacoes": sum(len(anot["anotacoes"])
                          for _doc, _texto, anot in itens),
    }
    # O diagnóstico junta tudo num só ficheiro: completude de cada documento,
    # relatório, ambiente e a última aquisição. É o que se envia quando algo
    # corre mal, em vez de abrir os documentos um a um. Escreve-se antes do
    # manifesto final, que regista o seu hash.
    (out / "diagnostico.md").write_text(diagnostico(
        medidas, manifesto_inicial | {"summary": resumo},
        "\n".join(relatorio),
        {"Última aquisição": ultima_aquisicao(out.parent / "aquisicao")}),
        encoding="utf-8", newline="\n")
    manifesto = construir_manifesto(
        raiz=raiz,
        inicio_utc=inicio_utc,
        parametros=parametros,
        entradas=entradas,
        saidas=saidas,
        resumo=resumo,
        problemas=problemas,
        comando=comando,
    )
    escrever_manifesto(out / "manifest.json", manifesto)
    print(f"\n{relatorio[0]}")
    print(f"→ {out/'projeto.qdpx'}\n→ {out/'sugestoes_peritas.xlsx'}"
          f"\n→ {out/'manifest.json'}\n→ {out/'diagnostico.md'}")
    veredictos = Counter(m.veredicto for m in medidas)
    print(f"Completude: {veredictos['OK']} OK, {veredictos['ATENÇÃO']} com atenção, "
          f"{veredictos['FALHA']} com falha, {veredictos['SEM MEDIDA']} sem medida "
          f"— ver {out/'diagnostico.md'}")
    if problemas:
        print(f"⚠ {len(problemas)} problemas — ver {out/'relatorio.txt'}")


if __name__ == "__main__":
    main()
