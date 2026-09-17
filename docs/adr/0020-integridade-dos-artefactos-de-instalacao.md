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
ficheiro faltar ou não corresponder. **O que isto apanha é corrupção acidental e
cópia incompleta**, não adulteração deliberada: o manifesto viaja dentro de
`vendor/wheels/`, na mesma pasta que verifica, pelo que quem consiga alterar uma
*wheel* consegue igualmente reescrever o manifesto. O procedimento está descrito em
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
| Manifesto SHA-256 do pacote offline | que os bytes instalados na estação chegaram intactos desde a preparação, apanhando corrupção, truncagem e cópia incompleta | autenticidade: o manifesto viaja com as *wheels* e não é autenticado, pelo que não resiste a adulteração deliberada, nem prova o que o PyPI publicou |
| `--require-hashes` do pip | ambas as anteriores, em qualquer instalação | nada além disso, e ao custo de fixar a árvore transitiva por plataforma |

## Decisão

**A integridade por hashes é responsabilidade do pacote offline, e é aí que já
está. O CI fica-se pelas versões exactas declaradas nas *constraints*.**

Em concreto:

1. O CI instala com `-c requirements/runtime.txt -c requirements/dev.txt`. Não
   usa `--require-hashes` nem ficheiros de hashes por plataforma.
2. A instalação institucional continua a passar pelo par
   `preparar_pacote_offline.py` e `instalar_offline.py`. A verificação de
   SHA-256 é uma prova de **integridade**, contra corrupção e cópia incompleta.
   Não é uma prova de **autenticidade**, e não deve ser apresentada como tal em
   nenhum documento nem perante uma auditoria.
3. O algoritmo é SHA-256 em todo o projeto, através de `cct/proveniencia.py`,
   tal como já acontece nos manifestos de corrida do ADR-0014. Não se introduz
   um segundo mecanismo.

4. **`--require-hashes` também não entra no pacote offline.** Seria possível:
   o preparador tem todas as *wheels* e podia gerar um ficheiro de requisitos
   com um `--hash` por distribuição. Mas esse ficheiro viajaria na mesma pasta,
   com a mesma raiz de confiança do manifesto, pelo que trocaria quem faz a
   verificação sem tornar a verificação mais forte. O único buraco concreto que
   cobriria — uma *wheel* presente na pasta mas ausente do manifesto, que o pip
   podia resolver como dependência sem nunca ter sido conferida — passou a ser
   fechado directamente: o instalador recusa qualquer `.whl` fora do manifesto.
   Reavalia-se quando a lacuna de autenticidade estiver fechada, porque é aí
   que `--require-hashes` passaria a acrescentar alguma coisa.

Das quatro lacunas reconhecidas na primeira redacção deste ADR, três ficaram
fechadas e uma continua aberta, com o trabalho a ser seguido no issue #56:

| Lacuna | Estado |
|---|---|
| O preparador lê `requirements.txt`, com mínimos, e não as *constraints* | **Fechada.** `preparar_pacote_offline.py` e `instalar_offline.py` aplicam `-c requirements/runtime.txt`, mais `dev.txt` quando o pacote inclui o pytest. O manifesto regista que *constraints* foram usadas, e o SHA-256 de cada uma |
| A ausência de `manifesto.json` faz o instalador avisar e continuar | **Fechada.** Passou a parar. A saída explícita `--aceitar-sem-manifesto` existe para pacotes preparados por versões anteriores, e obriga quem a usa a declarar o que está a dispensar |
| Uma *wheel* fora do manifesto podia ser instalada sem ser conferida | **Fechada.** O instalador compara a pasta com o manifesto nos dois sentidos, e recusa ficheiros a mais tal como recusa ficheiros a menos |
| O manifesto não é autenticado | **Aberta.** Está na mesma pasta que as *wheels* e o instalador confia no hash que ele próprio traz, pelo que quem adultere uma *wheel* pode adulterar o manifesto no mesmo gesto. Fechá-la exige assinatura, com a gestão de chaves que implica, ou o SHA-256 do próprio manifesto comunicado por um canal independente e conferido à chegada. É uma decisão institucional, não técnica |

Enquanto a última linha desta tabela estiver aberta, a garantia que o pacote
offline dá é **integridade**, não autenticidade, e é assim que deve ser descrita
em qualquer documento ou resposta a auditoria.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| `--require-hashes` no CI, com ficheiros por plataforma | quatro combinações de sistema e versão, ficheiros gerados que ninguém revê, e a garantia que acrescenta (bytes idênticos) não é a que falta ao CI (versões conhecidas) |
| Um segundo mecanismo de hashes só para dependências | já existe `cct/proveniencia.py`, usado pelos manifestos de corrida e pelo pacote offline; duplicar o mecanismo duplicaria os sítios onde se pode divergir |
| Assinatura criptográfica dos pacotes | é a resposta certa para a lacuna 4 e fica em aberto no issue de seguimento; não entra nesta decisão porque exige gestão de chaves e um procedimento de confiança que o CRL ainda não tem, e decidi-la à pressa aqui seria decidi-la mal |
| Não fazer nada e deixar o issue #30 em aberto | a avaliação pedida ficou feita; deixar o issue aberto esconderia o que está decidido atrás do que falta implementar |

## Consequências

**Torna fácil:** explicar a uma auditoria onde está a prova de integridade e o
que ela cobre, sem depender de quem escreveu o CI.

**Torna difícil:** duas afirmações que ficam interditas até as lacunas fecharem.
Que uma instalação institucional usa exactamente as versões testadas pelo CI,
enquanto a lacuna 1 estiver aberta. E que os bytes instalados são
comprovadamente os aprovados, enquanto a lacuna 4 estiver aberta: o que se pode
dizer é que chegaram intactos.

**Passa a ser obrigatório manter:** a coerência entre as *constraints* em
`requirements/` e o que o preparador do pacote offline consome. Se uma delas
mudar sem a outra, a lacuna 1 agrava-se em silêncio.

**Custo assumido:** o CI não prova integridade de bytes. Prova que as versões
declaradas foram testadas. Quem precisar da prova mais forte usa o pacote
offline, que é o caminho institucional de qualquer modo.

## Revisitar quando

Houver distribuição do produto a terceiros fora do CRL, ou quando uma exigência
de auditoria pedir prova de autenticidade e não apenas de integridade. Nessa
altura há duas peças a decidir em conjunto, e nenhuma delas no CI:
`--require-hashes` dentro do pacote offline, para a lacuna 3, e a autenticação
do manifesto, para a lacuna 4.
