# ADR-0004: fases desacopladas por ficheiros, e linha de comandos antes de interface

- **Estado:** Aceite
- **Data:** 2026-07-05
- **Decidido por:** CRL (António Fula)

## Contexto

O processo tem quatro etapas com naturezas muito diferentes: extrair texto de PDF,
codificar por termos, comparar versões, triar e exportar. A extração é lenta e é onde
estão quase todos os problemas difíceis; a codificação é rápida e afina-se dezenas de
vezes.

Havia ainda a tentação de começar pela interface gráfica, por ser o que se vê.

## Decisão

Cada fase **comunica com a seguinte apenas por ficheiros** (`doc.json`, `doc.txt`,
`anotacoes.json`), com contratos validados por JSON Schema. Qualquer fase pode ser
corrida, inspecionada e repetida isoladamente.

E: **primeiro a linha de comandos, a interface depois**. Quando a interface chegou
(ver [ADR-0008](0008-interface-em-tkinter.md)), foi construída como casca fina — lança os
mesmos comandos em subprocesso e não contém lógica própria.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Pipeline em memória, de uma ponta à outra | Cada afinação do codebook obrigaria a reextrair todos os PDFs; e quando algo corre mal não há nada para inspecionar |
| Interface primeiro | A interface teria fixado decisões sobre um processo que ainda não estava compreendido |

## Consequências

- Afinar um codebook custa segundos: o texto já está extraído em `data/interim/`.
- Quando um documento sai mal, abre-se o `.txt` e o `.doc.json` e vê-se onde partiu — foi
  assim que quase todos os problemas dos gates foram diagnosticados.
- A interface e a linha de comandos não podem divergir, porque partilham 100% da lógica.
- Custo assumido: mais escritas em disco e ficheiros intermédios a gerir — daí a pasta
  `data/interim/`, inteiramente descartável.

## Revisitar quando

O volume tornar o custo de escrita em disco proibitivo (milhares de documentos por
corrida), o que hoje não acontece.
