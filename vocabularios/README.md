# Vocabulários controlados

Listas fechadas que a aplicação consulta para não inventar valores. Todos em
CSV com separador `;` e UTF-8. Versionados com o código: um `git diff` mostra
exatamente o que mudou de um export da DGERT para o seguinte.

Na árvore de dados do RNC vivem em `0_gestao/vocabularios/` — é o mesmo
ficheiro, referenciado, não copiado.

| Ficheiro | O que é | Gerado? |
|---|---|---|
| `siglas_organizacoes.csv` | 2 403 organizações da DGERT com sigla canónica, origem da sigla, tipo, lado e estado | sim |
| `siglas_ambiguas.csv` | 147 siglas usadas por linhagens diferentes; coluna `resolucao` por preencher | sim |
| `actos_negociacao.csv` | 1 860 actos de negociação, com o primeiro e o último ano de cada um | sim |
| `empregadores_ambito.csv` | empregadores com âmbito conhecido (PRI/SPE/APU) | não — escrito à mão |
| `tipos_documento.csv` | o universo de tipos do BTE, com a família e se altera outro documento | não |
| `estados.csv` | os estados por que um documento passa, com quem o move e quando | não |
| `temas.csv` | crosswalk roteiro ↔ macro temas europeus ↔ codebook | não — **incompleto** |

## Regerar os três primeiros

```bash
python scripts/construir_vocabularios.py caminho/para/data-export_….xlsx
```

Corre offline e é determinístico: a mesma entrada dá sempre a mesma saída.

## A coluna `origem_sigla`

Diz de onde veio cada sigla, e é o que impede que um palpite passe por facto:

- `registo` — o acrónimo consta do registo da DGERT;
- `derivada` — extraída da denominação por um padrão fiável (entre parênteses,
  ou a seguir a um travessão);
- `recurso` — **inventada pelo script**, em CamelCase das palavras
  significativas. `Sindicato Nacional dos Motoristas` → `Motoristas`.

**As de origem `recurso` não são carregadas** pela bandeira `--siglas`. Ficam no
ficheiro para se ver o que falta. Promovem-se editando a coluna para `equipa`,
depois de alguém as ter visto e decidido.

## A regra

Se um valor não está no vocabulário, **não se inventa** — acrescenta-se ao
vocabulário, com data e responsável. É o que impede que «Teletrabalho»,
«teletrabalho» e «Tele-trabalho» convivam como se fossem coisas diferentes.

Contexto completo: [docs/rnc/README.md §8](../docs/rnc/README.md#8-vocabulários-controlados).
