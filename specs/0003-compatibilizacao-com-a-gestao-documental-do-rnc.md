# SPEC-0003: compatibilização com a gestão documental do RNC

- **Estado:** Implementada
- **Data:** 2026-09-16
- **Autoria:** CRL (António Fula)
- **Decisões relacionadas:** [ADR-0016](../docs/adr/0016-esquema-de-nomes-do-rnc.md),
  [ADR-0017](../docs/adr/0017-regra-de-desambiguacao-de-siglas.md),
  [ADR-0018](../docs/adr/0018-familias-documentais-em-pastas-separadas.md),
  [ADR-0019](../docs/adr/0019-lista-do-ine-como-sinal-de-ambito.md),
  [ADR-0015](../docs/adr/0015-recolha-em-rede-desligada-por-omissao.md),
  [ADR-0004](../docs/adr/0004-fases-desacopladas-por-ficheiros.md),
  [ADR-0009](../docs/adr/0009-layout-do-repositorio.md)

## Problema

A gestão documental do Relatório da Negociação Coletiva fixou uma convenção de
nomes, uma árvore de pastas e um catálogo, descritos na versão 2.1 do seu
README. A AppCCT faz recolha, nomeação, extração e pré-codificação com outra
convenção. Os dois lados descrevem o mesmo trabalho e não encaixam.

Quatro pontos de atrito, por ordem de gravidade:

0. **Portarias de extensão e acordos de adesão sem tratamento próprio.** Todas
   as famílias não-convenção iam para uma só pasta `extensoes/`, cujo propósito
   era ficar fora do `glob` do pipeline — e no esquema RNC nem isso, o que fazia
   com que uma portaria fosse codificada como se fosse uma convenção. Os acordos
   de adesão não eram sequer recolhidos por omissão.
1. **A aplicação não lê o índice de 2026.** A DGERT distribui o índice do BTE em
   dois dialetos de cabeçalho, e nenhum campo relevante coincide entre eles
   (`TIPO DE DOCUMENTO:` / `TipoSubTipoDoc`, `COD:\n(IRCT)` / `CodigoGEPDGERT`).
   `ler_indice` sobre o `BTE31_2026.xlsx` devolve **zero linhas** — e devolve-as
   sem erro, o que é pior do que falhar.
2. **Os esquemas de nome são incompatíveis.** Três módulos leem o nome do
   ficheiro e falham em silêncio se ele mudar de forma.
3. **A aplicação não conhece o âmbito.** Não distingue o que é processável
   (privado, público empresarial) do que ainda não é (Administração Pública).
   A SPEC-0001 declarava isto como não-objetivo: «o token do nome é sempre PR».
4. **Não há catálogo.** O documento do RNC declara-o a fonte de verdade, mas
   descreve-o como saída de uma ferramenta que vive fora do repositório e não
   tem testes.

E três tarefas que o README v2.1 declarava bloqueantes, por decidir: se o código
IRCT é estável entre revisões; como separar sectores de matérias; como resolver
as retificações sem outorgantes.

## Objetivo

Que um número do BTE entre na aplicação a partir do índice que a DGERT
distribui hoje, saia com os nomes e a arrumação que o RNC fixou, e deixe um
catálogo que a equipa possa anotar e a aplicação possa regerar sem apagar o que
a equipa escreveu.

## Não-objetivos

- **Não** renomeia o corpus já existente. Os dois esquemas convivem.
- **Não** processa a Administração Pública. Classifica-a, cataloga-a e separa-a
  fisicamente, para que o dia em que for possível não exija mexer na estrutura.
- **Não** decide o vocabulário de destino dos sectores (CAE/NACE). Separa-os das
  matérias e entrega o material para a decisão.
- **Não** liga a rede. O que aqui se acrescenta corre inteiramente offline.
- **Não** inventa siglas nem âmbitos: deriva-os e **assinala** os que exigem
  confirmação humana.

## Comportamento

```text
índice do BTE (qualquer dos dois dialetos)
        │
        │  cct/recolha.py       aliases dos dois lados, comparação normalizada
        ▼
   registo_bte.jsonl
        │
        │  cct/nomeacao.py --esquema rnc      cct/ambito.py decide PRI/SPE/APU
        ▼
1_fontes/irct/PRI/2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf
1_fontes/irct/APU/…                          ← catalogado, não processado
        │
        │  cct/catalogo.py
        ▼
0_gestao/catalogo/catalogo_irct_2026.csv     26 colunas geradas + 5 da equipa
```

### Leitura do índice

Cada campo interno aceita os *aliases* dos dois dialetos, comparados sobre o
nome normalizado (sem acentos, sem pontuação, sem maiúsculas) e não pela posição
da coluna. A cadeia de alterações, que o dialeto técnico parte em duas colunas,
é **junta** e não escolhida — escolher a primeira perdia metade da cadeia.

### Âmbito

Vocabulário fechado de três valores, decidido por três vias pela ordem da
fiabilidade: vocabulário editável, regra, omissão (PRI). Tudo o que a *regra*
classifique como SPE ou APU sai com aviso. A regra nunca decide um APU em
silêncio: um falso APU retira um documento do pipeline sem ninguém dar por isso.

### Nome

`{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}`, ≤ 63 caracteres, com
as siglas encurtadas antes do prefixo quando não cabe. O `SEQ` é o do boletim,
não o ordinal interno. Ver ADR-0016.

### Catálogo

Uma linha por documento. As cinco colunas da equipa são recuperadas do catálogo
anterior pelo `nome_canonico`; uma linha que deixe de aparecer nos índices é
mantida com aviso, não apagada.

## Critérios de aceitação

- [x] Os 14 documentos do `BTE31_2026.xlsx`, no dialeto técnico, são lidos com
      tipo, código IRCT, outorgantes, cadeia de alterações e URL corretos.
- [x] O índice no dialeto de 2025 continua a ser lido como antes (os testes da
      SPEC-0001 passam sem alteração).
- [x] A cadeia de alterações partida em duas colunas é junta, não escolhida.
- [x] Todo o nome gerado no esquema RNC é aceite por
      `cct.localizador.interpretar_doc_id` e tem ≤ 63 caracteres.
- [x] `interpretar_doc_id` continua a ler os nomes do esquema de 2025.
- [x] O número sequencial do nome é o do boletim; sem `ID:` no índice, cai no
      ordinal interno **e avisa**.
- [x] Uma retificação sem outorgantes é nomeada a partir do título, com aviso, e
      **sem** catálogo acumulado.
- [x] Uma empresa municipal é classificada SPE e fica por rever; um ACEP é APU e
      não é processável; o vocabulário ganha à regra; o privado por omissão não
      gera aviso.
- [x] A forma jurídica `, EM` não é apanhada dentro de uma palavra («Armazém»).
- [x] Um valor de âmbito fora do vocabulário fechado é recusado, com aviso.
- [x] Na separação de sectores e matérias nada se perde: cada item cai num dos
      dois lados.
- [x] Regerar o catálogo preserva as cinco colunas da equipa e o estado.
- [x] Uma linha que desapareça dos índices é assinalada, não apagada.
- [x] Uma sigla de origem `recurso` não é carregada pela tabela de siglas.
- [x] Um esquema de nome desconhecido é recusado com erro explícito.
- [x] Uma sigla que só uma organização usa não é alterada.
- [x] Uma sigla pedida por duas linhagens é resolvida pela escada, e fica com o
      degrau 1 a linhagem de código DGERT mais baixo.
- [x] O resultado da desambiguação não depende da ordem de chegada das
      organizações.
- [x] Gerações da mesma organização partilham a sigla e não são conflito.
- [x] Uma sigla já atribuída não é reatribuída numa corrida seguinte.
- [x] A unicidade das siglas ignora maiúsculas.
- [x] Quando o nome não cabe, encurta-se a base e não o que distingue.
- [x] O construtor falha, e não avisa, se sobrar um duplicado.
- [x] Um `COD: (IRCT)` de família não verificada não é traduzido para acto.
- [x] Cada família documental vai para a sua pasta, cruzada com o âmbito.
- [x] `ACEP` e `DA` são classificados como convenção; um tipo desconhecido não é
      adivinhado.
- [x] Os acordos de adesão são recolhidos por omissão.
- [x] Só a família `convencao` é marcada processável, e só em âmbito PRI ou SPE.
- [x] A relação com a convenção-base é nomeada (`altera`, `estende`, `adere`,
      `refere`) a partir do tipo, não da coluna do índice.
- [x] Uma portaria sem outorgantes é nomeada a partir do título.
- [x] `pipeline_tema` recusa-se a correr se a pasta de entrada tiver um ficheiro
      de outra família, e a mensagem diz para onde apontar.
- [x] O âmbito subdivide `convencoes/` e não as portarias nem as adesões.
- [x] Um aviso de projeto não tem ficheiro, mas mantém linha de catálogo com
      `estado=metadado`, e passa para a coluna `avisos_projeto` da portaria.
- [x] Uma entidade com forma jurídica empresarial na lista do INE é proposta
      como **SPE** e continua processável — verificado pelo nome para o
      Metropolitano de Lisboa, a RTP e o TUB.
- [x] Um município ou freguesia da lista do INE é proposto como APU.
- [x] Nenhuma proposta vinda da lista do INE passa sem aviso.
- [x] O vocabulário da equipa ganha à lista do INE.
- [x] A ausência da lista do INE não é tratada como «privado confirmado».
- [x] Um nome curto da lista do INE não encaixa por acaso dentro de outro.

## Plano de verificação

- **Testes automáticos** — `tests/test_rnc.py`, 29 testes: leitura do índice no
  dialeto técnico (reconstruído em `openpyxl` a partir das linhas reais do BTE
  31/2026, para não versionar binários), esquema de nomes nos dois sentidos,
  classificação de âmbito, separação de sectores e da cadeia de alterações,
  extração de páginas, identidade de acto de negociação, regra de desambiguação
  de siglas, e regeração do catálogo.
  Correm offline, sem rede e sem dados locais.
- **Verificação manual** — correr `python -m cct.catalogo` sobre o
  `BTE31_2026.xlsx` real e conferir os 14 nomes contra o índice publicado.
  Resultados no ponto 11.2 do [README do RNC](../docs/rnc/README.md#112-estado-verificado-bte-312026-14-documentos).
- **Verificação das três tarefas bloqueantes** — a estabilidade do código IRCT
  foi verificada por cruzamento do índice com a folha «Negociação coletiva» do
  export da DGERT; o método e o resultado estão no
  [ponto 4.4](../docs/rnc/README.md#44-código-irct).

## Riscos

| Risco | O que se faz |
|---|---|
| Um terceiro dialeto de índice voltar a devolver zero linhas em silêncio | Um cabeçalho desconhecido deixa a coluna vazia e o problema aparece no relatório; a leitura é por nome normalizado, não por posição |
| Uma sigla derivada pelo script entrar num nome como se fosse confirmada | A origem de cada sigla é declarada no vocabulário; as de origem `recurso` não são carregadas, e a nomeação recusa-se a escrever o ficheiro |
| A lista do INE retirar do pipeline empresas públicas processáveis | As entradas com forma jurídica empresarial propõem SPE e nunca APU; os casos-armadilha estão fixados por nome em teste (ADR-0019) |
| Uma portaria de extensão ser codificada como convenção | Família em pasta própria, coluna `processavel` no catálogo, e recusa do pipeline coberta por teste (ADR-0018) |
| A leitura da relação portaria↔convenção estar errada | Está testada contra um índice de ensaio, não contra dados reais: fica assinalado no ponto 4.6 do README do RNC e é a tarefa 3 do ponto 9 |
| Um falso APU retirar um documento do pipeline sem ninguém dar por isso | A regra nunca decide APU em silêncio: sai sempre com aviso e `ambito_origem=regra` no catálogo |
| Regerar o catálogo apagar trabalho humano | As cinco colunas da equipa são recuperadas pelo `nome_canonico`, e as linhas órfãs são mantidas com aviso; teste dedicado |
| O dígito de família do código IRCT não ser o observado para ACT e portarias | Só se traduzem os dígitos verificados (`2` e `4`); os outros deixam `acto_negociacao` vazio em vez de produzirem uma junção errada. Tarefa 2 do ponto 9 do README do RNC |
| Duas pessoas atribuírem siglas diferentes à mesma organização | A desambiguação é por regra, determinística e independente da ordem; as siglas atribuídas são fixadas no vocabulário versionado (ADR-0017) |
| Os dois esquemas de nome divergirem ao ponto de partirem o MaxQDA | Teste que verifica que todo o nome gerado é aceite pelo localizador e cabe em 63 caracteres |
