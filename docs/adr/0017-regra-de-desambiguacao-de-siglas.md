# ADR-0017: siglas duplicadas resolvem-se por regra, não por decisão caso a caso

- **Estado:** Aceite
- **Data:** 2026-09-16
- **Decidido por:** coordenação do RNC

## Contexto

As siglas das organizações entram no nome dos ficheiros. No registo da DGERT há
2 403 organizações e, depois de reduzir cada uma à sua sigla, **391 siglas são
pedidas por mais do que uma organização genuinamente diferente**.

Alguém tem de decidir quem fica com a sigla curta e como se chamam as outras. Se
essa decisão for tomada caso a caso, por quem estiver a processar o boletim
nesse dia, o mesmo sindicato aparece como `SNM` num ficheiro e como `SNMot`
noutro. Como o nome do ficheiro é o que liga o documento ao trabalho já feito no
MaxQDA, e como um nome atribuído não se altera, um engano destes não se corrige
— fica.

Duas observações delimitam o problema:

- **Gerações não são conflito.** O SITESE mudou de nome seis vezes e continua a
  ser o SITESE. As coincidências entre gerações da mesma organização são
  inofensivas; distinguem-se pelos dois primeiros componentes do código DGERT.
- **Duas linhagens com a mesma sigla são conflito**, e é esse que é preciso
  resolver — 391 vezes.

## Decisão

**Resolvemos os duplicados por uma escada de candidatos, percorrida por ordem
até encontrar um livre.** Está em `cct/siglas.py`.

```text
1. SIGLA                         SNM
2. SIGLA + palavra distintiva    SNMotoristas
3. SIGLA + concelho da sede      SNMLisboa
4. SIGLA + 1.ª e 2.ª palavras
5. SIGLA + código DGERT          SNM14021       ← garantidamente único
```

As quatro propriedades que a tornam utilizável:

1. **Só mexe no que colide.** Uma sigla que só uma organização usa fica como
   está. O script resolve duplicados; não corrige o registo da DGERT.
2. **Quem fica com o degrau 1 é a linhagem com o código DGERT mais baixo** — a
   mais antiga no registo. Não é quem chegou primeiro ao script, pelo que o
   resultado não depende da ordem de processamento.
3. **A unicidade ignora maiúsculas.** `SNMotoristas` e `SNMOTORISTAS` são o
   mesmo ficheiro no Windows e no macOS.
4. **Uma sigla já atribuída não se reatribui.** O construtor lê o vocabulário
   anterior e fixa o que lá está. Recalcular tudo exige `--reatribuir`, uma
   bandeira explícita.

Detalhes que a tornam operacional:

- a *palavra distintiva* é a primeira palavra da denominação que não seja
  ligação, forma jurídica nem genérico; as que aparecem em meio ramo
  («comercial», «industrial», «regional», «norte») são despreferidas, não
  excluídas — é o que faz a Associação Comercial de Espinho ser `ACEspinho` e
  não `ACEComercial`;
- a sobreposição (`SNM` + `Motoristas` → `SNMotoristas`, e não
  `SNMMotoristas`) aplica-se só a bases de 8 caracteres ou menos e a um máximo
  de 3 caracteres: numa base longa comia o princípio da palavra que distingue;
- quando não cabe nos 20 caracteres, **encurta-se a base, nunca o sufixo** —
  cortar o sufixo devolvia `COMERCIALCONCELeiras`, que já não diz Oeiras nem se
  distingue de Oliveira;
- o construtor **falha** se sobrar um duplicado. Não é um aviso: a escada só
  termina em candidatos livres, pelo que um duplicado significa um defeito da
  regra, e um duplicado silencioso produz dois ficheiros com o mesmo nome.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Decidir caso a caso, com registo numa tabela | É o que se faz hoje, e é o problema: duas pessoas decidem de maneira diferente, e o erro só aparece meses depois |
| Numerar os duplicados (`ACE`, `ACE2`, `ACE3`) | Único e determinístico, mas ilegível: ninguém sabe qual é a associação `ACE2`, e a ordem é arbitrária para quem lê |
| Usar sempre o código DGERT como sigla | Único, estável e ilegível. As siglas estão no nome porque é por elas que a equipa procura |
| Dar a todas as gerações de uma linhagem a sigla da geração mais recente | Foi implementado e recusado: mudava 805 linhas para resolver 391 conflitos, e substituía no registo histórico a sigla que a DGERT publicou por outra. Passou a mexer-se só no que colide |
| Pôr o concelho antes da palavra distintiva | Mais informativo para as associações regionais, que são a maioria dos conflitos, mas dá `SNMLisboa` onde a coordenação pediu `SNMotoristas`. O concelho fica no degrau seguinte |

## Consequências

**Torna fácil:** processar um boletim sem decisões de nomenclatura. A sigla de
cada outorgante já está decidida antes de alguém abrir o índice.

**Torna difícil:** mudar a regra. Alterar a escada renomeia siglas em uso, e
siglas em uso estão em nomes de ficheiro que não mudam. Daí a pinagem por
omissão e a bandeira `--reatribuir`.

**Passa a ser obrigatório manter:** o vocabulário versionado (é ele que fixa as
atribuições), a verificação de que não sobram duplicados, e o teste de que o
resultado não depende da ordem de chegada.

**Custo assumido:** 391 organizações passam a ter uma sigla que não é a que
consta do registo da DGERT. A coluna `sigla_base` guarda a original, e a coluna
`origem_sigla` regista que houve desambiguação, para que a diferença seja
visível e não uma surpresa.

## Revisitar quando

Se a proporção de siglas fabricadas pelo script (as de origem `recurso`) descer
muito — hoje são 1 017 das 2 403 — a maioria dos conflitos desaparece, e vale a
pena verificar se a escada ainda é necessária para lá do degrau 2.

Também se a DGERT passar a publicar acrónimos para as organizações que hoje não
os têm: nesse caso as siglas fabricadas saem de cena e a regra fica a resolver
apenas os conflitos reais entre acrónimos publicados.
