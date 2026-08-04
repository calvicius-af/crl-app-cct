---
type: project
subtype: plano-aprendizagem
created: 2026-06-07
tags:
  - formacao
  - python
  - tracer
  - cct
estado: rascunho
projeto: "[[Processo de Formação Pragmática]]"
é-parte-de:
  - "[[Processo de Formação Pragmática]]"
norte:
  - "[[Referencial de competências — Python e pipeline CCT]]"
  - "[[Rubrica de avaliação — tracer PDF Python+CCT]]"
oeste:
  - "[[Análise de necessidades — Python e blueprint CCT]]"
  - "[[Decisão — v1 por tracers curtos com evidência executável]]"
---

# Plano do tracer PDF — Python e pipeline CCT

## Função

Este plano operacionaliza o primeiro ciclo da v1: aprender Python através de uma fatia pequena, completa e verificável do pipeline CCT.

O tracer não tenta resolver todo o pipeline. O seu trabalho é provar que o [[Processo de Formação Pragmática]] consegue transformar um problema real em aprendizagem estruturada com evidência.

## Resultado esperado

Um PDF real de convenção coletiva é processado localmente e gera:

- output textual ou Markdown;
- relatório curto de qualidade;
- comando de execução reproduzível;
- decisão técnica sobre a abordagem usada;
- avaliação pela rubrica;
- notas de capitalização no vault.

## Entrada

- 1 PDF real de convenção coletiva.
- Código legado ou exemplo mínimo de extração.
- Critérios de qualidade definidos na rubrica.
- Ambiente Python local.

## Saída

| Artefacto | Função |
|---|---|
| Script ou comando | Executa a extração |
| Output `.txt` ou `.md` | Material processado e inspecionável |
| Relatório de qualidade | Regista perdas, estrutura, limitações e próximos passos |
| Decisão técnica | Justifica ferramenta e formato de saída |
| Nota de capitalização | Transfere conhecimento reutilizável para o vault |

## Sequência de trabalho

### 1. Delimitar o caso

Escolher um PDF que seja suficientemente realista, mas não extremo. Evitar começar por documentos digitalizados, tabelas muito complexas ou convenções com estrutura excepcional.

**Evidência:** nota curta com o PDF escolhido, razão da escolha e localização.

### 2. Fazer inventário do legado útil

Identificar que código ou documentação existente pode ser reutilizada:

- preprocessador CCT legado;
- recomendações de implementação;
- análise de conformidade;
- documentação do pipeline IRCT;
- protótipo de codificação rápida MAXQDA.

**Evidência:** lista curta do que será usado, ignorado ou diferido.

### 3. Executar a abordagem base

Executar a abordagem mais simples disponível para extrair texto.

Opções iniciais:

- `pdfplumber`, se o objectivo for comparar com o legado;
- PyMuPDF, se o objectivo for uma rotina leve e controlável;
- Docling, se o objectivo for preservar estrutura Markdown.

**Evidência:** comando, output e primeiro erro ou sucesso.

### 4. Validar o output

Verificar manualmente uma amostra do PDF contra o output:

- início do documento;
- preâmbulo;
- primeira cláusula;
- uma cláusula intermédia;
- anexos ou tabelas, se existirem.

**Evidência:** relatório curto com achados.

### 5. Comparar ou justificar

Comparar duas abordagens se o esforço for baixo. Se não for, justificar a escolha de uma abordagem única para o primeiro ciclo.

**Evidência:** matriz curta de trade-offs.

### 6. Avaliar pela rubrica

Aplicar [[Rubrica de avaliação — tracer PDF Python+CCT]] e registar nível atingido.

**Evidência:** pontuação ou apreciação por critério.

### 7. Capitalizar

Criar notas reutilizáveis apenas quando houver conceito transferível. Candidatas:

- extração de texto de PDFs;
- critérios de qualidade em ingestão documental;
- segmentação de convenções coletivas;
- diferença entre texto extraído, Markdown estruturado e JSON rastreável.

**Evidência:** links para notas criadas ou atualizadas.

## Exercícios

| Exercício | Tipo Laurillard | Produto |
|---|---|---|
| Ler e explicar o fluxo legado | Aquisição + investigação | diagrama ou resumo operacional |
| Executar extractor num PDF | Prática | output textual |
| Comparar output com PDF original | Investigação | relatório de qualidade |
| Ajustar um parâmetro ou função | Prática | melhoria observável |
| Escrever decisão técnica | Produção | nota de decisão |
| Rever rubrica e próximo passo | Discussão/reflexão | feedback ao processo |

## Definição de pronto

O tracer está pronto quando:

- existe um output gerado a partir de PDF real;
- a execução é reproduzível por comando registado;
- o output foi avaliado contra o PDF;
- há uma decisão técnica;
- há avaliação pela rubrica;
- há pelo menos uma capitalização no vault;
- o próximo tracer ficou explicitamente definido.

## Próximo tracer provável

Depois de PDF → texto/Markdown, o tracer seguinte deve ser **segmentação jurídica mínima**: transformar texto extraído em unidades como preâmbulo, cláusulas, artigos, anexos e tabelas.
