# SPEC-0004: um só esquema de nomes para convenções, portarias de extensão e acordos de adesão

- **Estado:** Aprovada; passos 1 a 3 implementados, passo 0 por fazer, passo 4 reduzido a nova recolha
- **Data:** 2026-09-23
- **Autoria:** CRL (António Fula)
- **Decisões relacionadas:** [ADR-0022](../docs/adr/0022-esquema-de-nomes-comum-as-tres-familias.md),
  [ADR-0016](../docs/adr/0016-esquema-de-nomes-do-rnc.md) (substituído),
  [ADR-0018](../docs/adr/0018-familias-documentais-em-pastas-separadas.md),
  [ADR-0021](../docs/adr/0021-corte-por-ano-do-esquema-de-nomes.md)

## Problema

As portarias de extensão (PE) e os acordos de adesão (AA) são nomeados com o esquema
das convenções, que não tem lugar para o número da portaria no Diário da República,
põe-lhes um âmbito que não decide nada e não as liga de forma legível à convenção a que
se referem. A equipa renomeou à mão as PE de 2026 com um padrão próprio
(`2026_001_BTE_01_PE_0452_ADCP_SETAAB`) que a aplicação não reconhece: nem
`RE_DOC_ID` nem `RE_DOC_ID_RNC` o aceitam (verificado a 2026-09-23), pelo que o
`pipeline_tema` não o identifica como portaria. A fundamentação completa está no
[ADR-0022](../docs/adr/0022-esquema-de-nomes-comum-as-tres-familias.md).

## Objetivo

Que as três famílias documentais sejam nomeadas com um só esquema, agrupável por ano e
boletim, com uma convenção de base no nome, e que a aplicação o escreva, o leia e o use
para proteger o pipeline.

## Não-objetivos

1. **Não** renomeia o corpus até 2025. O esquema de 2025 continua a ser lido.
2. **Não** processa PE nem AA no pipeline temático. Continuam na fase 1 do ciclo de vida.
3. **Não** adivinha o código IRCT da convenção de base. Sem código confirmado, o
   ficheiro não é escrito.
4. **Não** altera a árvore de pastas do [ADR-0018](../docs/adr/0018-familias-documentais-em-pastas-separadas.md).
5. **Não** trata os avisos: continuam sem ficheiro, só no catálogo.

## Comportamento

### O esquema

```text
{ANO}_BTE_{NN}_{X}_{SEQ}_{miolo}_{CODIRCT}_{SIGLA1}-{SIGLA2}[+N]
```

| Família | Esquema | Exemplo |
|---|---|---|
| Convenção | `{ANO}_BTE_{NN}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_{SIGLAS}` | `2026_BTE_31_PRI_377_CCT-ALT_27251_ACRAL-CESP+3` |
| PE, PCT, PRT | `{ANO}_BTE_{NN}_{TIPO}_{SEQ}_{NNNN}-{AAAA}_{CODIRCT}_{SIGLAS}` | `2026_BTE_01_PE_012_0452-2025_27251_ACRAL-CESP` |
| AA | `{ANO}_BTE_{NN}_AA_{SEQ}_{CODIRCT}_{SIGLAS}` | `2026_BTE_12_AA_412_27251_ABC-CESP` |

As regras de cada campo estão no ADR-0022. As que têm efeito direto no código são:

1. `ANO` é o ano do BTE; `NN` tem 2 dígitos; `SEQ` é o da DGCP, com 3 dígitos.
2. O quarto campo é `PRI|SPE|APU` nas convenções e o tipo (`PE|PCT|PRT|AA`) nas outras
   famílias.
3. O miolo da PE é `NNNN[A-Z]?-AAAA` (número da portaria e ano do DR).
4. `CODIRCT` é o da convenção de base.
5. Siglas: primeira patronal, primeira sindical, `+N` para as restantes.
6. Máximo de 63 caracteres; encurtam-se só as siglas.

### Casos-limite e o que deve acontecer

| Caso | Resultado |
|---|---|
| Sem `IDDocumento` | `por_confirmar`, ficheiro não escrito (comportamento atual, mantém-se) |
| PE sem número ou ano da portaria | `por_confirmar`, ficheiro não escrito |
| PE ou AA sem código IRCT da convenção de base confirmado | `por_confirmar`, ficheiro não escrito |
| PE que estende várias convenções | nome com a primeira na ordem confirmada do índice; aviso; catálogo com relação a todas as convenções, incluindo os códigos que não cabem no nome |
| AA que adere a convenção de um ano anterior | nome com o código dessa convenção, que é estável entre revisões |
| Só partes de um lado (patronal ou sindical) | as duas primeiras desse lado; aviso |
| Portaria com letra de sufixo (50-A/2025) | `0050A-2025` |
| Tipo fora do vocabulário do quarto campo (ex.: retificação de portaria) | família desconhecida: `por_classificar/` e relatório, como hoje; família conhecida com subtipo novo (ex.: `AA-ALT`): `por_confirmar`, ficheiro não escrito. O vocabulário alarga-se por decisão registada |
| Nome com mais de 63 caracteres | siglas encurtadas, aviso; cabeça e miolo intactos |

## Alterações a realizar

### Passo 0. Verificação prévia (bloqueia a escrita de PE e AA)

Com um índice real do BTE que traga pelo menos uma PE e um AA, e com os metadados da
DGCP correspondentes:

1. Identificar o campo onde a DGCP regista o código IRCT da convenção de base de cada PE
   e AA, e o nome da coluna nos dois dialetos do índice.
2. Verificar se esse código coincide com o `COD: (IRCT)` da convenção (ex.: `27251`) ou
   se difere, por exemplo no dígito de família.
3. Verificar onde está o número da portaria e o ano do DR (título do documento, coluna
   própria ou outra fonte).
4. Registar o resultado no §4.4 e no §9 (tarefa 3) do README do RNC.

Fonte alternativa, caso a DGCP não traga o código: a coluna de alterações do índice já
dá, para a PE, o documento de base no formato `CCT.20260822.377/2026`
(`relacao_alvo`, ver `tests/test_rnc.py`). Resolver esse identificador para o código
IRCT da convenção, através do catálogo acumulado ou do `vocabularios/actos_negociacao.csv`,
é aceitável, desde que a resolução seja exata. Uma correspondência aproximada não serve.

A parte do esquema que diz respeito às convenções (passos 1 a 3) não depende desta
verificação e pode avançar já.

### Passo 1. Código

| Ficheiro | Alteração |
|---|---|
| `cct/recolha.py` | Acrescentar aos *aliases* do índice os campos identificados no passo 0: código IRCT da convenção de base (novo campo interno, ex.: `cod_irct_base`) e, se existirem em coluna, número e ano da portaria. Guardá-los no registo |
| `cct/nomeacao.py` | Reescrever `_nome_rnc` com a nova ordem dos campos e um ramo por família (convenção, extensão, adesão). Nova função `referencia_portaria(entrada)` que devolve `(numero, sufixo, ano_dr)` a partir do campo ou do título (padrão do tipo `Portaria n.º 452/2025`, com sufixo opcional `-A`), ou `None`. Nova função `cod_irct_base(entrada)`: numa convenção é o seu código; numa PE ou AA é o do passo 0, ou `None`. `None` em qualquer destas funções gera `por_confirmar` e bloqueia a escrita, sem recurso a `--aceitar-heuristicas` |
| `cct/nomeacao.py` | Substituir `siglas_outorgantes` pela regra patronal mais sindical: usar `separar_outorgantes`, primeira sigla de cada lado, `+N` com o total menos as escolhidas; aviso quando só há um lado. `MAX_SIGLAS_RNC` passa a 2 |
| `cct/nomeacao.py` | Atualizar a docstring do módulo, o comentário de `ESQUEMAS` e a docstring de `familia_do_nome`. `ESQUEMAS` mantém `("pipeline", "rnc")`: `rnc` passa a designar o esquema do ADR-0022, e o do ADR-0016 deixa de ser escrito. Nota: as linhas de comando já usam `rnc` por omissão, mas as funções `nome_documento` e `nomear` usam `ESQUEMA_OMISSAO = "pipeline"`, e `cct/catalogo.py` usa essa constante como nome do esquema antigo. Não é um defeito visível para quem usa a linha de comando, mas convém renomear a constante (ex.: `ESQUEMA_2025`) para deixar de sugerir que é a omissão, ajustando os testes de `tests/test_nomeacao.py` que dependem dela |
| `cct/localizador.py` | Três expressões regulares novas, com grupos nomeados: `RE_DOC_ID_CONVENCAO` (quarto campo restrito a `PRI|SPE|APU`), `RE_DOC_ID_EXTENSAO` (quarto campo `PE|PCT|PRT`, miolo `\d{4}[A-Z]?-\d{4}`) e `RE_DOC_ID_ADESAO` (quarto campo `AA`, sem miolo). Manter `RE_DOC_ID` (2025) e `RE_DOC_ID_RNC` (ADR-0016) para leitura, restringindo em `RE_DOC_ID_RNC` o âmbito a `PRI|SPE|APU`. `interpretar_doc_id` passa a aceitar os cinco padrões e continua a devolver `(ano de 2 dígitos, n.º do BTE, tokens das partes)`. `interpretar_nome_rnc` devolve também `familia`, `portaria` e `ano_dr` quando existirem. Atualizar a docstring do módulo |
| `cct/nomeacao.py`, `familia_do_nome` | Reconhecer a família pelos três padrões novos (pelo quarto campo ou pelo tipo), para que o `pipeline_tema` recuse PE e AA pelo nome |
| `cct/comparar.py` | `_ano` já cai no padrão `^(20\d{2})` para os nomes novos. Acrescentar um caso explícito e um comentário para o esquema do ADR-0022, para que a dedução do ano não dependa de um recurso genérico |
| `cct/catalogo.py` | Nova coluna `cod_irct_base` (o código que vai no nome; igual a `cod_irct` nas convenções) e nova coluna `portaria_dr` (ex.: `452/2025`; vazia fora da família `extensao`). Colocá-las junto de `cod_irct` e `relacao_alvo`. Para PE com várias convenções, representar explicitamente todas as relações e códigos, sem sobrecarregar os campos singulares; definir o formato persistente e a ordem estável antes da migração. A recuperação das colunas da equipa pelo `nome_canonico` tem de continuar a funcionar depois da migração: ver passo 4 |
| `cct/pipeline_tema.py` | Atualizar a mensagem de recusa e o exemplo de pasta, se citarem nomes do esquema antigo. A lógica não muda |

### Passo 2. Testes

Em `tests/test_rnc.py` (e em `tests/test_localizador.py` e `tests/test_nomeacao.py`
quando o teste for desses módulos):

1. Ida e volta para as três famílias: o nome gerado é aceite por `interpretar_doc_id` e
   por `interpretar_nome_rnc`, e tem no máximo 63 caracteres.
2. A cabeça é sempre `{ANO}_BTE_{NN}_`, e ordenar os nomes alfabeticamente agrupa por
   (ano, n.º do BTE). Dentro de cada BTE, a ordenação integral por posição requer o
   catálogo; os nomes agrupam primeiro por quarto campo e só depois pelo sequencial.
3. `familia_do_nome` devolve `extensao` e `adesao` para os nomes novos, e `convencao`
   para as convenções.
4. `pipeline_tema` recusa uma pasta com uma PE ou um AA nomeados no esquema novo.
5. PE de 2025 publicitada em BTE de 2026: `ANO` 2026 e miolo `NNNN-2025`.
6. Portaria com sufixo: `0050A-2025`.
7. PE sem referência de portaria, e PE ou AA sem código da convenção de base: ficam
   `por_confirmar` e o ficheiro não é escrito, mesmo com `--aceitar-heuristicas`.
8. O código no nome de uma PE e de um AA é o da convenção de base, e
   `*_{CODIRCT}_*` apanha a convenção, a PE e o AA do índice de ensaio.
   Numa PE que abrange várias convenções, a pesquisa pelo nome encontra apenas a
   primeira; o catálogo devolve também as restantes relações.
9. Siglas: primeira patronal e primeira sindical, `+N` correto; aviso quando só há um
   lado; um AE (empresa e sindicato) fica `EMPRESA-SINDICATO`.
10. O quarto campo de uma convenção nunca é um tipo, e o de uma PE ou AA nunca é um
    âmbito.
11. Os nomes de 2025 e do ADR-0016 continuam a ser lidos por `interpretar_doc_id`.
12. Atualizar os testes existentes que fixam o esquema do ADR-0016
    (`test_a_familia_le_se_do_nome_nos_dois_esquemas`, `test_a_portaria_herda_as_partes_do_titulo`
    e os que comparam nomes literais), mantendo as asserções sobre os nomes antigos
    como testes de leitura.
13. Atualizar o índice de ensaio (`itens_mistos`) com o campo do passo 0 e com o título
    de uma portaria que traga o número e o ano do DR.

### Passo 3. Documentação

| Ficheiro | Alteração |
|---|---|
| `docs/rnc/README.md` | Versão 4.2. Exemplo inicial e diagrama de campos; §4.1 (regra, tabela de campos, explicação do número do BTE à cabeça); §4.2 se mencionar o esquema; §4.4 (`ls 1_fontes/irct/*/*_27251_* 1_fontes/irct/convencoes/*/*_27251_*` passa a apanhar as três famílias); §4.6 (o âmbito deixa de constar do nome das PE e AA); §6 (colunas `cod_irct_base` e `portaria_dr`, contagem de colunas); §9 (tarefa 3 com o resultado do passo 0); §10 (transição do corpus de 2026); §11.1 e §11.2 (exemplos e verificação refeita); registo de alterações |
| `docs/rnc/pastas/1_fontes.md` e `docs/rnc/pastas/2_processamento.md` | Exemplos de nomes |
| `docs/operacao/guia-operacao.md` | Árvore de exemplo e descrição do esquema (linhas com `{ANO}_{AMBITO}_…` e exemplos `2026_PRI_…`) |
| `docs/dados/README.md` | Exemplo de nome do corpus de 2026 |
| `docs/adr/README.md` e `specs/README.md` | Já atualizados com esta spec e o ADR-0022 |
| `issues/0015` a `issues/0021` | Sem alteração obrigatória. Se forem revistas, acrescentar o nome no esquema novo ao lado do antigo |
| Docstrings de `cct/nomeacao.py`, `cct/localizador.py`, `cct/comparar.py` | Ver passo 1 |

Correr `python scripts/verificar_referencias.py --verboso` no fim.

### Passo 4. Migração do corpus de 2026 (fora do Git)

`data/` e os ficheiros do RNC não estão versionados: esta migração faz-se na estação,
e o merge não a propaga.

1. **Confirmar com a equipa que não há trabalho no MAXQDA sobre o corpus de 2026.** Se
   houver, parar e voltar à equipa (ADR-0022, «Transição»).
2. Guardar uma cópia do `catalogo_irct_2026.csv` e do `registo_bte.jsonl`.
3. Convenções (14 ficheiros do BTE 31/2026): voltar a correr a nomeação a partir do
   registo, com `--aplicar`, para o destino novo, e apagar os ficheiros antigos depois de
   conferir os `sha256`. Em alternativa, repetir a recolha a partir do índice, como se
   fez no ADR-0021.
4. PE renomeadas à mão: voltar a nomeá-las a partir do índice do BTE onde foram
   publicadas. A contagem da equipa (`001`) desaparece. O ano do DR e o código da
   convenção de base vêm do índice ou do título; as que não os tiverem ficam
   `por_confirmar` até se resolverem.
5. Catálogo: as cinco colunas da equipa são recuperadas pelo `nome_canonico`, que muda
   nesta migração. Antes de regerar, reescrever a coluna `nome_canonico` do catálogo
   anterior com uma tabela de correspondência nome antigo para nome novo (gerada no
   passo 3, a partir do `sha256` ou do `IDDocumento`), para que nada do trabalho da
   equipa se perca. Esta tabela fica guardada em `0_gestao/catalogo/`.
6. Regerar o catálogo e confirmar que nenhuma linha aparece como «já não consta dos
   índices lidos».

### Ordem de execução

1. Passos 1 a 3 para as convenções e para a leitura dos três padrões. Não dependem do
   passo 0.
2. Passo 0.
3. Passos 1 e 2 para a escrita de PE e AA.
4. Passo 4.
5. Marcar esta spec como `Implementada`.

## Critérios de aceitação

- [x] Todo o nome gerado, nas três famílias, começa por `{ANO}_BTE_{NN}_`, é aceite por
      `interpretar_doc_id` e tem no máximo 63 caracteres.
- [x] O quarto campo é `PRI`, `SPE` ou `APU` nas convenções, e o tipo nas PE e AA.
- [x] Uma PE tem o miolo `NNNN-AAAA`, com o ano do DR, e `ANO` igual ao ano do BTE.
- [x] O código no nome de uma PE e de um AA é o da convenção de base.
- [x] Sem código da convenção de base ou sem referência da portaria, o ficheiro não é
      escrito, mesmo com `--aceitar-heuristicas`.
- [x] As siglas são a primeira patronal e a primeira sindical, com `+N`.
- [x] Nenhuma contagem interna entra no nome.
- [x] `familia_do_nome` reconhece as três famílias no esquema novo, e o `pipeline_tema`
      recusa PE e AA pelo nome.
- [x] Os nomes do esquema de 2025 e do ADR-0016 continuam a ser lidos.
- [x] O catálogo tem as colunas `cod_irct_base` e `portaria_dr`.
- [ ] O passo 0 está feito e registado no README do RNC.
- [ ] Os 14 ficheiros do BTE 31/2026 e as PE de 2026 estão no esquema novo, sem perda
      das colunas da equipa no catálogo.
- [x] `pytest`, `verificar_seguranca.py` e `verificar_referencias.py` passam.

## Estado da implementação (23/09/2026)

Passos 1 a 3 feitos. Testes em `tests/test_esquema_adr0022.py` (critérios do passo 2),
`tests/test_rnc.py` e `tests/test_escolher_par.py`. Decisões tomadas na implementação,
dentro do que o ADR-0022 deixa em aberto:

1. **Fonte alternativa do código de base, com salvaguarda.** Sem coluna do índice
   conhecida, o código resolve-se pela cadeia de alterações, com correspondência exata
   de tipo e `IDDocumento` contra o registo ou os índices lidos
   (`resolver_convencoes_base`). Enquanto o passo 0 não confirmar esta leitura com dados
   reais, o nome assim obtido sai com o aviso `AVISO_BASE_PELA_CADEIA` e fica por
   confirmar; só `--aceitar-heuristicas` o escreve. Fechar o passo 0 é retirar esse aviso
   e, se a DGCP tiver coluna própria, acrescentar o seu nome aos *aliases* de
   `cod_irct_base` e `portaria_dr` em `cct/recolha.py`.
2. **Várias convenções numa PE.** O nome leva a primeira pela ordem da cadeia do índice;
   o catálogo guarda as restantes em `cod_irct_base_adicionais`, separadas por `; `.
3. **Avisos.** Não têm ficheiro, mas têm nome no catálogo. Recebem a forma de uma
   adesão com o tipo no quarto campo (`2026_BTE_31_AVISO_403_26651_…`), lida por
   `RE_DOC_ID_AVISO`.
4. **Migração do passo 4.** `cct.nomeacao --migrar --correspondencia CSV` passa os nomes
   do ADR-0016 para o esquema novo, apaga o ficheiro antigo depois de conferir o
   `sha256` e escreve a tabela de correspondência; `cct.catalogo --correspondencia CSV`
   usa-a para levar as colunas da equipa para o nome novo. Sem `--migrar`, um nome já
   escrito que mudaria continua a ser `conflito`.
5. **PE renomeadas à mão.** O `cct.pipeline_tema` passa a recusar também os nomes fora de
   qualquer esquema que tragam `PE`, `PCT`, `PRT` ou `AA` como campo próprio.
6. **Omissão do esquema.** `ESQUEMA_OMISSAO` passa a `rnc` também nas funções, alinhado
   com as linhas de comando (ADR-0021); o esquema de 2025 chama-se `ESQUEMA_2025`.

**Passo 4, confirmado pela equipa a 23/09/2026:** não há trabalho no MAXQDA sobre o
corpus de 2026. Os PDF de 2026 descarregados até aqui eram de teste e foram apagados
depois dos testes. Não há, por isso, ficheiros a migrar nem colunas da equipa a
preservar: o corpus de 2026 recolhe-se de novo já com o esquema do ADR-0022. O
`--migrar` fica disponível para cópias antigas do corpus noutras estações.

## Plano de verificação

1. **Testes automáticos:** os do passo 2, offline, sem dados locais, com índices de
   ensaio reconstruídos em `openpyxl`, como na SPEC-0003.
2. **Verificação manual:** correr a nomeação em simulação sobre o `BTE31_2026.xlsx` e
   sobre o índice real com PE e AA do passo 0; conferir os nomes contra o índice
   publicado; confirmar que `ls` agrupa por ano e BTE, e que `*_{CODIRCT}_*`
   junta as relações principais. Conferir no catálogo a ordem integral do BTE e as
   relações adicionais de portarias que abrangem várias convenções.
3. **Dados de ensaio:** `BTE31_2026.xlsx` e o índice do passo 0.

## Riscos

| Risco | O que se faz |
|---|---|
| A DGCP não ligar PE e AA à convenção de base | Ficheiros `por_confirmar`, nunca nome com código adivinhado; o esquema das PE e AA volta à equipa (ADR-0022, «Revisitar quando») |
| O código da DGCP para a PE diferir do da convenção no dígito de família | Verificado no passo 0; o nome leva o código tal como aparece na convenção, com a tradução documentada |
| Perder o trabalho da equipa no catálogo ao mudar o `nome_canonico` | Tabela de correspondência antes de regerar (passo 4.5), cópia prévia do catálogo |
| Renomear depois de começado o trabalho no MAXQDA | Passo 4.1 bloqueia a migração |
| Um nome do ADR-0016 ser lido como PE ou AA, ou o contrário | Quarto campo com vocabulário fechado nas cinco expressões regulares; teste dedicado |
| Uma cópia antiga do corpus numa estação continuar com nomes antigos | O `localizador` continua a lê-los; a migração está descrita no passo 4 e no registo de alterações do README do RNC |
