# ADR-0011: adotar um fluxo *spec-driven* para as próximas funcionalidades

- **Estado:** Proposto
- **Data:** 2026-08-04
- **Decidido por:** CRL (António Fula) — por confirmar na prática

## Contexto

As fases 0 a 5 foram desenvolvidas em conversas longas com um assistente de IA, com bons
resultados: 99 testes, cinco gates passados, decisões sólidas. Mas o registo do que se ia
decidir vivia sobretudo na conversa. Cada sessão nova recomeçava do contexto que
conseguisse reconstruir.

Com o repositório organizado, faz sentido passar a um modo em que o trabalho a fazer está
escrito antes de começar, em ficheiros que tanto uma pessoa como um agente conseguem ler.
A intenção declarada é usar as *skills* de Matt Pocock para esse fluxo.

## Decisão (proposta)

Adotar três lugares distintos, com fronteiras claras:

| Lugar | Responde a | Quando se escreve |
|---|---|---|
| `docs/adr/` | **porquê** decidimos assim | quando a decisão é tomada |
| `specs/` | **o quê** vamos construir a seguir, e como se sabe que está feito | antes de implementar |
| `issues/` | **o que está partido ou em falta** | quando se descobre |

O repositório fica preparado — pastas, README e templates —, mas a adoção efetiva só se
confirma quando o primeiro ciclo real (spec → implementação → verificação) estiver
concluído. Até lá, este ADR fica em `Proposto`.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Só GitHub Issues | Excelente para colaboração humana, mas fica fora do repositório: um agente que clona o código não vê nada |
| Só ADR | ADR responde ao *porquê* de decisões tomadas; não serve para descrever trabalho por fazer |
| Nenhuma estrutura, continuar em conversa | É o estado atual, e o custo é conhecido: o contexto perde-se entre sessões |

## Consequências

- Uma barreira de entrada nova: escrever a spec antes de programar. Justifica-se para
  funcionalidades com desenho não trivial, não para correções pequenas.
- `issues/` duplica parcialmente o GitHub Issues. A convenção é: **o GitHub é a fonte de
  verdade** para discussão e estado; `issues/` é o espelho legível dentro do repositório.
- Se ao fim de dois ou três ciclos a estrutura estiver a ser ignorada, este ADR passa a
  `Substituído` e as pastas são removidas — melhor não ter do que ter desatualizado.

## Revisitar quando

Depois do primeiro ciclo completo: se funcionou, passa a `Aceite` com o exemplo apontado.
