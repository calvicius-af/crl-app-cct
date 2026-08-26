"""Prova de integração com os tipos reais do docling (opcional).

Os testes de tests/test_extractor_docling.py usam objetos de teste, para
que a suite normal corra sem a dependência opcional. Este ficheiro
fecha a única lacuna que isso deixa: confirmar que os tipos reais do
docling têm mesmo a forma que o extrator assume — os índices de span na
grelha e o nome da origem das coordenadas.

Precisa apenas de `docling-core` (os tipos; ~30 pacotes, sem PyTorch),
não do docling completo. Sem ele, ignora-se sozinho.
"""
import pytest

pytest.importorskip("docling_core",
                    reason="docling-core não instalado (dependência opcional)")

from types import SimpleNamespace  # noqa: E402

from docling_core.types.doc import TableCell, TableData  # noqa: E402
from docling_core.types.doc.base import (BoundingBox,  # noqa: E402
                                         CoordOrigin)

from cct.extractor_docling import (_linhas_de_tabela,  # noqa: E402
                                   distancia_ao_topo, ORIGEM_INFERIOR)


def _celula(texto, li, lf, ci, cf):
    return TableCell(text=texto, row_span=lf - li, col_span=cf - ci,
                     start_row_offset_idx=li, end_row_offset_idx=lf,
                     start_col_offset_idx=ci, end_col_offset_idx=cf)


def test_grelha_real_com_rowspan():
    # o caso da revisão do PR #23, com os tipos verdadeiros
    tabela = SimpleNamespace(data=TableData(
        table_cells=[_celula("Categoria", 0, 2, 0, 1),
                     _celula("A", 0, 1, 1, 2),
                     _celula("B", 1, 2, 1, 2)],
        num_rows=2, num_cols=2))
    assert _linhas_de_tabela(tabela) == ["Categoria | A", " | B"]


def test_grelha_real_com_colspan():
    tabela = SimpleNamespace(data=TableData(
        table_cells=[_celula("Competência", 0, 1, 0, 3),
                     _celula("Encarregado geral (DI)", 0, 1, 3, 4)],
        num_rows=1, num_cols=4))
    assert _linhas_de_tabela(tabela) == ["Competência | Encarregado geral (DI)"]


def test_nome_da_origem_das_coordenadas_nao_mudou():
    # o extrator compara pelo nome para não importar docling_core
    assert CoordOrigin.BOTTOMLEFT.name == ORIGEM_INFERIOR
    assert {m.name for m in CoordOrigin} == {"TOPLEFT", "BOTTOMLEFT"}


def test_distancia_ao_topo_com_bbox_real():
    caixa = BoundingBox(l=79, t=742, r=518, b=700,
                        coord_origin=CoordOrigin.BOTTOMLEFT)
    assert distancia_ao_topo(caixa, 841.0) == pytest.approx(99.0)
    de_cima = BoundingBox(l=79, t=99, r=518, b=140,
                          coord_origin=CoordOrigin.TOPLEFT)
    assert distancia_ao_topo(de_cima, 841.0) == pytest.approx(99.0)
