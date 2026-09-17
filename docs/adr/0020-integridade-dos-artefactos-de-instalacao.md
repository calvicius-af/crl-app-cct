# ADR-0020: a integridade dos artefactos vive no pacote offline, não no CI

- **Estado:** Aceite
- **Data:** 2026-09-17
- **Decidido por:** coordenação do CRL
- **Refina:** ADR-0014

## Contexto

O issue #30 pedia que se avaliasse o uso de hashes de artefactos em instalações
de release. A pergunta subjacente é simples: como é que alguém prova que o
software instalado numa estação é o mesmo que foi testado e aprovado?

A avaliação encontrou duas coisas que valem a pena separar, porque foram
confundidas na primeira redacção do `SECURITY.md` e essa confusão é a razão de
ser deste ADR.

**Primeira: o projeto já tem integridade verificada por hashes.** O
`scripts/preparar_pacote_offline.py` corre `pip download --only-binary=:all:`,
calcula o SHA-256 de cada *wheel* e escreve `vendor/wheels/MANIFESTO.txt`,
legível por pessoas, e `vendor/wheels/manifesto.json`, legível pela máquina. O
`scripts/instalar_offline.py` recalcula todos os SHA-256 e recusa instalar se um
ficheiro faltar ou não corresponder. O procedimento está descrito em
[`docs/institucional/instalacao-offline.md`](../institucional/instalacao-offline.md)
e testado em `tests/test_pacote_offline.py`. Nada disto precisava de ser criado.

**Segunda: o CI é outro problema.** A matriz cobre Linux e macOS em Python 3.11
e 3.12. Usar `--require-hashes` aí obrigaria a fixar a árvore transitiva
completa para cada uma das quatro combinações, em ficheiros gerados por
plataforma que ninguém revê linha a linha.

As duas perguntas são diferentes porque o adversário é diferente. No CI, a
pergunta é *estamos a testar versões conhecidas?* Na estação institucional, é
*estes bytes são os que foram aprovados?*

| Camada | Garante | Não garante |
|---|---|---|
| `requirements/*.txt` (constraints) | que o CI e uma release usam as versões exactas que foram testadas | que os bytes descarregados são os mesmos de uma corrida para a outra |
| Manifesto SHA-256 do pacote offline | que os bytes instalados na estação são os que foram preparados e aprovados | que os bytes preparados correspondem ao que o PyPI publicou no momento da preparação |
| `--require-hashes` do pip | ambas as anteriores, em qualquer instalação | nada além disso, e ao custo de fixar a árvore transitiva por plataforma |

## Decisão

**A integridade por hashes é responsabilidade do pacote offline, e é aí que já
está. O CI fica-se pelas versões exactas declaradas nas *constraints*.**

Em concreto:

1. O CI instala com `-c requirements/runtime.txt -c requirements/dev.txt`. Não
   usa `--require-hashes` nem ficheiros de hashes por plataforma.
2. A instalação institucional continua a passar pelo par
   `preparar_pacote_offline.py` e `instalar_offline.py`, cuja verificação de
   SHA-256 é a prova de integridade que vale para uma estação.
3. O algoritmo é SHA-256 em todo o projeto, através de `cct/proveniencia.py`,
   tal como já acontece nos manifestos de corrida do ADR-0014. Não se introduz
   um segundo mecanismo.

Ficam reconhecidas três lacunas, que são trabalho identificado e não decisão
adiada:

1. O preparador do pacote offline lê `requirements.txt`, que declara mínimos.
   Um pacote preparado hoje pode, por isso, trazer versões diferentes das que o
   CI testou. As *constraints* introduzidas pelo issue #30 ainda não estão
   ligadas a este caminho.
2. A ausência de `manifesto.json` faz o instalador avisar e continuar, em vez de
   parar. A tolerância existe para pacotes preparados por versões anteriores do
   preparador, mas transforma a garantia em opcional.
3. O manifesto prova que os bytes não mudaram entre a preparação e a instalação.
   Não prova que correspondem ao que o PyPI publicou. É precisamente isso que
   `--require-hashes` acrescentaria, e é a razão para o reavaliar dentro do
   pacote offline, onde o custo por plataforma já foi pago.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| `--require-hashes` no CI, com ficheiros por plataforma | quatro combinações de sistema e versão, ficheiros gerados que ninguém revê, e a garantia que acrescenta (bytes idênticos) não é a que falta ao CI (versões conhecidas) |
| Um segundo mecanismo de hashes só para dependências | já existe `cct/proveniencia.py`, usado pelos manifestos de corrida e pelo pacote offline; duplicar o mecanismo duplicaria os sítios onde se pode divergir |
| Assinatura criptográfica dos pacotes | resolve uma ameaça que este projeto não tem: não há distribuição pública de binários nem terceiros a instalar a partir de uma origem nossa |
| Não fazer nada e deixar o issue #30 em aberto | a avaliação pedida ficou feita; deixar o issue aberto esconderia o que está decidido atrás do que falta implementar |

## Consequências

**Torna fácil:** explicar a uma auditoria onde está a prova de integridade e o
que ela cobre, sem depender de quem escreveu o CI.

**Torna difícil:** afirmar que uma instalação institucional usa exactamente as
versões testadas pelo CI, enquanto a lacuna 1 não estiver fechada. Essa
afirmação não deve ser feita até lá.

**Passa a ser obrigatório manter:** a coerência entre as *constraints* em
`requirements/` e o que o preparador do pacote offline consome. Se uma delas
mudar sem a outra, a lacuna 1 agrava-se em silêncio.

**Custo assumido:** o CI não prova integridade de bytes. Prova que as versões
declaradas foram testadas. Quem precisar da prova mais forte usa o pacote
offline, que é o caminho institucional de qualquer modo.

## Revisitar quando

Houver distribuição do produto a terceiros fora do CRL, ou quando uma exigência
de auditoria pedir prova de que os artefactos instalados correspondem ao que o
índice público publicou. Nessa altura, o sítio para aplicar `--require-hashes` é
o pacote offline, não o CI.
