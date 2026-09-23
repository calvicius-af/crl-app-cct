"""Teste do encadeamento recolha → nomeação (SPEC-0001), sem rede."""
import json
from pathlib import Path

import pytest

from cct import aquisicao, recolha

from .test_recolha import AbridorFalso, escrever_indice


def _argumentos(pasta: Path) -> list[str]:
    return ["--indices", str(escrever_indice(pasta)),
            "--interim", str(pasta / "interim"),
            "--destino", str(pasta / "bte"),
            "--registo", str(pasta / "registo.jsonl"),
            "--relatorio", str(pasta / "relatorios"),
            "--pausa", "0"]


def test_indice_indicado_mas_inexistente_para_antes_da_rede(tmp_path, monkeypatch):
    def recusar(url, cabecalhos=None):
        raise AssertionError("não pode ligar à rede sem índice")

    monkeypatch.setattr(recolha, "abridor_urllib", recusar)
    with pytest.raises(SystemExit, match="Sem ficheiros-índice"):
        aquisicao.main(["--indices", str(tmp_path / "inexistente.xlsx"),
                        "--confirmar-rede", "--aplicar"])


def test_simulacao_nao_liga_a_rede_nem_escreve(tmp_path, monkeypatch, capsys):
    def recusar(url, cabecalhos=None):
        raise AssertionError("simulação não pode fazer pedidos de rede")

    monkeypatch.setattr(recolha, "abridor_urllib", recusar)
    aquisicao.main(_argumentos(tmp_path))

    saida = capsys.readouterr().out
    assert "rede desligada — simulação" in saida
    assert not list((tmp_path / "interim").rglob("*.pdf")) \
        if (tmp_path / "interim").exists() else True
    assert not (tmp_path / "bte").exists()
    assert list((tmp_path / "relatorios").glob("relatorio_*.txt"))


def test_corrida_completa_escreve_so_os_documentos_sem_aviso(tmp_path, monkeypatch):
    """Por omissão (sem --aceitar-heuristicas), os documentos com sigla
    derivada por heurística ficam por confirmar — ver PR #35, achado nº5.

    Por omissão, `--esquema` é `rnc` (ADR-0021): os nomes já saem no formato
    do RNC, não no de 2025."""
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    codigo = aquisicao.main(_argumentos(tmp_path) + ["--confirmar-rede", "--aplicar"])

    assert codigo == 0
    pdfs = sorted(p.name for p in (tmp_path / "bte" / "bte_2026").rglob("*.pdf"))
    assert pdfs == ["2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP.pdf",
                    "2026_PRI_378_CCT-ALT_26760_BTE_31_CNIS-FNSTFPS.pdf",
                    "2026_PRI_379_CCT-ALT_26651_BTE_31_AEVP-FESAHT.pdf"]
    relatorio = next((tmp_path / "relatorios").glob("relatorio_*.txt")).read_text(
        encoding="utf-8")
    assert "2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP" in relatorio
    assert "Rede: autorizada" in relatorio
    assert "por_confirmar: 3" in relatorio


def test_corrida_completa_produz_a_pasta_do_pipeline_com_aceitar_heuristicas(
        tmp_path, monkeypatch):
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    codigo = aquisicao.main(_argumentos(tmp_path) +
                            ["--confirmar-rede", "--aplicar", "--aceitar-heuristicas"])

    assert codigo == 0
    pdfs = sorted(p.name for p in (tmp_path / "bte" / "bte_2026").rglob("*.pdf"))
    assert pdfs == ["2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP.pdf",
                    "2026_PRI_378_CCT-ALT_26760_BTE_31_CNIS-FNSTFPS.pdf",
                    "2026_PRI_379_CCT-ALT_26651_BTE_31_AEVP-FESAHT.pdf",
                    "2026_PRI_385_AE-ALT_47140_BTE_31_APSolutionsGMBH-STAS.pdf",
                    "2026_SPE_382_AE_47252_BTE_31_EmpresaMetropolitana-SINTAP.pdf",
                    "2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-Transportes.pdf"]
    relatorio = next((tmp_path / "relatorios").glob("relatorio_*.txt")).read_text(
        encoding="utf-8")
    assert "2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP" in relatorio
    assert "Rede: autorizada" in relatorio


def test_corrida_produz_manifest_json(tmp_path, monkeypatch):
    """Ver PR #35, achado nº8: cada corrida de aquisição tem de produzir um
    manifest.json, como ADR-0014 exige de qualquer corrida do pipeline."""
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    aquisicao.main(_argumentos(tmp_path) + ["--confirmar-rede", "--aplicar"])

    manifesto_path = tmp_path / "relatorios" / "manifest.json"
    assert manifesto_path.exists()
    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    assert manifesto["schema_version"] == 1
    assert manifesto["status"] in ("completed", "completed_with_warnings")
    assert manifesto["summary"]["documentos_no_indice"] == 7
    assert manifesto["summary"]["descarregados"] == 6
    assert manifesto["summary"]["nomeados"] == 3       # 3 ficam por_confirmar
    assert manifesto["summary"]["por_confirmar"] == 3
    # entradas (índices) e saídas (relatório, registo) hasheadas para auditoria
    assert manifesto["inputs"]
    assert manifesto["outputs"]


def test_pipeline_tema_encontra_os_pdfs_que_a_aquisicao_escreveu(
        tmp_path, monkeypatch, capsys):
    """A pasta que a aquisição escreve tem de ser a mesma que o pipeline lê.

    Bloqueante apontado na revisão do PR #69: com o esquema RNC, a
    aquisição arruma os PDFs em `bte_2026/convencoes/{PRI,SPE}/`, mas a
    app gráfica e o guia de operação continuam a apontar `--pdfs` para
    `bte_2026` (a pasta do ano) — e `cct.pipeline_tema` só procurava com
    `glob("*.pdf")`, sem descer às subpastas. `_pdfs_da_pasta` tem de
    encontrar os PDFs nos dois casos."""
    from cct import pipeline_tema

    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    aquisicao.main(_argumentos(tmp_path) +
                   ["--confirmar-rede", "--aplicar", "--aceitar-heuristicas"])

    pasta_ano = tmp_path / "bte" / "bte_2026"
    assert not list(pasta_ano.glob("*.pdf")), \
        "pré-condição: o esquema RNC não escreve PDFs direto na pasta do ano"

    codebook = tmp_path / "cb.yaml"
    codebook.write_text("tema: ensaio\ncodigos: []\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["cct.pipeline_tema", "--pdfs", str(pasta_ano),
         "--codebook", str(codebook), "--out", str(tmp_path / "out")])

    pipeline_tema.main()  # não pode dar SystemExit("Sem PDFs em …")

    manifesto = json.loads((tmp_path / "out" / "manifest.json").read_text(
        encoding="utf-8"))
    assert manifesto["summary"]["documentos_encontrados"] == 6


def test_repetir_a_corrida_nao_descarrega_nem_reescreve(tmp_path, monkeypatch):
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    args = _argumentos(tmp_path) + ["--confirmar-rede", "--aplicar"]
    aquisicao.main(args)

    def recusar(url, cabecalhos=None):
        raise AssertionError("segunda corrida não pode voltar a descarregar")

    monkeypatch.setattr(recolha, "abridor_urllib", recusar)
    assert aquisicao.main(args) == 0
