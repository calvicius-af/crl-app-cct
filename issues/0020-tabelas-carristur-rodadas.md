# ISSUE-0020: as tabelas dos CARRISTUR estão rodadas 90º e saem invertidas

- **Estado:** Aberta
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor.py` (`_extrair_pagina`, `_formatar_tabela`),
  `cct/extractor_docling.py` (`_linhas_de_tabela`)

## O que acontece

Nos quatro documentos CARRISTUR (`26_PR_011` a `26_PR_014`), as tabelas estão rodadas
90º no sentido contrário ao dos ponteiros do relógio. O extrator não o deteta e o texto
sai invertido, carácter a carácter:

```text
oãssergorp
arap
)sona(
aicnênamrep
ed
sopmeT
```

(é `Tempos de permanência (anos) para progressão` lido de baixo para cima e ao contrário)

## O que devia acontecer

A tabela rodada detetada e o texto lido na orientação correta — ou, no mínimo, um aviso
no relatório a dizer que a tabela não pôde ser lida, em vez de a emitir invertida como
se fosse conteúdo válido.

## Como reproduzir

```bash
.venv/bin/python - <<'PY'
import pdfplumber
with pdfplumber.open("data/raw/bte/bte_2026/26_PR_011_BTE_31_CARRISTUR_ASPTC.pdf") as p:
    for i, pg in enumerate(p.pages):
        for tab in pg.find_tables():
            print(f"p{i+1}", tab.bbox, tab.extract()[0][:3])
PY
```

## Notas

- **O docling lê estas tabelas corretamente.** No QDPX gerado com `--extrator docling`,
  o `26_PR_011` traz `Tempos de permanência (anos) para progressão 2 3 4 5 6 Escolha |
  Escolha | …` — orientação certa. O defeito é **específico do pdfplumber**, que é o
  extrator de omissão.
- Isto reforça a decisão da ronda de 2026-09-17 (docling como extrator de tabelas): a
  correção pode ser simplesmente documentar que o pdfplumber não serve para estes
  documentos, ou detetar a rotação e avisar.
- Deteção possível: a proporção da bbox (largura 315 × altura 672 — muito mais alta que
  larga) é atípica para uma tabela de remunerações e sugere rotação. Um aviso quando
  `altura > 2 × largura` numa tabela é barato e não arrisca falsos positivos graves.
- Relacionada com a ISSUE-0014 (os mesmos quatro documentos CARRISTUR, que também não
  produzem cláusulas).
