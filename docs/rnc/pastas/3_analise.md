# `3_analise/`

## O que vive aqui

O projeto master do MAXQDA, os exports individuais por integrar, os registos de cada integração, e as comparações diacrónicas entre versões de uma convenção.

## O que não vive aqui

As entregas às peritas ficam em `4_temas/` e os capítulos em `5_redacao/`. Os QDPX de entrada ficam em `2_processamento/qdpx/`.

## Como se chamam os ficheiros

```text
master/           RNC_Dados_2026_master.mqda          um só, sem data
mqex/             2026_C9-SALARIOS_AF_20270315.mqex   tema, iniciais, data
logs_integracao/  20270315_integracao.md
comparacoes/      ACIP.xlsx                           uma por convenção comparada
```

O master não leva data, e é assim que se reconhece o ficheiro ativo. Os `.mqex` levam sempre data, porque são vários e é a data que os ordena.

## Quem escreve e quem lê

Escrevem os técnicos por tema, em `mqex/`, e o responsável de integração, em `master/` e `logs_integracao/`. Lê a coordenação, para gerar as entregas por tema.

Uma só pessoa escreve no master. Dois MAXQDA abertos sobre o mesmo `.mqda` produzem duas versões divergentes sem qualquer indicação.

## Quando sai daqui

Um `.mqex` sai de `mqex/` no momento em que é integrado, e vai para `9_arquivo/`. É isso que faz com que `mqex/` signifique sempre «por integrar».

Cada integração escreve uma linha no log com a data, o ficheiro, quem integrou, o número de segmentos e os conflitos resolvidos. É o único registo que permite reconstruir o master a partir dos `.mqex` arquivados, caso se corrompa.
