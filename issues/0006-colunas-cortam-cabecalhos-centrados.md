# ISSUE-0006: o corte em duas colunas parte cabeçalhos centrados (extrator pdfplumber)

- **Estado:** Aberta
- **Data:** 2026-08-27
- **Onde dói:** `cct/extractor.py` (`_duas_colunas`, `_extrair_pagina`)

## O que acontece

Numa página com corpo em duas colunas mas **cabeçalhos centrados** (que
atravessam a goteira), o corte parte esses cabeçalhos ao meio e o texto sai
truncado.

Caso concreto: `25_PR_068_BTE_14_AguasNorte_SINDEL.pdf`, página 24 (extrator
`pdfplumber`, que é o de omissão):

```text
'8- A comissão paritária principiará por elaborar o seu CAPÍTU'
'Cláusula gera Cláusu'
'Cláusula gera'
'1- Todas as cláusulas e disposições deste ACT que v veis enquanto se mantiverem'
```

`CAPÍTULO XV` e `Cláusula geral e transitória` são títulos centrados; ao cortar
a página em duas metades, ficam divididos entre elas.

## Evidência

```bash
.venv/bin/python - <<'PY'
import pdfplumber
from cct.extractor import _duas_colunas, _extrair_pagina
with pdfplumber.open("data/raw/bte/bte_2025/25_PR_068_BTE_14_AguasNorte_SINDEL.pdf") as p:
    pg = p.pages[23]
    print("goteira:", _duas_colunas(pg))
    palavras = pg.extract_words()
    atravessam = [w["text"] for w in palavras if w["x0"] < 297.638 < w["x1"]]
    print(f"palavras que atravessam a goteira: {len(atravessam)} → {atravessam[:8]}")
PY
```

Resultado: goteira em 297.638 e **33 palavras a atravessá-la**
(`['podem', 'da', 'devendo', 'seu', 'CAPÍTULO', 'geral', 'Cláusula', 'geral']`).

Os caracteres não desaparecem — a cauda cortada reaparece no recorte da coluna
direita — mas a ordem de leitura fica destruída e as palavras partidas ao meio.

Alcance medido nos 6 documentos de 2025: 478 páginas, 4 com goteira detetada.
Só esta apresenta cabeçalhos centrados a atravessá-la, mas o padrão é comum nos
BTE antigos (2021/2022), que são todos a duas colunas.

## O que devia acontecer

Uma linha que atravessa a goteira pertence a uma só coluna lógica (é um título
a toda a largura) e deve sair inteira, antes ou depois do bloco de duas
colunas, conforme a sua posição vertical.

## Notas

Não foi corrigido nesta ronda por ser uma alteração de desenho da heurística de
colunas, com risco próprio: exige separar as linhas de largura total das linhas
de coluna antes de recortar, em vez de cortar a página em duas metades. O
extrator `docling` não sofre deste problema — ordena por geometria e trata cada
item como uma unidade (ver `ordenar_por_leitura`).

Relacionada com a ISSUE-0001 (numeração por extenso) apenas por tocarem no mesmo
módulo.
