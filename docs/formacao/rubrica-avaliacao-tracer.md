---
type: project
subtype: rubrica-avaliacao
created: 2026-06-07
tags:
  - formacao
  - avaliacao
  - python
  - cct
estado: rascunho
projeto: "[[Processo de Formação Pragmática]]"
é-parte-de:
  - "[[Processo de Formação Pragmática]]"
norte:
  - "[[Referencial de competências — Python e pipeline CCT]]"
  - "[[Plano do tracer PDF — Python e pipeline CCT]]"
oeste:
  - "[[Análise de necessidades — Python e blueprint CCT]]"
---

# Rubrica de avaliação — tracer PDF Python+CCT

## Função

Esta rubrica avalia se o primeiro tracer PDF → texto/Markdown demonstrou competência suficiente para avançar. O foco não é perfeição técnica; é evidência observável de aprendizagem, qualidade mínima e capacidade de decisão.

## Escala

| Nível | Significado |
|---|---|
| 0 | Não demonstrado |
| 1 | Demonstrado com apoio forte |
| 2 | Demonstrado autonomamente em caso simples |
| 3 | Demonstrado com robustez e justificação |

## Critérios

| Critério | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Execução | Não executa | Executa com instruções incompletas ou erros não compreendidos | Executa comando reproduzível | Executa e adapta a novo input simples |
| Completude textual | Output vazio ou inutilizável | Texto parcial sem diagnóstico | Texto principal presente sem perdas óbvias | Texto completo com amostra verificada contra PDF |
| Preservação estrutural | Estrutura destruída | Estrutura parcialmente legível | Preâmbulo e cláusulas/artigos identificáveis | Estrutura útil para segmentação posterior |
| Rastreabilidade | Não há registo | Há output, mas sem comando ou fonte clara | Comando, input e output registados | Inclui versões, limitações e decisão técnica |
| Qualidade do código/comando | Não compreendido | Copiado sem explicação suficiente | Explicado em termos funcionais | Parametrizado ou preparado para reutilização |
| Gestão de erros | Ignora falhas | Descreve falha sem hipótese | Identifica causa provável e próximo teste | Cria verificação simples ou mitigação |
| Decisão técnica | Não decide | Preferência sem critério | Justifica escolha com trade-offs básicos | Compara abordagens ou explicita razão de diferimento |
| Capitalização | Nada entra no vault | Nota solta sem ligação | Nota ligada ao projeto | Conceito reutilizável integrado em MOC ou nota atómica |

## Critério mínimo de sucesso

Para fechar o primeiro ciclo, é suficiente atingir:

- nível 2 ou superior em Execução;
- nível 2 ou superior em Completude textual;
- nível 2 ou superior em Rastreabilidade;
- pelo menos nível 1 em todos os restantes critérios;
- uma decisão técnica escrita.

## Evidências aceites

- comando executado;
- script Python;
- output `.txt`, `.md` ou `.json`;
- relatório de qualidade;
- comparação com amostra do PDF;
- nota de decisão;
- nota atómica ou MOC atualizado.

## Interpretação pedagógica

Se a rubrica falhar em critérios técnicos, o próximo passo é reforço de Python e bibliotecas. Se falhar em rastreabilidade ou decisão, o problema é metodológico. Se falhar em capitalização, o Processo de Formação Pragmática ainda não está a cumprir a sua função de Personal Knowledge Management.

## Feedback ao processo

Depois da avaliação, registar:

- o que tornou a aprendizagem mais clara;
- onde houve fricção desnecessária;
- que artefacto faltou;
- que parte do processo deve mudar antes do próximo tracer.
