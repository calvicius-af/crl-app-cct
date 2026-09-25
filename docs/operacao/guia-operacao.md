# Guia de operação — Pipeline CCT → MaxQDA

Este guia explica como usar o pipeline sem saber programação.
Regra de ouro: **se algo falhar, o problema está quase sempre no nome ou no
sítio de um ficheiro.** Verifica primeiro a secção "Onde ficam os ficheiros".

---

## 1. O que o pipeline faz

Recebe PDFs de convenções coletivas do BTE e produz:
1. **projeto.qdpx** — para importar no MaxQDA, com as convenções já
   pré-codificadas por tema e organizadas em faixas:
   - `AUTO/…` — codificações fiáveis (quase não precisam de revisão)
   - `REVER/…` — codificações a rever por humanos
   - `CONSOLIDADO/…` — texto republicado sem novidade (fora da análise)
   - `00 Estrutura` — preâmbulos, assinaturas, marca do texto consolidado
2. **sugestoes_peritas.xlsx** — a mesma informação em Excel, com contexto,
   para quem não tem MaxQDA.
3. **relatorio.txt** — o que correu bem e o que precisa de atenção.
4. **manifest.json** — proveniência da corrida: comando, commit, ambiente,
   hashes dos inputs/outputs e contagens.
5. **diagnostico.md** — um só ficheiro com tudo o que é preciso para
   perceber o que correu mal: para cada documento, se o texto tem todas as
   palavras do PDF (comparado com uma segunda leitura independente, feita
   pelo PDFium), palavras a mais ou invertidas, blocos fora de ordem,
   cabeçalhos do BTE que ficaram no texto e tabelas colapsadas numa linha,
   com o número de parágrafo que o MaxQDA mostra. Traz também o relatório,
   o ambiente e a última aquisição. **É este o ficheiro a enviar quando uma
   corrida tem problemas.** Para o gerar de novo sobre uma corrida já feita:
   `.venv\Scripts\python -m cct.completude --corrida results\corrida`.

---

## 2. Onde ficam os ficheiros (OBRIGATÓRIO)

```
Projeto_CRL_AppCCT/                ← corre os comandos SEMPRE a partir daqui
├── data/
│   ├── registo/
│   │   └── registo_bte.jsonl      ← registo da recolha — NÃO APAGAR
│   └── raw/
│       ├── indices/               ← índices .xlsx do BTE, para a recolha automática
│       ├── bte/
│       │   └── bte_2026/          ← PDFs das convenções, UM POR CONVENÇÃO
│       │       └── convencoes/
│       │           ├── PRI/
│       │           │   ├── 2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf
│       │           │   └── …
│       │           └── SPE/
│       │               └── …
│       ├── maxqda/                ← exportados do MaxQDA (ver 3.2)
│       │   ├── VariaveisDocumento2026.xlsx
│       │   └── MAXQDA_…Lista de Códigos.qdc
│       └── textos_consolidados/   ← só para convenções com texto consolidado
│           ├── ACIP_FESAHT/       ← UMA SUBPASTA POR CONVENÇÃO
│           │   ├── ACIP_FESAHT_2009.pdf   ← versão anterior COMPLETA
│           │   └── (o PDF de 2026 NÃO precisa de estar aqui)
│           └── …
├── codebooks/                     ← um YAML por tema (ver prompts-codebooks.md)
└── results/                       ← é aqui que aparecem os resultados
```

### 2.1 Encher a pasta automaticamente (recolha do BTE)

Se a DGERT enviou os ficheiros-índice do boletim (`BTE31_2026.xlsx` e afins), não é
preciso descarregar nem renomear nada à mão:

1. Copiar pelo menos um índice `.xlsx` para `data/raw/indices/` e confirmar o
   nome com `Get-ChildItem .\data\raw\indices\*.xlsx` no PowerShell. Um índice
   não vem no repositório: tem de ser fornecido pela equipa. Não copiar os PDFs
   manualmente para esta pasta.
2. Na app gráfica, carregar em **"Recolher do BTE…"** — a aplicação pergunta se pode
   ligar-se à internet. Responder *Não* faz uma simulação, que mostra o que seria
   descarregado sem descarregar nada.
3. Por linha de comandos, a partir da raiz do projeto, usar **sempre o Python
   do ambiente virtual**. No PowerShell do Windows:

```powershell
.\.venv\Scripts\python.exe -m cct.doctor
.\.venv\Scripts\python.exe -m cct.aquisicao --indices data\raw\indices
.\.venv\Scripts\python.exe -m cct.aquisicao --indices data\raw\indices --confirmar-rede --aplicar
```

No macOS, substituir o interpretador por `.venv/bin/python` e usar `/` nos
caminhos. A primeira corrida é uma **simulação sem rede nem escrita de PDFs**;
a segunda autoriza a descarga e a cópia nomeada. `--aplicar` sozinho não
autoriza a rede. Se faltar o índice, a operação para antes da descarga.

O comando `cct.aquisicao` encadeia duas fases autónomas: `cct.recolha` lê o
índice e guarda os PDFs com os nomes de origem em `data/interim/recolha/`;
`cct.nomeacao` copia os que podem ser nomeados para
`data/raw/bte/bte_<ano>/`, nas pastas da respetiva família. Chamar apenas
`cct.nomeacao` antes da recolha não descarrega PDFs. Os relatórios da corrida
ficam em `results/aquisicao/` e o registo persistente em
`data/registo/registo_bte.jsonl`; não apagar este registo para repetir uma
corrida. **Ler sempre os estados `por_confirmar`, `falhado` e `conflito`**:
um PDF pode ter sido descarregado e, ainda assim, não ter sido copiado com
um nome canónico. Uma segunda corrida reaproveita os PDFs válidos.
Se a pasta de destino mudar, a versão atual verifica os PDFs **no novo
destino**; a existência de uma cópia noutro caminho guardado no registo não
conta como `ja_existente`. A nova descarga pode ser necessária. Não corrigir
`caminho` no JSONL à mão.

**Caso observado em 23-09-2026, BTE 31/2026:** o índice
`BTE31_2026_CRL.xlsx` tinha 14 documentos. A simulação encontrou os 14 PDFs
já recolhidos, sem pedidos de rede; seis nomes já existiam e oito ficaram
`por_confirmar`. Com `--aceitar-heuristicas --confirmar-rede --aplicar`, os
mesmos 14 PDFs foram reaproveitados, sem pedidos de rede, e os oito restantes
foram copiados com nomes gerados. `nomeado` significa **ficheiro escrito**,
não sigla confirmada: os 11 avisos de nomeação continuaram no relatório.
`--confirmar-rede` autoriza pedidos caso sejam necessários, mas não força uma
nova descarga. Não voltar a aplicar siglas diferentes sobre estes nomes sem
seguir o procedimento de correção da secção 5.2.

Se a rede institucional não permitir a descarga, usar os PDFs obtidos por via
institucional e registar a origem e a correspondência com o índice antes de
qualquer cópia ou renomeação. Não colocar um PDF diretamente na pasta final
com um nome presumido: a nomeação automática depende do registo de recolha e
dos metadados confirmados do índice. Escalar ao responsável pelos dados os
casos sem identificador ou correspondência segura.

### Regras de nomes (importante!)
- **PDFs a partir do corpus de 2026**: esquema RNC, obrigatório
  ([ADR-0021](../adr/0021-corte-por-ano-do-esquema-de-nomes.md)), na forma do
  [ADR-0022](../adr/0022-esquema-de-nomes-comum-as-tres-familias.md): começa
  sempre por ano e boletim, e o quarto campo diz o que o ficheiro é.
  Convenções: `{ANO}_BTE_{NN}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_{SIGLAS}.pdf`, ex.:
  `2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf`. Descrito em
  [docs/rnc/README.md §4.1](../rnc/README.md#41-a-regra). O nome deve ser IGUAL ao
  usado no MaxQDA (sem o sufixo `_TXT`). Sem espaços no início/fim.
- **Portarias e acordos de adesão**: `2026_BTE_01_PE_012_0452-2025_27251_ACRAL-CESP.pdf`
  (número e ano da portaria no DR, código da convenção de base) e
  `2026_BTE_12_AA_412_27251_ABC-CESP.pdf`. Sem o código da convenção de base,
  ou sem o número e ano da portaria, a aplicação não atribui nome e o documento
  fica por confirmar. Até ao passo 0 da SPEC-0004, o código lido da cadeia de
  alterações também fica por confirmar. Não renomear à mão: as portarias e
  adesões não entram no pipeline temático, e o `cct.pipeline_tema` recusa-as.
- **PDFs de 2026 ainda com o esquema do ADR-0016**
  (`2026_PRI_377_CCT_27251_BTE_31_…`): passam uma vez para o esquema novo com
  `python -m cct.nomeacao --migrar --correspondencia …`, antes de começar o
  trabalho no MaxQDA — ver [docs/rnc/README.md §10](../rnc/README.md#10-migração-do-ciclo-anterior).
- **PDFs de corpos anteriores a 2026**: mantêm o esquema de 2025,
  `AA_PR_NNN_BTE_NN_Partes_Sindicato.pdf` (AA = ano com 2 dígitos) — não se renomeiam.
- **Subpastas de versões**: o nome da subpasta tem de estar CONTIDO no nome
  do PDF da convenção (ex.: subpasta `AEVP_FESAHT` ↔ PDF
  `2026_BTE_31_PRI_379_CCT-ALT_26651_AEVP-FESAHT.pdf`). É assim que o pipeline as
  encontra.
- **Versões anteriores** dentro da subpasta: o nome deve começar pelo ano —
  `2021_...pdf`, `24122_...pdf` (24 = 2024), `ACIP_FESAHT_2009.pdf`.
  Ficheiros `Comparei_*.pdf` e `Diferencas_*.docx` são ignorados.

---

## 3. Antes de correr — checklist

### 3.1 Verificar a instalação (fazer sempre primeiro)
```powershell
.\.venv\Scripts\python.exe -m cct.doctor
```
No Mac, usar `.venv/bin/python -m cct.doctor`. O `doctor` verifica o
interpretador, as bibliotecas e as pastas. Antes da primeira recolha é
normal ainda não haver PDFs; a ausência das variáveis do MaxQDA é opcional
para a recolha. Confirmar separadamente que há índices `.xlsx`.

### 3.2 Exportar as variáveis do MaxQDA
No MaxQDA: **Variáveis → Variáveis de documento → Exportar (Excel)**.
Guardar como `VariaveisDocumento2026.xlsx` em `data/raw/maxqda/`.
É daqui que vêm o tipo/subtipo, CAE e entidades. Sem este ficheiro o
pipeline funciona, mas o subtipo fica "desconhecido" e a deteção do
texto consolidado fica mais fraca.

### 3.3 Preparar as versões anteriores (só para comparações)
Para cada convenção "…e texto consolidado" de 2026, criar a subpasta em
`data/raw/textos_consolidados/` com **o último texto COMPLETO** (primeira convenção,
revisão global ou consolidado anterior). ⚠ Uma revisão parcial (2-3 páginas)
NÃO serve de base — o pipeline avisa se detetar isso.

---

## 4. Correr o pipeline

### Opção A — App gráfica (recomendado)
Duplo clique em `scripts/AppCCT.command` (Mac) ou `scripts/AppCCT.bat` (Windows),
ou: `python -m cct.app`. Preencher os campos e carregar em "Correr".

### Opção B — Linha de comandos
```
.venv/bin/python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026 \
    --codebook codebooks/4_08_protecao_dados.yaml \
    --variaveis data/raw/maxqda/VariaveisDocumento2026.xlsx \
    --master "data/raw/maxqda/MAXQDA_..._Lista de Códigos.qdc" \
    --metricas results/benchmarks/tema-4.08/metricas/baseline_4_08_v4/metricas.json \
    --pasta-versoes data/raw/textos_consolidados \
    --out results/runs/2026/2026_4_08
```
Em Windows, o interpretador é `.venv\Scripts\python`:
```
.venv\Scripts\python -m cct.pipeline_tema ^
    --pdfs data\raw\bte\bte_2026 ^
    --codebook codebooks\4_08_protecao_dados.yaml ^
    --out results\runs\2026\2026_4_08
```
Só `--pdfs`, `--codebook` e `--out` são obrigatórios; o resto melhora o
resultado mas pode faltar.

**`--extrator docling`** (opcional): usa o docling em vez do pdfplumber na
extração. Recupera tabelas de anexos (tabelas salariais, perfis de função)
e layouts difíceis que o extrator clássico perde, ao custo de ser mais
lento (1,7 s/página a quente e cerca de 4 GB de memória, medidos no corpus) e de exigir instalação à parte:
`.venv/bin/python -m pip install docling`
(Windows: `.venv\Scripts\python -m pip install docling`)
(≈4 GB com PyTorch; em Mac Apple Silicon o Python tem de ser arm64 —
`python3 -c "import platform; print(platform.machine())"` deve dizer
`arm64`). A primeira corrida descarrega os modelos de layout.

### Docling sem rede: modelos na partilha

Os modelos do docling descarregam-se uma vez, numa máquina com internet, e verificam-se
pelo SHA-256 antes de cada uso. Depois, a extração corre sem rede e sem nenhum serviço
remoto: o conteúdo dos documentos nunca sai da máquina.

```
# numa máquina com internet
.venv/bin/python -m cct.modelos_docling descarregar --destino modelos_docling
# copiar a pasta modelos_docling para a partilha; na estação:
.venv/bin/python -m cct.modelos_docling verificar --pasta L:/partilha/modelos_docling
CCT_DOCLING_MODELOS=L:/partilha/modelos_docling .venv/bin/python -m cct.pipeline_tema --extrator docling ...
```

Em Windows (PowerShell), a variável define-se antes do comando:
`$env:CCT_DOCLING_MODELOS = "L:\partilha\modelos_docling"`.

Com a pasta dos modelos, o OCR fica desligado (os PDF do BTE têm texto). Para o ligar,
`CCT_DOCLING_OCR=1`, com os modelos do OCR completos na pasta.

**Limites.** Antes de extrair, o PDF é aberto com o PDFium. Um PDF corrompido, protegido
por palavra-passe, com mais de 500 páginas (`CCT_MAX_PAGINAS`) ou mais de 100 MB
(`CCT_MAX_MB`) é recusado com uma mensagem que diz o que fazer, e a corrida continua com
os outros documentos. No docling, cada documento tem um tempo máximo de 900 s
(`CCT_DOCLING_TEMPO_MAX_S`). Uma conversão que não acabe é um erro, e não um texto com
buracos. Registo: [docling-isolado-2026-09-26.md](../validacao/docling-isolado-2026-09-26.md).

### Medir o desempenho dos extratores

```
.venv/bin/python -m cct.desempenho medir                      # pdfplumber, sobre data/corpus
.venv/bin/python -m cct.desempenho medir --extrator docling   # o docling, com os modelos já em cache
.venv/bin/python -m cct.desempenho medir --comparar           # falha acima da referência + 15% ou do orçamento
```

Mede cada PDF do corpus de regressão num processo à parte: o arranque, a extração a
frio (com o carregamento dos modelos, no docling) e a quente, os segundos por página e a
memória máxima. O resultado fica em `results/desempenho/`, com a máquina, o Python e as
versões identificados. A referência e o orçamento estão em
`tests/desempenho/referencia.json`, por ambiente; `--atualizar` grava a referência do
ambiente em que se corre. Para medir o docling sem rede, com os modelos já descarregados:
`HF_HUB_OFFLINE=1`. Registo das medidas:
[desempenho-2026-09-26.md](../validacao/desempenho-2026-09-26.md).

### Comparar duas versões de uma convenção (avulso)
```
.venv/bin/python -m cct.comparar --pasta data/raw/textos_consolidados/ACIP_FESAHT \
    --out results/benchmarks/tema-4.08/comparacoes/ACIP.xlsx
```
Sai um Excel com cada cláusula classificada: `=` / `alteracao` / `nova` /
`removida`, com as diferenças exatas.

---

## 5. Se algo correr mal

| Mensagem / sintoma | Causa provável | Solução |
|---|---|---|
| "Sem PDFs em …" | pasta errada ou vazia | confirmar o caminho em --pdfs |
| "N documento(s) com texto consolidado sem pasta de versões correspondente" (uma linha com os nomes) | o nome da subpasta não está contido no nome do PDF | renomear a subpasta (ex.: `ACIP_FESAHT`); sem ela, o consolidado fica todo na faixa CONSOLIDADO |
| "A pasta de versões anteriores não existe" | `--pasta-versoes` (ou o campo «Versões anteriores» da app) aponta para uma pasta que não existe | corrigir o caminho, ou retirar a opção: sem ela os consolidados ficam todos na faixa CONSOLIDADO. Antes, cada documento consolidado ficava fora do QDPX (corrida de 2025) |
| "ERRO, documento fora do QDPX" / `EXCLUÍDO` no diagnostico.md | o documento foi extraído mas falhou num passo seguinte | enviar o `diagnostico.md`: diz o erro de cada documento excluído |
| "a versão antiga parece parcial" | a base da comparação é uma revisão de 2-3 páginas | juntar à subpasta o último texto completo |
| "PDF digitalizado?" / 0 cláusulas | o PDF é uma imagem (scan) | obter o PDF nativo do BTE; OCR ainda não suportado |
| subtipo sempre "desconhecido" | falta o ficheiro de variáveis ou o nome do PDF não bate certo com o MaxQDA | ver 3.2; o cruzamento usa os primeiros ~30 caracteres do nome |
| códigos todos em REVER, nada em AUTO | falta `--metricas` (calibração) | usar o metricas.json da última avaliação contra a amostra de referência |
| erro ao importar QDPX no MaxQDA | versão antiga do MaxQDA | usar MaxQDA 2022 ou superior (REFI-QDA) |
| a app gráfica não abre no macOS | o Python não tem o Tk (Homebrew) ou tem um Tk antigo (o Python da Apple) | abrir `scripts/AppCCT.command`: a janela do terminal fica aberta com a causa e a solução (por exemplo, `brew install python-tk@3.11`); o mesmo em `python -m cct.doctor`. O pipeline no terminal não precisa do Tk |
| a app/comando "não faz nada" | ambiente por instalar | correr `python -m cct.doctor` e seguir as instruções |
| `.venv/bin/python` não é reconhecido no PowerShell | caminho de macOS usado em Windows | usar `.\.venv\Scripts\python.exe` em todos os comandos; não é necessário ativar o ambiente |
| `ModuleNotFoundError: No module named 'jsonschema'` depois de instalar as dependências | `python` chama outro interpretador | repetir com `.\.venv\Scripts\python.exe`; confirmar o caminho mostrado pelo `doctor` antes de reinstalar |
| `doctor` indica falta de PDFs antes da primeira recolha | pasta final ainda vazia | verificar primeiro os índices e correr a aquisição; a ausência das variáveis MaxQDA não bloqueia a recolha |
| `Sem ficheiros-índice` | pasta vazia ou ficheiro `.xlsx` errado | confirmar `Get-ChildItem .\data\raw\indices\*.xlsx`; copiar o índice fornecido pela equipa |
| PDFs em `data/interim/recolha/`, mas não em `data/raw/bte/` | nomeação por confirmar, execução sem `--aplicar` ou conflito no destino | ler `results/aquisicao/relatorio_*.txt` e o estado no registo; corrigir siglas confirmadas com `--siglas` e repetir a nomeação apenas dos documentos ainda não escritos |
| `ja_existente: 14`, `pedidos de rede: 0`, mas oito nomes `por_confirmar` | PDFs recolhidos, ainda sem nome aprovado | rever os avisos por documento e a fonte de cada sigla antes de `--aplicar`; a rede não resolve avisos de nomeação |
| `nomeado: 8` com `--aceitar-heuristicas`, mas ainda há avisos | os PDFs foram escritos com nomes provisórios | inventariar os oito ficheiros e rever as siglas e os outorgantes; não interpretar `nomeado` como validação humana |
| `conflito: nome já atribuído … novo nome proposto …` | uma sigla ou metadado alterou o nome de um PDF já escrito | guardar o relatório e seguir a migração controlada da secção 5.2; o comando preserva o nome e o PDF anteriores |
| `campos estruturais do nome RNC excedem o limite` | tipo ou código do índice tornam impossível um nome íntegro de 63 caracteres | confirmar os metadados na fonte; o PDF fica `por_confirmar`, sem truncar campos nem aceitar a heurística |

**Regra dos erros:** o `relatorio.txt` lista sempre os documentos com
problemas — o resto do lote NÃO é afetado. Corrige só esses e volta a correr
(o pipeline pode repetir-se à vontade; não estraga nada).

### 5.1 Registar soluções manuais no guia

Cada dificuldade resolvida na estação deve produzir uma nota curta para a
próxima revisão deste guia: comando e ambiente usados (sem nomes de pessoas
nem caminhos pessoais), sintoma literal, causa confirmada, passo que resolveu,
ficheiros afetados e verificação final. Distinguir uma hipótese de uma causa
confirmada. Quando a solução exigir um nome de PDF ou uma relação entre
documentos, anexar ao registo de trabalho o identificador do índice e a fonte
da confirmação. Rever a nota com a equipa antes de a transformar numa regra
geral ou num teste automático. Não copiar o registo JSONL nem dados do corpus
para o repositório.

### 5.2 Rever nomes e corrigir os que já foram escritos

1. Guardar uma cópia de segurança do índice, de
   `data/registo/registo_bte.jsonl`, dos PDFs em `data/interim/recolha/` e
   `data/raw/bte/`, do catálogo e das variáveis/documentos do MaxQDA, se já
   existirem. Conservar `results/aquisicao/manifest.json` e o relatório da
   corrida. Não apagar o registo nem alterar o ordinal.
2. Fazer uma tabela de revisão com **chave do registo, código IRCT, nome atual,
   hash do PDF, nome proposto, fonte da sigla, decisão e presença no MaxQDA**.
   Conferir título, outorgantes e código com o índice e com a fonte institucional;
   resolver as abreviaturas com a equipa responsável. O mesmo par
   `AEVP-FESAHT` nos ordinais 379 e 380 tem códigos distintos (26651 e 26652):
   o aviso de par repetido é informativo, não prova duplicação. Nos casos
   387–390 (`CARRISTUR`, retificações), os outorgantes vieram do título:
   confirmar a correspondência com o ato que é retificado. No 381 há uma
   terceira sigla cortada pelo limite de 63 caracteres; examinar os
   outorgantes completos. Rever ainda as siglas derivadas de Empresa
   Metropolitana, AWP e AP Solutions. O título do 390 explicita
   `Sindicato Nacional dos Motoristas e Outros Trabalhadores - SNMOT`:
   `Motoristas` resultou de um corte incorreto da expressão «e Outros».
   O código corrigido propõe `SNMOT`; se já existir o PDF com `Motoristas`,
   a proteção assinala `conflito` e mantém ambos o nome e o PDF antigos até
   à migração controlada. O exemplo `SNM` de documentos antigos não deve ser
   aplicado ao 390.
3. Se um documento **ainda não foi escrito**, preencher um `siglas.csv` local
   apenas com siglas confirmadas, executar primeiro sem `--aplicar` e verificar
   o nome proposto. Se o nome **já foi escrito**, uma alteração de sigla produz
   `conflito` e preserva o `doc_id`, o caminho e o PDF anteriores. Não renomear
   à mão nem correr repetidamente `--aceitar-heuristicas` para ultrapassar o
   conflito. Aprovar uma migração que atualize em conjunto PDF, registo,
   catálogo, referências de versões, variáveis/documentos do MaxQDA e
   manifestos que dependam do nome. Se o MaxQDA já tiver importado o PDF,
   coordenar a alteração com a equipa antes de a executar. A migração para o
   futuro esquema comum das três famílias segue a [SPEC-0004](../../specs/0004-esquema-de-nomes-comum-as-tres-familias.md);
   essa especificação ainda não está implementada.
4. Verificar que cada chave mantém um só PDF final com hash igual ao PDF
   recolhido, que não há colisões de nomes sem distinção de maiúsculas no
   Windows, que os 14 documentos e respetivos códigos estão representados
   uma vez no catálogo e que as ligações no MaxQDA continuam válidas. Registar
   no guia a decisão e a fonte de cada caso que produziu uma regra reutilizável.

O `doctor` do ramo de instalação de 17-09-2026 podia indicar, por engano,
que o `.venv` não estava em uso e contabilizar a ausência opcional das
variáveis MaxQDA como problema. Executar o `doctor` com
`.\.venv\Scripts\python.exe` e usar o ramo principal atualizado para obter o
diagnóstico corrigido; nenhum desses dois avisos explica por si só os oito
nomes por confirmar. Um *checkout* antigo não se atualiza automaticamente
quando o ramo principal muda.

### 5.3 O que o índice BTE 31/2026 permite confirmar

Revisão do `BTE31_2026_CRL.xlsx` fornecido em 23-09-2026, sem alterar o
ficheiro de origem: há 14 linhas, IDs 377/2026 a 390/2026, com 14 códigos
IRCT, nomes de PDF e URL distintos. Os quatro `AE-ALT-RECT` (387 a 390)
têm `Outorgantes` vazio; o título identifica as entidades e a coluna
`DocAlteradosPorEste` aponta, respetivamente, para os documentos 323, 324,
325 e 326/2026. Estas relações devem ser conferidas nos atos publicados
antes de se considerar o nome definitivo. O 381 lista três outorgantes;
o nome de 63 caracteres contém a terceira sigla abreviada. Os documentos
379 e 380 partilham outorgantes mas têm códigos IRCT e referências anteriores
distintos.

O índice ainda tem `PagVersaoEscrita`, `CAE`, `LinkDocEmVigor`,
`DocAlteradosPorEste2` e `DocAlteramEste` vazios nas 14 linhas; a coluna
`Outorgantes` falta nas quatro retificações. Estes vazios são uma lista de
verificação para o enriquecimento futuro, não prova de que o BTE não contém
essa informação. Não preencher por inferência nem substituir o índice
original sem preservar a proveniência. Para cada valor acrescentado, guardar
o ID do documento, a fonte, a data de consulta e a decisão de revisão.

### 5.4 Avisos de extração de texto e tabelas no QDPX

Na corrida BTE 31/2026 de 23-09-2026, `--pdfs` apontou primeiro para
`bte_2026/convencoes` e o programa respondeu `Sem PDFs`. O código antigo
acrescentava indevidamente outra pasta `convencoes` a esse caminho. Ao
apontar para `bte_2026/convencoes/PRI`, processou nove ficheiros e omitiu
os cinco em `SPE`. Usar a pasta do ano para abranger os dois âmbitos,
inclusive na versão antiga, ou atualizar o código para aceitar também a
pasta `convencoes`. Confirmar a contagem esperada no relatório **antes** de
importar o QDPX; guardar a nova corrida noutra pasta de resultados para
preservar a evidência anterior. Por exemplo, a partir da raiz no PowerShell:

```powershell
.\.venv\Scripts\python.exe -m cct.pipeline_tema --pdfs data\raw\bte\bte_2026 --codebook codebooks\4_08_protecao_dados.yaml --out results\corrida_completa
```

Uma corrida pode indicar `Convenções processadas: 9/9` e ainda ter tabelas
salariais mal estruturadas. Nesta corrida, o manifesto confirma que o
extrator foi `pdfplumber`. A limpeza de cabeçalhos apagou as marcas
internas que protegem linhas de tabela quando estas ocorrem em várias
páginas. Os textos de 380, 384, 385 e 386 foram colados em linhas longas.
A correção preserva as marcas e recupera blocos de linhas; **a comparação
de todas as células com os PDFs continua necessária**, sobretudo nas
grelhas largas de 384/385. O aviso `nenhum bloco de tabela` não significa
necessariamente ausência dos valores: a auditoria só reconhece blocos com
pelo menos duas linhas consecutivas de células separadas por ` | `.
O aviso `tabela fora do corpo do nó` pode referir-se apenas ao facto de
o cabeçalho do anexo ser um nó separado do respetivo corpo. Um artigo que
termina com dois pontos para introduzir cláusulas também pode ser sinalizado
indevidamente como `sem corpo válido`. **Nenhuma destas explicações valida
os valores extraídos:** conferir a tabela e o artigo no PDF de origem.

Guardar o PDF, o TXT, o QDPX, o relatório e o
`manifest.json`; registar documento, página, anexo, categoria/valor e
divergência observada. Não usar tabelas assinaladas para indicadores de
remuneração sem revisão. Não voltar a correr só com `--extrator docling`
e presumir que resolveu: comparar as duas saídas com a mesma página do PDF.
O procedimento de diagnóstico, correção e validação está em
[Intervenção na extração BTE 31/2026](../validacao/intervencao-extracao-bte31-2026-09-23.md).

---

## 6. Ciclo de melhoria dos temas
1. As peritas marcam sugestões erradas/em falta no XLSX (ou em memos MaxQDA
   exportados para HTML).
2. Ajustam-se os termos no YAML do tema (ver `prompts-codebooks.md`,
   incluindo a mineração automática dos dados de 2025).
3. Remede-se contra a amostra de referência:
   `python -m cct.avaliar_baseline --xlsx <amostra-referencia>.xlsx --pdfs <pasta>
   --codebook <tema>.yaml --out results/benchmarks/<tema>/metricas/baseline_X`
4. A triagem AUTO/REVER recalibra-se sozinha na corrida seguinte
   (passar o novo `metricas.json` em `--metricas`).

## 7. Limitações conhecidas
- PDFs digitalizados (imagens) não funcionam.
- Numeração por extenso ("Cláusula primeira") já é reconhecida na extração,
  mas ainda não é convertida para número canónico na comparação diacrónica
  (ISSUE-0001 / GitHub #28).
- Blocos de título com várias linhas no início dos documentos podem ficar
  com quebras imperfeitas.
- A camada semântica (modelo local, por exemplo LM Studio + gemma) é opcional e as suas
  sugestões vão sempre para REVER. Aceita apenas servidores em `localhost`/loopback;
  serviços externos não são suportados.
