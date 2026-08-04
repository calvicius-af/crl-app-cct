# ADR-0003: codebooks em YAML — configuração é dados, não código

- **Estado:** Aceite
- **Data:** 2026-07-05
- **Decidido por:** CRL (António Fula)

## Contexto

O que define a codificação de um tema — os termos que identificam uma cláusula sobre
proteção de dados, as condições que distinguem um subcódigo de outro — é conhecimento da
equipa de análise, não do informático. E muda: à medida que as peritas revêem os
resultados, aparecem variantes que faltavam.

Se esse conhecimento viver dentro de ficheiros `.py`, cada afinação passa a exigir
alguém que saiba programar, e cada erro de sintaxe parte o programa todo.

## Decisão

Os temas de codificação são **ficheiros YAML** em `codebooks/`, um por tema, com os
códigos, os termos, e as condições de contexto (`requer_algum`, `excluir`). O código do
pipeline **não conhece nenhum tema**: recebe um YAML e aplica-o.

Acrescentar um tema novo é escrever um ficheiro YAML. Não se toca em Python.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Termos e regras em Python | Prende cada afinação a quem programa; um erro de sintaxe parte a aplicação inteira |
| Base de dados com interface de edição | Muito mais trabalho, e perde-se a coisa mais útil: um codebook em YAML vê-se num diff do Git, linha a linha |
| JSON | Igualmente válido, mas mais hostil a quem escreve à mão (sem comentários, vírgulas obrigatórias) |

## Consequências

- A equipa de análise mantém os codebooks sem intervenção informática; o
  [guia de prompts](../operacao/prompts-codebooks.md) inclui o formato e um procedimento
  em quatro passos para minerar termos em falta a partir dos falsos negativos.
- O histórico de afinações do codebook fica visível no Git, tema a tema.
- Em troca, um YAML mal formado só dá erro quando se corre o pipeline — mitigado por
  validação e por uma mensagem de erro em português.

## Revisitar quando

Os codebooks passarem a precisar de lógica que o YAML não exprime (por exemplo, condições
com aritmética ou dependências entre documentos).
