"""Número canónico das cláusulas (ISSUE-0001, issue #28).

O extrator já reconhecia «Cláusula décima segunda»; faltava dar-lhe o número
12, para que a comparação diacrónica a emparelhe com a «Cláusula 12.ª» de
outra versão. E a letra de inserção («16.ª-A») passa a distinguir a cláusula
inserida da original.
"""
import pytest

from cct.diacronia import comparar_versoes
from cct.extractor import estruturar
from cct.numeracao import chave_numero, ordinal_por_extenso


@pytest.mark.parametrize("texto,valor", [
    ("primeira", 1), ("segundo", 2), ("terceira", 3), ("quarta", 4),
    ("quinta", 5), ("sexta", 6), ("sétima", 7), ("setima", 7), ("oitava", 8),
    ("nona", 9), ("décima", 10), ("décima segunda", 12), ("DÉCIMA SEGUNDA", 12),
    ("vigésima primeira", 21), ("trigésima", 30), ("quadragésima quinta", 45),
    ("nonagésima nona", 99), ("septuagésima", 70), ("setuagésima", 70),
    ("centésima", 100), ("centésima vigésima primeira", 121),
])
def test_ordinais_por_extenso(texto, valor):
    assert ordinal_por_extenso(texto) == valor


@pytest.mark.parametrize("texto", [
    "geral", "geral e transitória", "primeira décima", "décima décima",
    "", "12", "prévia",
])
def test_nao_sao_ordinais(texto):
    assert ordinal_por_extenso(texto) is None


@pytest.mark.parametrize("rotulo,chave", [
    ("Cláusula 12.ª - Horário", "cl12"),
    ("Cláusula décima segunda - Horário", "cl12"),
    ("CLÁUSULA DÉCIMA SEGUNDA - Horário", "cl12"),
    ("Cláusula décima segunda", "cl12"),
    ("Cláusula 16.ª-A - Férias", "cl16A"),
    ("Cláusula 16.ª - Férias", "cl16"),
    ("Artigo 3.º - Vigência", "ar3"),
    ("Artigo terceiro - Vigência", "ar3"),
    ("Artigo único - Âmbito", "arunico"),
    ("Cláusula única", "clunico"),
    ("Cláusula prévia - Âmbito da revisão", "clprevia"),
    ("Cláusula geral e transitória", None),
    ("PREÂMBULO", None),
    ("CAPÍTULO I - Disposições gerais", None),
])
def test_chave_numero(rotulo, chave):
    assert chave_numero(rotulo) == chave


def test_a_chave_coincide_com_os_rotulos_que_o_extrator_produz():
    doc, _ = estruturar("Cláusula décima segunda - Horário\nTexto.\n"
                        "Cláusula 16.ª-A - Férias\nTexto.\n"
                        "Artigo único - Âmbito\nTexto.\n", "x")
    chaves = [chave_numero(n["rotulo"]) for n in doc["nos"]
              if n["tipo"] in ("clausula", "artigo")]
    assert chaves == ["cl12", "cl16A", "arunico"]


def _comparar(antiga, nova):
    doc_a, txt_a = estruturar(antiga, doc_id="antiga")
    doc_n, txt_n = estruturar(nova, doc_id="nova")
    return comparar_versoes(doc_a, txt_a, doc_n, txt_n)["clausulas"]


def test_extenso_e_algarismos_emparelham_pelo_numero():
    """Critério de aceitação do #28: a mesma cláusula, escrita como «décima
    segunda» numa versão e «12.ª» na outra, emparelha pelo número — mesmo com
    o texto muito reescrito, que a passagem por conteúdo não apanharia."""
    antiga = ("Cláusula décima segunda - Horário de trabalho\n"
              "O período normal de trabalho é de quarenta horas semanais, "
              "distribuídas de segunda a sexta-feira.\n")
    nova = ("Cláusula 12.ª - Horário de trabalho\n"
            "Os trabalhadores cumprem trinta e cinco horas, com banco de horas "
            "anual e adaptabilidade grupal nos termos da lei.\n")
    [c] = _comparar(antiga, nova)
    assert c["classificacao"] == "alteracao"
    assert c["rotulo_antigo"] == "Cláusula décima segunda - Horário de trabalho"
    assert c["rotulo_novo"] == "Cláusula 12.ª - Horário de trabalho", \
        "o rótulo fica como está no documento"


def test_clausula_inserida_nao_rouba_o_numero_da_original():
    """Antes, «16.ª-A» e «16.ª» tinham a mesma chave (16): se a versão nova
    revogasse a 16.ª e mantivesse a 16.ª-A, esta era emparelhada com a 16.ª
    antiga, pelo título igual, em vez de com a 16.ª-A."""
    antiga = ("Cláusula 16.ª - Férias\nO período anual de férias é de 22 dias úteis.\n"
              "Cláusula 16.ª-A - Férias\nAcrescem três dias por assiduidade.\n")
    nova = "Cláusula 16.ª-A - Férias\nAcrescem três dias por assiduidade.\n"
    resultado = _comparar(antiga, nova)
    inserida = next(c for c in resultado if c["rotulo_novo"])
    assert inserida["rotulo_antigo"] == "Cláusula 16.ª-A - Férias"
    assert inserida["classificacao"] == "="
    assert any(c["rotulo_antigo"] == "Cláusula 16.ª - Férias"
               and c["classificacao"] == "removida" for c in resultado)
