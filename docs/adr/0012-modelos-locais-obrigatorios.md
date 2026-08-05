# ADR-0012: modelos locais obrigatórios; remover backend externo Claude CLI

- **Estado:** Aceite
- **Data:** 2026-08-05
- **Decidido por:** CRL (António Fula)

## Contexto

O ADR-0006 definiu que a camada semântica deveria ser local e desligada por omissão. No
entanto, permanecia no código um backend de avaliação que invocava a CLI do Claude. Mesmo
sem estar exposto pela aplicação gráfica ou pelo pipeline normal, esse caminho podia enviar
prompts com conteúdo das convenções para um serviço externo e contradizia a documentação
institucional de funcionamento offline.

O Instituto de Informática poderá, no futuro, decidir implementar uma solução interna. Essa
possibilidade não autoriza entretanto qualquer integração com modelos externos.

## Decisão

- Remover o backend Claude CLI e toda a seleção de backends externos da distribuição.
- Suportar apenas servidores de modelos OpenAI-compatíveis na própria estação, como o LM
  Studio.
- Validar no código o destino do servidor: somente `localhost`, `127.0.0.1` e `::1` são
  aceites. URLs remotas falham antes de uma chamada de rede.
- Manter a camada semântica desligada por omissão e as suas sugestões na faixa `REVER`.

## Consequências

- A aplicação mantém a garantia de não enviar dados para fora da máquina.
- A avaliação semântica requer um modelo local em execução; não requer sessão, credencial ou
  conta num serviço de IA.
- Uma solução interna futura exige novo ADR, avaliação de segurança e implementação
  explícita. Não deve ser reativada por configuração de uma URL externa.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Manter Claude CLI, mas escondido ou documentado | Continua a permitir saída de dados e não satisfaz a restrição atual. |
| Permitir qualquer URL com aviso | Um aviso não impede configuração acidental nem fornece a garantia institucional exigida. |
| Desativar definitivamente toda a camada semântica | Perde a possibilidade de avaliação local útil sem resolver melhor a política de execução. |

## Revisitar quando

O Instituto de Informática aprovar uma solução interna concreta, com arquitetura, controlo de
acesso, tratamento de dados e avaliação de segurança documentados.
