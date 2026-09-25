"""Testes de propriedades: invariantes sobre documentos gerados ao acaso (#27).

Os outros testes fixam casos; estes fixam leis. Geram-se centenas de
documentos com cabeçalhos, corpo, listas e tabelas misturados ao acaso, e
verifica-se, em cada um, o que nunca pode falhar:

1. zero perda: as folhas da estrutura cobrem o texto final, sem buracos nem
   sobreposições, e cada nó cabe no texto;
2. o espaçamento do QDPX é reversível: tirando as quebras inseridas, volta o
   texto canónico, e cada intervalo remapeado volta ao seu trecho;
3. no QDPX real, relido do zip, cada seleção é o texto do seu nó.

Não se usa uma biblioteca de propriedades (seria uma dependência nova): o
gerador é o `random` com sementes fixas, para que uma falha se reproduza
sempre igual. Com `PROPRIEDADES_CASOS` no ambiente corre-se com mais casos.
"""
import os
import random

import pytest

from cct.extractor import MARCA_TABELA_FIM, MARCA_TABELA_INI, estruturar
from cct.qdpx import _remapear, espacar, indices_inseridos, pontos_de_espacamento, verificar_offsets

CASOS = int(os.environ.get("PROPRIEDADES_CASOS", "150"))

PALAVRAS = ("trabalhador", "empresa", "retribuição", "férias", "horário", "cláusula",
            "subsídio", "nível", "anexo", "artigo", "secção", "presente", "acordo")


def _frase(r: random.Random, fim: str = ".") -> str:
    palavras = [r.choice(PALAVRAS) for _ in range(r.randint(1, 14))]
    return palavras[0].capitalize() + " " + " ".join(palavras[1:]) + fim


def _linha(r: random.Random, numero: list[int]) -> list[str]:
    tipo = r.choice(["clausula", "artigo", "capitulo", "seccao", "anexo", "corpo",
                     "corpo", "corpo", "lista", "tabela", "titulo", "vazia"])
    numero[0] += 1
    n = numero[0]
    if tipo == "clausula":
        return [f"Cláusula {n}.ª" + r.choice(["", f" - {_frase(r, '')}"])]
    if tipo == "artigo":
        return [f"Artigo {n}.º", _frase(r, "")]
    if tipo == "capitulo":
        return [f"CAPÍTULO {r.choice(['I', 'II', 'IV', 'X'])} - {_frase(r, '')}"]
    if tipo == "seccao":
        return [f"SECÇÃO {r.choice(['I', 'II'])}"]
    if tipo == "anexo":
        return [f"ANEXO {r.choice(['I', 'II', 'III', 'II-A'])}", _frase(r, "")]
    if tipo == "lista":
        return [f"{r.choice(['a)', 'b)', '1-', '2-', '-'])} {_frase(r, r.choice(['.', ';', ',']))}"]
    if tipo == "tabela":
        return [MARCA_TABELA_INI,
                *(" | ".join(r.choice(PALAVRAS) for _ in range(r.randint(2, 4)))
                  for _ in range(r.randint(1, 4))),
                MARCA_TABELA_FIM]
    if tipo == "titulo":
        return [_frase(r, "")]
    if tipo == "vazia":
        return [""]
    return [_frase(r, r.choice([".", ".", ":", ";", ""]))]


def _documento(semente: int) -> str:
    r = random.Random(semente)
    numero = [0]
    linhas = ["PRIVADO", "CONVENÇÕES COLETIVAS",
              f"Acordo de empresa entre a {r.choice(PALAVRAS)} e o sindicato - Revisão global"]
    for _ in range(r.randint(1, 40)):
        linhas.extend(_linha(r, numero))
    return "\n".join(linhas) + "\n"


@pytest.mark.parametrize("semente", range(CASOS))
def test_folhas_cobrem_o_texto_sem_buracos(semente):
    doc, final = estruturar(_documento(semente), f"d{semente}")
    folhas = sorted((n for n in doc["nos"] if n.get("folha", True)),
                    key=lambda n: n["char_start"])
    assert folhas and folhas[0]["char_start"] == 0
    for a, b in zip(folhas, folhas[1:]):
        assert a["char_end"] == b["char_start"], (a["rotulo"], b["rotulo"])
    assert folhas[-1]["char_end"] == len(final)
    for n in doc["nos"]:
        assert 0 <= n["char_start"] <= n["char_end"] <= len(final)


@pytest.mark.parametrize("semente", range(CASOS))
def test_espacamento_do_qdpx_e_reversivel(semente):
    r = random.Random(semente)
    doc, final = estruturar(_documento(semente), f"d{semente}")
    pontos = pontos_de_espacamento(final, doc)
    espacado = espacar(final, pontos)
    inseridos = set(indices_inseridos(pontos))
    assert "".join(c for i, c in enumerate(espacado) if i not in inseridos) == final
    for _ in range(20):
        ini = r.randint(0, max(0, len(final) - 1))
        fim = r.randint(ini + 1, len(final)) if len(final) > ini else ini
        a, b = _remapear(ini, fim, pontos)
        assert "".join(c for i, c in enumerate(espacado[a:b], start=a)
                       if i not in inseridos) == final[ini:fim]


@pytest.mark.parametrize("semente", range(0, CASOS, 5))
def test_selecoes_do_qdpx_real_sao_o_texto_de_cada_no(semente):
    doc, final = estruturar(_documento(semente), f"d{semente}")
    assert verificar_offsets(doc, final) == []
