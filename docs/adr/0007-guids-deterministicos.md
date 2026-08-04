# ADR-0007: GUIDs determinísticos e reutilização do codebook master

- **Estado:** Aceite
- **Data:** 2026-07-06
- **Decidido por:** CRL (António Fula)

## Contexto

Cada corrida do pipeline produz um novo `.qdpx`. Se os identificadores dos códigos fossem
aleatórios, o MaxQDA veria em cada importação um conjunto de códigos completamente novo:
a equipa ficaria com árvores duplicadas e sem forma de comparar o trabalho de uma ronda
com o da seguinte.

Além disso, o CRL já tem um livro de códigos oficial — 1393 códigos com nomes, cores e
descrições (definição, critérios, base legal) — exportado do MaxQDA como `.qdc`. Ignorá-lo
significaria entregar às peritas códigos sem descrição e com cores arbitrárias.

## Decisão

- Os identificadores dos códigos são **GUIDs determinísticos**, gerados por `uuid5` a
  partir de um nome estável. A mesma entidade tem sempre o mesmo GUID, em qualquer corrida.
- Quando existe codebook master (`.qdc`), o exportador **reutiliza dele o nome, a cor e a
  descrição**, cruzando por identificador numérico, por nome ou por prefixo.

## O erro que isto corrigiu

Numa versão intermédia, os GUIDs vindos do master eram reaproveitados diretamente e
**duplicavam entre faixas** (o mesmo código em `AUTO`, `REVER` e `CONSOLIDADO` recebia o
mesmo GUID), o que o MaxQDA rejeitava. A regra passou a ser: o GUID é **sempre** gerado
por `uuid5` a partir do caminho completo do código na árvore; do master vêm apenas os
atributos de apresentação.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| `uuid4` (aleatório) | Cada importação criaria códigos novos; impossível acumular trabalho entre rondas |
| Reutilizar os GUIDs do master tal como estão | Foi tentado e falhou: colide quando o mesmo código aparece em faixas diferentes |
| Não usar o master | Perde-se a nomenclatura oficial do CRL e as descrições que orientam quem codifica |

## Consequências

- Os `.qdpx` de rondas sucessivas são compatíveis entre si: v1, v2, v3 falam dos mesmos
  códigos.
- Os códigos chegam ao MaxQDA com o nome oficial, a cor e a descrição do livro de códigos
  do CRL.
- O `.qdc` do master passa a ser uma entrada relevante do sistema, embora opcional
  (ver [docs/dados](../dados/README.md)).

## Revisitar quando

O livro de códigos do CRL for reestruturado a ponto de os caminhos dos códigos mudarem —
nesse caso, é preciso decidir explicitamente o que fazer com os GUIDs antigos.
