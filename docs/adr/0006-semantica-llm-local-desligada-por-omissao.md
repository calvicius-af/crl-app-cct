# ADR-0006: camada semântica por LLM local, desligada por omissão

- **Estado:** Aceite
- **Data:** 2026-07-06
- **Decidido por:** CRL (António Fula)

## Contexto

A codificação lexical falha onde a linguagem varia: uma cláusula que fala de "cadastro
individual do trabalhador" não é apanhada por um codebook que só conhece "registo de
pessoal". Vinte e sete falsos negativos do subcódigo 4.08.5.1 eram exatamente disto.

Um modelo de linguagem podia resolver estes casos por semelhança de sentido. Mas
introduzir um LLM num processo institucional levanta três questões: envio de documentos
para fora, custo, e — a mais séria — se de facto melhora.

## Decisão

Existe uma camada semântica opcional (`cct/semantico.py`), com estas propriedades:

- **Local, nunca remota**: fala com o LM Studio em `127.0.0.1:1234`. O sistema continua
  offline por omissão; este é o único tráfego de rede possível, e é dentro da máquina.
- **Só onde a lexical não chegou**: aplica-se apenas às cláusulas sem anotação, em lotes,
  com cache por hash — reexecutar não repete trabalho.
- **Validada contra o codebook**: um código inventado pelo modelo é descartado.
- **Sempre em `REVER`**, nunca em `AUTO`.
- **Desligada por omissão.** Ativa-se com `--semantica`.

## O gate, e porque a decisão é esta

A camada foi avaliada com o mesmo harness usado para tudo o resto:

| Modelo | Resultado |
|---|---|
| DeepSeek R1 8B | **falhou**: 0 verdadeiros positivos novos, +7 falsos positivos |
| Amália 9B | inútil na tarefa: devolve sempre lista vazia em lotes |
| gemma-4-e2b | **passou**: +1 verdadeiro positivo, 0 falsos positivos novos |

Num banco de ensaio com 12 casos construídos (incluindo negativos armadilhados), o
gemma-4-e2b acertou 12/12 e o DeepSeek R1 3/12, devolvendo códigos-pai e códigos
inventados.

O ganho real do período não veio do LLM: veio de **ler os falsos negativos e acrescentar
ao codebook as variantes morfológicas em falta** — 4.08.5.1 subiu de F1 0,72 para 0,84.
Esse método é replicável, barato e auditável; o LLM, neste momento, não é melhor do que
isso.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| API remota (Claude, GPT) | Envio de documentos de trabalho do CRL para fora, custo recorrente, dependência de terceiros |
| Embeddings puros | Testado conceptualmente e rejeitado: não distinguem os subcódigos, que dependem de contexto jurídico fino |
| Ligar a camada por omissão | Não passou o critério: um modelo que acrescenta falsos positivos custa tempo às peritas |

## Consequências

- Quem quiser experimentar liga o LM Studio, escolhe um modelo e acrescenta `--semantica`.
- A instalação normal não precisa de LLM nenhum, o que simplifica o parecer do Instituto
  de Informática.
- O banco de ensaio (`cct/bench_llm.py`) fica como régua para avaliar modelos futuros.

## Revisitar quando

Um modelo local disponível passar o gate com ganho claro (vários verdadeiros positivos
novos, zero falsos positivos) numa corrida completa e não apenas em dois lotes.
