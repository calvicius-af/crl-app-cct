# Exemplos completos: do PDF do BTE ao projeto MaxQDA

Esta pasta responde a uma pergunta simples — **o que entra e o que sai desta aplicação?** —
com dois casos reais. É a única parte de dados/resultados que está versionada no
repositório: tudo o resto (`data/`, `results/`) fica fora do Git.

## Privacidade dos exemplos publicados

Os PDFs de entrada e das versões anteriores **não são versionados**: são cópias dos
documentos oficiais/originais e podem conter nomes de signatários. Para repetir a extração,
obtêm-se os PDFs na origem oficial indicada abaixo ou através do arquivo autorizado do CRL.

Os textos, QDPX e ficheiros Excel aqui publicados preservam o comportamento demonstrativo,
mas os nomes dos signatários foram substituídos por marcadores como `[SIGNATÁRIO 01]`. O
comprimento de cada substituição é igual ao do nome original, pelo que os offsets do
`.doc.json` e do QDPX permanecem válidos. Esta anonimização é **deliberada** e não indica
erro de extração, comparação ou exportação. O procedimento verificável está em
`scripts/anonimizar_exemplos.py --check` e é decidido pelo
[ADR-0013](../docs/adr/0013-anonimizacao-dos-exemplos-publicados.md).

Cada exemplo tem a mesma organização:

```text
<exemplo>/
├── entrada/           o que o utilizador fornece (PDF publicado no BTE)
│   └── versoes/       (opcional) versão anterior da convenção, para a comparação diacrónica
└── saida/             o que a aplicação produz
    ├── *.txt                    texto extraído do PDF
    ├── *.doc.json               estrutura hierárquica com offsets
    ├── projeto.qdpx             projeto REFI-QDA para abrir no MaxQDA
    ├── sugestoes_peritas.xlsx   os mesmos segmentos em Excel, para quem não usa MaxQDA
    └── relatorio.txt            problemas encontrados na corrida
```

---

## Exemplo A — ACIP / FESAHT (caso rico)

Contrato coletivo entre a ACIP e a FESAHT, publicado no **BTE n.º 2 de 2025**, com
**texto consolidado** (republicação integral), tabelas salariais e anexos.
É o caso mais exigente do corpus: serve para mostrar o comportamento do extrator
perante estrutura complexa.

| | Ficheiro | Tamanho | O que é |
|---|---|---|---|
| **Entrada** | `entrada/25_PR_003_BTE_02_ACIP_FESAHT.pdf` | — | PDF original, não versionado; obter na origem oficial |
| | `entrada/versoes/ACIP_FESAHT/ACIP_FESAHT_2009.pdf` | — | versão anterior, não versionada; arquivo autorizado do CRL |
| **Saída** | `saida/25_PR_003_BTE_02_ACIP_FESAHT.txt` | 117 KB | 113 106 caracteres de texto limpo |
| | `saida/25_PR_003_BTE_02_ACIP_FESAHT.doc.json` | 130 KB | 577 nós, dos quais **91 cláusulas** |
| | `saida/projeto.qdpx` | 37 KB | 24 segmentos codificados, 22 códigos |
| | `saida/sugestoes_peritas.xlsx` | 14 KB | os mesmos segmentos com contexto |

Resultado da comparação com a versão de 2009, feita automaticamente durante a corrida:
**79 cláusulas alteradas, 9 iguais, 3 novas, 6 removidas → 82 novidades** no texto consolidado
(é isto que evita mandar rever cláusulas que não mudaram desde a versão anterior).

### Como regenerar

```bash
# 1. só a extração: PDF → .txt + .doc.json
python -m cct.cli extrair \
    --pdf examples/acip_fesaht/entrada/25_PR_003_BTE_02_ACIP_FESAHT.pdf \
    --out-dir examples/acip_fesaht/saida

# 2. a corrida completa: PDF → .qdpx + .xlsx (inclui a extração acima)
python -m cct.pipeline_tema \
    --pdfs examples/acip_fesaht/entrada \
    --codebook codebooks/4_08_protecao_dados.yaml \
    --metricas examples/metricas_calibracao.json \
    --pasta-versoes examples/acip_fesaht/entrada/versoes \
    --out examples/acip_fesaht/saida
```

Os ficheiros aqui guardados foram gerados com dois parâmetros adicionais, que dependem de
exports do MaxQDA não versionados (`data/raw/maxqda/`, ver [docs/dados](../docs/dados/README.md)):
`--variaveis VariaveisDocumento2025.xlsx` (metadados de cada convenção) e
`--master "…Lista de Códigos.qdc"` (nomes, cores e descrições oficiais dos códigos do CRL).

Sem eles a corrida funciona na mesma, com duas diferenças: os códigos saem sem as
descrições oficiais, e o subtipo da convenção fica "desconhecido" — o que enfraquece a
deteção do texto consolidado e, neste caso concreto, faz desaparecer a faixa
`CONSOLIDADO` (23 anotações em vez de 24). É a razão pela qual o guia de operação
insiste em exportar as variáveis do MaxQDA antes de correr o pipeline.

---

## Exemplo B — TINITA / SITEMAQ (caso de renumeração)

Contrato coletivo publicado no **BTE n.º 19 de 2025**, sem texto consolidado, mas com
uma reorganização substancial face à versão de 2020. Serve para mostrar a comparação
diacrónica a funcionar quando os números das cláusulas mudam.

| | Ficheiro | Tamanho | O que é |
|---|---|---|---|
| **Entrada** | `entrada/25_PR_112_BTE_19_TINITA_SITEMAQ.pdf` | — | PDF original, não versionado; obter na origem oficial |
| | `entrada/versoes/TINITA_SITEMAQ/2020_TINITA_SITEMAQ.pdf` | — | versão anterior, não versionada; arquivo autorizado do CRL |
| **Saída** | `saida/25_PR_112_BTE_19_TINITA_SITEMAQ.txt` | 42 KB | 41 428 caracteres |
| | `saida/25_PR_112_BTE_19_TINITA_SITEMAQ.doc.json` | 30 KB | 139 nós, **34 cláusulas** |
| | `saida/projeto.qdpx` | 14 KB | 6 segmentos codificados |
| | `saida/sugestoes_peritas.xlsx` | 7 KB | idem, em Excel |
| | `saida/comparacao_2020_2025.xlsx` | 13 KB | diferenças cláusula a cláusula |

Resultado da comparação 2020 → 2025: **12 alteradas, 11 novas, 12 removidas** e, o ponto
importante, **14 cláusulas renumeradas emparelhadas por conteúdo** — sem esse emparelhamento
apareceriam falsamente como 14 remoções + 14 novidades.

### Como regenerar

```bash
python -m cct.cli extrair \
    --pdf examples/tinita_sitemaq/entrada/25_PR_112_BTE_19_TINITA_SITEMAQ.pdf \
    --out-dir examples/tinita_sitemaq/saida

python -m cct.pipeline_tema \
    --pdfs examples/tinita_sitemaq/entrada \
    --codebook codebooks/4_08_protecao_dados.yaml \
    --metricas examples/metricas_calibracao.json \
    --out examples/tinita_sitemaq/saida

python -m cct.comparar \
    --antigo examples/tinita_sitemaq/entrada/versoes/TINITA_SITEMAQ/2020_TINITA_SITEMAQ.pdf \
    --novo   examples/tinita_sitemaq/entrada/25_PR_112_BTE_19_TINITA_SITEMAQ.pdf \
    --out    examples/tinita_sitemaq/saida/comparacao_2020_2025.xlsx
```

---

## Como ler cada formato

### O `.txt` — o texto, e só o texto

Ficheiro de texto simples em **UTF-8 sem BOM, com quebras de linha LF**. Não é um detalhe
estético: os offsets das codificações contam caracteres sobre este texto exato, pelo que
qualquer alteração de codificação ou de quebras de linha desalinharia todas as marcações.
Ambos os ficheiros desta pasta foram verificados quanto a isso.

Vale a pena abri-lo lado a lado com o PDF: os cabeçalhos e rodapés repetidos do BTE
desapareceram, as frases partidas ao longo de várias linhas foram reunidas, e as duas
colunas dos boletins antigos foram lidas pela ordem certa.

### O `.doc.json` — a estrutura

O mesmo texto, agora com a árvore do documento: título → capítulo → cláusula → número/alínea,
cada nó com o intervalo de caracteres (`ini`, `fim`) que ocupa no `.txt`. Inclui também as
marcas que o pipeline deteta sozinho: preâmbulo, assinaturas e o arranque do texto consolidado.

Propriedade garantida por teste automático (**zero perda de texto**): concatenar os nós
reconstrói integralmente o `.txt`, sem um único carácter a mais ou a menos.

### O `.qdpx` — o projeto para o MaxQDA

Ficheiro no formato aberto **REFI-QDA 1.5**, que é um ZIP com `project.qde` (XML com a
árvore de códigos e as posições dos segmentos) e `Sources/` (o texto). Os exemplos
versionados atuais são byte a byte iguais ao `.txt` emparelhado. O exportador atual pode
inserir linhas em branco para legibilidade; nesse caso, os offsets são remapeados e a
garantia passa a ser equivalência carácter a carácter depois de remover exatamente as
inserções registadas pelo exportador.

Quando estes exemplos forem regenerados, devem conservar também o `manifest.json` da
corrida, para fixar commit, inputs, parâmetros e hashes.

A árvore de códigos organiza-se em faixas, que dizem à equipa **o que fazer** com cada segmento:

| Faixa | Significado |
|---|---|
| `AUTO` | precisão medida ≥ 0,85 no gabarito — aceitar com verificação rápida |
| `REVER` | sugestão a validar por pessoa |
| `CONSOLIDADO` | texto republicado que não mudou face à versão anterior — pode ser lido por último |
| `00 Estrutura` | preâmbulo, assinaturas e texto consolidado, excluídos da análise temática |

**Para abrir:** MaxQDA 2022 ou superior → *Importar* → *Projetos de outros programas QDA* →
*REFI-QDA Project (.qdpx)* → escolher o ficheiro. Os códigos aparecem já na árvore, com os
nomes, cores e descrições do livro de códigos do CRL.

### O `.xlsx` — para quem não usa MaxQDA

A mesma informação em Excel, um segmento por linha com o texto, o código sugerido, a faixa e
o contexto (cláusula e capítulo onde se insere). É o formato que as peritas usaram nas rondas
de validação.

---

## Proveniência dos ficheiros de entrada

Os PDFs são documentos publicados no *Boletim do Trabalho e Emprego* pelo Gabinete de
Estratégia e Planeamento (GEP/MTSSS), descarregáveis em
`https://bte.gep.msess.gov.pt/completos/<ano>/bte<n>_<ano>.pdf`. Foram recolhidos em abril
de 2026, já separados por convenção. As versões anteriores (2009 e 2020) vêm do arquivo de
textos consolidados do CRL. Não são redistribuídos neste repositório; ver
[docs/dados/README.md](../docs/dados/README.md).

`metricas_calibracao.json` é o resultado da avaliação da baseline lexical contra o gabarito
manual do tema 4.8 (89 convenções de 2025, 788 segmentos codificados por peritas). É ele que
determina que códigos podem ir para a faixa `AUTO`.
