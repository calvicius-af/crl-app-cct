"""Testes do comparador diacrónico (Fase 5) — classificador =/alteração/novo do CRL."""
from cct.extractor import estruturar
from cct.diacronia import comparar_versoes

ANTIGA = """Preâmbulo da versão de 2021.
Cláusula 1.ª - Âmbito
O presente CCT obriga as empresas do setor e os trabalhadores ao seu serviço.
Cláusula 2.ª - Vigência
O CCT vigora por 24 meses a contar da publicação.
Cláusula 3.ª - Subsídio de refeição
O subsídio de refeição é de 6,00 euros por dia de trabalho.
Cláusula 4.ª - Diuturnidades
Os trabalhadores têm direito a diuturnidades de 20 euros.
Cláusula 5.ª - Comissão paritária
A comissão paritária é composta por quatro elementos.
"""

NOVA = """Preâmbulo da versão de 2025.
Cláusula 1.ª - Âmbito
O presente CCT obriga as empresas do setor e os trabalhadores ao seu serviço.
Cláusula 2.ª - Vigência
O CCT vigora por 12 meses a contar da publicação, renovando-se automaticamente.
Cláusula 3.ª - Subsídio de refeição
O subsídio de refeição é de 7,50 euros por dia de trabalho.
Cláusula 4.ª - Teletrabalho
O regime de teletrabalho depende de acordo escrito entre as partes.
Cláusula 5.ª - Antiguidade
Os trabalhadores têm direito a diuturnidades de 20 euros.
"""


def _comparar():
    doc_a, txt_a = estruturar(ANTIGA, doc_id="v2021")
    doc_n, txt_n = estruturar(NOVA, doc_id="v2025")
    return comparar_versoes(doc_a, txt_a, doc_n, txt_n)


def test_igual():
    r = _comparar()
    c1 = next(x for x in r["clausulas"] if x["rotulo_novo"] == "Cláusula 1.ª - Âmbito")
    assert c1["classificacao"] == "="


def test_alteracao_com_diff():
    r = _comparar()
    c2 = next(x for x in r["clausulas"] if x["rotulo_novo"] == "Cláusula 2.ª - Vigência")
    assert c2["classificacao"] == "alteracao"
    assert "12 meses" in c2["diff"] and "24 meses" in c2["diff"]
    c3 = next(x for x in r["clausulas"] if "Subsídio" in (x["rotulo_novo"] or ""))
    assert c3["classificacao"] == "alteracao"
    assert 0 < c3["semelhanca"] < 1


def test_nova_clausula():
    r = _comparar()
    c4 = next(x for x in r["clausulas"] if x["rotulo_novo"] == "Cláusula 4.ª - Teletrabalho")
    assert c4["classificacao"] == "nova"
    assert c4["rotulo_antigo"] is None


def test_renumeracao_recuperada_por_conteudo():
    # a cláusula das diuturnidades passou de 4.ª para 5.ª com título diferente:
    # deve emparelhar pelo conteúdo, não ficar nova+removida
    r = _comparar()
    c5 = next(x for x in r["clausulas"] if x["rotulo_novo"] == "Cláusula 5.ª - Antiguidade")
    assert c5["classificacao"] == "="
    assert c5["rotulo_antigo"] == "Cláusula 4.ª - Diuturnidades"
    assert c5["renumerada"] is True


def test_removida():
    r = _comparar()
    rem = [x for x in r["clausulas"] if x["classificacao"] == "removida"]
    assert len(rem) == 1
    assert rem[0]["rotulo_antigo"] == "Cláusula 5.ª - Comissão paritária"


def test_resumo():
    r = _comparar()
    assert r["resumo"] == {"=": 2, "alteracao": 2, "nova": 1, "removida": 1}
