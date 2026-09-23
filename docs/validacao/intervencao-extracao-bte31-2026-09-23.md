# Intervenção na extração de texto e tabelas do BTE 31/2026

- **Estado:** proposta para execução e validação com os PDFs de origem
- **Data:** 2026-09-23
- **Evidência:** `relatorio.txt` e `projeto.qdpx` da corrida fornecida pela equipa.
  Os artefactos contêm texto do corpus e não são versionados no repositório.

## Objetivo e limite da evidência

Garantir que as tabelas e os artigos dos documentos processados chegam ao
texto e ao MaxQDA completos, legíveis e ligados à estrutura correta. O
relatório diz `Convenções processadas: 9/9`: o QDPX contém nove fontes
`TextSource` (377–381 e 383–386), não os 14 documentos do índice BTE 31.
Os outros cinco não fazem parte desta prova. Há 76 seleções de texto no QDPX;
a sua presença não comprova que apontem para o trecho certo após uma correção.

Não foram fornecidos os nove PDFs, o `manifest.json` nem o comando da corrida.
Por isso, não é possível confirmar a integridade dos valores perante a fonte,
qual extrator foi selecionado, nem a versão importada no MaxQDA. O aviso
`pdfplumber deteta` identifica o **auditor** que conta grelhas no PDF;
não identifica, por si só, o extrator que produziu o TXT.

## Diagnóstico com os artefactos recebidos

| Caso | Evidência no QDPX e no relatório | Interpretação sustentada | A verificar no PDF |
|---|---|---|---|
| 377, anexos II e IV; 379, anexo III; 383, anexo I | Há linhas com ` | ` depois dos respetivos cabeçalhos; no 379 a tabela ocupa várias linhas (26–35 da fonte TXT). O relatório afirma que a tabela está fora do corpo do nó. | A auditoria examina somente o nó folha `anexo`, que o `estruturar` fecha depois do cabeçalho; o corpo fica no nó filho `bloco`. O aviso não prova orfandade. | Correspondência das linhas e células com o PDF e relação do bloco com o anexo certo. |
| 380, anexo III | Uma linha de 1371 caracteres concentra a tabela salarial; o auditor não encontra bloco de duas linhas com ` | `. | Há conteúdo tabular, mas perdeu-se a separação por linhas/células. A mensagem «nenhum bloco» não equivale a «nenhum valor». | Número de linhas e colunas, valores, cabeçalhos e eventuais células em falta. |
| 384 e 385, anexo IV | Cada TXT tem três linhas isoladas com ` | `, incluindo uma de 3781 caracteres noutro anexo e uma linha salarial de cerca de 265 caracteres. O auditor vê cinco tabelas por PDF e zero blocos. | Deteção presente no PDF e linearização deficiente no TXT; a contagem bruta de grelhas não estabelece quantas sobreviveram. | Tabelas concretas nas páginas de origem, especialmente anexos com grelhas longas. |
| 386, anexos III e IV | As duas tabelas ficaram em linhas únicas de 933 e 1187 caracteres. O auditor vê três tabelas por PDF e zero blocos. | Há texto, mas a estrutura tabular não é utilizável para revisão. | Divisão em linhas e colunas e correspondência dos valores por categoria. |
| 384 e 385, artigo 1.º | O texto do artigo termina com `passam a ter a redação seguinte:` e é seguido por cabeçalhos de cláusulas. | O controlo `clausulas_sem_corpo` exige ponto final e emite um provável falso positivo para um artigo introdutório com dois pontos. | Confirmar no PDF que a lista de cláusulas pertence ao artigo e não há texto truncado. |

O QDPX demonstra a presença de texto, mas não substitui o PDF na validação.
Não interpretar a ausência de aviso nos outros documentos como validação
integral das suas tabelas. Não usar o valor `9/9` como taxa de qualidade.

## Intervenção por etapas

### 1. Fixar uma base verificável

Guardar fora do repositório os PDFs individuais, hashes, índice, registo,
`manifest.json`, comando, opção `--extrator`, versão do código, versão do
MaxQDA, TXT e QDPX. Construir uma grelha por documento, página, anexo e tabela:
cabeçalho, número de linhas e colunas, células de controlo escolhidas no PDF,
resultado no TXT, decisão e pessoa/data da revisão. Começar por 379 (controlo
positivo), 380 (tabela colapsada), 384 ou 385 (várias grelhas), 386 (anexos
consecutivos) e 377 (anexo longo).

### 2. Corrigir a auditoria antes de avaliar a recuperação

Em `cct/auditoria.py`, associar ao anexo os nós filhos por `pai` e respetivos
intervalos de texto. Distinguir **sem tabela**, **tabela no bloco filho**,
**tabela fora da árvore do anexo** e **tabela linearizada numa linha**.
Não contar uma ocorrência isolada de ` | ` como tabela recuperada; também
não a descrever como perda total. Associar avisos a documento, página e
anexo sempre que os metadados estiverem disponíveis. Em `cct/sanidade.py`,
aceitar artigos introdutórios terminados em dois pontos quando são seguidos
pelas cláusulas anunciadas; manter o aviso para corpo vazio ou truncado.
Testes devem reproduzir ambos os casos e proteger o verdadeiro negativo.

### 3. Comparar extratores e recuperar as grelhas

Correr os mesmos PDFs separadamente com `pdfplumber` e `docling` em ambiente
offline preparado, com o mesmo código e parâmetros. Confrontar cada saída
com o PDF, por página e por célula, para decidir se a correção pertence à
deteção, à ordem de leitura, à serialização de grelhas ou à junção posterior
de linhas (`cct/extractor.py` e `cct/extractor_docling.py`). Só escolher
fallback por página/documento depois de medir falhas e preservar a origem
de cada bloco. Não assumir que Docling resolve automaticamente todas as
tabelas: o caso TINITA de [#42](https://github.com/calvicius-af/crl-app-cct/issues/42)
continua com ordem de semanas e cabeçalho incorretos.

### 4. Fechar a cadeia TXT → QDPX → MaxQDA

Testar que cada anexo salarial tem cabeçalho antes dos dados, linhas e
colunas verificáveis, sem junção de grelhas diferentes e sem anexos vazios
indevidos. Regerar QDPX e testar que todas as seleções conservam o mesmo
trecho semântico antes, dentro e depois das tabelas após o remapeamento dos
offsets. Importar a amostra no MaxQDA e registar a revisão humana. A via
`richTextPath` com DOCX já falhou duas vezes; a investigação sobre outras
representações é independente da correção dos dados em texto plano.

### 5. Gate operacional e guia

Uma corrida com avisos de tabela não deve ser apresentada como extração
validada só por ter processado todos os PDFs. Registar estado por documento:
`por_rever`, `validado` ou `reprovado`, com evidência de páginas/células e
decisão. Um documento reprovado fica disponível para inspeção, mas não
alimenta indicadores dependentes dos valores tabulares até correção e
revalidação. Incorporar no guia de operação o comando, o sintoma, a causa
confirmada e o procedimento que funcionou, sem versionar PDFs ou texto do
corpus.

## Critérios de aceitação

1. Para cada tabela salarial dos documentos de prova, a grelha do TXT
   corresponde ao PDF em número de linhas e colunas, cabeçalhos, associação
   das categorias aos valores e células de controlo. Divergências ficam
   explícitas com página e estado `reprovado`, nunca escondidas num `9/9`.
2. O relatório deixa de dizer que uma tabela está fora do anexo se estiver
   num bloco filho desse anexo. Continua a detetar tabela realmente órfã.
3. As tabelas colapsadas de 380, 384, 385 e 386 deixam de ser linhas únicas,
   ou permanecem assinaladas como falha com evidência de perda de estrutura.
4. Os artigos 1.º de 384/385 passam no controlo apenas após confirmação de
   que introduzem as cláusulas seguintes. Um artigo truncado continua a falhar.
5. Todas as seleções QDPX mantêm os trechos corretos; a amostra importada
   no MaxQDA confirma legibilidade antes e depois das tabelas. Os testes de
   zero-perda e a matriz Windows/Linux/macOS continuam verdes.

## Relação com o trabalho existente

- [GitHub #83](https://github.com/calvicius-af/crl-app-cct/issues/83) e
  [ISSUE-0023](../../issues/0023-auditoria-anexos-artigos-falsos-positivos.md):
  corrigir os falsos positivos de anexos e artigos (etapa 2).
- [GitHub #84](https://github.com/calvicius-af/crl-app-cct/issues/84) e
  [ISSUE-0024](../../issues/0024-tabelas-salariais-colapsadas-bte31.md):
  recuperar e validar as grelhas salariais (etapas 3 e 4).
- [GitHub #13](https://github.com/calvicius-af/crl-app-cct/issues/13):
  definir o gate humano e estado de validação; esta intervenção fornece
  exemplos concretos para esse desenho.
- [GitHub #21](https://github.com/calvicius-af/crl-app-cct/issues/21):
  decisão sobre Docling após comparação com PDFs reais. O número local
  [ISSUE-0021](../../issues/0021-alternativas-tabelas-maxqda.md) refere-se
  **a outro tema**, a apresentação de tabelas no MaxQDA.
- [GitHub #31](https://github.com/calvicius-af/crl-app-cct/issues/31) e
  [ISSUE-0003](../../issues/0003-qdpx-perde-ganhos-do-docling.md):
  validar importação e offsets; não repetir a tentativa `richTextPath`.
- [ISSUE-0018](../../issues/0018-titulo-anexo-depois-da-tabela.md):
  título perdido do anexo da Empresa Metropolitana; incluir este caso na
  amostra seguinte, separado dos avisos desta corrida.
- [ISSUE-0020](../../issues/0020-tabelas-carristur-rodadas.md) e
  [GitHub #42](https://github.com/calvicius-af/crl-app-cct/issues/42):
  rotação e ordem de leitura noutros PDFs; não generalizar uma solução
  das tabelas salariais horizontais.
- [ISSUE-0014](../../issues/0014-carristur-sem-clausulas-nem-nota-de-deposito.md):
  os quatro CARRISTUR não entram neste QDPX; não extrapolar `9/9` para eles.
  [SPEC-0004](../../specs/0004-esquema-de-nomes-comum-as-tres-familias.md)
  trata nomes documentais e não resolve a extração.

Trata-se de correções e validação de comportamento existente, por isso a
execução cabe em issues específicos; uma spec nova só será necessária se o
gate de estados por documento for aprovado como funcionalidade nova, no
âmbito do GitHub #13.
