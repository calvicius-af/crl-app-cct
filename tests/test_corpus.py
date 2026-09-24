"""Corpus de regressão (cct/corpus.py).

Os testes sintéticos verificam o mecanismo: obter pelo hash, medir, guardar a
referência e apanhar uma regressão. O último teste é o próprio corpus: corre
sobre os PDF reais de data/corpus quando existem e há referência, e falha se
algum documento piorar. Sem os PDF (o caso normal fora da estação), é ignorado.
"""
import hashlib
import json

import pytest

from cct import corpus
from cct.recolha import Resposta
from tests.pdf_sintetico import escrever_pdf, pagina_bte


def _pdf(pasta, nome, n_paginas=3):
    corpo = [[f"Cláusula {n}.ª - Férias",
              *[f"Linha {n}.{k} do texto da cláusula." for k in range(12)]]
             for n in range(1, n_paginas + 1)]
    return escrever_pdf(pasta / nome, [pagina_bte(n, c) for n, c in enumerate(corpo, 1)])


def _manifesto(*pdfs, url=None):
    return {"documentos": [
        {"nome": p.stem, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
         "bytes": p.stat().st_size, "url": url} for p in pdfs]}


@pytest.fixture
def ambiente(tmp_path):
    origem = tmp_path / "estacao" / "PRI"
    origem.mkdir(parents=True)
    a = _pdf(origem, "2026_BTE_31_PRI_001_CCT_1_A-B.pdf")
    b = _pdf(origem, "2026_BTE_31_PRI_002_CCT_2_C-D.pdf", 2)
    manifesto = _manifesto(a, b)
    # o nome no corpus é o do manifesto, não o do ficheiro encontrado
    manifesto["documentos"][1]["nome"] = "outro_nome"
    caminho = tmp_path / "manifesto.json"
    corpus.gravar(caminho, manifesto)
    return tmp_path, caminho


def _obter(tmp, manifesto):
    return corpus.main(["obter", "--pasta", str(tmp / "estacao"),
                        "--manifesto", str(manifesto), "--corpus", str(tmp / "corpus")])


def _medir(tmp, manifesto, *extra):
    return corpus.main(["medir", "--manifesto", str(manifesto),
                        "--corpus", str(tmp / "corpus"),
                        "--referencia", str(tmp / "referencia.json"),
                        "--saida", str(tmp / "saida"), *extra])


def test_obter_encontra_pelo_hash_e_nao_pelo_nome(ambiente):
    tmp, manifesto = ambiente
    assert _obter(tmp, manifesto) == 0
    assert sorted(p.name for p in (tmp / "corpus").iterdir()) == [
        "2026_BTE_31_PRI_001_CCT_1_A-B.pdf", "outro_nome.pdf"]


def test_ciclo_referencia_igual_e_regressao(ambiente, monkeypatch, capsys):
    tmp, manifesto = ambiente
    _obter(tmp, manifesto)

    assert _medir(tmp, manifesto, "--atualizar") == 0
    referencia = json.loads((tmp / "referencia.json").read_text(encoding="utf-8"))
    assert referencia["pdfplumber"]["outro_nome"]["cobertura"] == 1.0
    assert "Linha" not in json.dumps(referencia), "a referência não guarda texto"

    assert _medir(tmp, manifesto) == 0
    assert "| outro_nome | igual |" in capsys.readouterr().out

    # um extrator que perde uma linha tem de ser apanhado, com o motivo
    from cct import extractor
    original = extractor.extrair_pdf

    def extrator_com_perda(pdf, **kw):
        doc, texto = original(pdf, **kw)
        return doc, texto.replace("Linha 1.3 do texto da cláusula.", "")
    monkeypatch.setattr(extractor, "extrair_pdf", extrator_com_perda)
    assert _medir(tmp, manifesto) == 1
    saida = capsys.readouterr().out
    assert "REGRESSÃO" in saida and "cobertura desceu" in saida
    comparacao = (tmp / "saida" / "comparacao.md").read_text(encoding="utf-8")
    assert "# Diagnóstico da corrida" in comparacao, "o detalhe vem junto"


def test_pdf_em_falta_nao_passa_despercebido(ambiente, capsys):
    tmp, manifesto = ambiente
    assert _medir(tmp, manifesto) == 2
    assert "correr primeiro" in capsys.readouterr().out


def test_mudanca_de_estrutura_pede_confirmacao():
    ref = {"clausulas": 65, "cobertura": 0.999}
    assert corpus.comparar({"clausulas": 66, "cobertura": 0.999}, ref) == [
        "clausulas mudou de 65 para 66 (confirmar)"]
    assert corpus.comparar({"clausulas": 65, "cobertura": 1.0}, ref) == []
    assert corpus.melhorias({"clausulas": 65, "cobertura": 1.0}, ref) == [
        "cobertura: 0.999 → 1.0"]


def test_descarga_verifica_o_hash(tmp_path):
    pdf = _pdf(tmp_path, "x.pdf", 1)
    manifesto = _manifesto(pdf, url="https://bte.dgcp.mtsss.gov.pt/documentos/2026/31/x.pdf")
    certo = lambda url, cab: Resposta(200, {}, pdf.read_bytes())       # noqa: E731
    errado = lambda url, cab: Resposta(200, {}, b"%PDF-1.4 outro")     # noqa: E731
    assert corpus.obter(manifesto, [], tmp_path / "c1", rede=True, abridor=errado) == {
        "x": "em falta: o BTE devolveu um ficheiro diferente (hash não confere)"}
    assert corpus.obter(manifesto, [], tmp_path / "c2", rede=True, abridor=certo) == {
        "x": "descarregado"}
    assert corpus.obter(manifesto, [], tmp_path / "c3") == {
        "x": "em falta: usar --rede para descarregar"}


def test_urls_vem_do_registo_da_recolha(tmp_path):
    manifesto = {"documentos": [{"nome": "a", "sha256": "abc", "url": None},
                                {"nome": "b", "sha256": "def", "url": None}]}
    registo = tmp_path / "registo_bte.jsonl"
    registo.write_text(json.dumps({"url": "https://bte.dgcp.mtsss.gov.pt/documentos/2026/31/1.pdf",
                                   "descarga": {"sha256": "abc"}}) + "\n\n", encoding="utf-8")
    assert corpus.urls_do_registo(manifesto, registo) == 1
    assert manifesto["documentos"][0]["url"].endswith("/1.pdf")
    assert manifesto["documentos"][1]["url"] is None


def test_manifesto_do_corpus_esta_bem_formado():
    manifesto = corpus.carregar(corpus.MANIFESTO)
    docs = manifesto["documentos"]
    assert len(docs) == len({d["sha256"] for d in docs}) == len({d["nome"] for d in docs})
    assert all(len(d["sha256"]) == 64 and d.get("motivo") for d in docs)


_PRESENTES = [d["nome"] for d in corpus.carregar(corpus.MANIFESTO).get("documentos", [])
              if (corpus.PASTA / f"{d['nome']}.pdf").exists()]


@pytest.mark.skipif(not _PRESENTES or not corpus.REFERENCIA.exists(),
                    reason="corpus real ausente (python -m cct.corpus obter)")
def test_corpus_real_sem_regressoes(tmp_path):
    assert corpus.main(["medir", "--saida", str(tmp_path)]) == 0, \
        (tmp_path / "comparacao.md").read_text(encoding="utf-8")
