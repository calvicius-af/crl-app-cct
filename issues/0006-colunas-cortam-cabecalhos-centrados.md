# ISSUE-0006: o corte em duas colunas parte cabeçalhos centrados (extrator pdfplumber)

- **Estado:** Resolvida — 2026-09-26 (ver "Resolução")
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

## Evidência e correção parcial (2026-09-24)

O corpus de regressão (BTE 31/2026) mostrou o defeito em páginas de coluna única com
tabelas de coluna do meio vazia: 377 («Enquadramento das profissões», cabeçalho do BTE a
meio do texto, primeira coluna separada da terceira) e 384/385 (títulos partidos:
`ANEX` | `XO II`, `Gr` | `upos profissionais`). `_duas_colunas` passa a recusar o corte
quando há pelo menos dois traços horizontais a cruzar a goteira no corpo da página
(`_grelha_atravessa`), e nunca corta páginas com texto rodado. Testes com PDF sintéticos
para a tabela (não corta) e para duas colunas de texto sem grelha (continua a cortar).

Fica por resolver o caso original desta issue, um cabeçalho centrado numa página de duas
colunas verdadeiras, que precisa de um PDF do BTE antigo no corpus.

## Resolução (2026-09-26)

**O caso original já saía certo.** Na p24 do `25_PR_068` (Águas do Norte), a página não
é tratada como duas colunas (`_duas_colunas` devolve `None`), e «CAPÍTULO XV» e
«Cláusula geral e transitória» saem inteiros.

**Nenhuma palavra partida pela goteira.** Varridas todas as páginas em colunas de 565
PDF (boletins de 2021 e 2022 e documentos de 2025): das 11 663 palavras que atravessam
a goteira, nenhuma falta no texto da página. Os 15 alertas da varredura eram palavras
rodadas, que o extrator lê no sentido certo, e um cabeçalho lido sem tirar primeiro o
texto escondido (a varredura não aplicava `cct/recorte.py`; o extrator aplica).

**O que faltava era a ordem.** As linhas que atravessam a goteira já partiam a página em
faixas (`_faixas_de_colunas`). Um título de secção curto e encostado à esquerda, porém,
não atravessa. No boletim 28 de 2021, p44, «DECISÕES ARBITRAIS», por baixo de um bloco
em duas colunas, lia-se entre a coluna esquerda e a direita. No boletim 4 de 2021, p34,
«II - DIREÇÃO» e a eleição da AIT ficavam antes da coluna direita de cima.

A regra nova: uma faixa em colunas acaba também num espaço em branco que atravessa a
página inteira, com as duas colunas vazias à mesma altura, de pelo menos três alturas
de linha (`SALTO_DE_SECCAO`). É uma mudança de secção. O espaço entre parágrafos, ainda
que coincida nas duas colunas, é menor e não parte a faixa.

**Medido** em 6276 páginas em colunas de 579 PDF, com a regra ligada e desligada no
mesmo processo: mudam 253 páginas (213 dos boletins de 2021, 32 dos de 2022, 8 dos
documentos de 2025), todas sem uma palavra a mais ou a menos. Nos boletins, os títulos
de secção passam para depois das colunas de cima, conferido com a imagem das páginas.
Nos documentos de 2025, só o cabeçalho do boletim muda de sítio, e é retirado como
mobiliário: o texto final dos 8 documentos é igual antes e depois. O corpus do BTE 31
não muda. Teste: `tests/test_extractor.py::test_seccao_por_baixo_das_colunas_le_se_depois_das_duas`.

**Fica registado à parte:** na mesma p44 de 2021, o texto escondido deixa restos numa
tabela («1fi45», «150-»): letras da camada recortada que `tirar_escondidas` não emparelha.
