"""Banco de ensaio de modelos locais para codificação semântica 4.08.

Amostra fixa de cláusulas com resposta conhecida (positivas do gabarito,
incluindo recondução terminológica difícil, e negativas), corrida contra
cada modelo do LM Studio. Mede: validade do JSON, acertos, falsos
positivos, e latência — a base para decidir que modelo especializar.

Uso:
  .venv/bin/python -m cct.bench_llm --modelos "microsoft/phi-4-mini-reasoning" "google/gemma-4-e2b"
"""
import argparse
import json
import time

from .semantico import backend_lmstudio, _extrair_json, PROMPT_BASE

CODEBOOK_RESUMO = """- 4.08.1.1 Dignidade, honra e reserva da vida privada: exemplos de termos: dignidade, vida privada, intimidade, honra
- 4.08.2.1 Videovigilância e controlo de instalações: exemplos de termos: videovigilância, câmaras, CCTV
- 4.08.5.1 Registo de pessoal, atualização e consulta: exemplos de termos: registo de pessoal, processo individual, cadastro
- 4.08.5.2 Dados sensíveis e saúde: exemplos de termos: exames médicos, sigilo médico, dados de saúde
- 4.08.6.1 Gestão algorítmica e IA: exemplos de termos: algoritmo, decisão automatizada, inteligência artificial"""

# (rótulo, texto, código esperado ou None)
CASOS = [
    # positivos diretos
    ("Cláusula A - Processo individual",
     "1- A empresa mantém um processo individual de cada trabalhador, que este pode consultar.",
     "4.08.5.1"),
    ("Cláusula B - Videovigilância",
     "1- As câmaras de videovigilância instaladas destinam-se exclusivamente à proteção de pessoas e bens.",
     "4.08.2.1"),
    # recondução terminológica (o teste que separa os modelos)
    ("Cláusula C - Cadastro",
     "1- A empresa organiza um cadastro individual atualizado de cada trabalhador, com os seus dados pessoais e profissionais.",
     "4.08.5.1"),
    ("Cláusula D - Livro de matrícula",
     "1- Em cada estabelecimento existirá um livro de matrícula com os elementos de identificação de todos os trabalhadores.",
     "4.08.5.1"),
    ("Cláusula E - Ficha clínica",
     "1- Os resultados dos exames de saúde são registados em ficha própria, sujeita a sigilo, só acessível ao médico do trabalho.",
     "4.08.5.2"),
    ("Cláusula F - Sistemas inteligentes",
     "1- Quando sejam usados sistemas informáticos que tomem decisões sem intervenção humana, os trabalhadores serão informados dos parâmetros.",
     "4.08.6.1"),
    ("Cláusula G - Respeito mútuo",
     "1- Empregador e trabalhador devem respeitar-se mutuamente, guardando reserva quanto à intimidade da vida privada de cada um.",
     "4.08.1.1"),
    # negativos (temas próximos mas fora do 4.08)
    ("Cláusula H - Férias",
     "1- O período anual de férias tem a duração de 22 dias úteis.",
     None),
    ("Cláusula I - Quotização",
     "1- A empresa desconta na retribuição a quota sindical e envia-a ao sindicato até ao dia 10.",
     None),
    ("Cláusula J - Comissão de vigilância",
     "1- A comissão de vigilância do fundo reúne trimestralmente para fiscalizar as contas.",
     None),
    ("Cláusula K - Trabalho suplementar",
     "1- O trabalho suplementar é pago com acréscimo de 50% na primeira hora.",
     None),
    ("Cláusula L - Exames de admissão",
     "1- Os candidatos serão submetidos a exame médico de admissão antes de iniciarem funções.",
     "4.08.5.2"),
]


def avaliar_modelo(modelo: str, base_url: str) -> dict:
    resultados = {"modelo": modelo, "casos": [], "json_invalido": 0,
                  "acertos": 0, "fp": 0, "fn": 0, "latencias": []}
    for rotulo, texto, esperado in CASOS:
        prompt = PROMPT_BASE.format(tema="4.08", codebook=CODEBOOK_RESUMO,
                                    clausulas=f"[1] {rotulo}\n{texto}")
        t0 = time.time()
        try:
            resposta = backend_lmstudio(prompt, modelo=modelo,
                                        base_url=base_url, max_tokens=6000)
        except Exception as e:
            resultados["casos"].append((rotulo, esperado, f"ERRO {e}"))
            resultados["json_invalido"] += 1
            continue
        dt = time.time() - t0
        resultados["latencias"].append(dt)
        itens = [i for i in _extrair_json(resposta) if isinstance(i, dict)]
        if "[" not in resposta:
            resultados["json_invalido"] += 1
        obtido = itens[0].get("codigo") if itens else None
        resultados["casos"].append((rotulo, esperado, obtido))
        if esperado == obtido:
            resultados["acertos"] += 1
        elif esperado is None and obtido is not None:
            resultados["fp"] += 1
        elif esperado is not None and obtido != esperado:
            resultados["fn"] += 1
    return resultados


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--modelos", nargs="+", required=True)
    p.add_argument("--base-url", default="http://127.0.0.1:1234")
    args = p.parse_args()

    for modelo in args.modelos:
        r = avaliar_modelo(modelo, args.base_url)
        lat = (sum(r["latencias"]) / len(r["latencias"])) if r["latencias"] else 0
        print(f"\n=== {modelo} ===")
        print(f"acertos: {r['acertos']}/{len(CASOS)}  FP: {r['fp']}  "
              f"erros/FN: {r['fn']}  respostas inválidas: {r['json_invalido']}  "
              f"latência média: {lat:.1f}s")
        for rotulo, esperado, obtido in r["casos"]:
            marca = "✓" if esperado == obtido else "✗"
            print(f"  {marca} {rotulo:<38} esperado={esperado or '—':<10} obtido={obtido or '—'}")


if __name__ == "__main__":
    main()
