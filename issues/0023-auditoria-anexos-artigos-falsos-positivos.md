# ISSUE-0023: auditoria de anexos e artigos sinaliza falsos positivos

- **Estado:** Resolvida no código — 2026-09-24; falta confirmar na próxima corrida sobre o BTE 31/2026
- **Data:** 2026-09-23
- **GitHub:** [#83](https://github.com/calvicius-af/crl-app-cct/issues/83)
- **Onde dói:** `cct/auditoria.py`, `cct/sanidade.py`

O relatório da corrida BTE 31/2026 sinaliza oito anexos com «tabela fora do
corpo do nó». O `estruturar` fecha o nó folha `anexo` depois do cabeçalho
e guarda o corpo num `bloco` filho; a auditoria verifica apenas o intervalo
do cabeçalho. O QDPX mostra linhas tabulares após os títulos, mas não
permite confirmar sem os PDFs que todas as linhas e células estão corretas.
Nos documentos 384 e 385, o artigo 1.º termina com dois pontos e introduz
cláusulas seguintes; o controlo exige ponto final.

Corrigir a associação aos filhos e o diagnóstico de artigos introdutórios,
com testes que mantenham os avisos para tabela órfã, artigo vazio e texto
truncado. Critérios e plano de verificação em
[intervenção BTE 31/2026](../docs/validacao/intervencao-extracao-bte31-2026-09-23.md).

## Resolução (2026-09-24)

1. `tabelas_esperadas` (`cct/auditoria.py`) passa a ler o anexo com todos os
   seus descendentes na árvore, e não só o nó do cabeçalho. Uma tabela noutro
   sítio do documento continua a dar «fora do corpo do nó».
2. `clausulas_sem_corpo` (`cct/sanidade.py`) aceita o artigo que termina em
   dois pontos a anunciar redação («passam a ter a redação seguinte:») quando
   é seguido de imediato por uma cláusula. Continua a assinalar a cláusula que
   abre uma enumeração sem alíneas e o artigo que anuncia e acaba o documento.
3. Testes com a estrutura real do `estruturar`, em `tests/test_auditoria.py` e
   `tests/test_sanidade.py`; os positivos falham com o código anterior.

**Por confirmar.** Os casos foram construídos a partir das descrições do
relatório e da nota de intervenção, e não dos PDF. Na próxima corrida sobre o
BTE 31/2026, os avisos «fora do nó» de 377, 379, 380, 383, 384, 385 e 386 e os
dos artigos 1.º de 384 e 385 devem desaparecer; se algum ficar, é um caso que
estes testes não cobrem.
