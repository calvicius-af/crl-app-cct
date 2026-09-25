# ISSUE-0005: programa de qualidade técnica pós-PR #23

- **Estado:** Em curso — ponto de situação a 2026-09-23 no fim deste documento
- **Data:** 2026-08-26
- **GitHub:** #24
- **Onde dói:** segurança, desempenho, manutenção e garantia de qualidade

## Objetivo

Transformar as recomendações da revisão do PR #23 em trabalho rastreável, sem
duplicar problemas já registados. O issue #24 é o objetivo agregador no GitHub;
os itens abaixo estão ligados como sub-issues nativos.

## Avaliação dos issues existentes

| Issue | Avaliação após o PR #23 |
|---|---|
| #4 | Continua adequado para exemplos reproduzíveis; deve guardar comandos, inputs, versões e resultados esperados. |
| #5 | Continua adequado para fugas de dados e segredos. A cadeia de fornecimento fica separada em #30. |
| #6 | Continua adequado para validar automaticamente ligações da documentação. |
| #7 | Continua adequado para detetar métricas e contagens documentais desatualizadas. |
| #8 | Parcialmente cumprido pela matriz do PR; permanecem os warnings e os gates de higiene do diff. |
| #13 | Mantém a validação humana PDF→TXT; não substitui a validação MaxQDA do QDPX. |
| #19 | O procedimento operacional do MaxQDA deve incorporar a prova final #31. |
| #21 | A decisão arquitetural foi tomada: Docling é complemento opcional. Os riscos residuais estão em #25, #26 e #30. |
| #22 | A abordagem do pós-processador hierárquico foi experimentada e removida por não demonstrar ganho líquido. |

As issues locais também foram reconciliadas: ISSUE-0001 está parcialmente
resolvida e continua em #28; ISSUE-0002 continua em #29; ISSUE-0003 aguarda a
prova humana #31; ISSUE-0004 fica encerrada com a aprovação do PR.

## Hierarquia consolidada

Sub-issues existentes integradas no programa: #4, #5, #6, #7 e #8.

Novas sub-issues:

- #25 — isolar e limitar a execução de PDFs e modelos Docling;
- #26 — criar baseline e orçamentos de desempenho dos extratores;
- #27 — adicionar gates estáticos, tipagem e testes de propriedades;
- #28 — normalizar cláusulas com numeração por extenso;
- #29 — corrigir blocos de título multilinha no início das convenções;
- #30 — endurecer a cadeia de fornecimento e as permissões do CI;
- #31 — validar no MaxQDA o QDPX final do extrator Docling.

## Cobertura das avaliações

- **Segurança:** #5, #25 e #30 cobrem dados, isolamento de processamento,
  dependências, proveniência e permissões do CI.
- **Desempenho:** #26 estabelece corpus, medições, memória, tempo e limiares de
  regressão comparáveis entre extratores.
- **Manutenção:** #4, #6, #7, #8 e #27 tornam exemplos, documentação, métricas,
  compatibilidade, tipagem, propriedades e higiene do repositório verificáveis.
- **Correção funcional e validação humana:** #28, #29 e #31 preservam os
  problemas concretos encontrados no corpus e na utilização do MaxQDA.

## Critérios de conclusão do programa

- todas as sub-issues têm responsável, critério verificável e evidência de
  fecho;
- os gates críticos correm automaticamente no CI e bloqueiam regressões;
- os limites de segurança e desempenho estão documentados com medições;
- a validação humana no MaxQDA confirma o artefacto final;
- documentação e exemplos deixam de depender de contagens ou passos manuais
  não verificáveis.

## Ponto de situação (2026-09-24)

| Sub-issue | Estado | O que falta |
|---|---|---|
| #4 exemplos reproduzíveis | fechada no GitHub (2026-09-24) | — |
| #5 fugas de dados e segredos | fechada no GitHub | — |
| #6 referências documentais | fechada no GitHub | — |
| #7 afirmações quantitativas | fechada no GitHub (2026-09-24) | — |
| #8 matriz Python e avisos | fechada no GitHub (2026-09-24) | — |
| #25 isolar e limitar o Docling | aberta | não tratado nesta ronda |
| #26 desempenho dos extratores | aberta | precisa de um corpus autorizado de PDF para medir |
| #27 gates estáticos | resolvida (2026-09-26) | Ruff, mypy, `git diff --check`; `Protocol` para os objetos do Docling, confirmados com os tipos reais; heurísticas de colunas nomeadas, com testes de fronteira; testes de propriedades (`tests/test_propriedades.py`). Não se adotam, com fundamento no issue: cobertura mínima em percentagem e formatação automática |
| #28 numeração por extenso | resolvida (2026-09-26) | gate com a convenção real LPFP/SJPF (BTE 29/2025); os 49 cabeçalhos sem algarismos de 2025 têm chave (ISSUE-0001) |
| #29 títulos multilinha | resolvida (2026-09-26) | nos 277 títulos de 2025: um só título partido em duas linhas passou a zero; regras do travessão no cabeçalho, do subtipo «Alteração» e do capítulo só com o número (ISSUE-0002) |
| #30 cadeia de fornecimento | fechada no GitHub | — |
| #31 validação no MaxQDA | aberta | validação humana no MaxQDA |
| #56 acesso à partilha do pacote | aberta | configuração pelo Instituto de Informática, fora do repositório |
| #58 gate de instalação Windows | resolvida no código | ISSUE-0009 a 0013 verificadas; falta repetir o gate numa estação do CRL (ISSUE-0009) |
| #45 Tkinter fora da thread principal | resolvida no código (2026-09-24) | a thread de trabalho só escreve na fila; confirmar na estação que a app termina as corridas sem erros |
| #47 linhas repetidas removidas | resolvida no código (2026-09-24) | a remoção olha só para o topo e o fundo de cada página ou coluna; confirmar comparando o TXT de uma corrida real antes e depois |
| #64 CARRISTUR sem cláusulas | resolvida (2026-09-26) | os quatro PDF estão no corpus de regressão e dizem «retificação sem articulado próprio» (ISSUE-0014) |
| #49 processamento de um documento | resolvida (2026-09-26) | `processar_documento` e `ResultadoDocumento` em `cct/pipeline_tema.py`, com a política de continuação num só sítio; artefactos iguais nos 14 PDF do corpus |

«Resolvida no código» quer dizer que o defeito está corrigido e coberto por testes, mas
que o issue tem um critério que só se confirma com pessoas, dados reais ou configuração
externa, e que por isso não deve ser fechado só com o merge.
