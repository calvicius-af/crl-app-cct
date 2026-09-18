# ISSUE-0019: resíduo "BE" do cabeçalho do BTE no corpo do texto

- **Estado:** Aberta
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor_docling.py` (`limpar_texto_item`, `RE_BTE_CABECALHO`)

## O que acontece

No `26_PR_009_BTE_31_APSolutionsGMBH_STAS`, aparece um `BE` isolado entre dois
parágrafos:

```text
c) A situação económica e financeira da empresa o permita.
BE
3- Após conclusão de estágio de ingresso, caso haja lugar ao mesmo, a evolução dos
trabalhadores das subcategorias de operador de assistência, de o...
```

É resíduo do cabeçalho corrido do BTE (a sigla `BE` de *Boletim do Trabalho e Emprego*,
ou um fragmento de `BTE` partido). Não faz sentido no corpo e aparece em vários
documentos.

## O que devia acontecer

O resíduo descartado, como já se descarta o cabeçalho completo (`Boletim do Trabalho e
Emprego`), a data da edição e o número de página solto.

## Como reproduzir

```bash
.venv/bin/python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026 --codebook codebooks/demo_fase0.yaml \
    --extrator docling --out results/runs/2026/residuos
# procurar uma linha "BE" isolada no TXT do 26_PR_009
```

## Notas

- `limpar_texto_item` já descarta `RE_BTE_CABECALHO` (`^Boletim do Trabalho e Emprego`),
  `RE_BTE_DATA` e `^\d+$`. Falta o fragmento curto: uma linha que seja só `BE` (ou
  `BTE` truncado).
- **Cuidado**: `BE` pode ser sigla legítima de uma entidade. A regra deve ser estreita —
  linha isolada, exatamente `BE` ou `BTE`, sem pontuação, e idealmente só quando
  rodeada de itens de texto (não dentro de tabela). Confirmar nos 14 documentos que
  nenhuma sigla real é apanhada.
- Alternativa mais segura: descartar só quando o item não tem geometria própria
  (herdou a posição do anterior) — sinal de que é fragmento de cabeçalho, não conteúdo.
