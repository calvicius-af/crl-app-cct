# ISSUE-0017: o título da Cláusula 68.ª não é apanhado

- **Estado:** Resolvida — 2026-09-19
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor.py` (`estruturar`, `_titulo_candidato`, `_normalizar_rotulo`)

## O que acontece

No `26_PR_005_BTE_31_ACIBARCELOS_IndependenteSector`, a Cláusula 68.ª sai sem título —
o título foi absorvido pelo corpo:

```text
CAPÍTULO IX - Segurança, higiene e saúde no trabalho

Cláusula 68.ª
Organização de serviços de segurança, higiene e saúde no trabalho Independentemente
do número de trabalhadores que se encontrem ao seu serviço, a entidade empregadora é
obrigada a organizar serviços de segurança, higiene e saúde, visando a prevenção de
riscos profissionais e a promoção ...
```

O título é `Organização de serviços de segurança, higiene e saúde no trabalho`; o corpo
começa em `Independentemente do número de trabalhadores…`. O rótulo devia ser
`Cláusula 68.ª - Organização de serviços de segurança, higiene e saúde no trabalho`.

## O que devia acontecer

O título na linha seguinte ao cabeçalho `Cláusula 68.ª` reconhecido como título, como
já acontece noutras cláusulas do mesmo documento (ex.: `Cláusula 17.ª - Constituição da
relação de trabalho e preenchimento de vagas` no EMEM).

## Como reproduzir

```bash
.venv/bin/python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026/convencoes/PRI --codebook codebooks/demo_fase0.yaml \
    --extrator docling --out results/runs/2026/titulos
# procurar "Cláusula 68" no TXT do 2026_PRI_381_CCT-ALT_26957_BTE_31_ACIBARCEL-AEDVC-Independe
# (nome RNC; era 26_PR_005_BTE_31_ACIBARCELOS_IndependenteSector no esquema de 2025 —
# ver ISSUE-0022)
```

## Notas

- `_titulo_candidato` (extractor.py) aceita linhas até 90 caracteres. O título aqui tem
  ~70, logo cabe — mas a linha seguinte ao cabeçalho, no texto do docling, pode já vir
  **fundida** com o corpo (`Organização de serviços … Independentemente do número …`),
  ultrapassando o limite e deixando de ser candidata.
- Se for esse o caso, a correção não é alargar o limite (apanharia frases do corpo), mas
  detetar a fronteira título/corpo: o título não termina em pontuação forte e o corpo
  começa por maiúscula depois de um espaço — padrão que `juntar_linhas` já usa ao
  contrário.
- Verificar se o docling emite o título como item próprio (aí a fusão é do
  `documento_para_texto`) ou já fundido (aí é do PDF). A correção difere.

## O que foi feito

A hipótese da nota 1 estava certa, mas a causa era outra: o docling **não** funde o
título com o corpo — dá os três (`"Cláusula 68.ª"`, o título, o corpo) como itens
`TextItem`/`SectionHeaderItem` distintos (confirmado com `doc.iterate_items()`). A
fusão acontecia depois, em `juntar_linhas`: a marca "é este um título?" usada ali
(`e_titulo`) tinha um limite de **60 caracteres**, diferente e mais apertado do que o
de `_titulo_candidato` (90), usado para a mesma decisão mais à frente no pipeline. O
título da Cláusula 68.ª tem 65 caracteres — cabia em `_titulo_candidato` mas não no
limite duplicado de `juntar_linhas`, pelo que a linha não ficava protegida e juntava-se
ao parágrafo seguinte.

Alinhado o limite de `juntar_linhas` para 90, com uma salvaguarda nova: uma linha que
termine em vírgula nunca é título, porque isso significa que a frase continua (memo 23:
"Cumpre … qualquer organização,\npressupõe respostas coletivas." deixaria de se juntar
sem esta salvaguarda). Testado com os dois casos em
`tests/test_extractor_nuances.py` (`test_titulo_entre_60_e_90_caracteres_nao_se_funde_ao_corpo`
e `test_paragrafo_de_corpo_com_virgula_continua_a_juntar_se`), e verificado de novo no
documento real: `Cláusula 68.ª - Organização de serviços de segurança, higiene e saúde
no trabalho` sai com o rótulo completo.
