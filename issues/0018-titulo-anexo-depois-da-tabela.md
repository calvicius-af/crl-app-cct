# ISSUE-0018: o título do último anexo sai depois dos dados da tabela

- **Estado:** Resolvida — 2026-09-26 (ver "Resolução"); o que resta é do Docling, que
  não lê a tabela deste anexo (família da ISSUE-0020)
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/extractor_docling.py` (`ordenar_por_leitura`, `documento_para_texto`),
  `cct/extractor.py` (`estruturar`)

## O que acontece

No `26_PR_006_BTE_31_EmpresaMetropolitana_SINTAP`, o título do último anexo é mal lido e
colocado **depois** dos dados da tabela:

```text
... Correspondencia ao Nível Remuneratório da TUR 5

ANEXO III - Maia, 14 de julho de 2026.
Pela Empresa Metropolitana de Estacionamento da Maia, EM:
António Domingos Silva Tiago , presidente do conselho de administração, na qualidade
de mandatário.
```

`ANEXO III - Maia, 14 de julho de 2026.` não é o título do anexo: é a **data de outorga**
(`Maia, 14 de julho de 2026.`) que ficou colada ao rótulo `ANEXO III`, e o conjunto
aparece depois da tabela, quando devia estar antes. O título real do anexo (o mapa
remuneratório) perdeu-se ou ficou antes da tabela.

## O que devia acontecer

- O rótulo `ANEXO III` no início do anexo, com o seu título próprio.
- A data de outorga (`Maia, 14 de julho de 2026.`) no bloco de assinaturas, não colada
  ao rótulo do anexo.

## Como reproduzir

```bash
.venv/bin/python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026/convencoes/SPE --codebook codebooks/demo_fase0.yaml \
    --extrator docling --out results/runs/2026/anexos
# procurar "ANEXO III" no TXT do 2026_SPE_382_AE_47252_BTE_31_EmpresaMetropolitana-SINTAP
# (nome RNC; era 26_PR_006_BTE_31_EmpresaMetropolitana_SINTAP no esquema de 2025 —
# ver ISSUE-0022)
```

## Notas

- Duas causas prováveis, a confirmar:
  1. **Ordem de leitura**: a geometria do docling colocou o item do rótulo depois da
     tabela (`ordenar_por_leitura` ordena por página/coluna/distância ao topo — uma
     tabela que ocupa a página pode empurrar o rótulo para baixo).
  2. **Fusão rótulo+data**: `_normalizar_rotulo` junta o cabeçalho à linha seguinte
     quando esta é `_titulo_candidato`; `Maia, 14 de julho de 2026.` casa com
     `RE_DATA_OUTORGA`, que devia impedir a fusão — verificar por que não impediu.
- Relacionada com a ISSUE-0015 (bloco de assinaturas): a data de outorga pertence lá.
- Relacionada com a ISSUE-0006 (ordem de leitura em layouts difíceis).

## O que foi feito

A causa era a segunda hipótese, não a primeira. Inspecionado com `doc.iterate_items()`:
o `"ANEXO III"` (`SectionHeaderItem`, página 34) já vem **antes** da tabela na ordem do
docling, e a data (`TextItem`, página 35) vem depois — a ordem de leitura estava
correta desde sempre; `ordenar_por_leitura` não é a causa.

A tabela deste anexo em concreto extrai **vazia** (`_linhas_de_tabela` não produz
linhas), pelo que, depois de filtradas as sentinelas de tabela sem conteúdo, "ANEXO
III" fica com "Maia, 14 de julho de 2026." como linha seguinte imediata, sem nada a
separá-las. `_titulo_candidato` não tinha, de facto, nenhum guarda contra
`RE_DATA_OUTORGA` — a nota 2 presumia que existia e "não impedira"; na realidade nunca
foi implementado. Acrescentado o guarda: uma linha que corresponda a `RE_DATA_OUTORGA`
nunca é aceite como título de um cabeçalho.

Verificado com o pipeline real sobre `2026_SPE_382`: `"ANEXO III"` sai agora na sua
própria linha, sem a data colada.

**Fica por resolver, e é por isso que a issue continua "Em curso" e não "Resolvida"**
(apontado na revisão do PR #74): o "O que devia acontecer" pede duas coisas — a data
fora do rótulo (feito) e `"ANEXO III"` **com o seu título próprio** (ainda não). O
título real do anexo (o mapa remuneratório) continua sem aparecer, porque a tabela
desse anexo não produz conteúdo extraível — problema de leitura de tabela, não de
rótulo, relacionado com a família de defeitos da ISSUE-0020. O teste novo
(`test_data_de_outorga_nao_vira_titulo_do_anexo`) cobre só a parte da data; falta um
teste e uma correção para a recuperação do título quando a tabela devolve conteúdo.

## Resolução (2026-09-26)

**O anexo não tem título próprio.** A página 34 do 382 (rodada, a toda a largura) traz
só «ANEXO III» e, logo a seguir, as quatro grelhas de carreiras, cada uma com o seu
nome numa faixa própria («Carreira de Direção Geral», «Carreira de Coordenação», …). O
«título real do anexo (o mapa remuneratório)» que a secção anterior dava por perdido
não existe no PDF: o que devia acontecer é «ANEXO III» sozinho, seguido das tabelas.

**O defeito real estava no extrator por omissão.** Com o pdfplumber, a primeira linha
da tabela colava-se ao rótulo, «ANEXO III - | Carreira de Direção Geral», e saía da
tabela. A regra nova, em `estruturar`: uma linha de tabela com várias células nunca é
o título de um cabeçalho, como já não podia ser um cabeçalho (`_linha_de_tabela`,
partilhada pelas duas decisões).

Medido sobre os textos brutos de 336 PDF (corpus do BTE 31, 2026, 2025 e 31 boletins
de 2021), antes e depois: mudam os rótulos de 9 documentos, e em todos pela mesma
razão, o cabeçalho de uma tabela engolido pelo rótulo de um anexo («ANEXO II - Grupo |
Categorias | Nível salarial | …» na GENERALI de 2025, «ANEXO IV - Níveis | Valor» na
ANIPC, «ANEXO I - H | 870,20 €» num boletim de 2021). As palavras de cada documento
são as mesmas antes e depois; a linha volta à tabela. Teste:
`tests/test_extractor_nuances.py::test_linha_de_tabela_nao_vira_titulo_do_anexo`.

Com o Docling, a data de outorga já não se cola ao rótulo (2026-09-19); a tabela deste
anexo continua a sair vazia, o que é um problema de leitura de tabelas do Docling e não
de rótulos.
