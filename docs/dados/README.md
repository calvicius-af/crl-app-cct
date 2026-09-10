# Dados: o que existe, de onde vem, como repor

Os dados **não estão no Git**. A dimensão varia entre instalações e são, na maior parte,
documentos públicos que qualquer pessoa pode voltar a obter, ou exports de MaxQDA que
pertencem ao CRL. Versioná-los tornaria o repositório inutilizável e não acrescentaria
nada à reprodutibilidade — ver [ADR-0009](../adr/0009-layout-do-repositorio.md).

Quem só quer ver o sistema a funcionar não precisa de nada disto: a pasta
[`examples/`](../../examples/README.md) tem artefactos anonimizados de dois casos reais.
Os PDFs de origem não são redistribuídos; obtêm-se na fonte oficial ou através do arquivo
autorizado do CRL.

## Estrutura esperada

```text
data/
├── raw/                          entrada — só a nomeação escreve aqui
│   ├── indices/                  índices .xlsx do BTE, um por número (ver abaixo)
│   ├── bte/
│   │   ├── bte_2021/             48 números completos do BTE de 2021
│   │   ├── bte_2022/             240 convenções de 2022, uma por ficheiro
│   │   ├── bte_2025/             corpus disponível de 2025; pode ser parcial
│   │   ├── bte_2026/             convenções de 2026
│   │   │   └── extensoes/        portarias e avisos (fora do glob do pipeline)
│   │   └── bte2_2025.pdf         número completo usado pelos testes de extração
│   ├── maxqda/                   exports do MaxQDA (ver abaixo)
│   └── textos_consolidados/      21 pastas, uma por convenção, com as versões anteriores
├── reference/                    referências humanas preserváveis
│   └── maxqda/tema-4.08/         projectos MQDA e exports QDPX de trabalho
├── interim/                      resultados intermédios reproduzíveis (texto extraído, caches)
│   └── recolha/<ano>/<nº>/       PDFs descarregados, com o nome de origem
└── registo/
    └── registo_bte.jsonl         registo da recolha — NÃO APAGAR (ver abaixo)
```

`results/` guarda saídas, experiências, métricas e possíveis artefactos revistos por
pessoas. Também está fora do Git, mas **não deve ser apagada em bloco**. Apenas caches e
intermédios confirmados são descartáveis; projetos MQDA, Excel revisto, validações e
entregáveis podem conter trabalho humano não regenerável. Ver
[organização do workspace](organizacao-workspace.md).

`data/raw/` é fonte e requer cópia de segurança, tal como `data/reference/` e `data/registo/` (guarda os ordinais da recolha — ver abaixo). `data/interim/` é regenerável quando a
corrida tem inputs e manifesto conhecidos. Para inventariar a instalação atual sem mover
nada:

```bash
python scripts/inventariar_workspace.py
```

## Boletim do Trabalho e Emprego (`data/raw/bte/`)

Publicação oficial do Gabinete de Estratégia e Planeamento (GEP/MTSSS), de acesso
público. Os números completos descarregam-se de:

```
https://bte.dgcp.mtsss.gov.pt/completos/<ano>/bte<n>_<ano>.pdf
```

O endereço antigo (`bte.gep.msess.gov.pt/completos/…`) continua a funcionar, mas responde
com um redirecionamento para o anfitrião acima.

Há dois formatos em uso, e o pipeline lida com ambos:

- **Números completos** (`bte_2021/`): um PDF por edição do boletim, com dezenas de
  instrumentos. Serve para os testes e para o `cct/localizador.py`, que encontra as
  páginas de uma convenção dentro do número.
- **Convenções individuais** (`bte_2022/`, `bte_2025/`): um PDF por instrumento, já
  recortado. É o formato normal de operação.

Convenção de nomes de 2025 — `25_PR_003_BTE_02_ACIP_FESAHT.pdf`:

| Parte | Significado |
|---|---|
| `25` | ano (2025) |
| `PR` | setor privado |
| `003` | número sequencial dentro do ano |
| `BTE_02` | publicado no BTE n.º 2 |
| `ACIP_FESAHT` | entidade empregadora e sindicato |

Estes nomes não são decorativos: o pipeline cruza-os com a amostra de referência e com as variáveis do
MaxQDA por prefixo e por tokens, e o `cct/comparar.py` deduz o ano a partir deles para
escolher que versões comparar. Mudar o esquema de nomes parte esse cruzamento.

## Exports do MaxQDA (`data/raw/maxqda/`)

Produzidos pela equipa do CRL a partir do projeto MaxQDA. Não são públicos.

| Ficheiro | Como se obtém | Para que serve |
|---|---|---|
| `VariaveisDocumento2025.xlsx` | MaxQDA → Variáveis de documento → Exportar | Metadados de cada convenção: subtipo (revisão parcial, consolidado…), setor, CAE. Determina como o extrator interpreta o documento. **Nota:** o MaxQDA trunca os nomes das variáveis a 30 caracteres — o cruzamento é feito por prefixo |
| `MAXQDA_RNC_…Lista de Códigos.qdc` | MaxQDA → Livro de códigos → Exportar (.qdc) | Os 1393 códigos oficiais do CRL, com nomes, cores e descrições (definição, critérios, base legal). O QDPX gerado reutiliza-os, para que os projetos sejam compatíveis entre si |
| `4_08_ParaClaudeAppCCT.xlsx` | MaxQDA → Segmentos codificados → Exportar | **Amostra de referência** do tema 4.8: 788 segmentos codificados manualmente por peritas em 89 convenções de 2025, com 19 códigos hierárquicos. É a base contra a qual toda a qualidade é medida |

Sem estes ficheiros o pipeline corre na mesma, com menos metadados; sem a amostra de referência, não é
possível calibrar a faixa `AUTO` nem medir precisão e cobertura.

## Textos consolidados (`data/raw/textos_consolidados/`)

Uma pasta por convenção (21 no total), cada uma com o PDF de 2025 e as versões anteriores
que existirem, mais os documentos de comparação manual feitos pela equipa (`Comparei_*.docx`),
que serviram de amostra de referência para validar o comparador automático.

A regra de nomes importa: o `cct/comparar.py` deduz o ano do nome do ficheiro
(`2020_TINITA_SITEMAQ.pdf`, `25112_BTE_19_…`) e distingue textos completos de revisões
parciais pelo tamanho relativo — uma revisão parcial tem menos de metade do texto da
versão completa. Comparar contra uma revisão parcial produz resultados sem sentido, e foi
o principal problema encontrado no lote de 44 comparações (ver
[ADR-0010](../adr/0010-escolha-do-par-na-diacronia.md)).

## Repor os dados numa máquina nova

1. Criar a estrutura: `mkdir -p data/raw/bte data/raw/maxqda data/raw/textos_consolidados`
2. Copiar os PDFs para `data/raw/bte/bte_<ano>/` (do arquivo do CRL, ou descarregando do BTE)
3. Exportar do MaxQDA os três ficheiros da tabela acima para `data/raw/maxqda/`
4. Correr `python -m cct.doctor` — diz em português o que ainda falta e onde

## Proteção de dados

As convenções coletivas são documentos públicos e não contêm dados pessoais para além dos
nomes dos signatários, que constam da publicação oficial. Os exports do MaxQDA contêm
trabalho interno do CRL e não devem ser publicados sem decisão da instituição. O
`.gitignore` está construído para que nada disto entre no repositório por acidente; a
verificação está descrita no [CONTRIBUTING](../../CONTRIBUTING.md).


## Índices do BTE (`data/raw/indices/`) e recolha automática

A DGERT fornece, por cada número do boletim, um ficheiro Excel com a lista dos
documentos publicados: identificador, título, tipo, número do BTE, código IRCT,
outorgantes e a ligação direta para o PDF de cada documento (por exemplo
`BTE31_2026.xlsx`, com os 14 documentos do n.º 31 de 2026).

Depositar esses ficheiros em `data/raw/indices/` — tal como vêm, sem editar — é tudo o que
a recolha automática precisa:

```bash
python -m cct.aquisicao --indices data/raw/indices                       # simula
python -m cct.aquisicao --indices data/raw/indices --confirmar-rede --aplicar
```

O que acontece, em duas fases ([SPEC-0001](../../specs/0001-recolha-e-nomeacao-do-bte.md)):

1. **Recolha** (`cct/recolha.py`) — descarrega os PDFs para
   `data/interim/recolha/<ano>/<nº do BTE>/`, com o **nome de origem** (`00260057.pdf`).
   Nada é descarregado duas vezes: o registo guarda o `sha256`, o `ETag` e o
   `Last-Modified` de cada documento, e a segunda corrida sobre o mesmo índice não faz
   um único pedido de rede.
2. **Nomeação** (`cct/nomeacao.py`) — copia cada PDF para
   `data/raw/bte/bte_<ano>/` já com o nome do esquema
   (`26_PR_003_BTE_31_AEVP_FESAHT.pdf`). As portarias de extensão e os avisos vão para
   a subpasta `extensoes/`, para não entrarem no `glob("*.pdf")` do pipeline.

A rede está **desligada por omissão** e só liga com `--confirmar-rede`
([ADR-0015](../adr/0015-recolha-em-rede-desligada-por-omissao.md)). Numa rede fechada,
basta a equipa colocar os PDFs à mão em `data/interim/recolha/<ano>/<nº>/` e correr só a
nomeação.

### O registo (`data/registo/registo_bte.jsonl`)

Uma linha JSON por documento, com a proveniência (índice, tipo, código IRCT,
outorgantes), o estado da descarga e o nome atribuído. Junto com os PDFs nomeados em
`data/raw/bte/` (passo 2 acima), é uma das duas escritas que a aquisição faz fora de
`data/interim/`. **Não deve ser apagado**: é ele que guarda os números sequenciais já
atribuídos. Apagá-lo faz a numeração recomeçar em 1 e produz nomes diferentes para os
mesmos documentos.

### Siglas dos outorgantes

O nome usa a sigla de cada lado da mesa. Quando a sigla está declarada no nome do
outorgante — `… - ACRAL`, `(AEVP)`, `FESAHT - Federação…` — é usada tal e qual. Quando
não está, é derivada das palavras distintivas (`Sindicato Nacional dos Motoristas` →
`Motoristas`) e **assinalada no relatório para confirmação humana**. Para fixar os casos
que a equipa quer decididos de uma vez por todas:

```bash
python -m cct.nomeacao --siglas siglas.csv --aplicar     # ficheiro 'nome;sigla' por linha
```
