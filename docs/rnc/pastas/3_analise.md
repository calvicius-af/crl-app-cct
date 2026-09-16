# `3_analise/` — o trabalho no MAXQDA

## O que vive aqui
O projeto master, os exports individuais à espera de integração, os registos de
cada integração, e as comparações diacrónicas entre versões de uma convenção.

## O que não vive aqui
As entregas às peritas → `4_temas/`. Os capítulos → `5_redacao/`. Os QDPX de
entrada → `2_processamento/qdpx/`.

## Como se chamam os ficheiros
```text
master/           RNC_Dados_2026_master.mqda          ← um só, sem data
mqex/             2026_C9-SALARIOS_AF_20270315.mqex   ← tema, iniciais, data
logs_integracao/  20270315_integracao.md
comparacoes/      ACIP.xlsx
```

O master **não leva data**: é assim que se reconhece que é o ativo. Os `.mqex`
levam sempre, porque são vários e é a data que os ordena.

## Quem escreve e quem lê
Escrevem os técnicos por tema (`mqex/`) e o responsável de integração (`master/`
e `logs_integracao/`). Lê a coordenação, para gerar as entregas por tema.

**Uma só pessoa escreve no master.** Dois MAXQDA abertos sobre o mesmo `.mqda`
produzem duas versões divergentes sem aviso.

## Quando sai daqui
Um `.mqex` sai de `mqex/` no momento em que é integrado, e vai para
`9_arquivo/` — nunca fica. É o que faz com que `mqex/` signifique sempre «por
integrar»: se lá está, falta integrar.

Cada integração escreve uma linha no log: data, ficheiro, quem integrou, número
de segmentos, conflitos resolvidos. É o que permite reconstruir o master a
partir dos `.mqex` arquivados se ele se corromper — e é a única coisa que o
permite.
