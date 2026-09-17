# `4_temas/`

## O que vive aqui

Uma pasta por tema ativo, com o que a perita desse tema precisa para escrever o capítulo: os segmentos codificados, a matriz de códigos e um LEIAME com o âmbito do tema, os códigos, o prazo e o contacto.

É a única pasta da árvore em que o tema aparece no nome, e é deliberado: este é o ponto de entrega a pessoas externas, que recebem a sua pasta sem terem de navegar o resto. A razão da regra geral está no [ponto 5 do README](../README.md#5-temas).

## O que não vive aqui

O projeto MAXQDA de onde isto sai fica em `3_analise/master/`. Os capítulos que as peritas escrevem a partir daqui ficam em `5_redacao/`. O livro de códigos fica em `0_gestao/livro_codigos/`.

## Como se chamam os ficheiros

```text
4_temas/C9-SALARIOS/
├── 2026_C9-SALARIOS_segcod_20270401.xlsx
├── 2026_C9-SALARIOS_matriz_20270401.xlsx
└── LEIAME.md
```

O campo de conteúdo pertence a um vocabulário fechado: `segcod`, `matriz`, `vardoc`, `quadros` e `graficos`.

## Quem escreve e quem lê

Escreve a coordenação, gerando a partir do master. Lê cada perita, apenas a sua pasta.

## Quando sai daqui

Estas pastas são geradas e não mantidas. Se no ano seguinte os temas forem outros, apaga-se tudo e regenera-se a partir do `0_gestao/vocabularios/temas.csv`, sem afetar o resto da estrutura. É essa a razão de ser da regra que mantém os temas fora dos nomes das pastas.

Uma pasta de tema nunca se cria à mão. Se um tema não consta do `temas.csv`, o que falta é a linha no `temas.csv`.
