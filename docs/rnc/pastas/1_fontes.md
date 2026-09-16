# `1_fontes/` — tudo o que entra de fora. IMUTÁVEL.

## O que vive aqui
Os índices do BTE, os boletins completos, os PDF individuais de cada IRCT já
renomeados, e as fontes externas (DGERT, DGAEP, CITE, INE, RAA/RAM, Eurofound).

## O que não vive aqui
Nada que a equipa ou a aplicação produza. Texto extraído → `2_processamento/texto/`.
Catálogo → `0_gestao/catalogo/`. Vocabulários, mesmo os construídos de um export
que está aqui → `0_gestao/vocabularios/`.

## Como se chamam os ficheiros
Os PDF individuais seguem a convenção do
[§5.1 do README](../README.md#51-a-regra) e estão em subpastas por âmbito:

```text
1_fontes/irct/PRI/2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf
1_fontes/irct/SPE/2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-ASPTC.pdf
1_fontes/irct/APU/…                        ← recolhido e catalogado; NÃO processado
```

Índices: `2026_BTE_31_indice.xlsx`. Boletins completos: `2026_BTE_31.pdf`.
Fontes externas mantêm o nome de origem, com a data de recolha à frente:
`20260916_dgert_data-export.xlsx`.

## Quem escreve e quem lê
Escreve a aplicação, na fase 1, e mais ninguém. Lê a aplicação (é daqui que o
pipeline parte) e lê a equipa, para ir ver o original quando o texto extraído
levanta dúvidas.

## Quando sai daqui
**Nunca sai e nunca se edita.** Se um PDF estiver mal — ilegível, truncado, o
documento errado — não se corrige aqui: regista-se na coluna `observacoes` do
catálogo e trata-se a jusante. Um ficheiro corrigido à mão nesta pasta deixa de
corresponder ao que foi publicado, e a partir daí ninguém consegue provar o que
a convenção dizia.
