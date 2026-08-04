---
type: project
subtype: referencial-competencias
created: 2026-06-07
tags:
  - formacao
  - python
  - competencias
  - pipeline
estado: rascunho
projeto: "[[Processo de Formação Pragmática]]"
é-parte-de:
  - "[[Processo de Formação Pragmática]]"
norte:
  - "[[3 Cs dos objetivos de aprendizagem]]"
  - "[[Referenciais de competências]]"
oeste:
  - "[[Análise de necessidades — Python e blueprint CCT]]"
  - "[[Decisão — v1 por tracers curtos com evidência executável]]"
---

# Referencial de competências — Python e pipeline CCT

## Função

Este referencial define a competência de saída da primeira instância do [[Processo de Formação Pragmática]]: aprender Python enquanto se constrói uma fatia funcional do pipeline CCT.

Não descreve uma formação genérica em Python. Descreve o desempenho mínimo necessário para compreender, executar, avaliar e melhorar uma rotina de ingestão documental aplicada a convenções coletivas.

## Competência global de saída

No final do primeiro ciclo, o formando consegue **implementar, executar, explicar e avaliar uma rotina Python de ingestão PDF → texto/Markdown**, aplicada a uma convenção coletiva real, produzindo output reprodutível, relatório de qualidade e decisão técnica documentada.

## Objetivo pelos 3 Cs

| Componente | Formulação |
|---|---|
| Comportamento | Implementar, executar e explicar uma rotina Python de extração textual/documental |
| Contexto | Primeiro tracer do pipeline CCT, usando uma convenção coletiva real em PDF |
| Critério | Output reprodutível, texto sem perdas óbvias, preâmbulo preservado, estrutura verificável e decisão técnica documentada |

## Perfis de desempenho

| Perfil | Descrição | Evidência |
|---|---|---|
| Operador | Executa comandos, identifica inputs/outputs e interpreta erros simples | comando executado, output gerado, erro descrito |
| Construtor | Altera ou cria código com critérios explícitos de qualidade | script ou função ajustada, teste simples, comparação entre abordagens |
| Metodólogo | Liga decisões técnicas à qualidade analítica e à rastreabilidade do projeto CCT | nota de decisão, relatório de qualidade, trade-offs justificados |

## Níveis de proficiência

| Nível | Desempenho observável |
|---|---|
| Assistido | Consegue executar uma rotina existente com instruções e explicar o que entrou e saiu |
| Autónomo | Consegue adaptar a rotina a um novo PDF, resolver erros simples e produzir relatório curto |
| Robusto | Consegue comparar abordagens, criar critérios de validação e justificar a escolha técnica |

## Componentes de competência

| Componente | Competência | Evidência mínima |
|---|---|---|
| Saber | Compreender ficheiros, paths, ambientes Python, bibliotecas de PDF e formatos abertos | nota curta com exemplos e glossário operacional |
| Saber-fazer | Extrair texto de PDF, guardar output, registar erros e comparar resultados | script executável e output versionável |
| Saber-agir | Escolher entre abordagem simples e abordagem estruturada conforme o uso analítico | decisão documentada com trade-offs |
| Poder agir | Ter ambiente local, PDF de teste e critérios de qualidade definidos | setup reproduzível e comando registado |
| Querer agir | Manter ligação explícita ao problema CCT para evitar aprendizagem avulsa | reflexão curta no fim do tracer |

## Mapeamento leve para referenciais

| Eixo | Formulação local |
|---|---|
| ESCO leve | `esco::software development`, `esco::data processing`, `esco::document management`, `esco::quality assurance` |
| EQF aproximado | Entre nível 4 e 5 no primeiro ciclo: aplicação autónoma em contexto conhecido, com resolução de problemas previsíveis |
| Transferência | A competência é transferível para outros documentos jurídicos, relatórios, PDFs administrativos e corpus textuais |

## Critérios de saída do primeiro ciclo

- Executa o tracer sem depender de geração avulsa de código.
- Explica o papel de cada ficheiro produzido.
- Identifica perdas, artefactos ou falhas de estrutura no output.
- Compara pelo menos duas abordagens ou justifica porque só uma foi testada.
- Regista uma decisão técnica curta.
- Capitaliza pelo menos dois conceitos reutilizáveis no vault.

## Lacunas a fechar

- Escolha do PDF real de teste.
- Localização definitiva do código novo ou adaptado.
- Critérios de qualidade quantitativos para o primeiro output.
- Forma canónica de guardar outputs intermédios: `.txt`, `.md`, `.json` ou combinação.

## Próximo artefacto

Executar [[Plano do tracer PDF — Python e pipeline CCT]] e avaliar com [[Rubrica de avaliação — tracer PDF Python+CCT]].
