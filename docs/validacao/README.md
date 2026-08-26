# Validação: como se sabe que isto funciona

O projeto foi construído por fases, e nenhuma fase avançou sem passar um *gate*: um teste
de realidade feito por pessoas, não por código. Esta pasta guarda o registo desses gates.

Há duas formas de medir, e são complementares:

1. **Testes automáticos** (`python -m pytest -q`) — verificam propriedades que
   nunca podem falhar: zero perda de texto, conformidade dos ficheiros com o JSON Schema,
   estabilidade dos GUIDs, comportamento do comparador em casos construídos.
2. **Gates manuais** — o ficheiro é importado no MaxQDA e lido por quem faz a análise a
   sério. Os problemas encontrados foram devolvidos como memos exportados do próprio
   MaxQDA, que é o método que funcionou melhor: o comentário fica ancorado no segmento.

## Registo dos gates

| Fase | O que se validou | Registo |
|---|---|---|
| F0 | Primeira fatia vertical: texto pré-processado → QDPX importável no MaxQDA | [checklist-maxqda-f0.md](checklist-maxqda-f0.md) · [memos-gate-f0.html](memos-gate-f0.html) |
| F1 | Extração direta do PDF (sem pré-processador externo) | [checklist-maxqda-f1.md](checklist-maxqda-f1.md) · [memos-gate-f1.html](memos-gate-f1.html) |
| F1b | Rodapés do BTE, tabelas, texto sem linhas em branco | [checklist-maxqda-f1b.md](checklist-maxqda-f1b.md) |
| F3 | Triagem AUTO/REVER e árvore de códigos aninhada | [memos-peritas-4_08-v1.html](memos-peritas-4_08-v1.html) |
| F4 | Consolidado, assinaturas, GUIDs do codebook master | [memos-peritas-4_08-v3.html](memos-peritas-4_08-v3.html) |
| PR #23 | Docling opcional, ordem de leitura, spans, sanidade e offsets QDPX | [revisão técnica](../../issues/0004-revisao-pr-23.md) |

A validação visual do QDPX Docling final no MaxQDA continua pendente na
[ISSUE-0003](../../issues/0003-qdpx-perde-ganhos-do-docling.md). Testes automáticos e
importação humana são gates diferentes; um não substitui o outro.

Os memos são exports HTML do MaxQDA: abrem em qualquer navegador e mostram o comentário
de quem reviu, junto ao texto a que se refere. Vale a pena lê-los antes de mexer no
extrator — quase todos os casos difíceis do código nasceram de um destes comentários
(quebras de linha a meio de frase, títulos de cláusula fundidos com o capítulo, fronteiras
de segmento).

## Métricas contra o gabarito

O gabarito são 788 segmentos do tema 4.8 (proteção de dados) codificados manualmente por
peritas em 89 convenções de 2025. O `cct/harness.py` compara a codificação automática com
essa referência e produz precisão (quantas sugestões estão certas) e cobertura (quantos
segmentos reais foram apanhados).

| Versão do método | Precisão | Cobertura |
|---|---|---|
| Lexical pura (só termos do codebook) | 0,35 | 0,90 |
| Com condições de contexto (`requer_algum`, `excluir`) | 0,56 | 0,82 |
| Após mineração de variantes morfológicas nos falsos negativos | **0,57** | **0,88** |

A leitura correta destes números: **cobertura alta é o que interessa**, porque o objetivo
não é substituir a análise humana, é evitar que algo passe despercebido. A precisão baixa
custa tempo de revisão, mas não produz erro — todas as sugestões passam por pessoas,
exceto as da faixa `AUTO`, que só existe para códigos com precisão medida ≥ 0,85.

O salto do terceiro para o segundo caso mostra o método que funcionou melhor e é
replicável noutros temas: **ler os falsos negativos e extrair deles as variantes que o
codebook não previa** ("registo do pessoal", "registo dos trabalhadores", "cadastro
individual" onde o codebook só dizia "registo de pessoal"). No subcódigo 4.08.5.1 isso
levou o F1 de 0,72 para 0,84. O procedimento está descrito em
[../operacao/prompts-codebooks.md](../operacao/prompts-codebooks.md).

## Camada semântica: um gate que falhou primeiro

A codificação por LLM local foi avaliada com o mesmo harness, e o primeiro modelo testado
(DeepSeek R1 8B) **falhou**: zero verdadeiros positivos novos e sete falsos positivos.
Com o gemma-4-e2b passou: um verdadeiro positivo novo, zero falsos positivos.

Ficou desligada por omissão. Está documentado em
[ADR-0006](../adr/0006-semantica-llm-local-desligada-por-omissao.md) — é o exemplo mais
claro de uma funcionalidade que existe, funciona, e mesmo assim não é usada por omissão
porque não passou a régua.
