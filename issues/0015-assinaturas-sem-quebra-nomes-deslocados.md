# ISSUE-0015: o bloco de assinaturas sai sem quebra, com nomes deslocados e sem destaque

- **Estado:** Aberta
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor.py` (`_destacar_assinaturas`, `_inicio_assinaturas`),
  `cct/extractor_docling.py` (`documento_para_texto`, `ordenar_por_leitura`),
  `cct/qdpx.py` (`pontos_de_espacamento`)

## O que acontece

Três sintomas no mesmo bloco — o das assinaturas, no fim (e por vezes a meio) dos
documentos. Nenhum impede a leitura qualitativa, mas todos reduzem a credibilidade da
extração, que é o que se quer demonstrar.

### 1. Sem quebra de linha antes do bloco

O bloco de assinaturas cola-se ao último parágrafo do corpo. Não há linha em branco a
separá-lo, ao contrário do que já acontece com cláusulas e tabelas.

### 2. Nomes em itálico saem fora de ordem

Quando o nome do signatário está em itálico no PDF, o docling emite-o como item
separado e a geometria coloca-o depois da expressão que o qualifica. O resultado é um
nome órfão e uma qualificação sem sujeito:

```text
Pela FESAHT - Federação dos Sindicatos de Agricultura, Alimentação, Bebidas,
Hotelaria e Turismo de Portugal:
José Armando Figueiredo Correia , na qualidade de mandatário. , na qualidade de mandatário.
José Eduardo Pereira Andrade Declaração A FESAHT - ...
```

O correto seria `José Armando Figueiredo Correia, na qualidade de mandatário.` seguido
do nome seguinte, cada um com a sua qualificação.

### 3. "Declaração" da FESAHT não é destacada

No `26_PR_003_BTE_31_AEVP_FESAHT` (e no `26_PR_004`), a FESAHT assina **em representação
de outros sindicatos** e o PDF traz uma `Declaração` a identificá-los. Essa declaração
não é reconhecida como bloco próprio — sai colada ao nome anterior:

```text
José Eduardo Pereira Andrade Declaração A FESAHT - Federação dos Sindicatos de
Agricultura, Alimentação, Bebidas, Hotelaria e Turismo de Portugal, em representação
dos seguintes sindicatos:
- Sindicato dos Trabalhadores na Indústria ...
```

## O que devia acontecer

1. Uma linha em branco antes do bloco de assinaturas, como já há antes de cláusulas e
   tabelas (via `pontos_de_espacamento`, sem tocar no texto canónico).
2. Cada nome seguido da sua qualificação, na ordem do PDF — o nome em itálico pertence
   à linha da qualificação, não depois dela.
3. `Declaração` reconhecida como início de bloco próprio (ou de sub-bloco das
   assinaturas), com quebra antes, para que a representação de terceiros fique legível.

## Como reproduzir

```bash
.venv/bin/python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026 --codebook codebooks/demo_fase0.yaml \
    --extrator docling --out results/runs/2026/assinaturas
# abrir o TXT do 26_PR_003_BTE_31_AEVP_FESAHT no QDPX e ver o fim
```

## Notas

- Os três sintomas partilham a causa: o bloco de assinaturas é tratado como texto
  corrido, sem regras próprias. `_destacar_assinaturas` já o isola num nó `ASSINATURAS`;
  o que falta é (a) espaçamento na exportação, (b) reconstruir a ordem nome+qualificação
  a partir da geometria, (c) reconhecer `Declaração` como marcador.
- O ponto 2 é o mais delicado: exige juntar itens do docling que a geometria separou.
  `ordenar_por_leitura` é o sítio natural, mas a regra é de conteúdo (nome + "na
  qualidade de"), não só de posição — ver `_inicio_assinaturas` para o padrão já usado.
- Relacionada com a ISSUE-0002 (quebras de linha em blocos de título) pela mesma
  família de correções de legibilidade.
