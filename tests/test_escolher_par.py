"""Testes da seleção automática de pares para comparação diacrónica."""
import pytest

from cct.comparar import escolher_par

# candidatos: (nome, nº de caracteres do texto extraído)


def test_escolhe_completo_2025_e_anterior_completo():
    candidatos = [
        ("2023_BTE_15_NORQUIFAR.pdf", 90000),   # completo 2023? não: parcial
        ("2021_BTE_13_NORQUIFAR.pdf", 95000),   # completo 2021
        ("24122_BTE_19_NORQUIFAR.pdf", 8000),   # parcial 2024
        ("25146_BTE_23_NORQUIFAR.pdf", 100000), # completo 2025 → novo
    ]
    novo, antigo, avisos = escolher_par(candidatos)
    assert novo == "25146_BTE_23_NORQUIFAR.pdf"
    assert antigo == "2023_BTE_15_NORQUIFAR.pdf"  # o completo mais recente


def test_ignora_parciais_dos_dois_lados():
    candidatos = [
        ("AEVPadmin_2018.pdf", 80000),
        ("AEVPadmin_2022.pdf", 3000),    # parcial
        ("AEVPadmin_2023.pdf", 3600),    # parcial
        ("6_BTE_3_AEVPadministrativos.pdf", 85000),  # 2025 completo
    ]
    novo, antigo, _ = escolher_par(candidatos)
    assert novo == "6_BTE_3_AEVPadministrativos.pdf"
    assert antigo == "AEVPadmin_2018.pdf"


def test_novo_parcial_gera_aviso():
    # caso ADIPA: os candidatos de 2025 são parciais
    candidatos = [
        ("BTE_21_ADIPA.pdf", 120000),
        ("66_BTE_11_ADIPAGrossista.pdf", 6000),  # 2025 mas parcial
    ]
    novo, antigo, avisos = escolher_par(candidatos)
    assert novo == "66_BTE_11_ADIPAGrossista.pdf"
    assert antigo == "BTE_21_ADIPA.pdf"
    assert any("parcial" in a.lower() for a in avisos)


def test_anterior_sem_ano_no_nome():
    # ANIMEE: o único completo anterior não tem ano no nome
    candidatos = [
        ("BTE_23_Ass.Electron_FETESE.pdf", 100000),
        ("24143_BTE_21_ANIMEE_FE.pdf", 7000),
        ("25102_BTE_18_ANIMEE_FE.pdf", 110000),
    ]
    novo, antigo, _ = escolher_par(candidatos)
    assert novo == "25102_BTE_18_ANIMEE_FE.pdf"
    assert antigo == "BTE_23_Ass.Electron_FETESE.pdf"


def test_sem_candidato_2025_falha():
    with pytest.raises(ValueError):
        escolher_par([("2021_X.pdf", 50000), ("2023_X.pdf", 50000)])
