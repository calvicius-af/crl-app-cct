"""Testes do localizador de convenções nos números do BTE."""
from pathlib import Path

import pytest

from cct.localizador import (interpretar_doc_id, encontrar_convencao,
                             caminho_bte, _subtokens)

PASTA_BTE = Path(__file__).parent.parent / "data" / "raw" / "bte"


def test_interpretar_doc_id():
    ano, bte, tokens = interpretar_doc_id("25_PR_016_BTE_04_EMARP_SINTAP_TXT")
    assert (ano, bte) == (25, 4)
    assert "emarp" in tokens and "sintap" in tokens


@pytest.mark.parametrize("familia", ["PR", "PE", "AV", "AA"])
def test_interpretar_doc_id_aceita_qualquer_familia_de_duas_letras(familia):
    """cct.nomeacao nomeia extensões/avisos/adesões com PE/AV/AA, não só PR
    (ver TOKEN_FAMILIA em cct/nomeacao.py) — o localizador tem de os aceitar."""
    ano, bte, tokens = interpretar_doc_id(f"26_{familia}_001_BTE_31_ANX_SNY")
    assert (ano, bte) == (26, 31)
    assert tokens == ["anx", "sny"]


def test_subtokens_camel_case():
    assert _subtokens("AguasRibatejo") == ["aguas", "ribatejo"]
    assert _subtokens("STAL") == ["stal"]


def test_caminho_bte():
    p = caminho_bte(Path("/x/bte"), "25_PR_251_BTE_41_AguasRibatejo_STAL_TXT")
    assert str(p).endswith("bte_2025/bte41_2025.pdf")


@pytest.mark.skipif(not (PASTA_BTE / "bte_2025" / "bte4_2025.pdf").exists(),
                    reason="PDFs do BTE não disponíveis")
def test_encontrar_emarp_no_bte4():
    conv = encontrar_convencao(PASTA_BTE / "bte_2025" / "bte4_2025.pdf",
                               "25_PR_016_BTE_04_EMARP_SINTAP_TXT")
    assert conv is not None
    assert "EMARP" in conv["titulo"]
    assert conv["pontuacao"] >= 0.5
    assert conv["pag_fim"] > conv["pag_ini"]
