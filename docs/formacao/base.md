---
type: project
created: 2026-06-07
tags:
  - formacao
  - design-instrucional
  - meta-processo
  - processo
estado: rascunho
projeto: "[[Processo de Formação Pragmática]]"
é-parte-de:
  - "[[Processo de Formação Pragmática]]"
norte:
  - "[[Processo de Formação Pragmática]]"
  - "[[MOC — Aprendizagem e Design Instrucional]]"
oeste:
  - "[[Conversational Framework]]"
  - "[[3 Cs dos objetivos de aprendizagem]]"
  - "[[Referenciais de competências]]"
---

# Processo de Formação Pragmática — Base operacional

## Premissa

Este projeto não é um curso específico. É um processo para transformar um problema real numa formação estruturada, com produção de artefactos reutilizáveis e capitalização no vault.

Na v1, o processo prova-se num caso-âncora: aprender Python enquanto se implementa o `blueprint_cct_maxqda_pipeline` v2. O domínio CCT já existe como contexto; a lacuna principal é técnica e pedagógica.

## Restrições vinculativas

- Reaproveitar o que já existe no vault antes de gerar material novo.
- Manter a v1 em Markdown no vault; LMS, SCORM, H5P e design visual ficam para v2.
- Formular competências e objetivos com os [[3 Cs dos objetivos de aprendizagem]].
- Desenhar exercícios com variedade segundo a [[Conversational Framework]].
- Avaliar por desempenho: o código funcional e os critérios de sucesso do blueprint contam como evidência de aprendizagem.
- Capitalizar o que for aprendido em notas atómicas e MOCs, não apenas em documentos de projeto.

## Ciclo operacional

| Etapa | Pergunta orientadora | Entrada | Saída mínima da v1 |
|---|---|---|---|
| 1. Análise | Que problema real justifica aprender isto agora? | objetivo pragmático + contexto + lacunas | diagnóstico de necessidades |
| 2. Desenho | Que competência observável deve existir no fim? | diagnóstico + 3 Cs + referencial | objetivos, níveis e evidências |
| 3. Desenvolvimento | Que exercícios fazem a ponte entre saber e fazer? | referencial + blueprint | plano de atividades e exercícios |
| 4. Implementação | Como se executa a formação sem LMS? | plano de atividades | sequência em Markdown no vault |
| 5. Avaliação | Como sei que aprendi e transferi? | critérios de sucesso + rubrica | avaliação por desempenho |
| 6. Capitalização | O que passa a ser conhecimento reutilizável? | notas de trabalho + fontes | notas atómicas, decisões e MOC |

## Walking skeleton da v1

1. Escolher uma fatia fina do blueprint CCT: extração PDF como primeiro tracer.
2. Escrever um objetivo de aprendizagem com comportamento, contexto e critério.
3. Mapear a competência de saída com níveis simples: assistido, autónomo, robusto.
4. Criar um exercício de prática com evidência executável.
5. Avaliar a evidência contra uma rubrica curta.
6. Registar a aprendizagem em notas do vault e rever a etapa seguinte.

## Definição de pronto

Uma etapa está pronta quando tem:

- entrada explícita;
- saída escrita no vault;
- critério de sucesso verificável;
- ligação ao projeto-hub;
- decisão registada se houver escolha estrutural;
- pelo menos uma ligação de capitalização quando gerar conhecimento reutilizável.

## Riscos vivos

- Excesso de ambição: proteger a v1 de infraestrutura prematura.
- Duplicação: o projeto deve envolver o blueprint CCT, não o recriar.
- Expert técnico frágil: só instanciar skill/persona depois de construir contexto suficiente.
- Confusão terminológica: resolver a sobreposição de alias "CCT" entre contrato coletivo e convenções coletivas.

## Próximas ações

- [x] Redigir a análise de necessidades da formação Python+CCT.
- [x] Fixar o primeiro objetivo de aprendizagem com os 3 Cs.
- [ ] Extrair do blueprint CCT os critérios de sucesso do tracer PDF.
- [x] Criar a primeira rubrica de avaliação por desempenho.
- [ ] Identificar fontes técnicas autorizadas para construir o expert Python.

## Avanço validado em 2026-06-07

Foi validada a decisão [[Decisão — v1 por tracers curtos com evidência executável]].

Artefactos operacionais iniciados:

- [[Referencial de competências — Python e pipeline CCT]]
- [[Plano do tracer PDF — Python e pipeline CCT]]
- [[Rubrica de avaliação — tracer PDF Python+CCT]]

O próximo passo operacional é escolher o PDF real do primeiro tracer e extrair do blueprint CCT os critérios de sucesso aplicáveis à ingestão PDF → texto/Markdown.
