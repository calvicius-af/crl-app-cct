# SPEC-0001: recolha automática do BTE e nomeação dos ficheiros

- **Estado:** Implementada
- **Data:** 2026-09-08
- **Autoria:** CRL (António Fula)
- **Decisões relacionadas:** [ADR-0015](../docs/adr/0015-recolha-em-rede-desligada-por-omissao.md),
  [ADR-0004](../docs/adr/0004-fases-desacopladas-por-ficheiros.md),
  [ADR-0009](../docs/adr/0009-layout-do-repositorio.md)

## Problema

O corpus entra hoje na aplicação à mão. Alguém abre o sítio do BTE, descarrega os PDFs
das convenções publicadas, e renomeia-os um a um para o esquema
`25_PR_003_BTE_02_ACIP_FESAHT.pdf`. Em 2025 foram **277 convenções**; a cada número do
boletim repete-se o mesmo trabalho, com três consequências observadas no ciclo anterior:

- **duplicação** — o mesmo documento descarregado outra vez, com nome diferente, em
  pastas diferentes (o problema nº 1 do diagnóstico em `README_Estrutura_RNC_2026`);
- **nomes inconsistentes** — e como o `cct/localizador.py`, o `cct/comparar.py` e o
  cruzamento com as variáveis do MaxQDA leem o nome do ficheiro, um nome fora do esquema
  não parte com estrondo: parte em silêncio, deixando a convenção sem metadados;
- **omissões** — um número do boletim que ninguém descarregou não deixa rasto nenhum.

## Objetivo

Que o corpus de um ano entre na aplicação sozinho, a partir dos ficheiros-índice que a
DGERT fornece por número do BTE, com cada documento descarregado **uma só vez** e com um
nome que o resto do pipeline já sabe ler.

## Não-objetivos

- **Não** faz *scraping* do sítio do BTE nem descobre números novos sozinha: a lista vem
  sempre de um ficheiro-índice depositado pela equipa (ver ADR-0015).
- **Não** recorta convenções de dentro de um número completo do boletim — isso já é o
  `cct/localizador.py`, e continua a ser usado para os anos históricos.
- **Não** classifica setor público/privado: o token do nome é sempre `PR`, como em 2025.
- **Não** decide siglas por si em casos difíceis: deriva-as e **assinala** as que exigem
  confirmação humana.
- **Não** liga a rede por omissão, em nenhuma circunstância.

## Comportamento

Duas fases desacopladas por ficheiros, encadeáveis num só comando.

```
data/raw/indices/BTE31_2026.xlsx          ficheiro-índice fornecido pela DGERT
        │
        │  1. RECOLHA          cct/recolha.py     (a única fase que toca na rede)
        ▼
data/interim/recolha/2026/31/00260057.pdf  PDF com o nome de origem, imutável
        │
        │  2. NOMEAÇÃO         cct/nomeacao.py    (offline, repetível)
        ▼
data/raw/bte/bte_2026/26_PR_003_BTE_31_ACRAL_CESP.pdf
data/raw/bte/bte_2026/extensoes/26_PE_001_BTE_31_….pdf
        │
        ▼  o pipeline de sempre (python -m cct.pipeline_tema --pdfs data/raw/bte/bte_2026)
```

Entre as duas fases, e persistente para lá delas, está o **registo**
(`data/registo/registo_bte.jsonl`): uma linha JSON por documento, com a proveniência, o
estado da descarga, o `sha256` e o nome atribuído. É o registo — e não a existência do
ficheiro em disco — que responde à pergunta "isto já foi descarregado?".

### Fase 1 — recolha

```bash
python -m cct.recolha --indices data/raw/indices            # simulação: não liga a rede
python -m cct.recolha --indices data/raw/indices --confirmar-rede
```

1. Lê cada `.xlsx` da pasta de índices (cabeçalhos reconhecidos por normalização, não por
   posição de coluna).
2. Classifica cada linha numa **família**: `convencao` (CCT/ACT/AE e variantes `-ALT`,
   `-RECT`), `extensao` (PE, PCT), `aviso`, `adesao`. As famílias fora de
   `--familias` ficam registadas como ignoradas, com o motivo; os tipos que a tabela não
   conhece são listados no relatório para a equipa decidir.
3. Para cada documento aceite, decide se descarrega:
   - já no registo, ficheiro presente e `sha256` igual → **`ja_existente`**, sem pedido de rede;
   - já no registo, com `ETag`/`Last-Modified` → pedido condicional; `304` → **`inalterado`**;
   - caso contrário → descarrega.
4. Escreve o PDF com o **nome de origem** (`00260057.pdf`), de forma atómica
   (`.part` + `os.replace`), depois de verificar que começa por `%PDF`.
5. Atualiza o registo e escreve `relatorio.txt` na pasta de saída.

Sem `--confirmar-rede` faz tudo menos os pedidos: diz exatamente o que descarregaria.

### Fase 2 — nomeação

```bash
python -m cct.nomeacao --destino data/raw/bte      # simulação
python -m cct.nomeacao --destino data/raw/bte --aplicar
```

1. Atribui a cada documento um **ordinal** por ano e família, por ordem de
   (nº do BTE, posição no índice), continuando a numeração já registada. Um ordinal, uma
   vez atribuído, nunca muda.
2. Separa os outorgantes em patronais e sindicais (é sindical quem tiver "sindic" no
   nome — regra que classifica corretamente a CNIS como patronal e a FNSTFPS como
   sindical) e deriva a sigla de cada lado: `… - ACRAL` → `ACRAL`, `… (AEVP)` → `AEVP`,
   `FESAHT - Federação…` → `FESAHT`, e por fim, em último recurso, CamelCase das palavras
   significativas (`Águas do Norte` → `AguasNorte`). Quando os outorgantes vêm vazios —
   acontece nas retificações — usa o título.
3. Compõe `{aa}_PR_{nnn}_BTE_{bb}_{PATRONAL}_{SINDICAL}.pdf`, garantindo ≤ 63 caracteres
   (limite de nome de documento do MaxQDA) e conformidade com a `RE_DOC_ID` do
   `cct/localizador.py`.
4. Copia o PDF para `data/raw/bte/bte_<ano>/` (convenções) ou
   `…/bte_<ano>/extensoes/` (portarias e avisos — fora do `glob("*.pdf")` do pipeline).
5. Nunca sobrescreve: destino já existente com o mesmo `sha256` é `ja_existente`; com
   conteúdo diferente é **conflito**, reportado e não escrito.

Uma tabela opcional de siglas (`--siglas siglas.csv`, colunas `nome;sigla`) sobrepõe-se à
derivação automática, para os casos que a equipa quer fixar.

### Encadeado

```bash
python -m cct.aquisicao --indices data/raw/indices --confirmar-rede --aplicar
```

Corre as duas fases e escreve um relatório único. Também disponível na app gráfica, no
botão **"Recolher do BTE…"**.

## Critérios de aceitação

- [x] Correr duas vezes seguidas sobre o mesmo índice não faz nenhum pedido de rede na
      segunda corrida, e não escreve nenhum ficheiro novo.
- [x] Sem `--confirmar-rede` não é aberta nenhuma ligação, em nenhum caminho de código.
- [x] Um URL fora da lista de anfitriões permitidos é recusado antes do pedido, incluindo
      quando aparece como destino de um redirecionamento.
- [x] Todo o nome gerado é aceite por `cct.localizador.interpretar_doc_id` e tem ≤ 63
      caracteres.
- [x] Os 14 documentos de `BTE31_2026.xlsx` são lidos do índice com tipo, outorgantes e
      URL corretos, incluindo as quatro retificações sem coluna de outorgantes.
- [x] Um ordinal já registado não é reatribuído quando o índice é reprocessado.
- [x] Um destino ocupado por conteúdo diferente gera conflito e não é sobrescrito.
- [x] Uma descarga interrompida não deixa PDF truncado em sítio nenhum (`.part`).

## Plano de verificação

- **Testes automáticos** — `tests/test_recolha.py` e `tests/test_nomeacao.py`: leitura do
  índice real do BTE 31/2026 (reconstruído em `openpyxl` a partir das linhas publicadas,
  para não versionar binários), idempotência, recusa de anfitriões, escrita atómica,
  derivação de siglas, estabilidade dos ordinais, conflitos, e conformidade com a
  `RE_DOC_ID`. A rede é injetada como função (`abridor=`), pelo que os testes correm
  offline; há um teste contra o servidor real, ativado só com `CCT_TESTE_REDE=1`.
- **Verificação manual** — correr sobre `BTE31_2026.xlsx`, confirmar 14 PDFs, abrir dois
  ao acaso e verificar que o nome corresponde às partes do documento.
- **Dados de ensaio** — `BTE31_2026.xlsx` (índice real do BTE n.º 31 de 2026).

## Riscos

| Risco | O que se faz |
|---|---|
| A aplicação deixa de ser "sem rede" — e isso está declarado ao Instituto de Informática | Rede desligada por omissão, num só módulo, com lista de anfitriões; ADR-0015 e §5-A dos requisitos técnicos |
| Siglas erradas partem o cruzamento com o gabarito e com o MaxQDA | Cada sigla derivada por recurso é assinalada no relatório; tabela `--siglas` para fixar casos |
| Ordinais reatribuídos partiriam a correspondência com o trabalho já feito | Ordinal é escrito no registo e nunca recalculado; teste dedicado |
| Perder o registo repõe a numeração a zero | Fica em `data/registo/`, fora de `data/interim/` (descartável) e de `results/`; documentado em docs/dados |
| O vocabulário de tipos da DGERT mudar | Tipos desconhecidos não são silenciados: aparecem no relatório e ficam por descarregar |
