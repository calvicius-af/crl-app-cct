# RNC — Como organizamos e nomeamos os ficheiros

Relatório da Negociação Coletiva · Centro de Relações Laborais
**Versão 3.2 · 16 de setembro de 2026** · substitui `README.Estrutura_RNC_2027.docx` (v2.1),
`README_Estrutura_RNC_2026.md` (v1) e as secções 2–3 do `SOP_Gestao_Documental_RNC_2026.docx` (v1.0)

> **O que muda na v3.0.** A v2.1 descrevia a convenção assumindo uma ferramenta
> própria (`_ferramentas/catalogar_bte.py`). Esta versão compatibiliza a
> convenção com a AppCCT, que já faz recolha, nomeação e extração, e fecha as
> três tarefas que a v2.1 dava como bloqueantes. O resumo está no [§2](#2-o-que-muda-face-à-v21-e-porquê).

## Se só tiver dois minutos

Três regras. Se seguir estas três, o resto acerta sozinho.

1. **As pastas seguem a fase do trabalho, nunca o tema.** Um ficheiro está em
   `1_fontes/` porque acabou de chegar, não porque é sobre teletrabalho.
2. **O nome do ficheiro nunca muda depois de atribuído.** É atribuído uma vez,
   pela aplicação, à entrada. Muda a extensão e a pasta; o nome não.
3. **O catálogo manda.** Se a pasta e o catálogo discordarem, o catálogo está
   certo e a pasta está por arrumar.

Exemplo de um nome real, gerado a partir do BTE 31 de 2026:

```text
2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf
 │    │    │   │    │      │     └── siglas das partes (3 primeiras, +2 = há mais duas)
 │    │    │   │    │      └── número do boletim em que saiu
 │    │    │   │    └── código IRCT — o mesmo em todas as revisões desta convenção
 │    │    │   └── tipo de documento, tal como vem do BTE
 │    │    └── número sequencial do ano (o «377/2026» do índice)
 │    └── ÂMBITO — PRI · SPE · APU. Diz de imediato se é processável.
 └── ano de publicação
```

---

## 1. Para que serve este documento

Explica onde pôr cada ficheiro e como o nomear, para que qualquer pessoa da
equipa — ou uma perita externa que chega a meio do ciclo — encontre o que
precisa sem perguntar a ninguém.

Aplica-se a toda a gente que toca em ficheiros do RNC: recolha, processamento,
codificação, redação e coordenação.

**O que este documento não é:** não é o manual do MAXQDA, não é o livro de
códigos, não é o roteiro do relatório. Esses vivem em `0_gestao/` e são
referidos aqui quando necessário. Também não é o manual da aplicação: para a
operação da AppCCT, ver [guia de operação](../operacao/guia-operacao.md).

**Termos usados aqui, à primeira ocorrência.** *IRCT* — instrumento de
regulamentação coletiva de trabalho, o nome genérico para convenções, portarias
e acordos de adesão. *BTE* — Boletim do Trabalho e Emprego, onde são publicados.
*Índice do BTE* — o ficheiro XLSX que a DGERT distribui por número do boletim,
com uma linha por documento publicado. *Catálogo* — o CSV que a equipa mantém,
com uma linha por documento recolhido. *QDPX* — o formato REFI-QDA de troca de
projetos entre programas de análise qualitativa, que é como a AppCCT entrega o
trabalho ao MAXQDA.

---

## 2. O que muda face à v2.1, e porquê

A v2.1 acertou na convenção. O que faltava era ligá-la ao que a aplicação já
faz, e resolver três coisas que ficaram por decidir. Está tudo fechado.

| # | O que a v2.1 dizia | O que passa a valer | Onde |
|---|---|---|---|
| 1 | «Está por confirmar que o `COD: (IRCT)` se mantém igual entre revisões» (tarefa bloqueante) | **Confirmado. Mantém-se.** O código é o identificador de acto de negociação da DGERT com um dígito de família à frente, e acompanha a convenção ao longo dos anos | [§5.3](#53-o-código-irct-é-estável-e-porquê) |
| 2 | Retificações precisam de `--catalogo-anterior` para herdar as siglas | **Não precisam.** As partes estão no título do próprio documento, e a aplicação lê-as de lá | [§5.5](#55-os-casos-que-o-script-não-resolve-sozinho) |
| 3 | `_ferramentas/catalogar_bte.py`, ferramenta à parte | **`python -m cct.catalogo`**, dentro da aplicação, com testes no CI | [§11](#11-as-ferramentas) |
| 4 | Convenção de nome com seis campos | **Sete campos:** entra o `_BTE_{NN}`. Custa sete caracteres e é o que permite voltar do ficheiro ao boletim — e o que a aplicação lê para emparelhar versões | [§5.1](#51-a-regra), [ADR-0016](../adr/0016-esquema-de-nomes-do-rnc.md) |
| 5 | Sectores misturados com matérias, «decisão de equipa» | **Separados por omissão.** O que a aplicação não reconhece vai para `sectores_a_classificar`, nunca é assumido | [§7-b](#b-sectores-e-matérias-no-mesmo-campo) |
| 6 | `siglas_organizacoes.csv` com 2 401 organizações | **2 403, com a origem de cada sigla declarada.** As 1 017 que o script inventou não são carregadas enquanto ninguém as vir | [§8](#8-vocabulários-controlados) |
| 7 | Siglas ambíguas resolvidas à mão, caso a caso | **Resolvidas por regra, automaticamente.** 391 conflitos, zero duplicados à saída, resultado independente de quem corre o script | [§5.5-b](#55-os-casos-que-o-script-não-resolve-sozinho), [ADR-0017](../adr/0017-regra-de-desambiguacao-de-siglas.md) |
| 9 | Portarias de extensão e acordos de adesão sem tratamento próprio | **Cada família na sua pasta**, e só as convenções entram no pipeline. As adesões passam a ser recolhidas por omissão, o que não eram | [§5.7](#57-portarias-de-extensão-acordos-de-adesão-e-avisos), [ADR-0018](../adr/0018-familias-documentais-em-pastas-separadas.md) |
| 8 | O número sequencial era atribuído pelo CRL | **É o da DGCP (ex-GEP).** Decisão da coordenação, que substitui a da SPEC-0001: compatibilizar ao máximo com os códigos já existentes | [§5.1-bis](#51-bis-de-onde-vem-o-número-sequencial) |

O que se mantém da v2.1, e porque funcionava: as três regras do resumo; a
árvore por fase; o âmbito com três letras; o código IRCT no nome; os temas fora
das pastas; a pasta `9_arquivo/` explícita; a profundidade máxima de quatro
níveis; sem acentos, sem espaços, sublinhado como separador.

---

## 3. A árvore de pastas

```text
RNC_Dados_2026/
├── README.md                    ← este ficheiro
├── 0_gestao/
│   ├── roteiro/                 índice do relatório, versão vigente + anteriores
│   ├── livro_codigos/           árvore de códigos MAXQDA e crosswalk de temas
│   ├── catalogo/                ★ catalogo_irct_2026.csv — a fonte de verdade
│   ├── vocabularios/            listas controladas (siglas, âmbitos, tipos, temas, estados)
│   ├── atas/                    reuniões e decisões de codificação
│   └── procedimentos/           este README, SOP, guias
├── 1_fontes/                    tudo o que entra de fora. IMUTÁVEL.
│   ├── indices_bte/             os XLSX de índice (2026_BTE_31_indice.xlsx)
│   ├── bte_completo/            boletins inteiros em PDF
│   ├── irct/                    ★ PDF individuais, já renomeados — ver §5.7
│   │   ├── convencoes/          PRI/ SPE/ APU/   ← o pipeline lê daqui
│   │   ├── extensoes/           PRI/ SPE/        portarias de extensão
│   │   ├── adesoes/             PRI/ SPE/        acordos de adesão
│   │   └── avisos/              PRI/ SPE/        projetos, denúncias, caducidades
│   └── externas/                DGERT, DGAEP, CITE, INE, RAA/RAM, Eurofound
├── 2_processamento/             saídas automáticas da AppCCT
│   ├── texto/                   .txt e doc.json extraídos do PDF
│   ├── precodificado/           anotacoes.json e triagem
│   └── qdpx/                    pacotes QDPX prontos a importar
├── 3_analise/                   MAXQDA
│   ├── master/                  ★ um único .mqda ativo
│   ├── mqex/                    exports individuais à espera de integração
│   ├── comparacoes/             diacronia: o que mudou face à versão anterior
│   └── logs_integracao/         registo de cada integração no master
├── 4_temas/                     ★ entregas às peritas — ver §6
├── 5_redacao/                   capítulos em elaboração
├── 6_relatorio/                 relatório consolidado
├── 7_divulgacao/                apresentação, imprensa, fotografias
└── 9_arquivo/                   versões superadas de tudo o resto
```

**Nome da pasta-raiz:** `RNC_Dados_AAAA`, em que AAAA é o ano a que os dados
dizem respeito, não o ano de publicação. O relatório publicado em 2027 sobre
dados de 2026 vive em `RNC_Dados_2026/`.

As pastas marcadas com ★ são as que concentram o risco. Se alguma coisa correr
mal, é numa destas quatro.

**Onde é que isto se encontra com a aplicação.** A AppCCT tem uma árvore
própria (`data/`, `results/`), documentada em
[organização do workspace](../dados/organizacao-workspace.md). As duas não são
alternativas: a árvore do RNC é a do arquivo do projeto, partilhada e de longa
duração; a da aplicação é a da máquina onde ela corre. A correspondência é
direta e está em [§4-bis](#4-bis-a-correspondência-com-as-pastas-da-appcct).

---

## 4. O ciclo de vida de um documento

Esta é a tabela central. Um IRCT entra uma vez e atravessa oito fases. O nome
base nunca muda — mudam a extensão e a pasta.

| # | Fase | Quem | Entra | Sai | Fica em | Nome |
|---|---|---|---|---|---|---|
| 1 | Recolha | Técnico de recolha | índice XLSX do BTE | 1 PDF por IRCT, renomeado, + linha no catálogo | `1_fontes/irct/{FAMILIA}/{AMBITO}/` | `2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf` |
| 2 | Extração | AppCCT (automático) | PDF **de `convencoes/`** | texto + estrutura | `2_processamento/texto/` | `…_ACRAL-CESP-STRUP+2.txt` e `.doc.json` |
| 3 | Pré-codificação | AppCCT (automático) | texto | cláusulas candidatas por código | `2_processamento/precodificado/` | `…_ACRAL-CESP-STRUP+2.anotacoes.json` |
| 4 | Empacotamento | AppCCT (automático) | pré-codificado | pacote QDPX + sugestões | `2_processamento/qdpx/` | `RNC_2026_lote_NN.qdpx` |
| 5 | Validação | Técnico por tema | QDPX importado no MAXQDA | export individual | `3_analise/mqex/` | `2026_C9-SALARIOS_AF_20270315.mqex` |
| 6 | Integração | Responsável de integração | MQEX da semana | master atualizado + linha no log | `3_analise/master/` | `RNC_Dados_2026_master.mqda` |
| 7 | Entrega às peritas | Coordenação | master | XLSX por tema | `4_temas/{TEMA}/` | `2026_C9-SALARIOS_segcod_20270401.xlsx` |
| 8 | Redação | Perita | XLSX do tema | texto do capítulo | `5_redacao/` | `4_07_remuneracoes.docx` |

**Regras que tornam isto seguro:**

1. **A fase 1 é a única em que se atribui nome.** Nas fases 2 a 4 o nome é
   herdado pela aplicação. Se alguém renomear a meio, a rastreabilidade parte-se
   — e parte em silêncio, porque a aplicação lê o nome do ficheiro para saber o
   ano, o boletim e as partes.
2. **Depois de integrado no master, o MQEX vai para `9_arquivo/`.** Nunca fica
   em `3_analise/mqex/`, para que essa pasta signifique sempre «por integrar».
3. **Cada integração escreve uma linha em `logs_integracao/`:** data, ficheiro,
   quem integrou, n.º de segmentos, conflitos resolvidos. É o que permite
   reconstruir o master se ele se corromper.
4. **A pasta `1_fontes/` é só de leitura.** Se um PDF estiver mal, não se
   corrige — regista-se no catálogo e trata-se a jusante.
5. **Só a família `convencoes/` atravessa as fases 2 a 8.** As portarias de
   extensão, os acordos de adesão e os avisos param na fase 1: são recolhidos,
   nomeados e catalogados, e ficam disponíveis para consulta e para contagem —
   mas não são extraídos nem codificados. O porquê está em [§5.7](#57-portarias-de-extensão-acordos-de-adesão-e-avisos).
6. **Cada corrida da aplicação deixa um `manifest.json`** com o comando, o
   *commit*, as versões, os *hashes* das entradas e saídas, as contagens e os
   problemas. É o que responde, meses depois, a «como é que isto foi produzido?».

### 4-bis. A correspondência com as pastas da AppCCT

| Pasta do RNC | Pasta da AppCCT | Como se passa de uma à outra |
|---|---|---|
| `1_fontes/indices_bte/` | `data/raw/indices/` | cópia, ou a mesma pasta por atalho |
| `1_fontes/irct/{FAMILIA}/{AMBITO}/` | `data/raw/bte/bte_2026/{FAMILIA}/{AMBITO}/` | escrito por `python -m cct.nomeacao --esquema rnc` |
| `1_fontes/bte_completo/` | `data/raw/bte_completo/` | usado só para os anos históricos, pelo `cct/localizador.py` |
| `2_processamento/texto/` | `results/runs/2026/<corrida>/texto/` | saída da fase 1 do pipeline |
| `2_processamento/precodificado/` | `results/runs/2026/<corrida>/` | saída das fases 2 a 4 |
| `2_processamento/qdpx/` | `results/runs/2026/<corrida>/projeto.qdpx` | saída da fase 5 |
| `3_analise/comparacoes/` | `results/benchmarks/<tema>/comparacoes/` | `python -m cct.comparar` |
| `0_gestao/catalogo/` | — | `python -m cct.catalogo --saida …` escreve diretamente para aqui |
| `0_gestao/vocabularios/` | `vocabularios/` do repositório | versionados com o código; ver [§8](#8-vocabulários-controlados) |

Uma corrida da aplicação é datada e descartável; o que fica no arquivo do RNC é
o que a coordenação decide promover. A regra é: **promove-se a corrida que
gerou o QDPX que foi importado no master**, e o `manifest.json` vai com ela.

---

## 5. Como se nomeiam os ficheiros

### 5.1 A regra

```text
{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}
```

| Elemento | O que é | De onde vem (índice BTE) | Exemplo |
|---|---|---|---|
| `ANO` | ano de publicação, 4 dígitos | coluna `Ano` / `ANO` | `2026` |
| `AMBITO` | PRI · SPE · APU — ver §5.2 | inferido + vocabulário | `PRI` |
| `SEQ` | n.º sequencial do ano, 3 dígitos | `IDDocumento` / `ID:` (`377/2026` → `377`) | `377` |
| `TIPO` | tipo de documento, sem tradução | `TipoSubTipoDoc` / `TIPO DE DOCUMENTO:` | `CCT-ALT` |
| `CODIRCT` | código da convenção, estável entre revisões | `CodigoGEPDGERT` / `COD: (IRCT)` | `27251` |
| `NN` | número do boletim, 2 dígitos | `NBTE` / `Nº DO BOLETIM:` | `31` |
| `SIGLAS` | até 3 siglas das partes, separadas por `-`; se houver mais, `+N` | `Outorgantes` / `OUTORGANTE(S):` | `ACRAL-CESP-STRUP+2` |

Sem acentos, sem espaços, sem cedilhas. **Máximo 63 caracteres** — não 120. É o
limite de nome de documento do MAXQDA, e um nome que o ultrapasse é truncado na
importação, o que quebra o cruzamento com as variáveis de documento. A aplicação
encurta as siglas, nunca o prefixo, e assinala quando o fez.

**Porquê o `_BTE_{NN}`, que a v2.1 não tinha.** Três razões, por ordem de peso:
a aplicação lê o número do boletim do nome do ficheiro para emparelhar versões
de uma convenção e para voltar ao boletim de origem; sem ele, qualquer pergunta
sobre a proveniência de um ficheiro obriga a abrir o catálogo; e custa sete
caracteres num orçamento de 63 que a medição mostra folgado (o mais longo dos 14
nomes do BTE 31/2026 tem 59). A alternativa — deixar a aplicação ler tudo do
catálogo — foi considerada e recusada em [ADR-0016](../adr/0016-esquema-de-nomes-do-rnc.md):
acoplava cada fase do pipeline a um ficheiro que pode não estar na máquina.

**Nomes já atribuídos não se alteram.** Um corpus pode ter os dois esquemas à
mistura — o de 2025 (`26_PR_003_BTE_31_ACRAL_CESP`) e este. A aplicação lê os
dois e devolve a mesma coisa a quem os consome.

### 5.1-bis De onde vem o número sequencial

**Do `IDDocumento` da DGCP (ex-GEP), sem o ano.** O `377/2026` do índice dá o
`377` do nome.

Isto substitui a decisão tomada na [SPEC-0001](../../specs/0001-recolha-e-nomeacao-do-bte.md),
em que o número era atribuído pelo CRL, por um ordinal interno da aplicação. A
razão da mudança é de compatibilidade, e é a mais importante deste documento a
seguir ao código IRCT: **os nossos códigos devem coincidir ao máximo com os que
já existem**. Um número próprio obrigaria a manter uma segunda série, paralela e
sem correspondência com nada — e o número da DGCP é o que o próprio boletim usa
para citar o documento, e o que aparece nas cadeias de alteração
(`CCT-ALT.20250708.321/2025`).

O ordinal interno da aplicação continua a existir, mas só como recurso: quando o
índice não traz `IDDocumento`, o nome usa-o e **a linha fica marcada
`por_confirmar`, com o ficheiro por escrever**. Um número que parece da DGCP e
não é seria pior do que não ter número nenhum.

> Os ficheiros do ciclo de 2025 mantêm os números que têm. A regra aplica-se ao
> que entra de novo.

### 5.2 O âmbito — e porque tem de estar no nome

A equipa ainda não consegue processar as convenções da Administração Pública.
Chegar lá é um objetivo, mas está longe. Enquanto assim for, é preciso
distinguir à cabeça o que entra no pipeline do que fica só recolhido.

O número sequencial do BTE não serve para isso: é uma série única que atravessa
tudo. Sem um campo próprio, `377/2026` não diz se é processável.

Vocabulário fechado, três valores:

| Valor | O que é | Processável? |
|---|---|---|
| `PRI` | Sector privado | sim |
| `SPE` | Sector público empresarial — EPE, EM, SA de capitais públicos (Carris, Metropolitano, EPAL, RTP…) | sim |
| `APU` | Administração Pública — ACT e ACEP ao abrigo da LTFP, depositados na DGAEP | **não, ainda** |

Três letras e não duas, deliberadamente. O `PU` do SOP significava «sector
público empresarial», mas lê-se como «público». Essa ambiguidade custou caro.
`SPE` e `APU` não se confundem.

**Como é atribuído.** O âmbito não vem no índice. A aplicação propõe-o por três
vias, pela ordem da fiabilidade:

1. **Vocabulário** — `vocabularios/empregadores_ambito.csv`, lista editável de
   empregadores conhecidos. Tem prioridade sobre tudo.
2. **Regra** — tipo `ACEP` → APU; nome com `, EPE` / `, EM` / «Empresa
   Municipal» → SPE; município, câmara, freguesia, universidade, politécnico,
   direção-geral → APU.
3. **Omissão** — PRI, marcado como `omissao`.

Tudo o que a *regra* classifique como SPE ou APU sai com aviso e fica por rever.
**A aplicação nunca decide um APU em silêncio** — um falso APU retira um
documento do pipeline sem ninguém dar por isso. O catálogo regista, na coluna
`ambito_origem`, qual das três vias decidiu.

**Separação física também.** O `--esquema rnc` arruma em subpastas por âmbito:

```text
1_fontes/irct/convencoes/
├── PRI/    ← o pipeline lê daqui
├── SPE/    ← e daqui
└── APU/    ← recolhe-se e cataloga-se; NÃO se processa (ainda)
```

Assim «não conseguimos processar isto» deixa de ser uma nota num documento e
passa a ser a estrutura das pastas. O âmbito é o segundo eixo da arrumação; o
primeiro é a família documental, em [§5.7](#57-portarias-de-extensão-acordos-de-adesão-e-avisos).

### 5.3 O código IRCT é estável — e porquê

A v2.1 deixou isto como a única peça por confirmar, e como tarefa bloqueante.
**Está confirmado, e a verificação é reproduzível.**

O `COD: (IRCT)` que o BTE publica é o **identificador de acto de negociação da
DGERT com um dígito de família à frente**:

```text
27251  =  2  +  7251     2 → contrato coletivo
47252  =  4  +  7252     4 → acordo de empresa
```

A prova está no cruzamento do índice do BTE 31/2026 com o registo da DGERT
(`data-export`, folha «Negociação coletiva»). Os códigos dos 14 documentos do
boletim correspondem, um a um, a actos de negociação do registo — e esses actos
atravessam anos:

| Documento do BTE 31/2026 | `COD:` | Acto | Publicações do mesmo acto, no registo |
|---|---|---|---|
| 379 · CCT-ALT · AEVP–FESAHT | 26651 | 6651 | 2018 · 2022 · 2023 · 2025 (×2) · 2026 |
| 380 · CCT-ALT · AEVP–FESAHT | 26652 | 6652 | 2018 · 2022 · 2023 · 2025 (×2) · 2026 |
| 378 · CCT-ALT · CNIS–FNSTFPS | 26760 | 6760 | 2020 · 2021 (×2) · 2023 (×2) · 2024 · 2025 · 2026 |
| 384 · AE-ALT · AWP–STAS | 47120 | 7120 | 2024 · 2025 · 2026 |
| 387 · AE-ALT-RECT · CARRISTUR | 47109 | 7109 | 2024 · 2025 · 2026 |

No registo, **1 110 dos 1 860 actos abrangem mais do que um ano**. O acto mais
antigo (4481) vai de 1977 a 1981. Isto é o comportamento de uma identidade de
convenção, não de um número de documento.

> **Nota metodológica.** O argumento da v2.1 — «há 14 documentos com 14 códigos
> distintos, o que é consistente com a hipótese» — não provava nada: 14 códigos
> distintos num boletim são igualmente consistentes com um código atribuído por
> documento. O que prova é o cruzamento acima, que é de outra natureza: mostra o
> *mesmo* código a reaparecer em anos diferentes, na *mesma* convenção. Duas
> observações contrariavam a hipótese antes desta verificação e agora explicam-se:
> os pares 379/380 (26651/26652) e 382/383 (47252/47253) têm códigos
> consecutivos — porque são actos consecutivos no registo da DGERT, não porque
> sejam o mesmo documento.

**O que isto permite:**

```bash
ls 1_fontes/irct/*/*_27251_*      # toda a história desta convenção, em qualquer ano
```

E permite ligar o trabalho do RNC ao registo da DGERT: a coluna
`acto_negociacao` do catálogo dá o identificador sem o dígito de família, que é
a chave de junção com `vocabularios/actos_negociacao.csv`.

**O que fica por saber, e é preciso definir: a tabela de famílias da DGCP.**

O dígito à frente do código é uma família de instrumento. Estão **verificados
dois**, por cruzamento com o registo:

| Dígito | Família | Exemplo |
|---|---|---|
| `2` | contrato coletivo de trabalho | 27251 → acto 7251 |
| `4` | acordo de empresa | 47252 → acto 7252 |

Os dígitos dos **acordos coletivos de trabalho, portarias de extensão, acordos
de adesão e decisões arbitrais estão por determinar**: nenhum destes tipos
aparece no único boletim verificado, e a DGCP (ex-GEP) não publica a tabela.

Enquanto não estiver determinada, a aplicação **não adivinha**: um código de
cinco algarismos cujo primeiro dígito não seja 2 nem 4 sai com a coluna
`acto_negociacao` **vazia**, e a coluna `cod_irct` guarda na mesma o código
completo. Uma coluna vazia é um facto visível; um acto errado é uma junção
errada com o registo da DGERT, e essas não se notam.

Fechar isto é a [tarefa 2 do §10](#10-o-que-falta-fazer). Há dois caminhos: pedir
a tabela à DGCP, ou recolher três ou quatro boletins que tragam um ACT e uma
portaria de extensão e inferir os dígitos por cruzamento, como se fez para o 2 e
o 4.

### 5.4 Exemplos reais, gerados e testados

Estes 14 nomes foram produzidos pela aplicação sobre o `BTE31_2026.xlsx`, sem
intervenção manual, com `vocabularios/siglas_organizacoes.csv` e
`vocabularios/empregadores_ambito.csv`:

```text
2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2
2026_PRI_378_CCT-ALT_26760_BTE_31_CNIS-FNSTFPS
2026_PRI_379_CCT-ALT_26651_BTE_31_AEVP-FESAHT
2026_PRI_380_CCT-ALT_26652_BTE_31_AEVP-FESAHT
2026_PRI_381_CCT-ALT_26957_BTE_31_ACIBARCEL-AEDVC-Independe   ← sigla derivada, por confirmar
2026_SPE_382_AE_47252_BTE_31_EmpresaMetropolitana-SINTAP      ← âmbito pelo vocabulário
2026_PRI_383_AE_47253_BTE_31_IBERCOURIER-SNTCT
2026_PRI_384_AE-ALT_47120_BTE_31_AWP-STAS
2026_PRI_385_AE-ALT_47140_BTE_31_APSolutionsGMBH-STAS         ← sigla derivada, por confirmar
2026_PRI_386_AE-ALT_46771_BTE_31_COPEFAP-SPGL-CESP+1
2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-ASPTC         ← partes lidas do título
2026_SPE_388_AE-ALT-RECT_47126_BTE_31_CARRISTUR-FECTRANS      ← partes lidas do título
2026_SPE_389_AE-ALT-RECT_47110_BTE_31_CARRISTUR-SITRA         ← partes lidas do título
2026_SPE_390_AE-ALT-RECT_47111_BTE_31_CARRISTUR-Motoristas    ← partes do título + sigla derivada
```

Repare no par 379/380: mesmas partes, mesmo tipo, mesmo dia — mas códigos IRCT
diferentes (26651 e 26652). São duas convenções distintas da AEVP com a FESAHT,
uma para administrativos e outra para armazéns, e o registo da DGERT confirma-o:
são dois actos com histórias paralelas desde 2018. Sem o código IRCT seriam
indistinguíveis pelo nome.

### 5.5 Os casos que o script não resolve sozinho

**a) Retificações não trazem as partes — mas o título traz.** Os quatro
documentos `AE-ALT-RECT` do BTE 31 têm a coluna de outorgantes vazia. A v2.1
resolvia isto herdando as siglas do documento retificado, o que obrigava a
processar os boletins por ordem e a passar `--catalogo-anterior`.

**Não é preciso.** As partes constam do título do próprio documento
(«Acordo de empresa entre a CARRISTUR … e a Associação Sindical dos
Trabalhadores da Carris e Participadas, (ASPTC) - Retificação»), e a aplicação
lê-as de lá. Está verificado nos quatro casos. A linha fica marcada com
«outorgantes lidos do título — confirmar», porque um título é uma fonte menos
estruturada do que uma coluna, mas o ficheiro é nomeado e não fica bloqueado.

> Continua a valer processar os boletins por ordem crescente e a acumular o
> catálogo: é o que dá a cadeia de alterações completa (`§7-a`) e o que evita
> reatribuir números. Só deixou de ser *condição* para nomear uma retificação.

**b) Siglas em falta ou ambíguas.** Dois problemas diferentes, com respostas
diferentes.

*Siglas em falta.* Nem toda a entidade tem sigla no registo — tipicamente as
empresas, em acordos de empresa. A aplicação deriva um nome feio
(`EmpresaMetropolitana`, `APSolutionsGMBH`), marca a linha como `por_confirmar`
e **não escreve o ficheiro**. A confirmação tem de acontecer antes de o nome
ficar permanente, não depois. Resolve-se acrescentando uma linha à tabela da
equipa; não se inventa no nome do ficheiro.

*Siglas duplicadas.* Este era o caso que exigia decisão humana, e **deixou de
exigir**. Das 2 403 organizações do registo, **391 siglas são pedidas por mais
do que uma organização genuinamente diferente**. Decidir caso a caso significa
que o mesmo sindicato fica `SNM` num ficheiro e `SNMot` noutro, consoante quem
processou o boletim — e como um nome atribuído não muda, o engano não se
corrige.

A regra é uma **escada de candidatos**, percorrida por ordem até encontrar um
livre ([ADR-0017](../adr/0017-regra-de-desambiguacao-de-siglas.md)):

```text
1. SIGLA                         SNM
2. SIGLA + palavra distintiva    SNMotoristas
3. SIGLA + concelho da sede      SNMLisboa
4. SIGLA + 1.ª e 2.ª palavras
5. SIGLA + código DGERT          SNM14021       ← garantidamente único
```

Quatro propriedades fazem com que isto reduza o atrito em vez de o deslocar:

1. **Só mexe no que colide.** Uma sigla que só uma organização usa fica como
   está. O script resolve duplicados; não corrige o registo da DGERT.
2. **Quem fica com o degrau 1 é a linhagem mais antiga no registo** — o código
   DGERT mais baixo. Não é quem chegou primeiro ao script, pelo que duas
   pessoas, em máquinas diferentes, obtêm o mesmo resultado.
3. **A unicidade ignora maiúsculas**, porque `SNMotoristas` e `SNMOTORISTAS`
   são o mesmo ficheiro no Windows e no macOS.
4. **Uma sigla já atribuída não se reatribui.** O construtor lê o vocabulário
   anterior e fixa o que lá está; recalcular tudo exige `--reatribuir`.

E o construtor **falha** se sobrar um duplicado — não avisa, falha. A escada só
termina em candidatos livres, pelo que um duplicado significa um defeito da
regra, e um duplicado silencioso produz dois ficheiros com o mesmo nome.

> O `SNM` acima ilustra a regra, não é uma saída real: no registo da DGERT o
> Sindicato Nacional dos Motoristas não tem acrónimo, pelo que a sua sigla de
> base é `MOTORISTAS` e não colide com ninguém. Exemplos reais da escada, do
> export de 16/09/2026: `ACE` → `ACEAbrantes`, `AIM` → `AIMoagem`, `AES` →
> `AESines`, `ACIS` → `ACISBeira`, `AIT` → `AITomate` e `AITLisboa` (duas
> associações de industriais de tomate, resolvidas em degraus diferentes).

*Gerações não são conflito.* O SITESE mudou de nome seis vezes e continua a ser
o SITESE. A linhagem lê-se dos dois primeiros componentes do código DGERT
(`1.402.1` e `1.402.3` são a mesma organização; `1.402.1` e `5.10.0` não são).

Medido sobre o export de 16/09/2026: 2 403 organizações, 2 009 siglas distintas
à saída, **391 desambiguadas, 0 duplicados**. As mudanças ficam visíveis: a
coluna `sigla_base` guarda a sigla original e a `origem_sigla` regista que houve
desambiguação.

> A v2.1 dava 1 009 siglas distintas e 45 ambíguas. A diferença não é uma
> correção: são contagens de coisas diferentes. Aqui contam-se também as 1 017
> siglas que o próprio script fabricou para as organizações sem acrónimo no
> registo, precisamente para que se veja quantas são e não se confunda um
> palpite com um facto. Ver [§8](#8-vocabulários-controlados).

### 5.6 Nomes das outras famílias de ficheiro

| Família | Padrão | Exemplo |
|---|---|---|
| Índice BTE recebido | `AAAA_BTE_NN_indice.xlsx` | `2026_BTE_31_indice.xlsx` |
| BTE completo | `AAAA_BTE_NN.pdf` | `2026_BTE_31.pdf` |
| Export individual MAXQDA | `AAAA_{TEMA}_{INICIAIS}_AAAAMMDD.mqex` | `2026_C9-SALARIOS_AF_20270315.mqex` |
| Projeto master | `RNC_Dados_AAAA_master.mqda` | `RNC_Dados_2026_master.mqda` |
| Export por tema | `AAAA_{TEMA}_{CONTEUDO}_AAAAMMDD.xlsx` | `2026_C9-SALARIOS_segcod_20270401.xlsx` |
| Capítulo | `{codigo_roteiro}_{titulo_curto}.docx` | `4_07_remuneracoes.docx` |
| Relatório consolidado | `RNC_Dados_AAAA_AAAAMMDD.docx` | `RNC_Dados_2026_20270930.docx` |
| Catálogo | `catalogo_irct_AAAA.csv` | `catalogo_irct_2026.csv` |

`{CONTEUDO}` é uma palavra do vocabulário fechado: `segcod` (segmentos
codificados), `matriz` (matriz de códigos), `vardoc` (variáveis de documento),
`quadros`, `graficos`.

A versão ativa de um capítulo **não leva data**. É assim que se reconhece que é
a atual. As anteriores levam data e estão em `9_arquivo/`.

---

### 5.7 Portarias de extensão, acordos de adesão e avisos

O BTE publica quatro coisas diferentes sob o mesmo guarda-chuva dos IRCT. As três
últimas referem-se sempre a uma convenção concreta, mas **não são convenções**.

| Família | Tipos | O que é | Tem articulado? |
|---|---|---|---|
| `convencao` | CCT, ACT, ACEP, AE, DA | o articulado em si, e a decisão arbitral que o substitui | sim |
| `extensao` | PE, PCT, PRT | acto do **Governo** que alarga o âmbito de uma convenção a quem não está filiado nas partes | não — dois ou três artigos sobre âmbito e produção de efeitos |
| `adesao` | AA | uma **parte** adere a uma convenção de que não era outorgante | não |
| `aviso` | AVISO, AV | projeto de portaria, denúncia, caducidade | não |

Uma portaria de extensão não tem cláusula de retribuição, nem de tempo de
trabalho, nem nada do que o livro de códigos procura. Se entrar no pipeline
temático, **não dá erro: dá números errados** — cláusulas contadas a mais numa
convenção que as não tem, e uma portaria a aparecer nas estatísticas como se
fosse uma revisão.

#### Cada família na sua pasta

```text
1_fontes/irct/
├── convencoes/  PRI/ SPE/ APU/   ← o pipeline lê daqui, e só daqui
├── extensoes/   PRI/ SPE/
├── adesoes/     PRI/ SPE/
└── avisos/      PRI/ SPE/
```

A família vem antes do âmbito porque é a distinção que decide **o que se faz**
com o documento; o âmbito decide **se se consegue** fazer. São quatro níveis, o
máximo que a regra de higiene 5 admite — e é onde ela se gasta.

Um tipo que o vocabulário não conheça vai para `por_classificar/` e aparece no
relatório. Não é silenciado, mas também não é adivinhado.

#### Recolhem-se, catalogam-se, não se codificam

As três famílias param na fase 1 do [ciclo de vida](#4-o-ciclo-de-vida-de-um-documento).
São recolhidas, nomeadas e catalogadas — e ficam disponíveis para consulta e
para contagem, que é o que o relatório precisa delas. A coluna `processavel` do
catálogo cruza as duas peneiras:

| | família `convencao` | outra família |
|---|---|---|
| **âmbito PRI ou SPE** | processável | recolhido, não processado |
| **âmbito APU** | recolhido, não processado | recolhido, não processado |

E o pipeline **recusa-se a correr** se encontrar na pasta de entrada um ficheiro
cujo nome declare outra família, dizendo para onde apontar. Não avisa e
continua: um aviso no meio de 277 linhas de saída é um aviso que ninguém lê, e o
custo de errar aqui é uma análise inteira.

#### A relação com a convenção-base

Estes documentos só valem alguma coisa ligados à convenção a que se referem. O
catálogo tem duas colunas para isso:

| `relacao` | Quando | Significa |
|---|---|---|
| `altera` | CCT-ALT, AE-ALT, … | uma revisão do próprio articulado |
| `estende` | PE, PCT, PRT | alarga o âmbito da convenção a terceiros |
| `adere` | AA | uma parte passa a estar abrangida |
| `refere` | AVISO | menciona, sem produzir efeito |

`relacao_alvo` leva o documento-base no formato do índice
(`CCT.20260822.377/2026`). A distinção não se lê da coluna do índice — o formato
é o mesmo nos quatro casos — lê-se do **tipo** do documento. Sem ela, uma
contagem de revisões de uma convenção inclui portarias que nunca lhe alteraram
uma vírgula.

> **Por verificar.** O BTE 31/2026, o único boletim de que temos o índice, não
> traz nenhuma portaria de extensão nem nenhum acordo de adesão. A leitura da
> relação está implementada e testada contra um índice de ensaio construído com
> o mesmo cabeçalho, mas **não contra dados reais**. Duas coisas ficam por
> confirmar num boletim que os traga: se a coluna de alterações é mesmo onde a
> DGERT põe a convenção estendida, e se o `COD: (IRCT)` de uma portaria é o da
> convenção que ela estende ou um código próprio. Ver [§10, tarefa 3](#10-o-que-falta-fazer).

#### Uma família que estava a desaparecer

Os **acordos de adesão não eram recolhidos por omissão**. Uma adesão publicada
no BTE não deixava rasto nenhum — nem uma linha no catálogo a dizer que existia.
Passam a ser recolhidos como as outras três.

## 6. Os temas — e porque não estão nas pastas

Esta é a decisão mais importante deste documento e merece explicação.

### O problema

O CRL está a considerar a transição para o modelo europeu (Eurofound / OCDE /
WageIndicator), que substitui os pontos do roteiro atual (4.5 a 4.20) por 12
macro temas (`C1_PROFISSOES` a `C12_TECNOLOGIA_VERDE`), mais metadados de nível
1 e classificação de cláusulas de nível 3.

Se os temas estiverem nos nomes das pastas — como estavam no SOP v1.0
(`01_remuneracoes/`, `02_tempo_trabalho/`…) e nos códigos do README v1
(`4091_`, `4101_`) — a transição obriga a mexer em toda a árvore de ficheiros,
com todas as ligações a partir. E qualquer ajuste anual ao roteiro tem o mesmo
custo.

### A solução

Os temas são um **vocabulário**, não uma arrumação. Vivem num único ficheiro,
`vocabularios/temas.csv`, com, no mínimo, estas colunas:

| coluna | conteúdo |
|---|---|
| `codigo_roteiro` | `4.08` |
| `descricao_roteiro` | Direitos de personalidade e proteção de dados |
| `codigo_europeu` | `C10_TEMPO_TRAB` |
| `nivel` | 1 (metadado) / 2 (macro tema) / 3 (tipo de cláusula) |
| `ativo_em` | `2025+2026` |
| `perita_responsavel` | iniciais |
| `codebook` | `codebooks/4_08_protecao_dados.yaml` |

A coluna `codebook` é o acrescento face à v2.1, e é o que liga o vocabulário à
aplicação: **um tema novo é um ficheiro YAML em `codebooks/`, nunca uma
alteração ao código** (é uma das três invariantes da AppCCT). O `temas.csv` diz
qual é o YAML de cada tema; o pipeline recebe-o em `--codebook`.

Mudar de modelo passa a ser editar um CSV, não reorganizar pastas. As séries
históricas mantêm-se porque as duas colunas de código coexistem — é a «dupla
dinâmica» proposta no documento de transição europeia.

### A única exceção

`4_temas/` usa o tema no nome, porque é o ponto de entrega a pessoas externas —
cada perita recebe a sua pasta e não deve ter de navegar o resto. Mas essas
pastas são **geradas a partir do `temas.csv`**, nunca criadas à mão:

```text
4_temas/
├── C9-SALARIOS/
│   ├── 2026_C9-SALARIOS_segcod_20270401.xlsx
│   ├── 2026_C9-SALARIOS_matriz_20270401.xlsx
│   └── LEIAME.md          ← gerado: âmbito do tema, códigos, prazo, contacto
└── C10-TEMPO-TRAB/
```

Se no ano seguinte os temas forem outros, apaga-se e regenera-se. Nada mais na
estrutura é afetado.

> **Estado do `temas.csv`:** incompleto, e assumidamente. Estão preenchidas as
> linhas que se sustentam no que existe no projeto (o tema 4.08, que tem
> codebook e validação medida) e os quatro códigos europeus citados no documento
> de transição. Os restantes macro temas e o mapeamento dos pontos 4.5 a 4.20
> têm de ser copiados do `plano_transicao_livro_codigos_europeu.xlsx`, que não
> está no repositório. Não se inventaram. Ver [§10, tarefa 1](#10-o-que-falta-fazer).

---

## 7. O catálogo

`0_gestao/catalogo/catalogo_irct_2026.csv` — uma linha por documento, gerada
pela aplicação a partir dos índices do BTE:

```bash
python -m cct.catalogo \
    --indices 1_fontes/indices_bte \
    --saida 0_gestao/catalogo/catalogo_irct_2026.csv \
    --siglas 0_gestao/vocabularios/siglas_equipa.csv \
    --siglas vocabularios/siglas_organizacoes.csv
```

**Colunas produzidas automaticamente** (29):

`nome_canonico` · `ficheiro_destino` · `ficheiro_origem` · `ano` · `seq_anual` ·
`tipo_documento` · `familia` · `processavel` · `ambito` · `ambito_origem` ·
`cod_irct` · `acto_negociacao` · `bte_numero` · `bte_data` · `pagina_inicio` ·
`pagina_fim` · `n_outorgantes` · `outorgantes` · `relacao` · `relacao_alvo` ·
`altera_estruturado` · `altera_por_resolver` · `vide_em_vigor` ·
`materias_detectadas` · `sectores_a_classificar` · `url_fonte` · `titulo` ·
`estado` · `avisos`

**Colunas preenchidas pela equipa ao longo do ciclo** (5):

`temas_atribuidos` · `tecnico` · `data_validacao` · `perita` · `observacoes`

**Regerar o catálogo não apaga trabalho humano.** As cinco colunas da equipa são
recuperadas do catálogo anterior, procuradas pelo `nome_canonico` — que, por
convenção, nunca muda. E uma linha que deixe de aparecer nos índices **não é
apagada**: fica, com o aviso «já não consta dos índices lidos — verificar». Um
documento que desaparece de um índice é um facto a investigar, não a esquecer.

**Porque é que isto substitui a lista SharePoint do SOP v1.0:** não substitui —
alimenta-a. O catálogo é gerado, é versionável, e funciona sem SharePoint. Quem
quiser a lista importa este CSV. A diferença é que a fonte de verdade passa a
ser um ficheiro que se pode regerar, e não uma lista que só existe num sítio.

### Três coisas que o catálogo resolve

#### a) As relações entre documentos vêm estruturadas

A coluna de alterações do índice tem um formato regular:

```text
CCT-ALT.20250708.321/2025
   │        │        └── sequencial/ano do documento alterado
   │        └── data
   └── tipo
```

Os 13 valores presentes no BTE 31/2026 correspondem todos ao padrão. Isto dá a
cadeia de alterações sem trabalho de extração — a aplicação separa-a em
`altera_estruturado` (processado) e `altera_por_resolver` (o resto, para revisão
manual).

**Atenção a uma armadilha do dialeto técnico do índice:** a cadeia vem partida
em duas colunas (`DocAlteradosPorEste` e `DocAlteradosPorEste2`). A aplicação
junta-as. Ler só a primeira perdia metade da cadeia, em silêncio.

#### b) Sectores e matérias no mesmo campo

A coluna dos sectores mistura dois vocabulários. Exemplo real do BTE 31:

```text
VINHOS E BEBIDAS ESPIRITUOSAS   ← sector
VITICULTURA                     ← sector
COMÉRCIO POR GROSSO DE BEBIDAS  ← sector
REMUNERAÇÕES                    ← matéria
SUBSÍDIO DE REFEIÇÃO            ← matéria
```

A v2.1 deixava isto como decisão de equipa por tomar. **Está decidido, na
direção conservadora:** a aplicação reconhece as *matérias* — que são um
conjunto pequeno e fechado, o do livro de códigos — e trata como **candidato a
sector** tudo o resto, em `sectores_a_classificar`. Nada é descartado e nada é
assumido: cada item cai num dos dois lados, e o lado não reconhecido fica
explicitamente marcado para decisão humana.

A razão para reconhecer matérias e não sectores: as matérias são estáveis e
poucas; os sectores são abertos e mudam com a CAE. Uma lista de sectores
ficaria desatualizada e falharia em silêncio; uma lista de matérias, quando
falha, falha para o lado seguro — manda o item para revisão.

**Por decidir ainda:** se os sectores passam a CAE/NACE. É a
[tarefa 2 do §10](#10-o-que-falta-fazer) e é uma decisão de equipa, não técnica.
A coluna `sectores_a_classificar` é exatamente o material de trabalho para a
tomar.

#### c) As páginas saem do nome do ficheiro de origem

O nome que o BTE dá ao PDF codifica o intervalo de páginas em dois blocos de
quatro dígitos: `00260057.pdf` são as páginas 26 a 57. A aplicação extrai-o, e a
verificação é fácil: no BTE 31/2026 os 14 intervalos são contíguos e cobrem as
páginas 26 a 179 sem sobreposição nem lacuna. A coluna `PagVersaoEscrita` do
índice vem vazia neste dialeto, pelo que sem isto o catálogo não teria páginas.

---

## 8. Vocabulários controlados

Todos em `vocabularios/`, todos em CSV com separador `;` e UTF-8, todos
versionados com o código. Na árvore do RNC vivem em
`0_gestao/vocabularios/` — são o mesmo ficheiro.

| Ficheiro | Conteúdo | Estado |
|---|---|---|
| `siglas_organizacoes.csv` | 2 403 organizações com sigla canónica **sem duplicados**, sigla de origem, tipo, lado, concelho e estado | produzido |
| `siglas_ambiguas.csv` | verificação: fica **vazio** se a regra do ADR-0017 funcionou. Um valor aqui é um defeito | produzido |
| `actos_negociacao.csv` | 1 860 actos de negociação, com o primeiro e o último ano de cada um | produzido |
| `empregadores_ambito.csv` | empregadores com âmbito conhecido (PRI/SPE/APU) | semente com 10 entradas — a completar |
| `tipos_documento.csv` | CCT, CCT-ALT, AE, AE-ALT, AE-ALT-RECT, ACT, ACEP, PE, AA, DA… | produzido |
| `estados.csv` | recolhido → extraído → pré-codificado → empacotado → em validação → validado → integrado → exportado | produzido |
| `temas.csv` | crosswalk roteiro ↔ macro temas europeus ↔ codebook | **incompleto** — ver §6 e §10 |

Os três primeiros regeram-se do export da DGERT:

```bash
python scripts/construir_vocabularios.py 1_fontes/externas/data-export_….xlsx
```

Uma corrida normal **não mexe nas siglas já atribuídas**: lê o vocabulário
anterior e fixa o que lá está, acrescentando só as organizações novas. Para
recalcular tudo é preciso `--reatribuir`, que muda siglas em uso e só se usa
quando se sabe que nenhum ficheiro foi ainda nomeado com elas.

**Uma distinção que importa: `origem_sigla`.** Cada linha de
`siglas_organizacoes.csv` declara de onde veio a sigla:

- `registo` (1 360 linhas) — o acrónimo consta do registo da DGERT;
- `derivada` (26) — extraída da denominação por um padrão fiável, entre
  parênteses ou a seguir a um travessão;
- `recurso` (1 017) — **inventada pelo script**, em CamelCase das palavras
  significativas. `Sindicato Nacional dos Motoristas` → `Motoristas`;
- qualquer das anteriores com `+desambiguada` — a sigla colidia com a de outra
  organização e subiu a escada do [ADR-0017](../adr/0017-regra-de-desambiguacao-de-siglas.md).
  A coluna `sigla_base` guarda a que o registo dava.

**A aplicação não carrega as de origem `recurso`.** Se as carregasse, calava o
aviso de «confirmar» e transformava um palpite num facto: o ficheiro passaria a
chamar-se `Motoristas` sem ninguém ter decidido que se chama assim. Ficam no
CSV, para se ver o que falta; promovem-se editando `origem_sigla` para `equipa`
depois de alguém as ter visto.

**Regra geral:** se um valor não está no vocabulário, não se inventa —
acrescenta-se ao vocabulário, com data e responsável. É o que impede que
«Teletrabalho», «teletrabalho» e «Tele-trabalho» convivam como se fossem coisas
diferentes.

---

## 9. Regras de higiene

1. **Nunca editar ficheiros em `1_fontes/`.** Chegou de fora, fica como chegou.
2. **Uma versão ativa por documento.** As anteriores vão para `9_arquivo/` com
   data no nome. Nada fica «à mistura».
3. **Não duplicar.** Se um ficheiro é preciso em dois sítios, referencia-se o
   caminho. Duplicar garante que as duas cópias divergem.
4. **Limpar antes de arquivar:** `Thumbs.db`, `.DS_Store`, `~$*.docx`,
   atalhos `.url`.
5. **Máximo quatro níveis de pastas.** Se parecer preciso um quinto, o que falta
   é um ficheiro-índice, não outra pasta.
6. **Nomes:** só letras sem acento, dígitos, `_`, `-` e o `+` do contador de
   outorgantes. O sublinhado separa campos; o hífen separa itens dentro de um
   campo (as siglas).
7. **Nada de dados pessoais nos nomes de ficheiro.** As siglas são de
   organizações, não de pessoas. As iniciais de quem valida aparecem em
   `.mqex` e no log de integração, que ficam dentro do projeto.

### 9-bis. Os dois dialetos do índice

A DGERT distribui o índice do BTE em dois formatos de cabeçalho, e é preciso
saber porque nenhuma ferramenta que leia só um deles serve:

| | Dialeto **rótulo** (2025) | Dialeto **técnico** (2026) |
|---|---|---|
| tipo | `TIPO DE DOCUMENTO:` | `TipoSubTipoDoc` |
| código | `COD:\n(IRCT)` | `CodigoGEPDGERT` |
| boletim | `Nº DO BOLETIM:` | `NBTE` |
| ficheiro | `Página (criado)` | `NomePDF` |
| ligação | `Link para o documento (CRIADO)` | `URLPDF` |

Não há um único cabeçalho em comum entre os dois, além de `Ano`, `CAE` e
`Outorgantes`. A aplicação lê os dois: cada campo interno aceita os *aliases*
dos dois lados, e a comparação é feita sobre o nome normalizado (sem acentos,
sem pontuação, sem maiúsculas), não pela posição da coluna. Um índice novo com
um cabeçalho desconhecido não é silenciado — a coluna fica vazia e o problema
aparece no relatório.

### 9-ter. O que o registo da DGERT não cobre

O `data-export_….xlsx` **não cobre a Administração Pública**. Verificado:

| Verificação | Resultado |
|---|---|
| Registos com tipo ACEP | 0 |
| Municípios, câmaras, freguesias, universidades ou politécnicos no registo de empregadores | 0 |
| Categorias existentes no registo de empregadores | apenas associação / federação / união / confederação de empregadores |
| Os 1 358 «Acordo coletivo de trabalho» | todos do privado — são ACT do art. 2.º do Código do Trabalho, não da LTFP |
| Domínio dos URL | `bte.gep.mtsss.gov.pt` — os índices novos usam `bte.dgcp.mtsss.gov.pt` |

A razão é estrutural, não uma falha do export: um município não é uma associação
de empregadores, logo não cabe naquele registo. Os IRCT da Administração Pública
são depositados na DGAEP, não na DGERT.

**Consequências práticas:**

1. A tabela de siglas cobre bem o lado sindical — incluindo SINTAP, FESAP,
   FNSTFPS, STAL, que negoceiam também no privado — mas **não tem empregadores
   públicos**. Terão de ser acrescentados à mão à medida que aparecerem.
2. Qualquer estatística de cobertura calculada a partir deste export é do sector
   privado e público empresarial, **e tem de o dizer**.
3. Para chegar a processar a Administração Pública será preciso uma segunda
   fonte, do lado da DGAEP. É trabalho futuro, mas o campo `APU` já está no
   sítio para o receber sem alterar nada.

**E uma coluna que não deve ser usada como parece:** `Ativa ou Extinta` é o
estado de *registo*, não de atividade. Há organizações marcadas «Activa» sem
qualquer atividade registada há mais de dez anos. Para saber se uma organização
está viva, usar a coluna `ultima_atividade`, que
`vocabularios/siglas_organizacoes.csv` transporta.

---

## 10. O que falta fazer

As três tarefas que a v2.1 dava como bloqueantes estão fechadas
([§5.3](#53-o-código-irct-é-estável-e-porquê), [§7-b](#b-sectores-e-matérias-no-mesmo-campo),
[§5.5](#55-os-casos-que-o-script-não-resolve-sozinho)), e a desambiguação de
siglas deixou de ser trabalho manual ([ADR-0017](../adr/0017-regra-de-desambiguacao-de-siglas.md)).
O que fica é trabalho de preenchimento e de decisão, e **nada disto impede
começar o ciclo**. Só a tarefa 2 depende de informação que não temos.

| # | Tarefa | Porquê | Esforço | Bloqueia |
|---|---|---|---|---|
| 1 | **Completar o `temas.csv`** a partir do `plano_transicao_livro_codigos_europeu.xlsx` | Sem ele, `4_temas/` não se gera e a transição europeia não tem onde assentar | 1 dia | `4_temas/` |
| 2 | **Obter a tabela de famílias do `COD: (IRCT)` da DGCP (ex-GEP)** — ou inferir os dígitos em falta de boletins que tragam um ACT e uma portaria de extensão | Só estão verificados os dígitos `2` e `4`. Sem os restantes, esses documentos ficam sem ligação ao registo da DGERT. A aplicação não adivinha: deixa a coluna vazia | ½ dia se a tabela existir; 1 dia por inferência | ligação ao registo para ACT, PE, AA e decisões arbitrais |
| 3 | **Verificar as portarias de extensão e os acordos de adesão com dados reais** — um boletim que os traga. Confirmar onde a DGERT põe a convenção estendida, e se o `COD: (IRCT)` de uma portaria é o da convenção ou próprio | A leitura da relação está implementada e testada contra um índice de ensaio, não contra dados reais. Se o `COD:` for próprio, a ligação portaria↔convenção passa a depender só da coluna de relação | ½ dia | contagem de cobertura por extensão |
| 4 | **Completar o `empregadores_ambito.csv`** — passagem sobre os acordos de empresa dos últimos 2–3 anos | Sem isto, empresas públicas entram como PRI por omissão e contaminam qualquer leitura por âmbito | 1–2 dias | leitura por âmbito |
| 5 | **Decidir se os sectores passam a CAE/NACE** | A separação já está feita; falta decidir o vocabulário de destino. Afeta a ligação a NACE prevista no modelo europeu | ½ dia + decisão de equipa | análise sectorial |
| 6 | **Rever as 391 siglas desambiguadas** e promover as de origem `recurso` que forem boas | A regra garante que não há duplicados, não que a sigla escolhida é a que a equipa preferia. Rever uma vez fixa-a para sempre | 1 dia | nada — a regra já desbloqueou a nomeação em lote |
| 7 | **Migrar o ciclo anterior** para a nova estrutura | Ver a tabela de correspondência abaixo | 2–3 dias | — |

### Correspondência com o ciclo anterior, para a migração

| Ciclo 2025 (SOP v1.0 / README v1) | Nova estrutura |
|---|---|
| `01_roteiro/` | `0_gestao/roteiro/` + `0_gestao/livro_codigos/` |
| `02_recolha/bte/` | `1_fontes/bte_completo/` |
| `02_recolha/convencoes/por_sigla/` | `1_fontes/irct/convencoes/{AMBITO}/` (renomeado pela aplicação) |
| `data/raw/bte/bte_AAAA/extensoes/` (esquema de 2025) | separa-se em `extensoes/`, `adesoes/` e `avisos/`, pelo token do nome |
| `02_recolha/fontes_primarias/` | `1_fontes/externas/` |
| `03_analise/maxqda/` | `3_analise/master/` + `3_analise/mqex/` |
| `03_analise/temas_transversais/NN_tema/` | `4_temas/{CODIGO}/` — gerado, não migrado |
| `03_analise/comparacoes/` | `3_analise/comparacoes/` |
| `04_redacao/` | `5_redacao/` + `6_relatorio/` |
| lista SharePoint de metadados | `0_gestao/catalogo/` (o CSV alimenta a lista) |

**Sobre renomear o que já existe:** não se renomeia. Os ficheiros do ciclo de
2025 mantêm o nome que têm (`26_PR_003_BTE_31_ACRAL_CESP.pdf`) e a aplicação
continua a lê-los. O esquema novo aplica-se ao que entra de novo. Migrar a
estrutura de pastas é seguro; migrar nomes parte o trabalho já feito no MAXQDA,
que referencia os documentos pelo nome.

---

## 11. As ferramentas

Tudo dentro da aplicação, tudo com testes que correm no CI em Linux e macOS.

| Comando | O que faz |
|---|---|
| `python -m cct.recolha` | Lê os índices e descarrega os PDF. **Só liga à rede com `--confirmar-rede`**, só para anfitriões de uma lista fechada ([ADR-0015](../adr/0015-recolha-em-rede-desligada-por-omissao.md)) |
| `python -m cct.nomeacao --esquema rnc` | Atribui os nomes canónicos e arruma por família e âmbito. Sem `--aplicar` só simula |
| `python -m cct.catalogo` | Escreve o `catalogo_irct_AAAA.csv` |
| `python -m cct.aquisicao` | Encadeia recolha + nomeação, com relatório único |
| `python scripts/construir_vocabularios.py` | Reconstrói os vocabulários do export da DGERT |
| `python -m cct.pipeline_tema` | Extração, pré-codificação, diacronia, triagem → QDPX |
| `python -m cct.doctor` | Diz o que falta no ambiente, em português |

### A corrida de um número do BTE, do princípio ao fim

```bash
# 1. simulação — não liga à rede, não escreve ficheiro nenhum
python -m cct.recolha --indices 1_fontes/indices_bte

# 2. a sério (a única fase que toca na rede)
python -m cct.recolha --indices 1_fontes/indices_bte --confirmar-rede

# 3. nomear — simula primeiro, para ver os avisos
python -m cct.nomeacao --esquema rnc --destino 1_fontes/irct \
    --siglas 0_gestao/vocabularios/siglas_equipa.csv \
    --siglas vocabularios/siglas_organizacoes.csv \
    --ambitos vocabularios/empregadores_ambito.csv

# 4. resolver os avisos acrescentando linhas aos vocabulários, e só depois:
python -m cct.nomeacao --esquema rnc --destino 1_fontes/irct \
    --siglas 0_gestao/vocabularios/siglas_equipa.csv \
    --siglas vocabularios/siglas_organizacoes.csv \
    --ambitos vocabularios/empregadores_ambito.csv --aplicar

# 5. catálogo
python -m cct.catalogo --indices 1_fontes/indices_bte \
    --saida 0_gestao/catalogo/catalogo_irct_2026.csv \
    --siglas 0_gestao/vocabularios/siglas_equipa.csv \
    --siglas vocabularios/siglas_organizacoes.csv

# 6. pipeline do tema, só sobre o que é processável
python -m cct.pipeline_tema \
    --pdfs 1_fontes/irct/convencoes/PRI \
    --codebook codebooks/4_08_protecao_dados.yaml \
    --out 2_processamento
```

**Duas coisas sobre esta sequência.** A nomeação **recusa-se a escrever** um
ficheiro cujo nome dependa de uma sigla derivada por heurística: o passo 3
mostra o que falta, o passo 4 é o que resolve. Quem quiser aceitar o risco
conscientemente — uma corrida em lote já revista — usa `--aceitar-heuristicas`.
E `--siglas` é repetível: em caso de conflito ganha o primeiro ficheiro
indicado, pelo que a tabela da equipa vem antes da tabela gerada.

### Estado verificado (BTE 31/2026, 14 documentos)

| Verificação | Resultado |
|---|---|
| Linhas lidas do índice no dialeto técnico | 14/14 |
| Nomes canónicos gerados | 14/14 |
| Nomes com mais de 63 caracteres | 0 (o mais longo tem 59) |
| Colisões de nome | 0 |
| Nomes aceites pelo `cct.localizador` | 14/14 |
| Relações `altera` processadas | 13/13 |
| Páginas extraídas do nome de origem | 14/14, contíguas de 26 a 179 |
| Retificações resolvidas **sem** catálogo acumulado | 4/4 |
| Âmbitos SPE detetados | 5 (1 por regra, 4 por vocabulário) |
| Siglas por recurso final (nome feio) | 4 — `EmpresaMetropolitana`, `APSolutionsGMBH`, `Independe`, `Motoristas`. Acrescentar à tabela antes de usar em produção |
| Siglas duplicadas no vocabulário, depois da regra | 0, de 391 conflitos |
| Duas corridas do construtor dão o mesmo vocabulário | sim, byte a byte |
| Sectores/matérias separados | 14/14, sem perda de itens |
| Famílias no BTE 31/2026 | 14 convenções; 0 portarias, 0 adesões, 0 avisos |
| Portarias, adesões e avisos | verificados contra índice de ensaio, **não contra dados reais** — tarefa 3 do §10 |
| O pipeline recusa um ficheiro que não é convenção | sim, com mensagem a dizer para onde apontar |

Reproduzível com `python -m pytest tests/test_rnc.py`.

---

## Documentos relacionados

| Documento | O quê |
|---|---|
| [ADR-0016](../adr/0016-esquema-de-nomes-do-rnc.md) | Porque é que o esquema de nomes é este, e o que se recusou |
| [SPEC-0003](../../specs/0003-compatibilizacao-com-a-gestao-documental-do-rnc.md) | O que se construiu para chegar aqui, e como se sabe que ficou certo |
| [SPEC-0001](../../specs/0001-recolha-e-nomeacao-do-bte.md) | A recolha e a nomeação, antes desta compatibilização |
| [`pastas/`](pastas/) | Um README por pasta principal da árvore do RNC |
| [guia de operação](../operacao/guia-operacao.md) | Como se opera a aplicação, e o que fazer quando corre mal |
| [organização do workspace](../dados/organizacao-workspace.md) | O ciclo de vida das pastas da aplicação |

---

**Dúvidas sobre este documento:** coordenação do RNC.

**Alterações à convenção de nomes exigem decisão de equipa e nova versão deste
ficheiro** — e não se alteram nomes já atribuídos.
