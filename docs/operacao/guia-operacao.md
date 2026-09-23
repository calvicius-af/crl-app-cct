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
│       │           │   ├── 2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP.pdf
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

Se a rede institucional não permitir a descarga, usar os PDFs obtidos por via
institucional e registar a origem e a correspondência com o índice antes de
qualquer cópia ou renomeação. Não colocar um PDF diretamente na pasta final
com um nome presumido: a nomeação automática depende do registo de recolha e
dos metadados confirmados do índice. Escalar ao responsável pelos dados os
casos sem identificador ou correspondência segura.

### Regras de nomes (importante!)
- **Estado da alteração de 2026**: o [ADR-0022](../adr/0022-esquema-de-nomes-comum-as-tres-familias.md)
  aprovou um esquema com `{ANO}_BTE_{NN}_` à cabeça para convenções,
  portarias de extensão e acordos de adesão. A
  [SPEC-0004](../../specs/0004-esquema-de-nomes-comum-as-tres-familias.md)
  continua por implementar. O código deste ramo escreve o esquema RNC do
  ADR-0016 descrito abaixo. O ramo de instalação em Windows resolve problemas
  do ambiente, não faz a migração nem ativa o esquema do ADR-0022.
- **PDFs das convenções, a partir do corpus de 2026**: esquema RNC, obrigatório
  ([ADR-0021](../adr/0021-corte-por-ano-do-esquema-de-nomes.md)) —
  `{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}.pdf`, ex.:
  `2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP.pdf`. Sete campos, descritos em
  [docs/rnc/README.md §4.1](../rnc/README.md#41-a-regra). O nome deve ser IGUAL ao
  usado no MaxQDA (sem o sufixo `_TXT`). Sem espaços no início/fim.
- **Portarias e acordos de adesão**: o esquema atual ainda não garante o
  número e ano da portaria nem o código confirmado da convenção de base no
  nome. Não validar estes nomes pela aparência nem integrá-los no corpus de
  análise temática. Consultar o catálogo e a SPEC-0004 antes de qualquer
  migração manual; as portarias e adesões não entram no pipeline temático.
- **PDFs de corpos anteriores a 2026**: mantêm o esquema de 2025,
  `AA_PR_NNN_BTE_NN_Partes_Sindicato.pdf` (AA = ano com 2 dígitos) — não se renomeiam.
- **Subpastas de versões**: o nome da subpasta tem de estar CONTIDO no nome
  do PDF da convenção (ex.: subpasta `AEVP_FESAHT` ↔ PDF
  `2026_PRI_379_CCT-ALT_26651_BTE_31_AEVP-FESAHT.pdf`). É assim que o pipeline as
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
lento (~1-1,7 s/página) e de exigir instalação à parte:
`.venv/bin/python -m pip install docling`
(Windows: `.venv\Scripts\python -m pip install docling`)
(≈4 GB com PyTorch; em Mac Apple Silicon o Python tem de ser arm64 —
`python3 -c "import platform; print(platform.machine())"` deve dizer
`arm64`). A primeira corrida descarrega os modelos de layout.

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
| "sem pasta de versões correspondente" | nome da subpasta não está contido no nome do PDF | renomear a subpasta (ex.: `ACIP_FESAHT`) |
| "a versão antiga parece parcial" | a base da comparação é uma revisão de 2-3 páginas | juntar à subpasta o último texto completo |
| "PDF digitalizado?" / 0 cláusulas | o PDF é uma imagem (scan) | obter o PDF nativo do BTE; OCR ainda não suportado |
| subtipo sempre "desconhecido" | falta o ficheiro de variáveis ou o nome do PDF não bate certo com o MaxQDA | ver 3.2; o cruzamento usa os primeiros ~30 caracteres do nome |
| códigos todos em REVER, nada em AUTO | falta `--metricas` (calibração) | usar o metricas.json da última avaliação contra a amostra de referência |
| erro ao importar QDPX no MaxQDA | versão antiga do MaxQDA | usar MaxQDA 2022 ou superior (REFI-QDA) |
| a app/comando "não faz nada" | ambiente por instalar | correr `python -m cct.doctor` e seguir as instruções |
| `.venv/bin/python` não é reconhecido no PowerShell | caminho de macOS usado em Windows | usar `.\.venv\Scripts\python.exe` em todos os comandos; não é necessário ativar o ambiente |
| `ModuleNotFoundError: No module named 'jsonschema'` depois de instalar as dependências | `python` chama outro interpretador | repetir com `.\.venv\Scripts\python.exe`; confirmar o caminho mostrado pelo `doctor` antes de reinstalar |
| `doctor` indica falta de PDFs antes da primeira recolha | pasta final ainda vazia | verificar primeiro os índices e correr a aquisição; a ausência das variáveis MaxQDA não bloqueia a recolha |
| `Sem ficheiros-índice` | pasta vazia ou ficheiro `.xlsx` errado | confirmar `Get-ChildItem .\data\raw\indices\*.xlsx`; copiar o índice fornecido pela equipa |
| PDFs em `data/interim/recolha/`, mas não em `data/raw/bte/` | nomeação por confirmar, execução sem `--aplicar` ou conflito no destino | ler `results/aquisicao/relatorio_*.txt` e o estado no registo; corrigir siglas confirmadas com `--siglas` e repetir a nomeação, sem apagar os originais |

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
