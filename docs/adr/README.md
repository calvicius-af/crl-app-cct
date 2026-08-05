# Registo de decisões de arquitetura (ADR)

Um **ADR** (*Architecture Decision Record*) é uma página curta que regista **uma** decisão
com consequências duradouras: o que se decidiu, em que contexto, e o que isso implica.

Não é documentação de como o sistema funciona — isso está em
[../arquitetura/](../arquitetura/arquitetura.md). É a memória do **porquê**. Serve para
que, daqui a dois anos, quem olhar para o código não desfaça sem querer uma decisão que
foi tomada por uma boa razão — ou, ao contrário, perceba que a razão já não se aplica e
possa mudar com confiança.

## Regras

- **Um ficheiro por decisão**, numerado em sequência: `NNNN-titulo-em-kebab-case.md`.
- **Nunca se apaga nem se reescreve** um ADR aceite. Se a decisão mudar, escreve-se um
  novo que a substitui, e marca-se o antigo como `Substituído por ADR-NNNN`.
- **Estados**: `Proposto` (em discussão), `Aceite` (em vigor), `Substituído`.
- Escrever no momento da decisão, não no fim do projeto. Cinco minutos e meia página.

## Quando escrever um ADR

Quando a resposta a *"e porque é que isto é assim?"* não é óbvia a partir do código:
escolha de formato ou de tecnologia, um limiar de qualidade, uma restrição assumida de
propósito, uma alternativa razoável que foi rejeitada.

**Não** escrever ADR para: correções de erros, mudanças de implementação sem efeito
externo, ou tarefas a fazer — para isso há [`issues/`](../../issues/README.md) e
[`specs/`](../../specs/README.md). Um ADR diz *porquê*; uma spec diz *o quê construir a
seguir*.

## Decisões registadas

| # | Decisão | Estado |
|---|---|---|
| [0001](0001-sqlite-em-vez-de-neo4j.md) | SQLite como índice do corpus, não um grafo | Aceite |
| [0002](0002-qdpx-refi-qda-como-formato-de-troca.md) | QDPX/REFI-QDA como formato de troca com o MaxQDA | Aceite |
| [0003](0003-codebooks-em-yaml.md) | Codebooks em YAML: configuração é dados, não código | Aceite |
| [0004](0004-fases-desacopladas-por-ficheiros.md) | Fases desacopladas por ficheiros; CLI antes da interface | Aceite |
| [0005](0005-faixas-auto-rever-consolidado.md) | Faixas AUTO/REVER/CONSOLIDADO com limiar de precisão ≥ 0,85 | Aceite |
| [0006](0006-semantica-llm-local-desligada-por-omissao.md) | Camada semântica por LLM local, desligada por omissão | Aceite |
| [0007](0007-guids-deterministicos.md) | GUIDs determinísticos e reutilização do codebook master | Aceite |
| [0008](0008-interface-em-tkinter.md) | Interface gráfica em tkinter, sem dependências extra | Aceite |
| [0009](0009-layout-do-repositorio.md) | Layout do repositório: pacote na raiz, dados fora do Git | Aceite |
| [0010](0010-escolha-do-par-na-diacronia.md) | Escolha do par de versões na comparação diacrónica | Aceite |
| [0011](0011-fluxo-spec-driven.md) | Adoção de um fluxo *spec-driven* para as próximas funcionalidades | Proposto |
| [0012](0012-modelos-locais-obrigatorios.md) | Modelos locais obrigatórios; remover backend externo Claude CLI | Aceite |

Os dez primeiros foram escritos **retroativamente**, em agosto de 2026, a partir do
histórico do desenvolvimento (fases 0 a 5, entre janeiro e julho de 2026). Registam
decisões reais, tomadas na altura indicada em cada ficheiro; o que é retroativo é apenas
o registo. Daqui em diante, escrevem-se no momento.
