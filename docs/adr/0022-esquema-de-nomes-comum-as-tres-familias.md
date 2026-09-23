# ADR-0022: um só esquema de nomes para convenções, portarias de extensão e acordos de adesão

- **Estado:** Aceite
- **Data:** 2026-09-23
- **Decidido por:** CRL (António Fula)
- **Substitui:** [ADR-0016](0016-esquema-de-nomes-do-rnc.md). Altera em parte o
  [ADR-0018](0018-familias-documentais-em-pastas-separadas.md) e responde ao ponto
  «Revisitar quando» do [ADR-0021](0021-corte-por-ano-do-esquema-de-nomes.md).
- **Especificação:** [SPEC-0004](../../specs/0004-esquema-de-nomes-comum-as-tres-familias.md)

## Contexto

O [ADR-0016](0016-esquema-de-nomes-do-rnc.md) fixou o esquema de nomes das convenções:

```text
{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}
2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2
```

As portarias de extensão (PE) e os acordos de adesão (AA) recebem hoje o mesmo
esquema, mas ele não lhes serve. Há cinco problemas:

1. **A PE é um acto do Estado com número próprio no Diário da República.** O esquema
   não tem lugar para esse número, que é aquilo pelo qual a portaria é citada.
2. **O ano do DR e o ano do BTE podem ser diferentes.** Uma portaria publicada no DR
   em 2025 pode ser publicitada no BTE em 2026. A Portaria n.º 452/2025 e a Portaria
   n.º 452/2026 podem ambas entrar no corpus de 2026.
3. **Nem a PE nem o AA indicam diretamente, nos metadados do índice, a convenção a
   que se referem**, e um AA pode aderir a uma convenção de um ano anterior. A leitura
   da relação pela coluna de alterações foi testada apenas contra um índice de ensaio
   (tarefa 3 do §9 do README do RNC).
4. **O âmbito (PRI, SPE, APU) não diz nada útil numa PE ou num AA.** O âmbito serve
   para decidir se o documento entra no pipeline, e nenhuma PE ou AA entra
   ([ADR-0018](0018-familias-documentais-em-pastas-separadas.md)). Numa PE, que é um
   acto do Estado, nem sequer é claro que âmbito seria.
5. **A equipa já tinha renomeado à mão as PE de 2026** com outro padrão
   (`2026_001_BTE_01_PE_0452_ADCP_SETAAB`). Esse nome usa uma contagem interna,
   não tem o ano do DR nem o código IRCT, e não é reconhecido por nenhuma das
   expressões regulares do `cct/localizador.py`. Por isso, a recusa do
   `pipeline_tema` baseada no nome não o identifica como portaria.

Houve ainda dois pedidos da equipa. O primeiro: o número do BTE deve vir logo a seguir
ao ano, porque é também um critério de ordenação. O segundo: o nome deve levar apenas
os dois intervenientes principais.

Informação que a equipa trouxe para esta decisão:

1. É altamente provável que a DGCP tenha, nos metadados, o código IRCT que liga cada
   PE e cada AA à convenção de base. Esta informação ainda não foi verificada contra
   um índice real (ver «Condição» abaixo).
2. Uma PE publicada no DR em 2025 e no BTE em 2026 conta para os dados de 2026.
3. O `001` do padrão manual era uma contagem da equipa, e não o número da DGCP.

## Decisão

**Usamos um só esquema de nomes para as três famílias, com cabeça e cauda comuns e um
miolo próprio de cada família.**

```text
CABEÇA                      MIOLO                      CAUDA
{ANO}_BTE_{NN}_{X}_{SEQ}    _{o que é exatamente}      _{CODIRCT}_{SIGLA1}-{SIGLA2}[+N]
```

| Família | Esquema | Exemplo |
|---|---|---|
| Convenção | `{ANO}_BTE_{NN}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_{SIGLAS}` | `2026_BTE_31_PRI_377_CCT-ALT_27251_ACRAL-CESP+3` |
| Portaria de extensão | `{ANO}_BTE_{NN}_{TIPO}_{SEQ}_{NNNN}-{AAAA}_{CODIRCT}_{SIGLAS}` | `2026_BTE_01_PE_012_0452-2025_27251_ACRAL-CESP` |
| Acordo de adesão | `{ANO}_BTE_{NN}_AA_{SEQ}_{CODIRCT}_{SIGLAS}` | `2026_BTE_12_AA_412_27251_ABC-CESP` |

O exemplo da convenção reescreve, no esquema novo, o exemplo do README do RNC. Os
exemplos da PE e do AA são ilustrativos: mostram uma portaria que estende essa
convenção e um acordo de adesão a ela, e por isso partilham o código `27251`.

Três regras resumem o esquema:

1. **Começa sempre por ano e boletim.** A ordem alfabética agrupa os ficheiros por
   ano e número do BTE. Dentro de cada boletim, o quarto campo agrupa-os por âmbito
   ou família antes do número sequencial; para obter a ordem integral de publicação,
   usa-se o catálogo e a posição no índice.
2. **O quarto campo diz o que o ficheiro é.** `PRI`, `SPE` ou `APU` indicam uma
   convenção e o seu âmbito. `PE`, `PCT`, `PRT` ou `AA` indicam uma família que não é
   convenção e que nunca entra no pipeline.
3. **Termina sempre com o código da convenção e as duas siglas principais.** Com
   `*_27251_*` encontra-se a convenção, as suas revisões, as extensões e as adesões.

Regras de cada campo:

1. **`ANO`** é o ano do BTE, com 4 dígitos. É também o ano dos dados do relatório a que
   o documento pertence. Uma PE publicada no DR em 2025 e no BTE em 2026 tem `ANO`
   2026 e conta para os dados de 2026.
2. **`NN`** é o número do BTE, com 2 dígitos.
3. **`X`** é o âmbito nas convenções (vocabulário fechado `PRI`, `SPE`, `APU`) e o
   tipo nas outras famílias (`PE`, `PCT`, `PRT`, `AA`). Nas PE e nos AA o âmbito
   continua a existir, mas só no catálogo, na coluna `ambito`.
4. **`SEQ`** é o número sequencial da DGCP (`IDDocumento`, `12/2026` dá `012`), com 3
   dígitos. Nenhuma contagem interna, da aplicação ou da equipa, entra no nome.
5. **Miolo:**
   a) convenção: `TIPO`, tal como vem do índice (`CCT`, `CCT-ALT`, `AE-ALT-RECT`);
   b) PE, PCT, PRT: `NNNN-AAAA`, ou seja, o número da portaria com 4 dígitos e o ano
      do DR com 4 dígitos. Lê-se como a citação legal «Portaria n.º 452/2025». A letra
      de sufixo, quando existe, junta-se ao número: a Portaria n.º 50-A/2025 dá
      `0050A-2025`;
   c) AA: sem miolo.
6. **`CODIRCT`** é sempre o código da **convenção de base**, tal como aparece no nome
   dessa convenção. Numa convenção é o seu próprio código. Numa PE é o código da
   convenção que estende. Num AA é o código da convenção a que se adere, mesmo que seja
   de um ano anterior, porque o código é estável entre revisões (§4.4 do README do
   RNC). Se uma PE estender várias convenções, o nome leva a primeira na ordem do
   índice confirmado, fica um aviso e o catálogo conserva a relação com **todas** as
   convenções abrangidas. A pesquisa por `*_{CODIRCT}_*` encontra essa PE apenas
   para o primeiro código. Para reunir as PE dos outros códigos consulta-se o catálogo.
7. **`SIGLAS`**: a primeira sigla patronal e a primeira sigla sindical, por esta ordem,
   separadas por hífen. `+N` indica quantas partes ficaram de fora. A regra aplica-se
   às três famílias e substitui a regra das três primeiras siglas pela ordem do índice
   ([ADR-0016](0016-esquema-de-nomes-do-rnc.md)). Se só houver partes de um lado,
   usam-se as duas primeiras desse lado e fica um aviso.
8. **O limite continua a ser de 63 caracteres.** Quando o nome não cabe, encurtam-se
   as siglas, nunca a cabeça nem o miolo. Com o prefixo mais longo conhecido
   (`AE-ALT-RECT`) sobram 25 caracteres para as siglas.

### Condição para escrever o ficheiro

**Uma PE ou um AA sem código IRCT da convenção de base confirmado fica `por_confirmar`
e o ficheiro não é escrito.** O mesmo vale para uma PE sem número e ano da portaria.
É a salvaguarda que já existe para um documento sem `IDDocumento`
([ADR-0016](0016-esquema-de-nomes-do-rnc.md)). Como um nome atribuído não muda, um
código errado não pode chegar a um nome.

Antes de a implementação escrever o primeiro ficheiro de PE ou AA, é preciso verificar
num índice real que traga uma PE e um AA:

1. em que campo dos metadados da DGCP está o código da convenção de base;
2. se esse código coincide exatamente com o código que aparece nas convenções ou se
   difere, por exemplo, no dígito de família.

Se diferir, o nome leva o código tal como aparece na convenção, e a tradução fica
documentada. Se a DGCP não tiver esta informação, esta decisão volta à equipa, mas não
se volta a uma contagem interna.

### Transição

1. **Corpus até 2025:** os nomes não mudam ([ADR-0021](0021-corte-por-ano-do-esquema-de-nomes.md)).
2. **Corpus de 2026:** passa todo para este esquema, uma única vez. Isso inclui os 14
   ficheiros do BTE 31/2026, nomeados no esquema do ADR-0016, e as PE renomeadas à mão.
   A regra «um nome atribuído não muda» começa a valer para o corpus de 2026 quando esta
   migração terminar. Por isso a migração tem de estar feita **antes de começar o
   trabalho no MAXQDA sobre o corpus de 2026**. Se esse trabalho já tiver começado, a
   migração para e volta à equipa.
3. **Leitura:** o `cct/localizador.py` continua a ler o esquema de 2025 e o esquema do
   ADR-0016, para que cópias antigas do corpus não falhem em silêncio. A nomeação
   deixa de escrever o esquema do ADR-0016.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Manter o esquema do ADR-0016 para as três famílias | Não tem lugar para o número da portaria, põe nas PE e nos AA um âmbito que não decide nada, e deixa a PE sem ligação legível à convenção |
| Manter o padrão manual das PE (`2026_001_BTE_01_PE_0452_ADCP_SETAAB`) | Usa uma contagem da equipa que não se reconstrói a partir da fonte, não tem o ano do DR (452/2025 e 452/2026 ficam iguais), não tem o código IRCT e não é lido pela aplicação |
| Âmbito também nas PE e nos AA | Três letras que não respondem a nenhuma pergunta sobre o documento. O âmbito fica no catálogo |
| Número do BTE depois do código IRCT, como no ADR-0016 | Os nomes deixam de se ordenar pela ordem de publicação. Foi um pedido explícito da equipa |
| Convenção de base só no catálogo, fora do nome | Perde-se a possibilidade de reunir toda a família documental de uma convenção com `*_27251_*`, que é a pergunta mais frequente sobre PE e AA |
| Aplicar o esquema novo só às PE e aos AA, sem mexer nas convenções | Dois esqueletos diferentes no mesmo corpus. A regra «cabeça, miolo, cauda» deixa de ser verdadeira para todos os ficheiros e deixa de se poder decorar |
| Aderente primeiro nas siglas dos AA | Saber qual é a parte aderente obriga a interpretar o título. «Patronal primeiro, sindical depois» é determinístico e igual nas três famílias |
| Manter até três siglas | A equipa prefere os dois intervenientes principais. O `+N` mantém a indicação de que há mais partes, sem ocupar caracteres |

## Consequências

**Torna fácil:** agrupar os ficheiros por ano e número do BTE; saber pelo quarto
campo se um ficheiro é convenção; ver numa só listagem uma convenção, as suas extensões
e as suas adesões quando são a relação principal; citar uma portaria pelo número legal
a partir do nome do ficheiro. O catálogo permite ordenar dentro do BTE e consultar
relações adicionais de uma PE que abrange várias convenções.

**Torna difícil:** nomear uma PE ou um AA sem o código da convenção de base. É
deliberado: sem esse código, o ficheiro fica por escrever.

**Passa a ser obrigatório manter:** o `cct/localizador.py` a ler os três esquemas (2025,
ADR-0016 e este), com teste; o vocabulário fechado do quarto campo; a regra de que o
`CODIRCT` é o da convenção de base; o limite de 63 caracteres; e a recusa do
`pipeline_tema` a reconhecer PE e AA pelo nome.

**Custo assumido:** migrar uma vez o corpus de 2026 (os 14 ficheiros do BTE 31/2026 e
as PE já renomeadas), reescrever as partes do README do RNC e do guia de operação que
descrevem o esquema, e manter mais um esquema no `localizador`. As ISSUE-0015 a
ISSUE-0021 citam nomes do esquema do ADR-0016. O defeito que descrevem não muda, mas os
nomes citados ficam desatualizados.

## Revisitar quando

1. Se a verificação num índice real mostrar que a DGCP não liga as PE e os AA à
   convenção de base. Nesse caso o esquema das PE e dos AA volta à equipa.
2. Se aparecer uma família ou um tipo que não caiba no quarto campo (por exemplo, uma
   retificação de portaria). Nesse caso alarga-se o vocabulário do quarto campo, por
   decisão registada, em vez de o forçar.
3. Nas mesmas condições do ADR-0016: se o MAXQDA aceitar nomes mais longos ou se o
   código IRCT deixar de ser estável entre revisões.
