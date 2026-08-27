# Migração de artefactos — agosto de 2026

## Alterações executadas

- `results/xlsx_peritas/` foi eliminado por decisão explícita: continha seis
  exportações de testes não relevantes para a fase actual.
- `results/2025_4_08_issue0004/` passou para
  `results/validated/2025_4_08_issue0004/`.
- `results/2026_4_08/` passou para `results/runs/2026/2026_4_08/`.
- `results/comparacoes/` passou para
  `results/benchmarks/tema-4.08/comparacoes/`; os subdirectórios históricos
  ficaram em `legacy/manual/` e `legacy/auto/`.
- `results/metricas/` passou para
  `results/benchmarks/tema-4.08/metricas/`.

Os ficheiros não foram reescritos. O inventário foi regenerado depois da
operação, permitindo confirmar o número, tamanho e SHA-256 dos artefactos
restantes em [RESUMO.md](../../results/_inventory/RESUMO.md).

Foi também preparado `scripts/manifestar_legado.py`, que cria um manifesto
local para cada conjunto migrado. Estes manifestos registam hashes e origem de
migração, mas assinalam expressamente que a proveniência original é parcial e
que a aprovação humana está pendente.

## Estado e próximos critérios

Os resultados validados ainda precisam de uma evidência humana de aprovação e
os resultados reproduzíveis ainda precisam de manifesto associado à corrida
que os originou. Não se deve promover um conjunto apenas porque está numa pasta
com o nome correcto.

Antes de uma nova migração:

1. gerar o inventário;
2. confirmar que o conjunto não contém revisão humana não identificada;
3. copiar ou arquivar com os hashes preservados;
4. actualizar as referências documentais;
5. correr toda a bateria de testes.

Para reverter apenas a organização de pastas, mover cada conjunto para o
caminho anterior usando a tabela acima; não reconstruir os ficheiros a partir
do conteúdo.
