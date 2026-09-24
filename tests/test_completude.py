"""Completude da extração: o texto tem tudo o que o PDF tem.

Estes testes passam pela extração real (pdfplumber) sobre PDF sintéticos com o
mobiliário do BTE, e comparam com a leitura independente do PDFium. É o que
faltava para apanhar, antes da estação, uma correção que apaga texto: a
primeira versão da remoção de mobiliário por posição (#47) apagava as frases
repetidas de páginas curtas, e nenhum teste sobre texto já extraído o via.
"""
import json
import zipfile
from pathlib import Path

import pytest

from cct.completude import (diagnostico, main, medir, medir_pdf,
                            paginas_de_referencia, sem_mobiliario)
from cct.extractor import extrair_pdf
from tests.pdf_sintetico import escrever_pdf, pagina_bte

CORPO = ["O período anual de férias é de 22 dias úteis.",
         "O disposto no número anterior não prejudica os direitos adquiridos.",
         "Os trabalhadores têm direito a um subsídio de refeição por dia."]


def _paginas(n_paginas: int, extra: int = 0):
    """Páginas com texto próprio e, a meio, frases iguais em todas elas."""
    return [pagina_bte(n, [f"Cláusula {n}.ª - Férias",
                           *[f"Linha própria {n}.{k} da cláusula." for k in range(extra)],
                           *CORPO,
                           *[f"Outra linha {n}.{k} da cláusula." for k in range(extra)]])
            for n in range(1, n_paginas + 1)]


@pytest.mark.parametrize("extra", [0, 30], ids=["paginas-curtas", "paginas-cheias"])
def test_extracao_completa_de_paginas_com_mobiliario(tmp_path, extra):
    """Frases repetidas em todas as páginas ficam; o mobiliário sai."""
    pdf = escrever_pdf(tmp_path / "x.pdf", _paginas(5, extra))
    _doc, texto = extrair_pdf(pdf)
    m = medir_pdf("x", pdf, texto)
    assert m.veredicto == "OK", diagnostico([m])
    assert m.cobertura == 1.0
    assert "Boletim do Trabalho" not in texto and "BTE 31 |" not in texto


def test_texto_em_falta_e_localizado_na_pagina(tmp_path):
    pdf = escrever_pdf(tmp_path / "x.pdf", _paginas(4, 10))
    _doc, texto = extrair_pdf(pdf)
    texto = texto.replace(CORPO[2], "", 1)          # perde-se na página 1
    m = medir_pdf("x", pdf, texto)
    assert m.veredicto == "ATENÇÃO"
    assert m.em_falta["subsídio"] == 1
    assert [n for n, _ in m.perda_por_pagina] == [4], \
        "as páginas consomem as palavras por ordem: a falta aparece na última"
    assert "subsídio de refeição" in m.contexto_falta["subsídio"]


def test_perda_grande_e_falha():
    m = medir("x", ["Primeira frase inteira.\n" * 20, "Segunda página com texto."],
              "Segunda página com texto.")
    assert m.veredicto == "FALHA"


def test_palavras_invertidas_e_mobiliario_no_texto():
    """Os dois sintomas das tabelas rodadas e das colunas mal cortadas."""
    pdf = ["Folgas Serviço Semana\nTexto normal da escala."]
    texto = ("sagloF oçivreS Semana\nBoletim do Trabalho e Emprego 31\n"
             "Texto normal da escala.")
    m = medir("x", pdf, texto)
    assert ("sagloF", "Folgas") in m.invertidas
    assert m.residuos == [(2, "Boletim do Trabalho e Emprego 31")], \
        "o parágrafo é o número que o MAXQDA mostra"
    assert m.veredicto == "FALHA", "duas de sete palavras perdidas"


def test_tabela_colapsada_numa_linha():
    celulas = " | ".join(f"Categoria {i} | {1000 + i},00" for i in range(60))
    m = medir("x", [celulas.replace(" | ", "\n")], celulas)
    assert m.cobertura == 1.0
    assert m.linhas_longas and m.veredicto == "ATENÇÃO"


def test_blocos_trocados_baixam_a_ordem():
    a = " ".join(f"alfa{i}" for i in range(200))
    b = " ".join(f"beta{i}" for i in range(200))
    m = medir("x", [f"{a}\n{b}"], f"{b}\n{a}")
    assert m.cobertura == 1.0
    assert m.ordem < 0.6 and m.veredicto == "ATENÇÃO"


def test_numero_a_meio_da_pagina_nao_e_mobiliario():
    """Um valor de tabela numa linha própria conta; o número da página não."""
    pagina = "Boletim do Trabalho e Emprego, n.º 31\nTexto.\n1250\nMais texto.\nBTE 31 | 7\n7"
    limpa, saem = sem_mobiliario(pagina)
    assert "1250" in limpa
    assert saem == ["Boletim do Trabalho e Emprego, n.º 31", "BTE 31 | 7", "7"]


def test_hifenizacao_nao_conta_como_perda():
    m = medir("x", ["O traba-\nlhador tem direito."], "O trabalhador tem direito.")
    assert m.cobertura == 1.0 and not m.a_mais


def test_pdf_ilegivel_da_sem_medida(tmp_path):
    falso = tmp_path / "x.pdf"
    falso.write_bytes(b"%PDF-1.4\n")
    m = medir_pdf("x", falso, "texto")
    assert m.veredicto == "SEM MEDIDA"
    assert "SEM MEDIDA" in diagnostico([m])


def test_referencia_le_todas_as_paginas(tmp_path):
    pdf = escrever_pdf(tmp_path / "x.pdf", _paginas(3))
    paginas = paginas_de_referencia(pdf)
    assert len(paginas) == 3 and "Cláusula 3.ª" in paginas[2]


def test_pipeline_escreve_o_diagnostico(tmp_path, monkeypatch):
    """A corrida deixa um só ficheiro com tudo: completude, relatório e ambiente."""
    from cct import pipeline_tema
    pasta = tmp_path / "pdfs"
    pasta.mkdir()
    escrever_pdf(pasta / "26_PR_001_BTE_31_TESTE_X_Y.pdf", _paginas(3, 10))
    codebook = tmp_path / "cb.yaml"
    codebook.write_text("tema: ensaio\ncodigos: []\n", encoding="utf-8")
    out = tmp_path / "resultados" / "corrida"
    aquisicao = tmp_path / "resultados" / "aquisicao"
    aquisicao.mkdir(parents=True)
    (aquisicao / "relatorio_20260924_100000.txt").write_text(
        "documentos no total: 1", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["cct.pipeline_tema", "--pdfs", str(pasta),
                                     "--codebook", str(codebook), "--out", str(out)])
    pipeline_tema.main()

    diag = (out / "diagnostico.md").read_text(encoding="utf-8")
    assert "| 26_PR_001_BTE_31_TESTE_X_Y | OK | 100.0% |" in diag
    assert "## Relatório da corrida" in diag
    assert "documentos no total: 1" in diag, "a última aquisição vem junta"
    manifesto = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert any(s["path"].endswith("diagnostico.md") for s in manifesto["outputs"])


def test_diagnostico_de_uma_corrida_ja_feita(tmp_path, monkeypatch):
    """`python -m cct.completude --corrida` lê o QDPX, tal como chegou ao MaxQDA."""
    from cct import pipeline_tema
    raiz = tmp_path
    pasta = raiz / "pdfs"
    pasta.mkdir()
    escrever_pdf(pasta / "26_PR_001_BTE_31_TESTE_X_Y.pdf", _paginas(2, 25))
    codebook = raiz / "cb.yaml"
    codebook.write_text("tema: ensaio\ncodigos: []\n", encoding="utf-8")
    out = raiz / "corrida"
    monkeypatch.setattr("sys.argv", ["cct.pipeline_tema", "--pdfs", str(pasta),
                                     "--codebook", str(codebook), "--out", str(out)])
    monkeypatch.setattr(pipeline_tema, "__file__", str(raiz / "cct" / "pipeline_tema.py"))
    pipeline_tema.main()
    (out / "diagnostico.md").unlink()

    # estraga o texto dentro do QDPX: o diagnóstico tem de o ver
    qdpx = out / "projeto.qdpx"
    with zipfile.ZipFile(qdpx) as zf:
        conteudo = {n: zf.read(n) for n in zf.namelist()}
    fonte = next(n for n in conteudo if n.startswith("Sources/"))
    conteudo[fonte] = conteudo[fonte].replace(CORPO[1].encode("utf-8"), b"", 1)
    with zipfile.ZipFile(qdpx, "w") as zf:
        for n, dados in conteudo.items():
            zf.writestr(n, dados)

    assert main(["--corrida", str(out), "--raiz", str(raiz)]) == 0
    diag = (out / "diagnostico.md").read_text(encoding="utf-8")
    assert "| 26_PR_001_BTE_31_TESTE_X_Y | ATENÇÃO |" in diag
    assert "`prejudica`" in diag


def test_gerador_de_pdf_e_legivel_pelos_dois_motores(tmp_path):
    pdf = escrever_pdf(tmp_path / "x.pdf", [[(72, 700, "Olá, ação à mão (sim)")]])
    import pdfplumber
    with pdfplumber.open(pdf) as p:
        assert p.pages[0].extract_text() == "Olá, ação à mão (sim)"
    assert paginas_de_referencia(Path(pdf))[0] == "Olá, ação à mão (sim)"
