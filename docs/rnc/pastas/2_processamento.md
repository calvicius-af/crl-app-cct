# `2_processamento/`

## O que vive aqui

Os pacotes QDPX que a aplicação produz, prontos a importar no MAXQDA, e as saídas que os acompanham.

As subpastas `texto/` e `precodificado/` existem na árvore mas **hoje ficam vazias**. O `cct.pipeline_tema` vai do PDF ao QDPX numa só passagem e mantém o texto extraído e as anotações em memória, sem escrever ficheiros intermédios. As duas pastas estão preparadas para receberem esses ficheiros quando a aplicação passar a escrevê-los, e para receberem extrações feitas à mão durante um diagnóstico.

## O que não vive aqui

Qualquer ficheiro que uma pessoa tenha editado. A partir do momento em que alguém lhe mexe, passa a ser trabalho de análise e vai para `3_analise/`. Os PDF de origem ficam em `1_fontes/irct/`.

## Como se chamam os ficheiros

Cada execução do pipeline escreve quatro ficheiros: `projeto.qdpx`, `sugestoes_peritas.xlsx`, `relatorio.txt` e `manifest.json`. O `manifest.json` regista o comando, o commit, as versões, os `sha256` das entradas e saídas, as contagens e os problemas encontrados.

Ao promover uma execução para o arquivo do RNC, o QDPX recebe o nome do lote e o manifesto acompanha-o:

```text
qdpx/    RNC_2026_lote_03.qdpx
         RNC_2026_lote_03_manifest.json
```

Quando as subpastas `texto/` e `precodificado/` passarem a ser usadas, o nome base é herdado do PDF, mudando apenas a extensão: `2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.txt`, `.doc.json` e `.anotacoes.json`.

## Quem escreve e quem lê

Escreve a aplicação. Lê o MAXQDA, por importação do QDPX, e lê quem estiver a diagnosticar um problema de extração.

## Quando sai daqui

Quando o lote QDPX é importado no master. A partir desse momento a pasta é reconstituível: apagar e voltar a executar o pipeline sobre os mesmos PDF, com o mesmo codebook e o mesmo commit, produz o mesmo resultado, e é para isso que serve o `manifest.json`.

Não se arquiva o que se pode regerar. Arquiva-se o manifesto da execução que gerou o QDPX importado no master.
