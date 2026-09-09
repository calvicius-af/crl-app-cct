# ADR-0015: recolha do BTE isolada num módulo, com a rede desligada por omissão

- **Estado:** Aceite
- **Data:** 2026-09-08
- **Decidido por:** CRL (António Fula)

## Contexto

Até aqui a aplicação não fazia um único pedido de rede. Isso não é um pormenor de
implementação: está escrito no [README](../../README.md), está declarado nos
[requisitos técnicos](../institucional/requisitos-tecnicos.md) entregues ao Instituto de
Informática ("§2: Rede — não necessária em operação"), e foi um dos argumentos que
tornou a aplicação instalável numa estação do CRL sem processo de segurança pesado.

A recolha automática do BTE — a primeira linha da lista de trabalho por fazer em
[`specs/`](../../specs/README.md) — obriga a mexer nisso. A alternativa era não a fazer, e
continuar a descarregar 277 convenções por ano à mão.

Havia ainda a tentação de resolver o problema por *scraping*: percorrer o sítio do BTE,
descobrir os números novos, seguir as ligações. Isso teria feito da aplicação um cliente
do HTML de um sítio institucional que muda sem aviso, e teria tornado o comportamento
dependente do que estivesse publicado no momento — impossível de reproduzir e difícil de
testar.

## Decisão

**A rede vive num só módulo (`cct/recolha.py`), está desligada por omissão, e só sabe
descarregar URLs que lhe são dados.**

Em concreto:

1. **Consentimento explícito por corrida.** Sem `--confirmar-rede` (ou
   `CCT_RECOLHA_REDE=1`), nenhum caminho de código abre uma ligação. Por omissão, o
   comando simula e diz o que faria.
2. **Lista de anfitriões permitidos**, verificada antes do pedido e outra vez a cada
   redirecionamento: `bte.dgcp.mtsss.gov.pt`, `bte.gep.msess.gov.pt`,
   `bte.gep.mtsss.gov.pt`. Só `https`.
3. **Sem descoberta.** Os URLs vêm dos ficheiros-índice que a DGERT já fornece por número
   do boletim. A aplicação não navega, não pesquisa, não infere endereços.
4. **Só descarrega.** Pedidos `GET`/`HEAD`, sem cookies, sem autenticação, sem envio de
   dados nossos. O único cabeçalho que identifica o cliente é um `User-Agent` fixo com o
   nome da aplicação.
5. **Sem dependências novas.** `urllib.request` da biblioteca padrão, e não `requests`:
   acrescentar uma dependência obrigaria a rever a tabela de bibliotecas aprovadas nos
   requisitos técnicos, e a instalação em rede fechada faz-se por *wheels*.
6. **Só uma fase toca na rede.** A nomeação, e tudo o que vem a seguir, corre offline e
   pode ser repetida à vontade — como manda o [ADR-0004](0004-fases-desacopladas-por-ficheiros.md).

É o mesmo desenho da camada semântica ([ADR-0006](0006-semantica-llm-local-desligada-por-omissao.md)):
capacidade opcional, isolada, desligada por omissão, com o alcance limitado por código e
não por boa vontade.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| *Scraping* do sítio do BTE | Frágil, irreprodutível, difícil de testar, e transforma a aplicação em cliente de HTML alheio |
| Rede ligada por omissão | Contradiz o que está declarado ao Instituto de Informática, e faz de cada corrida do pipeline um pedido de rede potencial |
| Descarregar dentro do `pipeline_tema` | Misturaria a única fase com rede com a fase mais demorada e mais repetida; e obrigaria a ter rede para reafinar um codebook |
| Usar `requests` | Uma dependência a mais para fazer o que o `urllib` faz; obriga a rever o documento de requisitos |
| Um serviço agendado que descarrega sozinho | Sem supervisão, um erro de índice replica-se em silêncio; e o CRL não tem onde o correr |

## Consequências

- A afirmação "a aplicação não faz pedidos de rede" passa a ter duas exceções, ambas
  opcionais e explícitas: o LLM local em *loopback*, e a recolha do BTE para dois
  anfitriões públicos. Os requisitos técnicos passam a dizê-lo (§5-A).
- Em rede fechada, a recolha pode não funcionar sem autorização de saída para
  `bte.dgcp.mtsss.gov.pt`. Nesse caso a equipa continua a depositar os PDFs à mão em
  `data/interim/recolha/<ano>/<nº>/`, e só corre a nomeação — que é offline. O
  proxy do sistema é respeitado (`HTTPS_PROXY`).
- O registo (`data/registo/registo_bte.jsonl`) passa a ser o único ficheiro que a
  aplicação escreve dentro de `data/` fora de `interim/`. É deliberado: perder o registo
  perde os ordinais atribuídos.
- Os testes não dependem da rede: o transporte é injetado como função.

## Revisitar quando

O CRL passar a receber os documentos por uma via institucional (API da DGERT, pasta
partilhada, depósito) que dispense a descarga — nesse caso a fase de recolha reduz-se a
ler dessa origem, e a rede sai da aplicação outra vez.
