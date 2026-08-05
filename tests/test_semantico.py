"""Testes da camada semântica (Fase 4) — backend simulado, sem API.

O LLM só vê cláusulas sem anotação lexical; responde JSON com
{rotulo, codigo, confianca, justificacao}. As respostas são cacheadas.
"""
import json

import pytest

from cct.extractor import estruturar
from cct.semantico import _montar_lotes, _validar_url_local, backend_lmstudio, codificar_semantico

EXEMPLO = """Preâmbulo.
Cláusula 1.ª - Cadastro
1- A empresa organiza um cadastro individual atualizado de cada trabalhador.
Cláusula 2.ª - Férias
1- O período anual de férias é de 22 dias úteis.
"""

CODEBOOK = {
    "tema": "4.08",
    "eixos": ["4.08.5"],
    "codigos": [
        {"id": "4.08.5.1", "nome": "Registo de pessoal",
         "termos": ["registo de pessoal", "processo individual"]},
    ],
}


def _backend_simulado(prompt: str) -> str:
    # devolve o código certo para a cláusula do cadastro (sinónimo que o
    # lexical não conhece) e nada para a cláusula de férias
    assert "4.08.5.1" in prompt          # o codebook segue no prompt
    assert "Cadastro" in prompt          # a cláusula candidata também
    return json.dumps([{"rotulo": "Cláusula 1.ª - Cadastro",
                        "codigo": "4.08.5.1", "confianca": 0.8,
                        "justificacao": "cadastro individual = registo de pessoal"}])


def test_so_clausulas_sem_anotacao_vao_ao_llm(tmp_path):
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    ja_anotadas = set()  # nenhuma anotação lexical
    anot = codificar_semantico(doc, texto, CODEBOOK, backend=_backend_simulado,
                               nos_ja_anotados=ja_anotadas, cache_dir=tmp_path)
    codigos = [(a["codigo"], a["nivel"]) for a in anot["anotacoes"]]
    assert ("4.08.5.1", "clausula") in codigos
    assert ("4.08.5", "clausula") in codigos  # eixo propagado
    a = next(x for x in anot["anotacoes"] if x["codigo"] == "4.08.5.1")
    assert a["metodo"] == "llm"
    assert "cadastro" in a["evidencia"].lower()


def test_clausulas_anotadas_sao_excluidas(tmp_path):
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    cl1 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))

    def backend_sem_cl1(prompt: str) -> str:
        assert "Cadastro" not in prompt
        return "[]"

    anot = codificar_semantico(doc, texto, CODEBOOK, backend=backend_sem_cl1,
                               nos_ja_anotados={cl1["id"]}, cache_dir=tmp_path)
    assert anot["anotacoes"] == []


def test_cache_evita_segunda_chamada(tmp_path):
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    chamadas = []

    def backend(prompt):
        chamadas.append(1)
        return "[]"

    for _ in range(2):
        codificar_semantico(doc, texto, CODEBOOK, backend=backend,
                            nos_ja_anotados=set(), cache_dir=tmp_path)
    assert len(chamadas) == 1


def test_lotes_respeitam_limite():
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    candidatas = [n for n in doc["nos"] if n["tipo"] == "clausula"]
    lotes = _montar_lotes(candidatas, texto, max_chars=60)
    assert len(lotes) == 2  # cada cláusula excede o limite sozinha


def test_resposta_invalida_ignorada(tmp_path):
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    anot = codificar_semantico(doc, texto, CODEBOOK,
                               backend=lambda p: "isto não é JSON",
                               nos_ja_anotados=set(), cache_dir=tmp_path)
    assert anot["anotacoes"] == []


def test_array_de_strings_ignorado(tmp_path):
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    anot = codificar_semantico(doc, texto, CODEBOOK,
                               backend=lambda p: '["4.08.5.1", "coisa"]',
                               nos_ja_anotados=set(), cache_dir=tmp_path)
    assert anot["anotacoes"] == []


def test_codigo_fora_do_codebook_rejeitado(tmp_path):
    doc, texto = estruturar(EXEMPLO, doc_id="t")
    resposta = json.dumps([{"rotulo": "Cláusula 1.ª - Cadastro",
                            "codigo": "9.99.9", "confianca": 0.9,
                            "justificacao": "inventado"}])
    anot = codificar_semantico(doc, texto, CODEBOOK, backend=lambda p: resposta,
                               nos_ja_anotados=set(), cache_dir=tmp_path)
    assert anot["anotacoes"] == []


@pytest.mark.parametrize("url", ["http://127.0.0.1:1234", "http://localhost:1234",
                                  "http://[::1]:1234"])
def test_backend_so_aceita_urls_loopback(url):
    assert _validar_url_local(url) == url


def test_backend_recusa_destino_remoto_antes_de_ligar():
    with pytest.raises(ValueError, match="destinos remotos"):
        backend_lmstudio("teste", modelo="local", base_url="https://api.exemplo.pt")
