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
[§5.1 do README](../README.md#51-a-regra) e estão em subpastas por **família** e
depois por **âmbito**:

```text
1_fontes/irct/convencoes/PRI/2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf
1_fontes/irct/convencoes/SPE/2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-ASPTC.pdf
1_fontes/irct/convencoes/APU/…      ← recolhido e catalogado; NÃO processado (âmbito)
1_fontes/irct/portarias_extensao/…  ← NÃO processadas (família); sem âmbito
1_fontes/irct/acordos_adesao/…      ← idem
```

O âmbito só subdivide `convencoes/`: numa portaria não decide nada, porque
nenhuma portaria entra no pipeline. **Os avisos de projeto de portaria não têm
ficheiro aqui** — ficam como metadado da portaria correspondente, na coluna
`avisos_projeto` do catálogo.

Só `convencoes/` entra no pipeline temático. Uma portaria de extensão refere-se
a uma convenção mas não é uma: não tem o articulado que a codificação procura, e
codificá-la como se tivesse dá números errados sem dar erro. Ver
[§5.7 do README](../README.md#57-portarias-de-extensão-acordos-de-adesão-e-avisos).

Índices: `2026_BTE_31_indice.xlsx`. Boletins completos: `2026_BTE_31.pdf`.
Fontes externas mantêm o nome de origem, com a data de recolha à frente:
`20260916_dgert_data-export.xlsx`, `20260916_ine_entidades_s13_2025.pdf`.

## Quem escreve e quem lê
Escreve a aplicação, na fase 1, e mais ninguém. Lê a aplicação — mas só de
`irct/convencoes/{AMBITO}/`; apontar o `--pdfs` a outra pasta faz o pipeline
recusar-se a correr. E lê a equipa, para ir ver o original quando o texto
extraído levanta dúvidas, ou para consultar a portaria que estendeu uma
convenção.

## Quando sai daqui
**Nunca sai e nunca se edita.** Se um PDF estiver mal — ilegível, truncado, o
documento errado — não se corrige aqui: regista-se na coluna `observacoes` do
catálogo e trata-se a jusante. Um ficheiro corrigido à mão nesta pasta deixa de
corresponder ao que foi publicado, e a partir daí ninguém consegue provar o que
a convenção dizia.
