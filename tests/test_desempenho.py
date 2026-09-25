"""Desempenho dos extratores (#26): agregação, comparação e o comando.

Os tempos reais medem-se com `python -m cct.desempenho medir`; aqui fixa-se
o contrato: o que se agrega, quando uma medida é regressão, e que o comando
mede um PDF num subprocesso e grava a referência do ambiente.
"""
import json

from cct import desempenho
from tests.pdf_sintetico import escrever_pdf, pagina_bte


def _doc(paginas, frio, quente, rss, arranque=0.05):
    return {"documento": "d", "paginas": paginas, "arranque_s": arranque,
            "frio_s": frio, "quente_s": quente, "rss_max_mb": rss, "nos": 1}


def test_agregar_por_pagina_e_memoria_maxima():
    a = desempenho.agregar([_doc(10, 3.0, 2.0, 200.0), _doc(30, 5.0, 4.0, 300.0)])
    assert a["paginas"] == 40
    assert a["s_por_pagina"] == 0.15 and a["s_por_pagina_frio"] == 0.2
    assert a["rss_max_mb"] == 300.0 and a["total_s"] == 8.1


def test_regressao_acima_da_tolerancia_ou_do_orcamento():
    ref = {"s_por_pagina": 0.2, "rss_max_mb": 300.0}
    assert desempenho.comparar({"s_por_pagina": 0.229, "rss_max_mb": 344.0}, ref, None) == []
    problemas = desempenho.comparar({"s_por_pagina": 0.231, "rss_max_mb": 346.0}, ref, None)
    assert len(problemas) == 2 and "15%" in problemas[0]
    orcamento = {"s_por_pagina": 0.5}
    assert desempenho.comparar({"s_por_pagina": 0.6, "rss_max_mb": 1.0}, None, orcamento) == [
        "s_por_pagina = 0.6 passa o orçamento de 0.5"]


def test_chave_do_ambiente_tem_sistema_arquitetura_e_python():
    chave = desempenho.chave_ambiente()
    assert chave.count("-") >= 2 and "-py3." in chave


def test_medir_grava_a_referencia_do_ambiente_e_compara(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(desempenho, "RESULTADOS", tmp_path / "resultados")
    pdfs = tmp_path / "pdfs"
    pdfs.mkdir()
    escrever_pdf(pdfs / "x.pdf", [pagina_bte(1, ["Cláusula 1.ª - Férias", "Texto da cláusula."])])
    referencia = tmp_path / "referencia.json"
    assert desempenho.main(["medir", "--pdfs", str(pdfs), "--referencia", str(referencia),
                            "--atualizar"]) == 0
    guardado = json.loads(referencia.read_text(encoding="utf-8"))
    medida = guardado["ambientes"][desempenho.chave_ambiente()]["pdfplumber"]
    assert medida["agregado"]["paginas"] == 1 and medida["ambiente"]["python"]
    assert desempenho.main(["medir", "--pdfs", str(pdfs), "--referencia", str(referencia),
                            "--comparar"]) in (0, 1)
    assert "s/página" in capsys.readouterr().out


def test_sem_referencia_para_o_ambiente_diz_como_a_criar(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(desempenho, "RESULTADOS", tmp_path / "resultados")
    pdfs = tmp_path / "pdfs"
    pdfs.mkdir()
    escrever_pdf(pdfs / "x.pdf", [pagina_bte(1, ["Texto."])])
    assert desempenho.main(["medir", "--pdfs", str(pdfs), "--referencia",
                            str(tmp_path / "nao_existe.json"), "--comparar"]) == 0
    assert "--atualizar" in capsys.readouterr().out
