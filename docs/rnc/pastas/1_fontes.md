# `1_fontes/`

## O que vive aqui

Tudo o que entra de fora: os índices do BTE, os boletins completos, os PDF individuais de cada IRCT já renomeados, e as fontes externas (DGERT, DGAEP, INE, CITE, Eurofound, RAA e RAM).

## O que não vive aqui

Nada que a equipa ou a aplicação produza. O catálogo fica em `0_gestao/catalogo/`. Os vocabulários ficam em `0_gestao/vocabularios/`, mesmo os construídos a partir de um export que está aqui. As saídas do pipeline ficam em `2_processamento/`.

## Como se chamam os ficheiros

Os PDF individuais seguem a convenção do [ponto 4.1 do README](../README.md#41-a-regra) e estão em subpastas por família e, nas convenções, por âmbito:

```text
1_fontes/irct/convencoes/PRI/2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf
1_fontes/irct/convencoes/SPE/2026_BTE_31_SPE_387_AE-ALT-RECT_47109_CARRISTUR-ASPTC.pdf
1_fontes/irct/convencoes/APU/    recolhido e catalogado, não processado (âmbito)
1_fontes/irct/portarias_extensao/2026_BTE_01_PE_012_0452-2025_27251_ACRAL-CESP.pdf
                                     não processadas (família), sem subdivisão por âmbito
1_fontes/irct/acordos_adesao/2026_BTE_12_AA_412_27251_ABC-CESP.pdf
                                     idem
```

O âmbito subdivide apenas `convencoes/`, porque o que o âmbito decide é se o documento entra no pipeline e nenhuma portaria ou acordo de adesão entra. Os avisos de projeto de portaria não têm ficheiro nesta pasta: ficam registados na coluna `avisos_projeto` do catálogo, associados à portaria correspondente. Ver [ponto 4.6 do README](../README.md#46-famílias-documentais).

Os índices seguem `2026_BTE_31_indice.xlsx` e os boletins completos `2026_BTE_31.pdf`. As fontes externas mantêm o nome de origem, precedido da data de recolha: `20260916_dgert_data-export.xlsx`, `20260916_ine_entidades_s13_2025.pdf`.

## Quem escreve e quem lê

Escreve a aplicação, na fase 1 do ciclo de vida, e mais ninguém.

Lê a aplicação, mas apenas em `irct/convencoes/{AMBITO}/`: o `cct.pipeline_tema` recusa-se a correr se a pasta indicada em `--pdfs` contiver ficheiros de outra família. E lê a equipa, para consultar o original quando o texto extraído levanta dúvidas, ou para ver a portaria que estendeu uma convenção.

## Quando sai daqui

Não sai, e não se edita. Um PDF defeituoso, ilegível, truncado ou trocado, regista-se na coluna `observacoes` do catálogo e trata-se a jusante. Um ficheiro corrigido à mão nesta pasta deixa de corresponder ao que foi publicado, e a partir daí não é possível demonstrar o que a convenção dizia.
