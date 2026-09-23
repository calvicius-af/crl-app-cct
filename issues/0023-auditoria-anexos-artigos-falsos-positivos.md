# ISSUE-0023: auditoria de anexos e artigos sinaliza falsos positivos

- **Estado:** Aberta
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
