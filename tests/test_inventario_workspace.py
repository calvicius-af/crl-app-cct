import hashlib
import json
from pathlib import Path

from scripts.inventariar_workspace import (classificar, inventariar,
                                            resumo_markdown)


def test_classificacao_conservadora():
    assert classificar(Path("data/raw/maxqda/amostra_referencia.xlsx")) == "preservar_fonte"
    assert classificar(Path("data/interim/cache_llm/a.json")) == "cache_descartavel"
    assert classificar(Path("data/interim/docs/a.txt")) == "intermedio_regeneravel"
    assert (classificar(Path("results/mqda/revisto.mqda")) ==
            "possivel_trabalho_humano_preservar")
    assert (classificar(Path("results/docling_v2/projeto.qdpx")) ==
            "experiencia_preservar_ate_documentar")
    assert classificar(Path("results/validated/2025_4_08_issue0004/relatorio.txt")) == "resultado_validado_preservar"
    assert classificar(Path("results/runs/2026/2026_4_08/projeto.qdpx")) == "resultado_reproduzivel_manifestar"
    assert classificar(Path("results/benchmarks/tema-4.08/comparacoes/resultado.xlsx")) == "benchmark_reproduzivel_manifestar"
    assert classificar(Path("archive/v1/codigo.py")) == "historico_preservar"
    assert classificar(Path("vendor/projeto/LICENSE")) == "terceiro_repor_da_origem"


def test_inventario_tem_hash_e_ignora_lixo(tmp_path):
    ficheiro = tmp_path / "data" / "raw" / "fonte.txt"
    ficheiro.parent.mkdir(parents=True)
    ficheiro.write_text("conteúdo", encoding="utf-8")
    (ficheiro.parent / ".DS_Store").write_bytes(b"lixo")
    destino = tmp_path / "results" / "_inventory" / "workspace_inventory.json"

    inventario = inventariar(tmp_path, destino)

    assert inventario["summary"]["files"] == 1
    entrada = inventario["files"][0]
    assert entrada["path"] == "data/raw/fonte.txt"
    assert entrada["sha256"] == hashlib.sha256("conteúdo".encode()).hexdigest()
    assert entrada["classification"] == "preservar_fonte"
    assert "preservar_fonte" in resumo_markdown(inventario)
    json.dumps(inventario)
