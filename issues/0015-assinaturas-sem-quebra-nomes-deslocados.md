# ISSUE-0015: o bloco de assinaturas sai sem quebra, com nomes deslocados e sem destaque

- **Estado:** Em curso — pontos 1 e 3 resolvidos em 2026-09-19; ponto 2 fica aberto
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
    --pdfs data/raw/bte/bte_2026/convencoes/PRI --codebook codebooks/demo_fase0.yaml \
    --extrator docling --out results/runs/2026/assinaturas
# abrir o TXT do 2026_PRI_379_CCT-ALT_26651_BTE_31_AEVP-FESAHT no QDPX e ver o fim
# (nome RNC; era 26_PR_003_BTE_31_AEVP_FESAHT no esquema de 2025 — ver ISSUE-0022)
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

## O que foi feito

**Pontos 1 e 3 resolvidos:**

1. `pontos_de_espacamento` (`cct/qdpx.py`) passa a espaçar também os nós com
   `rotulo == "ASSINATURAS"`, não só os tipos estruturais
   (`capitulo`/`seccao`/`anexo`/`clausula`/`artigo`). O bloco de assinaturas ganha a
   mesma linha em branco antes que já separava cláusulas e tabelas.
3. `"Declaração"` passa a constar de `_MARCADOR_ESTRUTURAL` (`cct/extractor.py`), o
   que faz `juntar_linhas` manter a quebra antes dela. Deixa de se colar ao nome do
   signatário anterior, e o resto do texto da declaração continua a juntar-se
   normalmente (não vira um cabeçalho a sério — só protege a quebra antes).

Verificado com o pipeline real sobre `2026_PRI_379` e `2026_PRI_380`
(`AEVP-FESAHT`): a linha em branco aparece antes de "Lisboa, 22 de julho de 2026." e
"Declaração" passa a estar na sua própria linha nos dois documentos. Testado em
`tests/test_qdpx_espacamento.py::test_insere_linha_em_branco_antes_das_assinaturas` e
`tests/test_extractor_nuances.py::test_declaracao_nao_se_cola_ao_nome_anterior`.

**Ponto 2 continua aberto.** Investigação com os tipos reais do docling (ver
ADR-relacionado ISSUE-0016) mostrou a causa exata: quando duas qualificações
("na qualidade de mandatário.") vêm num único item do docling que abrange
verticalmente as posições de dois nomes distintos, a ordenação por geometria
(`ordenar_por_leitura`) desempata pela ordem de inserção original do docling, não
pela leitura visual — o item de qualificações fica colado ao primeiro nome, e o
segundo nome aparece isolado mais abaixo, sem a sua qualificação. Uma correção por
padrão de texto (juntar N nomes soltos com N qualificações repetidas na linha
seguinte) foi considerada e descartada nesta ronda: no caso real, o nome em falta
aparece **depois**, colado ao início da "Declaração" que se corrigiu no ponto 3, não
imediatamente a seguir às qualificações — um heurística de linhas adjacentes não
teria apanhado este caso, e uma mais ampla arriscava juntar nomes errados noutros
documentos. Fica como trabalho de investigação geométrica separado, não como
correção de texto.
