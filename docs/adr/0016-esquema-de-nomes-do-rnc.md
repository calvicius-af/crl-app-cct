# ADR-0016: o esquema de nomes do RNC leva o número do BTE

- **Estado:** Aceite
- **Data:** 2026-09-16
- **Decidido por:** CRL (António Fula), a partir da convenção da v2.1 do README
  de estrutura do RNC

## Contexto

A gestão documental do Relatório da Negociação Coletiva fixou, na versão 2.1 do
seu README, uma convenção de nomes de seis campos:

```text
{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_{SIGLAS}
2026_PRI_377_CCT_27251_ACRAL-CESP-STRUP+2.pdf
```

A AppCCT nomeia com outro esquema, o de 2025:

```text
{aa}_{FAM}_{nnn}_BTE_{bb}_{PATRONAL}_{SINDICAL}
26_PR_003_BTE_31_ACRAL_CESP.pdf
```

Não são compatíveis, e a incompatibilidade não é cosmética. Três módulos leem o
nome do ficheiro e falham em silêncio se ele mudar de forma: o
`cct/localizador.py` extrai dele o ano, o número do boletim e os tokens das
partes, para encontrar a convenção certa dentro de um boletim completo; o
`cct/comparar.py` deduz o ano para escolher o par da comparação diacrónica; e o
cruzamento com as variáveis de documento do MaxQDA é feito pelos primeiros
caracteres do nome.

O esquema do RNC resolve problemas reais que o da aplicação não resolve: o
âmbito à cabeça (o que é processável), o número que o próprio boletim usa para
citar o documento, o tipo tal como publicado, e a identidade da convenção ao
longo dos anos. O esquema da aplicação tem uma coisa que o do RNC não tem: o
número do boletim.

## Decisão

**Adotamos o esquema do RNC com o número do boletim acrescentado**, como sétimo
campo, entre o código IRCT e as siglas:

```text
{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}
2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf
```

Operacionalmente:

- o limite é **63 caracteres**, o de nome de documento do MaxQDA, e não os 120
  da v2.1: um nome mais longo é truncado na importação e parte o cruzamento com
  as variáveis de documento. Medido sobre o BTE 31/2026, o nome mais longo dos
  14 tem 59 caracteres;
- quando não cabe, encurtam-se as siglas, nunca o prefixo, e fica registado;
- o `SEQ` é o do índice do BTE (`377/2026` → `377`), não o ordinal interno da
  aplicação;
- as siglas vêm pela ordem do índice, até três, separadas por `-`, com `+N` a
  contar as restantes;
- os dois esquemas convivem. `cct.localizador.interpretar_doc_id` lê ambos e
  devolve sempre `(ano de dois dígitos, número do BTE, tokens das partes)`;
- **nomes já atribuídos não se alteram.** O esquema novo aplica-se ao que entra
  de novo.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Adotar o esquema do RNC tal como está na v2.1, sem o número do BTE | Perde-se a ligação directa ao boletim de origem. Toda a pergunta sobre a proveniência de um ficheiro passaria a obrigar a abrir o catálogo, e o emparelhamento de versões na diacronia deixaria de funcionar a partir do nome |
| Adotar o esquema do RNC e fazer a aplicação ler o número do BTE do catálogo | Acopla cada fase do pipeline a um ficheiro que pode não estar na máquina onde a fase corre. Contraria a invariante das fases desacopladas por ficheiros ([ADR-0004](0004-fases-desacopladas-por-ficheiros.md)): uma fase passaria a precisar de dois ficheiros em vez de um |
| Manter o esquema de 2025 e pôr o âmbito e o código IRCT só no catálogo | A separação física por âmbito deixa de ser possível, e «não conseguimos processar isto» volta a ser uma nota num documento em vez da estrutura das pastas. Era o problema que o âmbito no nome resolve |
| Dois nomes para o mesmo ficheiro — um para o arquivo, outro para a aplicação | Duas cópias divergem. É a regra 3 da higiene do próprio RNC |
| Renomear o corpus de 2025 para o esquema novo | Parte o trabalho já feito no MaxQDA, que referencia os documentos pelo nome. Custo alto, benefício nenhum: a aplicação lê os dois |

## Consequências

**Torna fácil:** saber, olhando para um ficheiro, se é processável, de que
convenção é, de que boletim veio e quem o negociou — sem abrir nada. Agrupar
toda a história de uma convenção com `ls *_27251_*`. Separar fisicamente o que o
pipeline lê do que ainda não sabe processar.

**Torna difícil:** mudar de convenção outra vez. Sete campos com vocabulários
associados são mais superfície de contacto do que dois. Qualquer alteração passa
a exigir decisão de equipa e nova versão do README do RNC.

**Passa a ser obrigatório manter:** os dois esquemas lidos pelo
`cct/localizador.py`, com teste que verifica que todo o nome gerado é aceite; o
limite de 63 caracteres; e a regra de que um nome atribuído não muda.

**Custo assumido:** sete caracteres por nome, e um desvio face à convenção
publicada na v2.1, que obrigou a escrever a v3.0 do README do RNC para o
documentar. O desvio é explícito e justificado no §5.1 desse documento, e não
silencioso.

## Revisitar quando

Se o MaxQDA passar a aceitar nomes de documento mais longos do que 63
caracteres, ou se o cruzamento com as variáveis de documento deixar de ser feito
pelo nome — nesse caso o orçamento de caracteres deixa de ser uma restrição e
vale a pena reconsiderar o que cabe no nome.

Também se o `COD: (IRCT)` deixar de ser estável entre revisões, ao contrário do
que a verificação do §5.3 do README do RNC mostra. Nesse caso o campo sai do
nome e passa a coluna do catálogo, e o resto da convenção mantém-se.
