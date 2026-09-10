"""Teste do encadeamento recolha → nomeação (SPEC-0001), sem rede."""
import json
from pathlib import Path

from cct import aquisicao, recolha

from .test_recolha import AbridorFalso, escrever_indice


def _argumentos(pasta: Path) -> list[str]:
    return ["--indices", str(escrever_indice(pasta)),
            "--interim", str(pasta / "interim"),
            "--destino", str(pasta / "bte"),
            "--registo", str(pasta / "registo.jsonl"),
            "--relatorio", str(pasta / "relatorios"),
            "--pausa", "0"]


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
    derivada por heurística ficam por confirmar — ver PR #35, achado nº5."""
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    codigo = aquisicao.main(_argumentos(tmp_path) + ["--confirmar-rede", "--aplicar"])

    assert codigo == 0
    pdfs = sorted(p.name for p in (tmp_path / "bte" / "bte_2026").glob("*.pdf"))
    assert pdfs == ["26_PR_001_BTE_31_ACRAL_CESP.pdf",
                    "26_PR_002_BTE_31_CNIS_FNSTFPS.pdf",
                    "26_PR_003_BTE_31_AEVP_FESAHT.pdf"]
    relatorio = next((tmp_path / "relatorios").glob("relatorio_*.txt")).read_text(
        encoding="utf-8")
    assert "26_PR_001_BTE_31_ACRAL_CESP" in relatorio
    assert "Rede: autorizada" in relatorio
    assert "por_confirmar: 3" in relatorio


def test_corrida_completa_produz_a_pasta_do_pipeline_com_aceitar_heuristicas(
        tmp_path, monkeypatch):
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    codigo = aquisicao.main(_argumentos(tmp_path) +
                            ["--confirmar-rede", "--aplicar", "--aceitar-heuristicas"])

    assert codigo == 0
    pdfs = sorted(p.name for p in (tmp_path / "bte" / "bte_2026").glob("*.pdf"))
    assert pdfs == ["26_PR_001_BTE_31_ACRAL_CESP.pdf",
                    "26_PR_002_BTE_31_CNIS_FNSTFPS.pdf",
                    "26_PR_003_BTE_31_AEVP_FESAHT.pdf",
                    "26_PR_004_BTE_31_EmpresaMetropolitana_SINTAP.pdf",
                    "26_PR_005_BTE_31_APSolutionsGMBH_STAS.pdf",
                    "26_PR_006_BTE_31_CARRISTUR_Transportes.pdf"]
    relatorio = next((tmp_path / "relatorios").glob("relatorio_*.txt")).read_text(
        encoding="utf-8")
    assert "26_PR_001_BTE_31_ACRAL_CESP" in relatorio
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


def test_repetir_a_corrida_nao_descarrega_nem_reescreve(tmp_path, monkeypatch):
    monkeypatch.setattr(recolha, "abridor_urllib", AbridorFalso())
    args = _argumentos(tmp_path) + ["--confirmar-rede", "--aplicar"]
    aquisicao.main(args)

    def recusar(url, cabecalhos=None):
        raise AssertionError("segunda corrida não pode voltar a descarregar")

    monkeypatch.setattr(recolha, "abridor_urllib", recusar)
    assert aquisicao.main(args) == 0
