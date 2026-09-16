# Vocabulários controlados

Listas fechadas que a aplicação consulta para não inventar valores. Todos em
CSV com separador `;` e UTF-8. Versionados com o código: um `git diff` mostra
exatamente o que mudou de um export da DGERT para o seguinte.

Na árvore de dados do RNC vivem em `0_gestao/vocabularios/` — é o mesmo
ficheiro, referenciado, não copiado.

| Ficheiro | O que é | Gerado? |
|---|---|---|
| `siglas_organizacoes.csv` | 2 403 organizações com sigla canónica **sem duplicados**, sigla de origem, tipo, lado, concelho e estado | sim |
| `siglas_ambiguas.csv` | verificação: fica vazio se a regra funcionou. Um valor aqui é um defeito, não um dado | sim |
| `actos_negociacao.csv` | 1 860 actos de negociação, com o primeiro e o último ano de cada um | sim |
| `empregadores_ambito.csv` | empregadores com âmbito conhecido (PRI/SPE/APU) | não — escrito à mão |
| `tipos_documento.csv` | o universo de tipos do BTE, com a família e se altera outro documento | não |
| `estados.csv` | os estados por que um documento passa, com quem o move e quando | não |
| `entidades_administracao_publica.csv` | 4 241 entidades do sector institucional S.13 (INE), em duas camadas de sinal | sim |
| `temas.csv` | crosswalk roteiro ↔ macro temas europeus ↔ codebook | não — **incompleto** |

## Regerar os três primeiros

```bash
python scripts/construir_vocabularios.py caminho/para/data-export_….xlsx
```

Corre offline e é determinístico: a mesma entrada dá sempre a mesma saída, seja
quem for a correr o script e por que ordem as organizações apareçam.

**Uma corrida normal não mexe nas siglas já atribuídas.** Lê o vocabulário
anterior e fixa o que lá está, acrescentando só as organizações novas — pela
mesma razão por que um nome de ficheiro não muda depois de atribuído. Para
recalcular tudo é preciso `--reatribuir`, que muda siglas em uso.

## A coluna `origem_sigla`

Diz de onde veio cada sigla, e é o que impede que um palpite passe por facto:

- `registo` — o acrónimo consta do registo da DGERT;
- `derivada` — extraída da denominação por um padrão fiável (entre parênteses,
  ou a seguir a um travessão);
- `recurso` — **inventada pelo script**, em CamelCase das palavras
  significativas. `Sindicato Nacional dos Motoristas` → `Motoristas`;
- qualquer das anteriores com `+desambiguada` — colidia com outra organização e
  subiu a escada do ADR-0017. A coluna `sigla_base` guarda a original.

**As de origem `recurso` não são carregadas** pela bandeira `--siglas`. Ficam no
ficheiro para se ver o que falta. Promovem-se editando a coluna para `equipa`,
depois de alguém as ter visto e decidido.

## A lista do INE não decide o âmbito

`entidades_administracao_publica.csv` vem da lista anual do INE das entidades do
sector institucional S.13 (SEC 2010). **Responde a outra pergunta:** o INE
classifica por contas nacionais, o RNC por regime laboral.

O Metropolitano de Lisboa, E.P.E., a RTP e as Infraestruturas de Portugal estão
em S.13 — e são SPE para o RNC, processáveis. A CP, a Carris e a EPAL não estão
em S.13 — e são SPE na mesma. Por isso:

- uma entrada com forma jurídica empresarial propõe **SPE**, nunca APU;
- toda a proposta vinda da lista sai **com aviso**, mesmo quando acerta;
- **a ausência da lista não significa nada.**

```bash
python scripts/construir_entidades_publicas.py Entidades_S13_2025.pdf --ano 2025
```

Contexto: [ADR-0019](../docs/adr/0019-lista-do-ine-como-sinal-de-ambito.md).

## Siglas sem duplicados

391 siglas do registo são pedidas por mais do que uma organização diferente.
Resolvem-se por regra e não caso a caso, para que duas pessoas não decidam de
maneira diferente e o mesmo sindicato não apareça com dois nomes:

```text
1. SIGLA                         SNM
2. SIGLA + palavra distintiva    SNMotoristas
3. SIGLA + concelho da sede      SNMLisboa
4. SIGLA + 1.ª e 2.ª palavras
5. SIGLA + código DGERT          SNM14021       ← garantidamente único
```

Fica com o degrau 1 a linhagem mais antiga no registo, e só se mexe no que
colide. O construtor **falha** se sobrar um duplicado. Detalhe e alternativas
recusadas em [ADR-0017](../docs/adr/0017-regra-de-desambiguacao-de-siglas.md).

## A regra dos vocabulários

Se um valor não está no vocabulário, **não se inventa** — acrescenta-se ao
vocabulário, com data e responsável. É o que impede que «Teletrabalho»,
«teletrabalho» e «Tele-trabalho» convivam como se fossem coisas diferentes.

Contexto completo: [docs/rnc/README.md §8](../docs/rnc/README.md#8-vocabulários-controlados).
