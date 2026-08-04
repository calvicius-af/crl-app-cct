"""Testes do leitor de variáveis de documento do MaxQDA (2025)."""
from pathlib import Path

import pytest

from cct.variaveis import carregar_variaveis, subtipo_pipeline, procurar

XLSX = Path(__file__).parent.parent / "data" / "raw" / "maxqda" / "VariaveisDocumento2025.xlsx"


def test_subtipo_pipeline():
    assert subtipo_pipeline("Revisão Parcial", "Alt. salarial e outras") == "revisao_parcial"
    assert subtipo_pipeline("Revisão Parcial",
                            "Alt. salarial e outras / texto consolidado") == "revisao_parcial_com_consolidado"
    assert subtipo_pipeline("1ª Convenção", "") == "primeira_convencao"
    assert subtipo_pipeline("Revisão Global", "") == "revisao_global"
    assert subtipo_pipeline("", "") == "desconhecido"


@pytest.mark.skipif(not XLSX.exists(), reason="VariaveisDocumento2025.xlsx não disponível")
class TestReal:
    @pytest.fixture(scope="class")
    def vars_(self):
        return carregar_variaveis(XLSX)

    def test_carrega_todos(self, vars_):
        assert len(vars_) >= 270

    def test_procura_por_prefixo_trunca_maxqda(self, vars_):
        # o MaxQDA trunca nomes a ~30 chars: "25_PR_001_BTE_01_AHP_SITESE_TX"
        v = procurar(vars_, "25_PR_001_BTE_01_AHP_SITESE")
        assert v is not None
        assert v["tipo_conv"] == "CC"
        assert v["subtipo"] == "revisao_parcial"
        assert v["entidade_patronal"].startswith("AHP")

    def test_consolidado_detectado(self, vars_):
        v = procurar(vars_, "25_PR_003_BTE_02_ACIP_FESAHT")
        assert v["subtipo"] == "revisao_parcial_com_consolidado"
        assert v["cae"].startswith("C")
