# ISSUE-0025: avisos de estrutura que ficaram na corrida de 2025

- **Estado:** Aberta
- **Data:** 2026-09-25
- **GitHub:** #91
- **Onde dói:** `cct/extractor.py` (estrutura), `cct/sanidade.py`, `cct/auditoria.py`

## O que acontece

Na terceira corrida de 2025 (277 PDF, commit `e44c0c0`), os 277 documentos chegam ao QDPX,
mas ficam 144 problemas no relatório. Por tipo:

| # | Aviso | Ocorrências |
|---|---|---|
| 1 | Anexo de remuneração sem nenhuma tabela (INCM ×3, Portway, SUPERBOOK, EMPORDEF) | 6 |
| 2 | Anexo com a tabela fora do corpo do nó | 24 |
| 3 | Corpo sem frase terminada em ponto («Mapas de horário», «Parentalidade») | 147 em 71 documentos |
| 4 | Cláusula ou artigo sem conteúdo | 21 |
| 5 | Nenhuma cláusula ou artigo reconhecido (EMPORDEF, EPAL, DHL) | 3 |
| 6 | Tabela provavelmente rodada, com palavras invertidas (AGEAS, p27) | 1 |
| 7 | Sem pasta de versões correspondente | 39 |

O TINITA está no #42 e as tabelas colapsadas no #84 (ISSUE-0024).

## O que devia acontecer

Cada aviso aponta um defeito real. Os que vêm de padrões de redação (corpos que remetem
para a lei, documentos só com tabelas) distinguem-se de uma perda de texto.

## Como reproduzir

```bash
python -m cct.pipeline_tema --pdfs data/raw/bte/bte_2025 \
    --codebook codebooks/4_08_protecao_dados.yaml --out results/runs/2025/2025_4_08
```

## Notas

Hipóteses e plano no #91. O aviso 4 pode ter diminuído com o commit `781b2f0`, que ainda
não passou por uma corrida. Registo das corridas:
[corrida-2025-macos-2026-09-24.md](../docs/validacao/corrida-2025-macos-2026-09-24.md).
