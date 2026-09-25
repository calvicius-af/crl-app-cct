"""Corrida do pipeline: nenhuma opção acessória pode custar documentos.

Na corrida de 2025 em macOS (277 PDF), `--pasta-versoes` apontava para uma
pasta que não existia. Cada um dos 39 documentos com texto consolidado
rebentava na diacronia, depois de extraído e codificado, e ficava fora do
QDPX; o diagnóstico dava-os como OK.
"""
import json

import pytest

from cct import pipeline_tema
from tests.pdf_sintetico import escrever_pdf, pagina_bte


def _pasta(tmp_path, nomes=("26_PR_001_BTE_31_TESTE_X_Y", "26_PR_002_BTE_31_TESTE_Z_W")):
    pasta = tmp_path / "pdfs"
    pasta.mkdir()
    for nome in nomes:
        escrever_pdf(pasta / f"{nome}.pdf", [pagina_bte(1, [
            "Cláusula 1.ª - Férias", "O período anual de férias é de 22 dias úteis."])])
    codebook = tmp_path / "cb.yaml"
    codebook.write_text("tema: ensaio\ncodigos: []\n", encoding="utf-8")
    return pasta, codebook


def _correr(monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["cct.pipeline_tema", *map(str, argv)])
    pipeline_tema.main()


def test_pasta_de_versoes_inexistente_para_a_entrada(tmp_path, monkeypatch):
    pasta, codebook = _pasta(tmp_path)
    out = tmp_path / "out"
    with pytest.raises(SystemExit, match="pasta de versões anteriores não existe"):
        _correr(monkeypatch, "--pdfs", pasta, "--codebook", codebook, "--out", out,
                "--pasta-versoes", tmp_path / "nao_existe")
    assert not (out / "projeto.qdpx").exists(), "falha antes de extrair o que quer que seja"


def test_falha_na_diacronia_nao_custa_o_documento(tmp_path, monkeypatch):
    pasta, codebook = _pasta(tmp_path)
    versoes = tmp_path / "versoes"
    versoes.mkdir()
    real = pipeline_tema.extrair_pdf

    def com_consolidado(pdf, **kw):
        doc, texto = real(pdf, **kw)
        for no in doc["nos"]:
            no["origem"] = "consolidado"
        return doc, texto

    def rebenta(*_a, **_k):
        raise OSError("disco desligado")
    monkeypatch.setattr(pipeline_tema, "extrair_pdf", com_consolidado)
    monkeypatch.setattr(pipeline_tema, "_novidades_via_versoes", rebenta)
    out = tmp_path / "out"
    _correr(monkeypatch, "--pdfs", pasta, "--codebook", codebook, "--out", out,
            "--pasta-versoes", versoes)

    relatorio = (out / "relatorio.txt").read_text(encoding="utf-8")
    assert relatorio.startswith("Convenções processadas: 2/2")
    assert "[diacronia]" in relatorio and "documento mantido" in relatorio


def test_documento_excluido_aparece_no_diagnostico(tmp_path, monkeypatch):
    pasta, codebook = _pasta(tmp_path)
    real = pipeline_tema.codificar

    def falha_num(doc, texto, codebook):
        if doc["doc_id"].endswith("Z_W"):
            raise ValueError("anotação inválida")
        return real(doc, texto, codebook)
    monkeypatch.setattr(pipeline_tema, "codificar", falha_num)
    out = tmp_path / "out"
    _correr(monkeypatch, "--pdfs", pasta, "--codebook", codebook, "--out", out)

    diag = (out / "diagnostico.md").read_text(encoding="utf-8")
    assert "| 26_PR_002_BTE_31_TESTE_Z_W | EXCLUÍDO |" in diag
    assert "**Fora do QDPX: 1.**" in diag
    assert "| 26_PR_001_BTE_31_TESTE_X_Y | OK |" in diag
    manifesto = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifesto["status"] == "completed_with_errors"
    assert any("ERRO, documento fora do QDPX: ValueError" in p
               for p in manifesto["problems"])


def test_versao_do_proprio_ano_nao_e_anterior(tmp_path, monkeypatch):
    """O ano do documento em comparação estava fixo em 2025."""
    from cct import diacronia
    pasta = tmp_path / "versoes" / "TESTE_X_Y"
    pasta.mkdir(parents=True)
    for nome in ("26_PR_001_BTE_31_TESTE_X_Y", "25_PR_007_BTE_03_TESTE_X_Y"):
        escrever_pdf(pasta / f"{nome}.pdf", [pagina_bte(1, [
            "Cláusula 1.ª - Férias", "O período anual de férias é de 22 dias úteis."])])
    vistos = []
    monkeypatch.setattr(pipeline_tema, "extrair_pdf",
                        lambda f, **kw: (vistos.append(f.name), ({"nos": []}, "x"))[1])
    monkeypatch.setattr(diacronia, "comparar_versoes", lambda *a: {"resumo": ""})
    monkeypatch.setattr(diacronia, "novidades_do_consolidado", lambda r, d: set())
    pdf = tmp_path / "26_PR_001_BTE_31_TESTE_X_Y.pdf"
    pipeline_tema._novidades_via_versoes(tmp_path / "versoes", pdf, {"nos": []}, "x", [])
    assert vistos == ["25_PR_007_BTE_03_TESTE_X_Y.pdf"]


def test_documentos_sem_pasta_de_versoes_numa_so_linha(tmp_path, monkeypatch):
    """Corrida de 2025: 39 linhas iguais, uma por documento. A causa é o nome
    das subpastas, e diz-se uma vez, com o total e a regra."""
    pasta, codebook = _pasta(tmp_path)
    versoes = tmp_path / "versoes"
    (versoes / "OUTRA_CONVENCAO").mkdir(parents=True)
    real = pipeline_tema.extrair_pdf

    def com_consolidado(pdf, **kw):
        doc, texto = real(pdf, **kw)
        for no in doc["nos"]:
            no["origem"] = "consolidado"
        return doc, texto
    monkeypatch.setattr(pipeline_tema, "extrair_pdf", com_consolidado)
    out = tmp_path / "out"
    _correr(monkeypatch, "--pdfs", pasta, "--codebook", codebook, "--out", out,
            "--pasta-versoes", versoes)

    relatorio = (out / "relatorio.txt").read_text(encoding="utf-8")
    linhas = [l for l in relatorio.splitlines() if "pasta de versões" in l]
    assert len(linhas) == 1, relatorio
    assert "2 documento(s)" in linhas[0] and "contido no nome do PDF" in linhas[0]
    assert "26_PR_001_BTE_31_TESTE_X_Y, 26_PR_002_BTE_31_TESTE_Z_W" in linhas[0]


def test_pasta_de_versoes_vazia_diz_que_esta_vazia(tmp_path, monkeypatch):
    """Corrida de 2026-09-25: a pasta existia mas sem subpastas. A regra dos
    nomes levava a procurar um erro de nome que não havia."""
    pasta, codebook = _pasta(tmp_path)
    versoes = tmp_path / "versoes"
    versoes.mkdir()
    real = pipeline_tema.extrair_pdf

    def com_consolidado(pdf, **kw):
        doc, texto = real(pdf, **kw)
        for no in doc["nos"]:
            no["origem"] = "consolidado"
        return doc, texto
    monkeypatch.setattr(pipeline_tema, "extrair_pdf", com_consolidado)
    out = tmp_path / "out"
    _correr(monkeypatch, "--pdfs", pasta, "--codebook", codebook, "--out", out,
            "--pasta-versoes", versoes)
    relatorio = (out / "relatorio.txt").read_text(encoding="utf-8")
    assert "não tem subpastas" in relatorio and "contido no nome" not in relatorio


# ---------- #49: um documento, sem argumentos, manifesto nem exportação ----------

def _contexto(**kw):
    return pipeline_tema.Contexto(extrair=pipeline_tema.extrair_pdf,
                                  codebook={"tema": "ensaio", "codigos": []}, **kw)


def test_processar_um_documento_sem_o_resto_da_corrida(tmp_path):
    pasta, _codebook = _pasta(tmp_path, nomes=("26_PR_001_BTE_31_TESTE_X_Y",))
    r = pipeline_tema.processar_documento(pasta / "26_PR_001_BTE_31_TESTE_X_Y.pdf", _contexto())
    assert r.erro is None and r.item is not None
    doc, texto, _anot = r.item
    assert [n["rotulo"] for n in doc["nos"] if n["tipo"] == "clausula"] == ["Cláusula 1.ª - Férias"]
    assert r.medida is not None and r.medida.veredicto == "OK"


def test_passo_essencial_que_falha_exclui_so_esse_documento(tmp_path, monkeypatch):
    pasta, _codebook = _pasta(tmp_path, nomes=("26_PR_001_BTE_31_TESTE_X_Y",))

    def rebenta(*_a, **_k):
        raise ValueError("anotação inválida")
    monkeypatch.setattr(pipeline_tema, "codificar", rebenta)
    r = pipeline_tema.processar_documento(pasta / "26_PR_001_BTE_31_TESTE_X_Y.pdf", _contexto())
    assert r.item is None and r.erro == "ValueError: anotação inválida"
    assert r.medida is not None and r.medida.excluido == r.erro
    assert any("ERRO, documento fora do QDPX" in p for p in r.problemas)


def test_passo_acessorio_que_falha_nao_custa_o_documento(tmp_path, monkeypatch):
    pasta, _codebook = _pasta(tmp_path, nomes=("26_PR_001_BTE_31_TESTE_X_Y",))
    from cct import auditoria

    def rebenta(*_a, **_k):
        raise OSError("auditor sem acesso ao PDF")
    monkeypatch.setattr(auditoria, "contar_tabelas_pdfplumber", rebenta)
    monkeypatch.setattr(auditoria, "paginas_com_imagem", rebenta)
    r = pipeline_tema.processar_documento(pasta / "26_PR_001_BTE_31_TESTE_X_Y.pdf", _contexto())
    assert r.item is not None and r.erro is None
    assert any("documento mantido" in p for p in r.problemas)


def test_subtipo_pelo_registo_ou_pelo_nome(tmp_path):
    registo = tmp_path / "registo.jsonl"
    registo.write_text('{"nomeacao": {"doc_id": "X"}, "tipo": "AE-ALT-RECT"}\nlixo\n\n',
                       encoding="utf-8")
    tipos = pipeline_tema.carregar_tipos_do_registo(registo)
    assert tipos == {"X": "AE-ALT-RECT"}
    assert pipeline_tema.subtipo_do("X", None, tipos) == ("retificacao", "AE-ALT-RECT")
    assert pipeline_tema.subtipo_do("X", "revisao_global", tipos) == ("revisao_global", "AE-ALT-RECT")
    assert pipeline_tema.carregar_tipos_do_registo(tmp_path / "nao_existe.jsonl") == {}
