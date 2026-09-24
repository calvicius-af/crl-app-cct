# ISSUE-0020: as tabelas dos CARRISTUR estão rodadas 90º e saem invertidas

- **Estado:** Resolvida — 2026-09-19
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor.py` (`_extrair_pagina`, `_formatar_tabela`),
  `cct/extractor_docling.py` (`_linhas_de_tabela`), `cct/auditoria.py`

## O que acontece

Nos quatro documentos CARRISTUR (`26_PR_011` a `26_PR_014` no esquema de 2025; agora
`2026_SPE_387` a `2026_SPE_390` no esquema RNC — ver ISSUE-0022), as tabelas estão rodadas
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
with pdfplumber.open(
    "data/raw/bte/bte_2026/convencoes/SPE/"
    "2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-ASPTC.pdf") as p:
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

## O que foi feito

Implementada a via do aviso (segunda opção da nota 2), não a deteção-e-correção: o
docling já lê estas tabelas bem, e é o extrator recomendado para tabelas desde a ronda
de 2026-09-17; corrigir a rotação no pdfplumber duplicaria trabalho que a aplicação já
resolve de outra forma.

Nova função `tabelas_rodadas_pdfplumber` em `cct/auditoria.py`, no mesmo espírito das
auditorias que já lá vivem (divergência de contagem entre extratores, anexos de
remuneração sem tabela): abre o PDF só para consultar `find_tables()` (não extrai
texto, não é um segundo extrator), e avisa quando `altura > 2 × largura` — exatamente
o limiar que a nota 3 propôs. Ligada ao `cct.pipeline_tema`, só quando o extrator em
uso é o pdfplumber (`--extrator docling` já lê bem, não há o que avisar).

Verificado com o pipeline real: a corrida com `--extrator pdfplumber` (omissão) sobre
os quatro CARRISTUR (`2026_SPE_387` a `390`) produz o aviso `"tabela com 315×672 pt
(...) — provavelmente rodada 90º (...) usar --extrator docling"` no relatório; a
corrida equivalente com `--extrator docling` não produz nenhum. O texto invertido
continua a sair no QDPX quando se usa pdfplumber — o aviso não o corrige, só o torna
visível, como a issue aceitava como solução mínima.

## Correção no pdfplumber (2026-09-24)

O corpus de regressão mostrou o texto invertido no QDPX dos quatro CARRISTUR e do 382
(`ahlocsE`, `ocincéT`, `oirótarenumeR`), porque a corrida normal usa o pdfplumber. O
extrator passa a ler o texto rodado no sentido certo (`char_dir_rotated` do pdfplumber
0.11, sem dependência nova) e a pôr as tabelas rodadas de pé (`_sentido_da_pagina`,
`_dados_tabela` em `cct/extractor.py`). Testado com PDF sintéticos nos dois sentidos de
rotação (`tests/test_extractor.py`); o aviso da auditoria só aparece se o texto ainda
tiver palavras invertidas.

**Confirmado no corpus real** (job «corpus» do CI, commit `0da8b02`): os quatro
CARRISTUR com 100% de cobertura e zero palavras invertidas, contra 626 palavras a mais
antes. O 382 com 99,8%; resta a ordem das grelhas da p34. Ver
[corpus BTE 31/2026](../docs/validacao/corpus-bte31-2026-09-24.md). Confirmado
visualmente no MaxQDA a 2026-09-24 (p34 do 382 e uma tabela de um CARRISTUR): sem erros.
