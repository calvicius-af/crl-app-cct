# Specs

Uma **spec** descreve uma funcionalidade **antes** de ser construída: o que tem de fazer,
o que não tem de fazer, e como se saberá que está feita.

Se um ADR responde a *"porque é que isto é assim?"*, uma spec responde a *"o que vamos
construir a seguir, e como sabemos que ficou certo?"*.

## Como usar

1. Copiar `0000-template.md` para `NNNN-nome-curto.md`, com o número seguinte na sequência.
2. Escrever a spec — meia hora, não meio dia. Se não se consegue escrever o critério de
   aceitação, é sinal de que a funcionalidade ainda não está compreendida.
3. Implementar, com os testes a serem escritos a partir da secção de critérios de aceitação.
4. No fim, marcar a spec como `Implementada` e apontar os testes e os ficheiros que a
   realizam. Se pelo caminho houver uma decisão estruturante, escrever também um
   [ADR](../docs/adr/README.md).

Uma spec implementada **não se apaga**: passa a ser o registo do que se pretendia e
permite verificar, mais tarde, se o que existe ainda corresponde ao que se quis.

## Quando não escrever uma spec

Correções de erros, ajustes de codebook, mudanças de texto, refactorações sem efeito
externo. Para isso há [`issues/`](../issues/README.md).

## Contexto

Esta pasta faz parte da adoção de um fluxo *spec-driven*, ainda em avaliação —
ver [ADR-0011](../docs/adr/0011-fluxo-spec-driven.md). O espaço está preparado para as
*skills* de desenvolvimento assistido que venham a ser instaladas em `.claude/skills/`.

## Índice

| # | Spec | Estado |
|---|---|---|
| — | *(ainda nenhuma)* | — |

## Ideias por especificar

Trabalho identificado nas fases 0-5 e ainda por fazer — cada uma destas linhas será uma
spec quando chegar a sua vez:

- **Recolha automática do BTE**: descarregar os números do boletim a partir de
  `bte.gep.msess.gov.pt` em vez de os copiar à mão.
- **Numeração por extenso**: o extrator já reconhece cabeçalhos como "cláusula décima
  segunda"; falta convertê-los para número canónico na comparação diacrónica
  ([ISSUE-0001](../issues/0001-numeracao-por-extenso.md)).
- **Nível N1 — remissões**: extrair as referências entre cláusulas e entre convenções, e
  representá-las como grafo (ver [ADR-0001](../docs/adr/0001-sqlite-em-vez-de-neo4j.md)).
- **Diacronia sobre 2021/2022**: os dados existem em `data/raw/bte/`, o método está
  validado para 2025.
- **Segundo tema**: provar que o pipeline é mesmo agnóstico de temas, correndo um tema
  diferente do 4.8 de ponta a ponta.
- **Afinação dos subcódigos fracos** (4.08.1.2, 4.08.2.1, 4.08.5.3-5) com as peritas,
  pelo método de mineração de falsos negativos descrito em
  [prompts-codebooks.md](../docs/operacao/prompts-codebooks.md).
