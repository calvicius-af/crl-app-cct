---
type: project
subtype: avaliacao-tecnica
created: 2026-08-21
tags:
  - formacao
  - docling
  - extracao
  - hierarquia
estado: concluido
projeto: "[[Processo de Formação Pragmática]]"
é-parte-de:
  - "[[Aprender Docling — oficina]]"
---

# Avaliação — `docling-hierarchical-pdf`

Inspeção do pacote [krrome/docling-hierarchical-pdf](https://github.com/krrome/docling-hierarchical-pdf)
(v0.1.8, MIT, commit `d6ba982` de 2026-04-24) para responder a uma pergunta:
**serve, ou adapta-se, ao problema de extrair a hierarquia das convenções coletivas do BTE?**

## Resposta curta

**Não serve tal como está. Adapta-se bem, com cerca de 25 linhas de código.** E a parte
mais valiosa do pacote para o AppCCT não é a que o README anuncia.

## O que o pacote faz

É um pós-processador que corre *depois* do Docling e corrige a hierarquia de cabeçalhos,
por três vias, nesta ordem:

1. **Marcadores do PDF** (índice embutido), lidos com `pymupdf`.
2. **Numeração** — árabe, romana e letras, com *parsers* próprios.
3. **Estilo visual** — agrupamento por tamanho de letra e negrito/itálico, com DBSCAN
   (`scikit-learn`).

São ~1000 linhas de Python em 6 módulos. A API é uma linha:
`ResultPostprocessor(result).process()`, que altera `result.document` no lugar.

## Porque é que não serve tal como está

Os *parsers* de numeração **exigem que a numeração esteja no princípio do texto**. Os
cabeçalhos das convenções portuguesas começam pela palavra, não pelo número. Medido
correndo os *parsers* do pacote directamente:

| Cabeçalho | romano | letra | numérico |
|---|---|---|---|
| `CAPÍTULO I` | `[]` | `[]` | `[]` |
| `CAPÍTULO XII` | `[]` | `[]` | `[]` |
| `Cláusula 1.ª` | `[]` | `[]` | `[]` |
| `Cláusula 1.ª — Âmbito` | `[]` | `[]` | `[]` |
| `SECÇÃO I` | `[]` | `[]` | `[]` |
| `ANEXO II` | `[]` | `[]` | `[]` |
| `1.3.2 Form der summarischen Anmeldung` | `[]` | `[]` | `[1, 3, 2]` |
| `II. Methods` | `[2]` | `[]` | `[]` |

**Nenhum** cabeçalho estrutural de uma convenção é reconhecido. Não é uma questão de
língua — `CHAPTER I`, em inglês, também falha: o pacote foi feito para documentos cujos
títulos são `1.3.2 Alguma coisa`, não `CAPÍTULO I`.

Consequência em cadeia: com 0 % de cabeçalhos numerados, o pacote desiste da via da
numeração (`prop_numbered <= 0.3`) e cai inteiramente na via do **estilo visual**. Isso
funciona *se* os tamanhos de letra diferirem — mas nas convenções do BTE `CAPÍTULO` e
`Cláusula` são frequentemente ambos a negrito e do mesmo tamanho. Testado com o construtor
de hierarquia real do pacote:

```
tamanhos distintos (CAPÍTULO 11pt, Cláusula 9,5pt)   →   hierarquia correcta
tamanhos iguais    (tudo 8,5pt negrito)              →   lista completamente plana
```

## Riscos adicionais, medidos

**Promoção indevida de parágrafos a cabeçalhos.** O pacote converte itens de lista com
numeração em cabeçalhos (`_is_list_item_header`). Numa convenção isso apanha o corpo do
texto, não a estrutura:

| Texto | Decisão do pacote |
|---|---|
| `1 — O presente contrato coletivo obriga as empresas` | **promovido a cabeçalho** |
| `2 — O período normal de trabalho semanal é de 40 horas` | **promovido a cabeçalho** |
| `a) Os trabalhadores em regime de turnos rotativos` | **promovido a cabeçalho** |

Sem adaptação, os números e alíneas de cada cláusula passariam a cabeçalhos — o oposto do
que o AppCCT precisa. A adaptação proposta abaixo elimina este risco, porque só reconhece
numeração precedida de `Cláusula`/`Artigo`.

## Compatibilidade com a versão actual do Docling

O pacote declara `docling>=2.53.0` e toca em interiores do Docling. Verificado contra o
**docling 2.121.0** instalado:

- Os módulos importam sem erro.
- Todos os atributos internos usados continuam a existir: `ConversionResult.pages`,
  `.input`, `Page.predictions`, `Page.size`, `LayoutPrediction.clusters`, `Cluster.cells`,
  `Cluster.label`, `SectionHeaderItem.level`, `ListItem.orig`.
- `font_name` **não** existe em `TextCell`, mas existe em `PdfTextCell` — que é o tipo
  usado nos PDFs de origem digital, como os do BTE. A deteção de negrito/itálico funciona,
  portanto, no nosso caso. Depende de o nome da fonte no PDF seguir a convenção
  `Fonte-Bold`; se o BTE usar outra nomenclatura, a deteção falha em silêncio (só fica o
  tamanho de letra).

Não foi possível correr uma conversão ponta a ponta neste ambiente (sem acesso à rede para
os modelos do Docling), pelo que **a compatibilidade está verificada ao nível da API, não
em execução**.

## A adaptação

Basta ensinar as palavras portuguesas aos *parsers* — remover o prefixo antes de procurar a
numeração. Primeira tentativa, ingénua:

```python
RE_PT = re.compile(r"^(CAP[IÍ]TULO|T[IÍ]TULO|SEC[ÇC][AÃ]O|ANEXO|Cl[aá]usula|Artigo)\s+",
                   re.IGNORECASE)
```

Resultado medido — quase certo, com um defeito:

```
CONTRATO COLETIVO ENTRE A ASSOCIAÇÃO X E O SINDICATO Y
CAPÍTULO I
  Cláusula 1.ª
  Cláusula 2.ª
CAPÍTULO II
  Cláusula 3.ª
  Cláusula 4.ª
    ANEXO II        ← errado: aninhado dentro da Cláusula 4.ª
```

`ANEXO II` colide com `CAPÍTULO II` — ambos dão romano `[2]`. Os anexos são uma série de
numeração própria, que recomeça. Corrigido tratando-os em separado:

```python
RE_CAP   = re.compile(r"^(CAP[IÍ]TULO|T[IÍ]TULO)\s+", re.IGNORECASE)
RE_ANEXO = re.compile(r"^ANEXO\s+", re.IGNORECASE)
RE_CLAU  = re.compile(r"^(Cl[aá]usula|Artigo)\s+", re.IGNORECASE)

def roman_pt(texto):
    t = texto.strip()
    if RE_CAP.match(t):
        return _orig_roman(RE_CAP.sub("", t))
    if RE_ANEXO.match(t):                      # série própria: desloca para não colidir
        base = _orig_roman(RE_ANEXO.sub("", t))
        return [100 + base[0]] if base else [100]
    return []

def num_pt(texto):
    t = texto.strip()
    return _orig_num(RE_CLAU.sub("", t)) if RE_CLAU.match(t) else []
```

Resultado medido, já com tamanhos de letra **todos iguais** — ou seja, sem depender de
nenhum sinal visual:

```
CONTRATO COLETIVO ENTRE A ASSOCIAÇÃO X E O SINDICATO Y
CAPÍTULO I
  Cláusula 1.ª
  Cláusula 2.ª
CAPÍTULO II
  Cláusula 3.ª
  Cláusula 4.ª
ANEXO I
ANEXO II
```

É exactamente a hierarquia que o AppCCT reconstrói hoje à custa de regex sobre texto plano.

**Nota de implementação:** os *parsers* são importados por nome em dois módulos
(`hierarchy_builder` e `postprocessor`), por isso a adaptação certa é um *fork* do módulo
`parsers.py`, não um remendo em tempo de execução.

## O que este pacote tem que o Docling não tem

Desde a v2.121 o Docling traz inferência de hierarquia própria
(`PdfPipelineOptions.heading_hierarchy_options`, desligada por omissão), que cobre as
mesmas três vias — e até reconhece palavras-chave, embora só em inglês. À primeira vista o
pacote seria redundante. Não é, por uma diferença que está escrita no código-fonte de
ambos:

> **Docling:** *"o modelo apenas reescreve níveis de cabeçalho — nunca acrescenta, remove
> ou reordena itens."*
>
> **`docling-hierarchical-pdf`:** reordena a árvore. *"Quaisquer itens que se sigam a um
> cabeçalho passam a ser filhos desse cabeçalho."*

Ou seja: o Docling diz-te que a `Cláusula 3.ª` é de nível 2, mas o texto dos seus números
continua ao lado dela, não dentro dela. Este pacote **aninha o corpo dentro da cláusula**.
Para quem quer aproximar-se do AKN4EU — em que o conteúdo vive dentro do elemento a que
pertence — é essa a peça que falta, e é a única implementação livre que a faz.

## Recomendação

**Adaptar, e adaptar pela razão certa.** O valor não está na inferência de níveis (as
regex do `cct/extractor.py` já fazem isso melhor para português, e continuarão a fazer);
está no **motor de reestruturação da árvore**, que o AppCCT não tem e que o Docling não
oferece.

Duas vias possíveis, por ordem de esforço:

1. **Mínima** — *fork* de `parsers.py` com as regras portuguesas acima (~25 linhas),
   usar o pacote como está. Rápido, e já dá a hierarquia certa mais o aninhamento.
2. **Melhor alinhada com o AppCCT** — usar só o `ResultPostprocessor` como motor de
   reestruturação, alimentando-o com a hierarquia que as regex do `cct/extractor.py` já
   produzem, em vez da inferida. Evita duplicar conhecimento de domínio em dois sítios e
   mantém as regex — que estão validadas contra uma amostra de referência humana — como fonte única da
   verdade sobre o que é uma cláusula.

Em qualquer das vias, a camada de validação de `docs/validacao/` continua a ser necessária.

## Custo de adoção

| Item | Peso |
|---|---|
| O pacote em si | ~1000 linhas, MIT, 6 módulos |
| Dependências novas | `pymupdf`, `scikit-learn`, `numpy` — além do que o Docling já traz |
| Manutenção | Autor único, última versão 2026-04-24. Depende de interiores do Docling, que mudam entre versões — risco real de partir numa actualização |

O risco de manutenção é o argumento mais forte para a via 2: usar uma superfície pequena do
pacote (ou copiar o algoritmo de reestruturação, ~80 linhas, dando o devido crédito MIT) em
vez de depender do todo.

## Por verificar

- [ ] Correr a adaptação num PDF real do BTE, ponta a ponta. Tudo acima foi medido com os
      módulos do pacote a sério, mas com cabeçalhos simulados — falta a prova no corpus.
- [ ] Confirmar se os PDFs do BTE trazem marcadores/índice embutido. Se trouxerem, a via 1
      do pacote (a mais fiável) entra em jogo e nada disto é preciso.
- [ ] Medir se `CAPÍTULO` e `Cláusula` têm mesmo o mesmo tamanho de letra nos PDFs reais —
      determina se a via do estilo, sozinha, seria suficiente.
- [ ] Verificar o comportamento com cláusulas numeradas por extenso ("Cláusula primeira"),
      que os *parsers* não apanham em caso nenhum.
