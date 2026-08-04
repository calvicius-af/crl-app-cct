# ADR-0005: faixas AUTO / REVER / CONSOLIDADO, com limiar de precisão medida ≥ 0,85

- **Estado:** Aceite
- **Data:** 2026-07-06
- **Decidido por:** CRL (António Fula)

## Contexto

A codificação automática não é fiável ao ponto de substituir a análise humana: na
avaliação contra o gabarito, a precisão global anda nos 0,57 (ver
[validação](../validacao/README.md)). Entregar 2 700 sugestões indiferenciadas às peritas
seria pior do que não entregar nada — o custo de as filtrar anularia o ganho.

Mas a precisão não é uniforme. Medida código a código, alguns subcódigos acertam quase
sempre (4.08.3, 4.08.5, 4.08.6) e outros são fracos (4.08.1.2, 4.08.2.1).

## Decisão

Os segmentos sugeridos são entregues em **faixas**, que dizem à equipa o que fazer com
cada um:

| Faixa | Critério | O que significa para quem revê |
|---|---|---|
| `AUTO` | precisão **medida no gabarito ≥ 0,85** para aquele código | aceitar com verificação rápida |
| `REVER` | tudo o resto | validar uma a uma |
| `CONSOLIDADO` | texto republicado sem alteração face à versão anterior | pode ser lido por último, ou não ser lido |
| `00 Estrutura` | preâmbulo, assinaturas, marca de texto consolidado | fora da análise temática |

O limiar é aplicado a partir de um ficheiro de métricas (`metricas.json`) produzido pela
avaliação contra o gabarito. **Se não houver métricas, não há faixa `AUTO`** — o sistema
não presume qualidade que não mediu.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Entregar tudo como sugestão indiferenciada | Descarrega nas peritas o trabalho de separar o fiável do duvidoso |
| Aplicar automaticamente as sugestões de alta confiança | Codificação sem supervisão humana num relatório institucional; inaceitável |
| Limiar baseado na confiança devolvida pelo próprio codificador | Autoavaliação não é evidência. O limiar tem de vir de comparação com trabalho humano |

## Consequências

- A faixa `AUTO` é sempre pequena e conservadora (208 a 330 segmentos, contra 1 700 a
  2 400 em `REVER`, nas rondas de 2025).
- Cada tema novo precisa de um gabarito para poder ter faixa `AUTO`. Sem gabarito, o
  sistema funciona na mesma, todo em `REVER`.
- As anotações vindas da camada semântica ([ADR-0006](0006-semantica-llm-local-desligada-por-omissao.md))
  vão **sempre** para `REVER`, independentemente da métrica.

## Revisitar quando

Uma nova geração de métodos elevar a precisão medida a ponto de o limiar de 0,85 deixar
demasiado trabalho manual em cima da mesa.
