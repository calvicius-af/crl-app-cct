# `2_processamento/` — as saídas automáticas da AppCCT

## O que vive aqui
O que a aplicação produz sem intervenção humana: o texto extraído com a
estrutura preservada, as anotações candidatas de cada codebook, e os pacotes
QDPX prontos a importar no MAXQDA.

## O que não vive aqui
Qualquer coisa que uma pessoa tenha editado. A partir do momento em que alguém
mexe num ficheiro, ele passa a ser trabalho de análise → `3_analise/`. Os PDF de
origem ficam em `1_fontes/irct/`.

## Como se chamam os ficheiros
O nome base é herdado do PDF, sem exceção. Muda a extensão:

```text
texto/          2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.txt
                2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.doc.json
precodificado/  2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.anotacoes.json
qdpx/           RNC_2026_lote_03.qdpx
```

Cada corrida deixa também um `manifest.json` com o comando, o *commit*, as
versões, os *hashes* das entradas e saídas, as contagens e os problemas.

## Quem escreve e quem lê
Escreve a aplicação. Lê o MAXQDA, por importação do QDPX, e lê quem estiver a
diagnosticar um problema de extração.

## Quando sai daqui
Quando o lote QDPX é importado no master. A partir daí, esta pasta é
**reconstituível**: apagar e voltar a correr o pipeline sobre os mesmos PDF, com
o mesmo codebook e o mesmo *commit*, dá o mesmo resultado — é para isso que
serve o `manifest.json`. Não se arquiva o que se pode regerar; arquiva-se o
manifesto da corrida que gerou o QDPX que foi importado.
