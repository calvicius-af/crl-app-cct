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
│   └── raw/
│       ├── bte/
│       │   └── bte_2026/          ← PDFs das convenções, UM POR CONVENÇÃO
│       │       ├── 26_PR_001_BTE_01_AHP_SITESE.pdf
│       │       └── …
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

### Regras de nomes (importante!)
- **PDFs das convenções**: `AA_PR_NNN_BTE_NN_Partes_Sindicato.pdf`
  (AA = ano com 2 dígitos). O nome deve ser IGUAL ao usado no MaxQDA
  (sem o sufixo `_TXT`). Sem espaços no início/fim.
- **Subpastas de versões**: o nome da subpasta tem de estar CONTIDO no nome
  do PDF da convenção (ex.: subpasta `ACIP_FESAHT` ↔ PDF
  `26_PR_003_BTE_02_ACIP_FESAHT.pdf`). É assim que o pipeline as encontra.
- **Versões anteriores** dentro da subpasta: o nome deve começar pelo ano —
  `2021_...pdf`, `24122_...pdf` (24 = 2024), `ACIP_FESAHT_2009.pdf`.
  Ficheiros `Comparei_*.pdf` e `Diferencas_*.docx` são ignorados.

---

## 3. Antes de correr — checklist

### 3.1 Verificar a instalação (fazer sempre primeiro)
```
.venv/bin/python -m cct.doctor          (Mac)
.venv\Scripts\python -m cct.doctor      (Windows)
```
Isto verifica o Python, as bibliotecas e as pastas, e diz-te em português
o que falta e como resolver.

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
    --metricas results/metricas/baseline_4_08_v4/metricas.json \
    --pasta-versoes data/raw/textos_consolidados \
    --out results/2026_4_08
```
Só `--pdfs`, `--codebook` e `--out` são obrigatórios; o resto melhora o
resultado mas pode faltar.

**`--extrator docling`** (opcional): usa o docling em vez do pdfplumber na
extração. Recupera tabelas de anexos (tabelas salariais, perfis de função)
e layouts difíceis que o extrator clássico perde, ao custo de ser mais
lento (~1-1,7 s/página) e de exigir instalação à parte:
`.venv/bin/python -m pip install docling docling-hierarchical-pdf`
(≈4 GB com PyTorch; em Mac Apple Silicon o Python tem de ser arm64 —
`python3 -c "import platform; print(platform.machine())"` deve dizer
`arm64`). A primeira corrida descarrega os modelos de layout.

### Comparar duas versões de uma convenção (avulso)
```
.venv/bin/python -m cct.comparar --pasta data/raw/textos_consolidados/ACIP_FESAHT \
    --out results/comparacoes/ACIP.xlsx
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
| códigos todos em REVER, nada em AUTO | falta `--metricas` (calibração) | usar o metricas.json da última avaliação contra gabarito |
| erro ao importar QDPX no MaxQDA | versão antiga do MaxQDA | usar MaxQDA 2022 ou superior (REFI-QDA) |
| a app/comando "não faz nada" | ambiente por instalar | correr `python -m cct.doctor` e seguir as instruções |

**Regra dos erros:** o `relatorio.txt` lista sempre os documentos com
problemas — o resto do lote NÃO é afetado. Corrige só esses e volta a correr
(o pipeline pode repetir-se à vontade; não estraga nada).

---

## 6. Ciclo de melhoria dos temas
1. As peritas marcam sugestões erradas/em falta no XLSX (ou em memos MaxQDA
   exportados para HTML).
2. Ajustam-se os termos no YAML do tema (ver `prompts-codebooks.md`,
   incluindo a mineração automática dos dados de 2025).
3. Remede-se contra o gabarito:
   `python -m cct.avaliar_baseline --xlsx <gabarito>.xlsx --pdfs <pasta>
   --codebook <tema>.yaml --out results/metricas/baseline_X`
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
