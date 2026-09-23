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

## Ponto de situação (2026-09-23)

| Sub-issue | Estado | O que falta |
|---|---|---|
| #4 exemplos reproduzíveis | resolvida no código | nada no código; o README dos exemplos distingue executar, verificar e reproduzir, e `tests/test_exemplos.py` confirma os números que ele afirma |
| #5 fugas de dados e segredos | fechada no GitHub | — |
| #6 referências documentais | fechada no GitHub | — |
| #7 afirmações quantitativas | resolvida no código | nada; a matriz do CI deixou de ser repetida nos documentos |
| #8 matriz Python e avisos | resolvida no código | nada; o CI cobre Linux, macOS e Windows, e os avisos do código do projeto fazem falhar a suite |
| #25 isolar e limitar o Docling | aberta | não tratado nesta ronda |
| #26 desempenho dos extratores | aberta | precisa de um corpus autorizado de PDF para medir |
| #27 gates estáticos | em curso | feito: Ruff, mypy no pacote `cct`, `git diff --check`; falta: tipos para os objetos do Docling, heurísticas de colunas nomeadas, testes de propriedades dos offsets, cobertura mínima |
| #28 numeração por extenso | resolvida no código | gate com uma convenção real, que o repositório não tem (ISSUE-0001) |
| #29 títulos multilinha | aberta | precisa dos casos reais (ACIP/FESAHT e outros) como fixtures |
| #30 cadeia de fornecimento | fechada no GitHub | — |
| #31 validação no MaxQDA | aberta | validação humana no MaxQDA |
| #56 acesso à partilha do pacote | aberta | configuração pelo Instituto de Informática, fora do repositório |
| #58 gate de instalação Windows | resolvida no código | ISSUE-0009 a 0013 verificadas; falta repetir o gate numa estação do CRL (ISSUE-0009) |
| #64 CARRISTUR sem cláusulas | resolvida no código | confirmar na próxima corrida sobre os PDF reais (ISSUE-0014) |

«Resolvida no código» quer dizer que o defeito está corrigido e coberto por testes, mas
que o issue tem um critério que só se confirma com pessoas, dados reais ou configuração
externa, e que por isso não deve ser fechado só com o merge.
