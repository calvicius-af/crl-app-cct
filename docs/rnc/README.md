# RNC — Como organizamos e nomeamos os ficheiros

Relatório da Negociação Coletiva · Centro de Relações Laborais
**Versão 3.0 · 16 de setembro de 2026** · substitui `README.Estrutura_RNC_2027.docx` (v2.1),
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
│   ├── irct/                    ★ PDF individuais, já renomeados, em PRI/ SPE/ APU/
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
| 1 | Recolha | Técnico de recolha | índice XLSX do BTE | 1 PDF por IRCT, renomeado, + linha no catálogo | `1_fontes/irct/{AMBITO}/` | `2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf` |
| 2 | Extração | AppCCT (automático) | PDF | texto + estrutura | `2_processamento/texto/` | `…_ACRAL-CESP-STRUP+2.txt` e `.doc.json` |
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
5. **Cada corrida da aplicação deixa um `manifest.json`** com o comando, o
   *commit*, as versões, os *hashes* das entradas e saídas, as contagens e os
   problemas. É o que responde, meses depois, a «como é que isto foi produzido?».

### 4-bis. A correspondência com as pastas da AppCCT

| Pasta do RNC | Pasta da AppCCT | Como se passa de uma à outra |
|---|---|---|
| `1_fontes/indices_bte/` | `data/raw/indices/` | cópia, ou a mesma pasta por atalho |
| `1_fontes/irct/{AMBITO}/` | `data/raw/bte/bte_2026/{AMBITO}/` | escrito por `python -m cct.nomeacao --esquema rnc` |
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
1_fontes/irct/
├── PRI/    ← o pipeline lê daqui
├── SPE/    ← e daqui
└── APU/    ← recolhe-se e cataloga-se; NÃO se processa (ainda)
```

Assim «não conseguimos processar isto» deixa de ser uma nota num documento e
passa a ser a estrutura das pastas.

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

**O que fica por saber.** O dígito de família está observado para dois valores
(`2` contrato coletivo, `4` acordo de empresa). Os acordos coletivos de trabalho
e as portarias de extensão não aparecem no BTE 31/2026, pelo que o seu dígito
não está verificado. A aplicação é conservadora: só retira o dígito quando o
código tem exatamente cinco algarismos, e devolve o código inteiro fora disso.
Confirmar com um boletim que traga um ACT é meio dia de trabalho.

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

**b) Siglas em falta ou ambíguas.** Nem toda a entidade tem sigla óbvia. A
aplicação consulta primeiro `vocabularios/siglas_organizacoes.csv`, construído
do registo da DGERT. Quando a entidade não estiver lá — tipicamente empresas em
acordos de empresa — **acrescenta-se uma linha à tabela e não se inventa no nome
do ficheiro**. Enquanto não se acrescentar, a aplicação deriva um nome feio
(`EmpresaMetropolitana`, `APSolutionsGMBH`, `Independe`), marca a linha como
`por_confirmar` e **não escreve o ficheiro** — a confirmação tem de acontecer
antes de o nome ficar permanente, não depois.

Dimensão do problema, medida sobre o export de 16/09/2026: 2 403 organizações,
1 618 siglas distintas, das quais **147 são usadas por linhagens genuinamente
diferentes** (as restantes coincidências são entre gerações da mesma
organização, o que é inofensivo para nomear ficheiros). A lista das 147 está em
`vocabularios/siglas_ambiguas.csv`, com uma coluna `resolucao` por preencher.

> A v2.1 dava 1 009 siglas distintas e 45 ambíguas. A diferença não é uma
> correção: são contagens de coisas diferentes. Aqui contam-se também as 1 017
> siglas que o próprio script derivou para as organizações sem acrónimo no
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

**Colunas produzidas automaticamente** (26):

`nome_canonico` · `ficheiro_destino` · `ficheiro_origem` · `ano` · `seq_anual` ·
`tipo_documento` · `familia` · `ambito` · `ambito_origem` · `cod_irct` ·
`acto_negociacao` · `bte_numero` · `bte_data` · `pagina_inicio` · `pagina_fim` ·
`n_outorgantes` · `outorgantes` · `altera_estruturado` · `altera_por_resolver` ·
`vide_em_vigor` · `materias_detectadas` · `sectores_a_classificar` ·
`url_fonte` · `titulo` · `estado` · `avisos`

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
| `siglas_organizacoes.csv` | 2 403 organizações da DGERT com sigla canónica, origem da sigla, tipo, lado e estado | produzido |
| `siglas_ambiguas.csv` | 147 siglas usadas por linhagens diferentes, com coluna `resolucao` por preencher | produzido, por decidir |
| `actos_negociacao.csv` | 1 860 actos de negociação, com o primeiro e o último ano de cada um | produzido |
| `empregadores_ambito.csv` | empregadores com âmbito conhecido (PRI/SPE/APU) | semente com 10 entradas — a completar |
| `tipos_documento.csv` | CCT, CCT-ALT, AE, AE-ALT, AE-ALT-RECT, ACT, ACEP, PE, AA, DA… | produzido |
| `estados.csv` | recolhido → extraído → pré-codificado → empacotado → em validação → validado → integrado → exportado | produzido |
| `temas.csv` | crosswalk roteiro ↔ macro temas europeus ↔ codebook | **incompleto** — ver §6 e §10 |

Os três primeiros regeram-se do export da DGERT:

```bash
python scripts/construir_vocabularios.py 1_fontes/externas/data-export_….xlsx
```

**Uma distinção que importa: `origem_sigla`.** Cada linha de
`siglas_organizacoes.csv` declara de onde veio a sigla:

- `registo` (1 360 linhas) — o acrónimo consta do registo da DGERT;
- `derivada` (26) — extraída da denominação por um padrão fiável, entre
  parênteses ou a seguir a um travessão;
- `recurso` (1 017) — **inventada pelo script**, em CamelCase das palavras
  significativas. `Sindicato Nacional dos Motoristas` → `Motoristas`.

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
[§5.5](#55-os-casos-que-o-script-não-resolve-sozinho)). O que fica é trabalho de
preenchimento e de decisão, e nada disto impede começar o ciclo.

| # | Tarefa | Porquê | Esforço | Bloqueia |
|---|---|---|---|---|
| 1 | **Completar o `temas.csv`** a partir do `plano_transicao_livro_codigos_europeu.xlsx` | Sem ele, `4_temas/` não se gera e a transição europeia não tem onde assentar | 1 dia | `4_temas/` |
| 2 | **Decidir se os sectores passam a CAE/NACE** | A separação já está feita; falta decidir o vocabulário de destino. Afeta a ligação a NACE prevista no modelo europeu | ½ dia + decisão de equipa | análise sectorial |
| 3 | **Completar o `empregadores_ambito.csv`** — passagem sobre os acordos de empresa dos últimos 2–3 anos | Sem isto, empresas públicas entram como PRI por omissão e contaminam qualquer leitura por âmbito | 1–2 dias | leitura por âmbito |
| 4 | **Resolver as 147 siglas ambíguas** e promover as `recurso` que forem boas | Cada uma que fique por resolver é um ficheiro que a aplicação recusa escrever | 1 dia | nomeação em lote |
| 5 | **Confirmar o dígito de família do código IRCT** para ACT e portarias de extensão, com um boletim que os traga | Só estão observados os dígitos 2 e 4. A aplicação é conservadora entretanto | ½ dia | ligação ao registo da DGERT |
| 6 | **Migrar o ciclo anterior** para a nova estrutura | Ver a tabela de correspondência abaixo | 2–3 dias | — |

### Correspondência com o ciclo anterior, para a migração

| Ciclo 2025 (SOP v1.0 / README v1) | Nova estrutura |
|---|---|
| `01_roteiro/` | `0_gestao/roteiro/` + `0_gestao/livro_codigos/` |
| `02_recolha/bte/` | `1_fontes/bte_completo/` |
| `02_recolha/convencoes/por_sigla/` | `1_fontes/irct/{AMBITO}/` (renomeado pela aplicação) |
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
| `python -m cct.nomeacao --esquema rnc` | Atribui os nomes canónicos e arruma em `PRI/`, `SPE/`, `APU/`. Sem `--aplicar` só simula |
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
    --pdfs 1_fontes/irct/PRI \
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
| Sectores/matérias separados | 14/14, sem perda de itens |

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
