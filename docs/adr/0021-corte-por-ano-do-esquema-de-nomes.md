# ADR-0021: o esquema RNC é obrigatório a partir do corpus de 2026

- **Estado:** Aceite
- **Data:** 2026-09-18
- **Decidido por:** CRL (António Fula), a partir da ISSUE-0022

## Contexto

O [ADR-0016](0016-esquema-de-nomes-do-rnc.md) decidiu o formato do esquema RNC e
estabeleceu que **os dois esquemas convivem** e que **nomes já atribuídos não se
alteram**. O que ficou por dizer é a partir de quando o esquema RNC passa a ser o único
aceitável para nomear ficheiro novo — e essa lacuna teve uma consequência real: os 14
documentos do BTE 31/2026 foram recolhidos e nomeados com o esquema de 2025
(`26_PR_001_BTE_31_ACRAL_CESP.pdf`), apesar de `docs/rnc/README.md` §4.1 apresentar o
esquema RNC como a convenção corrente. A ISSUE-0022 registou a confusão: o README diz
*o quê*, mas não *a partir de quando*.

## Decisão

**O corte é pelo ano do corpus, não pela data em que se corre a aplicação.**

- Ficheiros de corpos **até 2025** mantêm o nome que já têm. Isto já estava decidido no
  ADR-0016 e não muda: migrar quebraria o trabalho feito no MAXQDA, que referencia
  documentos pelo nome.
- **A partir do corpus de 2026, inclusive, o esquema RNC é obrigatório.** Não há
  período de transição nem exceção por já se ter começado a recolher: um corpus de
  2026 nomeado com o esquema de 2025 está fora de conformidade e tem de ser corrigido
  antes de avançar para as fases seguintes do ciclo de vida (3.1).
- Operacionalmente, `python -m cct.nomeacao` passa a ter **`--esquema rnc` por
  omissão**. Quem precisar do esquema de 2025 — por exemplo para reprocessar um corpo
  anterior a 2026 — pede-o explicitamente com `--esquema pipeline`.
- O caso concreto que motivou este ADR foi corrigido por recolha: os 14 ficheiros do
  BTE 31/2026 nomeados com o esquema de 2025, os PDF intermédios e as execuções do
  pipeline geradas a partir deles foram apagados (nenhum estava versionado; todos sob
  `data/` e `results/`, ignorados pelo Git), para que a próxima recolha do BTE 31/2026
  já nomeie com `--esquema rnc`. O índice do BTE (`BTE31_2026.xlsx`) manteve-se, por ser
  a fonte, não um artefacto de nomeação.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Manter os 14 ficheiros com o esquema de 2025, tratando-o como facto consumado | Contradiz a própria razão de ser do ADR-0016: o BTE 31/2026 é precisamente o corpus usado para verificar o esquema RNC no README v4.0 (§11.2), e ficaria documentado com nomes que a aplicação não gerou dessa forma |
| Corrigir só a documentação, sem mexer nos ficheiros ("o esquema RNC ainda não se aplica a 2026") | Adiava a aplicação real do esquema decidido no ADR-0016 sem razão técnica — a aplicação já suporta `--esquema rnc` e o BTE 31/2026 já foi verificado com ele (README v4.0 §11.2) |
| Renomear os 14 ficheiros no lugar, em vez de apagar e recolher de novo | Também seria válido tecnicamente, mas apagar e recolher de novo é mais simples aqui porque nada estava versionado e a recolha já é reprodutível a partir do índice; foi a opção escolhida por quem decidiu |
| Esquema RNC obrigatório a partir da data em que este ADR é aceite, não do ano do corpus | Um corpus de um ano processado antes e depois da data de corte ficaria com nomes inconsistentes dentro de si mesmo, dependendo de quando cada ficheiro foi recolhido |

## Consequências

**Torna fácil:** saber se um corpus está em conformidade só pelo ano — 2025 ou anterior,
esquema antigo; 2026 em diante, esquema RNC, sem exceções a verificar caso a caso.

**Torna difícil:** reprocessar em lote vários anos de uma vez sem indicar `--esquema`
por corpo, porque a omissão já não serve para ambos.

**Passa a ser obrigatório manter:** a distinção no `docs/rnc/README.md` (§4.1 e §10)
entre "esquema antigo, ficheiros já atribuídos até 2025" e "esquema RNC, obrigatório de
2026 em diante"; e o valor por omissão de `--esquema` em `cct/nomeacao.py` alinhado com
o de `cct/catalogo.py`, que já assumia `rnc`.

**Custo assumido:** os 14 ficheiros do BTE 31/2026 e as execuções do pipeline geradas a
partir deles foram apagados e têm de ser recolhidos e reprocessados de novo. As
ISSUE-0015 a ISSUE-0021, levantadas sobre esse corpus, continuam válidas quanto ao
defeito de extração que descrevem — o defeito está no código, não no nome do ficheiro —
mas os nomes de ficheiro concretos que citam ficam desatualizados até à nova recolha.

## Revisitar quando

Se aparecer um corpus cujo ano de referência não coincida com o ano em que é recolhido
— por exemplo, um boletim de 2026 recolhido tardio em 2027 — decidir então se o corte
segue o ano do BTE ou o ano da recolha. Não aconteceu até hoje.
