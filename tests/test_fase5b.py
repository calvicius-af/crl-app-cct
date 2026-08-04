"""Testes da promoção de novidades no texto consolidado (memo 6, fecho).

Regra do CRL: no texto consolidado só releva o que mudou face à versão
anterior. A comparação diacrónica identifica as cláusulas com novidade;
as codificações nessas cláusulas sobem para AUTO/REVER, as restantes
ficam na faixa CONSOLIDADO (fonte de verdade, fora da primeira análise).
"""
from cct.extractor import estruturar
from cct.lexical import codificar
from cct.diacronia import comparar_versoes, novidades_do_consolidado
from cct.triagem import triar

ANTIGA = """Preâmbulo 2021.
Cláusula 1.ª - Registo de pessoal
O empregador mantém um registo de pessoal atualizado de cada trabalhador.
Cláusula 2.ª - Videovigilância
As câmaras destinam-se exclusivamente à proteção de pessoas e bens.
"""

# revisão parcial c/ consolidado: artigo de alteração + republicação onde
# a cláusula 1.ª mudou (prazo novo) e a 2.ª ficou igual
NOVA = """Contrato coletivo - alteração e texto consolidado.
Artigo 1.º
O presente CCT altera a convenção anterior nos seguintes termos.
Texto consolidado
CAPÍTULO I
Disposições gerais
Cláusula 1.ª - Registo de pessoal
O empregador mantém um registo de pessoal atualizado de cada trabalhador, facultando-o no prazo de 5 dias.
Cláusula 2.ª - Videovigilância
As câmaras destinam-se exclusivamente à proteção de pessoas e bens.
"""

CODEBOOK = {"tema": "t", "eixos": ["4.08.5", "4.08.2"], "codigos": [
    {"id": "4.08.5.1", "termos": ["registo de pessoal"]},
    {"id": "4.08.2.1", "termos": ["câmaras"]},
]}


def _preparar():
    doc_a, txt_a = estruturar(ANTIGA, doc_id="v2021")
    doc_n, txt_n = estruturar(NOVA, doc_id="v2025",
                              subtipo="revisao_parcial_com_consolidado")
    resultado = comparar_versoes(doc_a, txt_a, doc_n, txt_n)
    novidades = novidades_do_consolidado(resultado, doc_n)
    anot = codificar(doc_n, txt_n, CODEBOOK)
    return doc_n, resultado, novidades, anot


def test_novidades_identificadas():
    doc_n, resultado, novidades, _ = _preparar()
    c1 = next(n for n in doc_n["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))
    c2 = next(n for n in doc_n["nos"] if n["rotulo"].startswith("Cláusula 2.ª"))
    assert c1["origem"] == "consolidado" and c2["origem"] == "consolidado"
    assert c1["id"] in novidades      # alterada → novidade
    assert c2["id"] not in novidades  # igual → sem novidade


def test_triagem_promove_novidades():
    doc_n, _resultado, novidades, anot = _preparar()
    t = triar(anot, aptos={"4.08.5.1"}, doc=doc_n, novidades=novidades)
    codigos = {a["codigo"] for a in t["anotacoes"]}
    # cláusula 1 (alterada): promovida — o subcódigo calibrado vai para AUTO
    assert any(c.startswith("AUTO/4.08.5.1") for c in codigos)
    # cláusula 2 (igual): fica na faixa CONSOLIDADO
    assert any(c.startswith("CONSOLIDADO/4.08.2.1") for c in codigos)
    assert not any(c.startswith("REVER/4.08.2.1") for c in codigos)


def test_paragrafos_herdam_promocao():
    doc_n, _res, novidades, anot = _preparar()
    t = triar(anot, aptos=set(), doc=doc_n, novidades=novidades)
    # anotações de parágrafo dentro da cláusula 1 também sobem (via nó-pai)
    c1 = next(n for n in doc_n["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))
    de_c1 = [a for a in t["anotacoes"]
             if a["no_id"] == c1["id"] or a["no_id"].startswith(c1["id"] + "p")]
    assert de_c1 and all(a["codigo"].startswith("REVER/") for a in de_c1)


def test_sem_novidades_mantem_comportamento():
    doc_n, _res, _nov, anot = _preparar()
    t = triar(anot, aptos=set(), doc=doc_n)  # sem diacronia
    tematicas = [a for a in t["anotacoes"] if not a["codigo"].startswith("Estrutura/")]
    assert all(a["codigo"].startswith("CONSOLIDADO/") for a in tematicas
               if a["no_id"] != "n0")
