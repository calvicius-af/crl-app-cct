# Organização do workspace local

Esta página define o ciclo de vida dos ficheiros que ficam fora do Git. O
objetivo é permitir experiências e corridas repetidas sem confundir cache,
resultados reproduzíveis e trabalho humano que não pode ser perdido.

## Regra principal

Um ficheiro só pode ser apagado automaticamente se estiver classificado como
**cache**. Tudo o que tenha passado pelo MaxQDA, por Excel ou por validação humana
é preservado até uma pessoa confirmar a sua natureza e existir cópia de segurança.

## Estrutura de destino

```text
data/
├── raw/
│   ├── public/                 fontes públicas do BTE
│   └── internal/               exports internos do MaxQDA
├── reference/                  amostras de referência e referências humanas
├── interim/<run-id>/           resultados intermédios regeneráveis
└── cache/<backend>/<modelo>/   cache explicitamente descartável

results/
├── runs/<ano>/<run-id>/
│   ├── manifest.json
│   ├── outputs/
│   ├── logs/
│   └── validation/
├── benchmarks/<tema>/<método>/<versão>/
├── experiments/<tópico>/<run-id>/
├── validated/                  resultados aprovados por pessoas
└── deliveries/                 entregáveis enviados

archive/
├── legacy-code/
├── historical-results/
└── inventory.csv

vendor/
├── sources.lock.yml
└── <projeto>-<commit>/
```

Esta é a estrutura de destino. A primeira migração foi aplicada em agosto de
2026; os conjuntos históricos mantêm a sua proveniência e os novos comandos já
escrevem directamente nos caminhos canónicos.
atuais. A migração é incremental porque alguns caminhos ainda são usados pelo
código e pela documentação.

## Classes de permanência

| Classe | Exemplos | Regra |
|---|---|---|
| Fonte | PDFs, QDC e exports MaxQDA | Preservar e manter cópia de segurança |
| Referência humana | amostras de referência, projetos anotados, Excel revisto | Nunca eliminar automaticamente |
| Resultado validado | QDPX/XLSX aprovados | Preservar com manifesto e evidência |
| Resultado reproduzível | saída integral de uma corrida identificada | Pode ser regenerado depois de validar o manifesto |
| Experiência | provas Docling, rich text, protótipos | Preservar até documentar a conclusão |
| Intermédio | `doc.json`, TXT e anotações de uma corrida | Regenerável a partir dos inputs fixados |
| Cache | respostas LLM e downloads temporários | Descartável por política de retenção |
| Terceiros | clones em `vendor/` | Repor da origem indicada, nunca guardar credenciais |

## Identificador de corrida

Usar um nome legível e único:

```text
2026-08-26T1100Z__tema-4.08__2025__docling
```

Não usar apenas `v2`, `v3` ou `teste`: esses nomes não dizem que código,
inputs ou decisão produziram o conteúdo.

## Manifesto obrigatório

Cada nova execução de `cct.pipeline_tema` escreve `manifest.json` com:

- comando e parâmetros;
- commit Git e indicação de alterações locais;
- Python e plataforma;
- SHA-256 e tamanho dos inputs e outputs;
- início, fim, contagens e problemas da corrida.

O manifesto prova proveniência; não prova qualidade. A aprovação humana fica em
`validation/` e promove o conjunto para `results/validated/`.

Para resultados antigos já migrados, usar `scripts/manifestar_legado.py`.
O manifesto resultante é uma prova de integridade e localização actual; não
substitui os inputs ou o comando original.

## Inventário da instalação atual

```bash
python scripts/inventariar_workspace.py
```

O comando não move nem apaga nada. Cria em `results/_inventory/`:

- `workspace_inventory.json` — detalhe e SHA-256 de cada ficheiro;
- `RESUMO.md` — volume por classificação conservadora.

Antes de qualquer migração:

1. guardar o inventário;
2. confirmar os artefactos marcados como possível trabalho humano;
3. fazer cópia de segurança;
4. mover um conjunto de cada vez;
5. validar hashes e atualizar referências;
6. só depois remover o caminho antigo.

### Classificação aplicada em agosto de 2026

O inventário actual aplica uma decisão conservadora aos resultados existentes:

| Caminho | Classe | Acção futura |
|---|---|---|
| `results/validated/2025_4_08_issue0004/` | resultado validado a preservar | associar manifesto e evidência de validação |
| `results/runs/2026/2026_4_08/` | resultado reproduzível a documentar | confirmar inputs e associar corrida |
| `results/benchmarks/tema-4.08/{comparacoes,metricas}/` | benchmark reproduzível a documentar | guardar método, versão e manifesto |
| `results/benchmarks/tema-4.08/comparacoes/legacy/{manual,auto}/` | exportações históricas | preservar; não usar como destino de novas corridas |
| `data/reference/maxqda/tema-4.08/` | projectos e exports MaxQDA | preservar como referência humana |
| `results/experiments/{docling,qdpx-richtext}/` | experiência a preservar | registar conclusão ou decisão de abandono |
| `results/**/*.mqda`, caminhos `anotad`/`triado` | trabalho humano a preservar | cópia de segurança antes de qualquer migração |

Os resultados que não encaixem nestas regras devem permanecer
`resultado_por_classificar` até existir evidência de corrida, revisão humana ou
decisão de arquivo. O inventário com caminhos, hashes e volumes é a fonte
operacional para essa triagem; não se devem inferir eliminações apenas pelo
nome do ficheiro.

## Retenção sugerida

- cache: 30 dias; remover com `python scripts/limpar_cache.py --apply`;
- intermédios de corridas falhadas: 90 dias; depois desse prazo, eliminar;
- corridas reproduzíveis não promovidas: manter as últimas 3 por combinação
  tema/ano/extrator;
- experiências: até existir conclusão documentada;
- fontes, referências humanas, validados e entregáveis: sem eliminação
  automática.

Todos os ficheiros removidos pela retenção devem constar de um inventário
gerado imediatamente antes da operação. A política só permite eliminar cache e
intermédios regeneráveis; os restantes casos exigem classificação explícita.
