# `4_temas/` — as entregas às peritas

## O que vive aqui
Uma pasta por tema ativo, com o que a perita desse tema precisa para escrever o
capítulo: os segmentos codificados, a matriz de códigos e um LEIAME com o
âmbito, os códigos, o prazo e o contacto.

**É a única pasta da árvore em que o tema aparece no nome**, e é deliberado:
este é o ponto de entrega a pessoas externas, que recebem a sua pasta e não
devem ter de navegar o resto. O porquê da regra geral está no
[ponto 5 do README](../README.md#5-temas).

## O que não vive aqui
O projeto MAXQDA de onde isto sai → `3_analise/master/`. Os capítulos que as
peritas escrevem a partir daqui → `5_redacao/`. O livro de códigos →
`0_gestao/livro_codigos/`.

## Como se chamam os ficheiros
```text
4_temas/C9-SALARIOS/
├── 2026_C9-SALARIOS_segcod_20270401.xlsx
├── 2026_C9-SALARIOS_matriz_20270401.xlsx
└── LEIAME.md
```

`{CONTEUDO}` vem de um vocabulário fechado: `segcod`, `matriz`, `vardoc`,
`quadros`, `graficos`.

## Quem escreve e quem lê
Escreve a coordenação, gerando a partir do master. Lê cada perita — só a sua
pasta.

## Quando sai daqui
**Estas pastas são geradas, não mantidas.** Se no ano seguinte os temas forem
outros, apaga-se tudo e regenera-se a partir do `0_gestao/vocabularios/temas.csv`.
Nada mais na estrutura é afetado, e é essa a razão de ser da regra dos temas fora
das pastas.

Uma pasta de tema nunca se cria à mão. Se um tema não está no `temas.csv`, o que
falta é a linha no `temas.csv`.
