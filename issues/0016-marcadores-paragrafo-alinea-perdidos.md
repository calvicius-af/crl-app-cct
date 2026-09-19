# ISSUE-0016: marcadores de parágrafo e alínea perdidos ou trocados por hífens

- **Estado:** Resolvida — 2026-09-19
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor.py` (`RE_NUMERO_SEM_SEPARADOR`, `RE_MARCADOR_LISTA`,
  `juntar_linhas`, `_subsegmentar_paragrafos`), `cct/extractor_docling.py`
  (`RE_MARCADOR_PROPRIO`, `documento_para_texto`)

## O que acontece

Cinco sintomas, todos na mesma família: o marcador que abre um parágrafo ou uma alínea
perde-se, troca-se por um hífen, ou cola-se ao texto. São o que mais salta à vista numa
leitura de controlo, porque a numeração é a espinha dorsal do articulado.

### 6a. Alíneas g), h), i) do Preâmbulo trocadas por hífens

`26_PR_006_BTE_31_EmpresaMetropolitana_SINTAP`, Preâmbulo: as alíneas saem como `-`
em vez de `g)`, `h)`, `i)`.

### 6b. Alínea n) sem quebra a separar da m)

`26_PR_006`, Preâmbulo: a alínea `n)` cola-se ao fim da `m)`.

### 7. Número de parágrafo colado ao texto

`3- A EMEM deve…` sai como `3A EMEM deve…`. A regra `RE_NUMERO_SEM_SEPARADOR` existe
para repor o hífen, mas não apanha todos os casos (exige maiúscula a seguir e início de
linha).

### 8. Números truncados com hífen de lista

`26_PR_006`, Cláusula 17.ª:

```text
2- Os requisitos gerais de admissão, são os seguintes:
- 3Idade igual ou superior a 18 anos;
- 4Habilitações literárias e/ou profissionais exigidas para a função;
- 5Inexistência de impedimento legal;
- 6Aptidão psicofísica para o desempenho da função, apurada em exame médico;
```

O correto é `3- Idade…`, `4- Habilitações…`, etc. O docling emitiu cada item como
`ListItem` e o `- ` foi acrescentado por cima de um número que já lá estava, sem o
separador.

### 10. Alíneas das cláusulas 42.ª e 43.ª trocadas por hífens

`26_PR_007_BTE_31_IBERCOURIER_SNTCT`:

```text
2- Para efeitos de recrutamento interno, a empresa dará conhecimento ... dos seguintes elementos:
- Designação e conteúdo funcional da categoria e sua remuneração base;
- Local e horário de trabalho;
- Requisitos a satisfazer pelos candidatos;
- Data-limite de apresentação de candidaturas.
```

As alíneas eram `a)`, `b)`, `c)`, `d)`.

### 11. Cláusula 6.ª do AWP mal extraída

`26_PR_008_BTE_31_AWP_STAS`: números e alíneas da cláusula 6.ª saem desalinhados —
`- 2Sem prejuízo do empregador…` (hífen + número colado), e a estrutura de alíneas
perde-se.

## O que devia acontecer

O marcador original do PDF preservado: `3- `, `a) `, `g) `, `n) ` — nunca substituído
por `- ` nem colado ao texto. Quando o docling emite um `ListItem` cujo texto já começa
por número/alínea, não se acrescenta `- ` (a regra `RE_MARCADOR_PROPRIO` existe mas não
cobre `3Idade`, em que o número perdeu o separador).

## Como reproduzir

```bash
.venv/bin/python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026 --codebook codebooks/demo_fase0.yaml \
    --extrator docling --out results/runs/2026/marcadores
# ver o Preâmbulo e a Cláusula 17.ª do 26_PR_006, e as cláusulas 42.ª/43.ª do 26_PR_007
```

## Notas

- Causa provável comum: o docling entrega `ListItem` com o marcador já no texto, e o
  `documento_para_texto` (L207) acrescenta `- ` quando `RE_MARCADOR_PROPRIO` não casa.
  `RE_MARCADOR_PROPRIO` exige separador (`\d+\s*[-–—.)]`); `3Idade` não tem, logo cai no
  ramo que acrescenta `- `.
- O ponto 7 (`3A EMEM`) é o mesmo defeito visto do lado do pdfplumber:
  `RE_NUMERO_SEM_SEPARADOR` só repõe o hífen em início de linha e antes de maiúscula.
- Os pontos 6a, 10 e 11 (alíneas → hífen) podem ter a mesma raiz que o ponto 8: o
  marcador de alínea do docling chega como `ListItem` sem o `a)` no texto, e o `- ` é
  acrescentado. Confirmar caso a caso antes de generalizar a correção.
- Testes a estender: `tests/test_extractor_docling.py` (marcadores de lista) e
  `tests/test_extractor_f1b.py` (numeração).
- Nomes de ficheiro atualizados para o esquema RNC (ISSUE-0022): `26_PR_006` →
  `2026_SPE_382_AE_47252_BTE_31_EmpresaMetropolitana-SINTAP`; `26_PR_007` →
  `2026_PRI_383_AE_47253_BTE_31_IBERCOURIER-SNTCT`; `26_PR_008` →
  `2026_PRI_384_AE-ALT_47120_BTE_31_AWP-STAS`.

## O que foi feito

Investigação com o docling real (`doc.iterate_items()`) confirmou três causas
distintas, não uma só:

1. **6a e 10** (alíneas → hífen): o docling separa o marcador para o campo próprio
   `ListItem.marker` (ex.: `'g)'`) e deixa `item.text` **sem** o marcador — não é um
   caso de "marcador já no texto sem separador" como a nota original supunha.
   `documento_para_texto` agora usa `item.marker` quando presente, em vez de assumir
   sempre `- `.
2. **8 e 11** (número colado, `3Idade…`): confirmado — `ListItem.marker` vem vazio e o
   número está mesmo colado ao texto. Nova regra `RE_NUMERO_COLADO_LISTA` repõe o
   separador (`3Idade` → `3- Idade`) em vez de acrescentar `- ` por cima.
3. **6b** (`n)` colada a `m)`): causa diferente das outras — o docling funde as duas
   alíneas no mesmo `TextItem`, sem as separar em items distintos. Nova regra
   `RE_ALINEA_FUNDIDA` (estreita: `; letra) Maiúscula`) repõe a quebra de linha.
4. **7** (`3A EMEM` do lado pdfplumber): `RE_NUMERO_SEM_SEPARADOR` exigia maiúscula
   **seguida de minúscula**, o que falhava quando a palavra colada era uma sigla ou
   artigo de uma letra (`3A EMEM`, em que "A" é seguido de espaço). Relaxada para só
   exigir a maiúscula.

Testado com casos novos em `tests/test_docling_integracao.py` (tipos reais do
docling) e `tests/test_extractor_nuances.py`, e verificado de novo com o pipeline
real sobre os três documentos: `2026_SPE_382` (alíneas g/h/i e m/n do Preâmbulo,
Cláusula 17.ª), `2026_PRI_383` (cláusulas 42.ª/43.ª) e `2026_PRI_384` (Cláusula 6.ª) —
todos corrigidos.
