# ADR-0001: SQLite como índice do corpus, não uma base de grafos

- **Estado:** Aceite
- **Data:** 2026-07-05
- **Decidido por:** CRL (António Fula), com apoio do assistente de desenvolvimento

## Contexto

A visão inicial do projeto incluía quatro níveis de análise, entre os quais o N1
(relações entre documentos, remissões entre cláusulas e entre convenções) e o N3
(ligações entre temas). Isso sugeria naturalmente uma base de dados de grafos — Neo4j
foi considerado desde o início.

Ao mesmo tempo, o problema imediato era outro e muito mais concreto: extrair texto de
PDFs do BTE com fidelidade suficiente para codificar cláusulas e devolver um projeto
importável no MaxQDA. Sem isso resolvido, nenhum nível de análise existe.

## Decisão

No MVP, o corpus é indexado em **SQLite** (ou simplesmente em ficheiros JSON, quando
chega), e não numa base de grafos. As remissões ficam registadas como dados no
`doc.json`; a sua exploração como grafo fica para uma fase posterior, se se justificar.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Neo4j desde o início | Acrescenta um servidor a instalar e manter numa instituição pública, para responder a perguntas que ainda não sabíamos formular. Custo de infraestrutura antes de haver valor demonstrado |
| Sem qualquer índice, só ficheiros | Suficiente para o MVP, e é de facto o que acontece hoje; SQLite fica como o passo seguinte natural quando o corpus crescer |

## Consequências

- A instalação no Instituto de Informática não exige servidor de base de dados: Python e
  quatro bibliotecas, tudo local (ver [ADR-0008](0008-interface-em-tkinter.md)).
- As análises N1/N3 não estão disponíveis. Continuam por fazer, e assumidamente.
- Se um dia for preciso o grafo, o `doc.json` já guarda a hierarquia e os offsets, que é a
  informação de que um grafo precisaria — a decisão não fecha portas.

## Revisitar quando

O corpus passar a milhares de convenções e as perguntas de investigação passarem a ser
sobre relações entre instrumentos (remissões, famílias de convenções, cadeias de revisão)
em vez de sobre o conteúdo de cada um.
