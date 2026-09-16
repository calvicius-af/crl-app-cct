# ADR-0018: cada família documental na sua pasta, e só as convenções no pipeline

- **Estado:** Aceite
- **Data:** 2026-09-16
- **Decidido por:** coordenação do RNC

## Contexto

O BTE publica quatro coisas diferentes sob o mesmo guarda-chuva dos IRCT:

- **convenções** — CCT, ACT, AE, ACEP, e as decisões arbitrais que as
  substituem. Têm articulado: capítulos, cláusulas, números, alíneas;
- **portarias de extensão** (PE, PCT, PRT) — actos do Governo que alargam o
  âmbito de uma convenção a empregadores e trabalhadores que não estão
  filiados nas partes outorgantes;
- **acordos de adesão** (AA) — uma parte adere a uma convenção de que não era
  outorgante;
- **avisos** — projetos de portaria, denúncias, caducidades.

Os três últimos referem-se sempre a uma convenção concreta, mas **não são
convenções**. Uma portaria de extensão tem dois ou três artigos sobre âmbito e
produção de efeitos; não tem cláusula de retribuição, nem de tempo de trabalho,
nem nada do que o livro de códigos procura.

Até aqui a estrutura tratava-os mal, de três maneiras:

1. No esquema de nomes do RNC, a pasta de destino era só o âmbito
   (`1_fontes/irct/PRI/`). Uma portaria ficava lado a lado com as convenções, e
   `pipeline_tema --pdfs 1_fontes/irct/PRI` apanhava-a no `glob("*.pdf")`.
   **Não dava erro: dava números errados.**
2. No esquema de 2025, as três famílias iam todas para uma única pasta
   `extensoes/`, cujo único propósito era ficar fora daquele `glob`. Servia como
   proteção, não como arrumação: um acordo de adesão numa pasta chamada
   «extensões» é uma arrumação que mente.
3. Os acordos de adesão **não eram recolhidos por omissão**. Uma adesão
   publicada no BTE não deixava rasto nenhum — nem uma linha no catálogo a
   dizer que existia.

## Decisão

**A família documental passa a ser um eixo da árvore, cruzado com o âmbito, e
só a família `convencao` entra no pipeline temático.**

```text
1_fontes/irct/
├── convencoes/  PRI/ SPE/ APU/   ← o pipeline lê daqui, e só daqui
├── extensoes/   PRI/ SPE/        PE, PCT, PRT
├── adesoes/     PRI/ SPE/        AA
└── avisos/      PRI/ SPE/        avisos de projeto, denúncias, caducidades
```

Quatro níveis, que é o máximo que a convenção do RNC admite. A família vem antes
do âmbito porque é a distinção que decide o que se faz com o documento; o âmbito
decide se se consegue fazer.

Operacionalmente:

- o vocabulário de tipos ganha `ACEP` e `DA`, que antes não eram classificados e
  caíam como tipo desconhecido;
- `adesao` entra nas famílias recolhidas por omissão;
- o catálogo ganha três colunas: `familia`, `processavel` (que cruza a família
  com o âmbito) e `relacao`/`relacao_alvo`, que dizem **o que** este documento
  faz à convenção a que se refere: `altera`, `estende`, `adere` ou `refere`;
- `pipeline_tema` **recusa-se a correr** se encontrar na pasta de entrada um
  ficheiro cujo nome declare uma família que não seja `convencao`, e a mensagem
  diz para onde apontar. Não avisa e continua: a contaminação de uma contagem
  por cláusula não se nota a jusante.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Manter tudo em `irct/{AMBITO}/` e filtrar pelo tipo no nome | É o que produzia o problema. Depender de toda a gente apontar o `--pdfs` para o sítio certo, todas as vezes, não é uma proteção |
| Manter uma só pasta `extensoes/` para as três famílias não-convenção | Era a solução de 2025. Protege o pipeline mas mente na arrumação, e impede contar adesões separadamente de portarias — que é precisamente o que o relatório faz |
| Família ao nível de `1_fontes/` (`1_fontes/extensoes/`, `1_fontes/adesoes/`) | Poupa um nível, mas separa do `irct/` documentos que, em direito português, são IRCT. A árvore deixaria de dizer a verdade sobre o que é o quê |
| Âmbito antes da família (`irct/PRI/convencoes/`) | Mesma profundidade e mesma informação, mas obriga a varrer três pastas de âmbito para contar as portarias do ano. A pergunta mais frequente é por família |
| Só avisar quando entra uma portaria no pipeline | Um aviso no meio de 277 linhas de saída é um aviso que ninguém lê. E o custo de errar aqui é uma análise inteira |

## Consequências

**Torna fácil:** contar portarias e adesões separadamente das convenções, que é
o que o relatório precisa; saber, pela pasta, o que é corpus e o que é contexto;
e seguir de uma convenção para as portarias que a estenderam, pela coluna
`relacao_alvo`.

**Torna difícil:** apontar o pipeline à pasta errada — deliberadamente.

**Passa a ser obrigatório manter:** o vocabulário de tipos alinhado com
`tipos_documento.csv`, e a recusa do pipeline coberta por teste. Um tipo novo que
o vocabulário não conheça fica em `por_classificar/` e aparece no relatório — não
é silenciado, mas também não é adivinhado.

**Custo assumido:** um quarto nível de pastas, que esgota o limite da convenção,
e a migração das pastas do ciclo anterior. Os nomes de ficheiro não mudam.

## Revisitar quando

Se aparecer uma quinta família — o vocabulário de tipos ainda não foi
confrontado com um ano inteiro de boletins, só com um. Um tipo que não encaixe
nas quatro existentes deve levar a rever este ADR, não a forçá-lo numa família
onde não pertence.

Também quando a aplicação souber processar portarias de extensão. O interesse
analítico existe — o âmbito de uma extensão diz a quem a convenção passou a
aplicar-se, que é matéria de cobertura — mas é outro tipo de extração, não o
articulado por cláusula.
