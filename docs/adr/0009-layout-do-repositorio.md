# ADR-0009: layout do repositório — pacote na raiz, dados fora do Git

- **Estado:** Aceite
- **Data:** 2026-08-04
- **Decidido por:** CRL (António Fula)

## Contexto

O projeto cresceu por experimentação: três gerações de pré-processador, uma dúzia de
repositórios de terceiros clonados para estudo, 670 MB de PDFs do BTE e exports do MaxQDA,
170 MB de resultados de rondas sucessivas — tudo na mesma pasta, sem controlo de versões.

Para apresentar o trabalho ao Instituto de Informática e passar a um modo de
desenvolvimento normal, era preciso decidir o que é o repositório.

## Decisão

**Pacote Python na raiz** (`cct/`), e não em `src/cct/`:

- mantém `python -m cct.app`, `python -m cct.pipeline_tema` e `python -m pytest -q` a
  funcionar sem instalação prévia (`pip install -e .`), o que importa para o cenário de
  instalação offline por *wheels* previsto nos
  [requisitos técnicos](../institucional/requisitos-tecnicos.md);
- o layout `src/` resolve sobretudo problemas de bibliotecas publicadas em PyPI, que não
  é o caso desta aplicação.

**Dados e resultados fora do Git**, mas dentro da pasta de trabalho:

| Pasta | Conteúdo | No Git? |
|---|---|---|
| `cct/`, `tests/`, `codebooks/`, `docs/`, `specs/`, `issues/`, `scripts/` | o produto | sim |
| `examples/` | dois casos completos, PDF → TXT → QDPX (~4 MB) | **sim** |
| `data/`, `results/` | 670 MB de fontes, 170 MB de saídas | não |
| `vendor/` | clones de terceiros, com licenças próprias | não |
| `archive/` | pré-processadores v1/v2/v2.1 e saídas antigas | não |

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Git LFS para os PDFs | Consome quota, torna o clone lento, e obriga a decidir a redistribuição de documentos que já são públicos e obtíveis na origem |
| Repositório novo só com código, dados noutra pasta | Separa a pesquisa e o histórico do produto; ficariam órfãos |
| Versionar `vendor/` | Redistribuição de código alheio, cinco projetos sem licença declarada |

## Consequências

- O repositório fica na ordem dos megabytes e clona em segundos.
- Quem clona não consegue reproduzir as corridas completas sem pedir os dados ao CRL —
  mitigado por `examples/`, que permite ver o sistema a funcionar ponta a ponta, e por
  [docs/dados](../dados/README.md), que explica como repor tudo.
- `data/interim/` e `results/` passam a ser descartáveis por definição.
- Os caminhos ficaram fixados: `data/raw/bte/`, `data/raw/maxqda/`,
  `data/raw/textos_consolidados/`. A auto-descoberta da aplicação e o `doctor` dependem
  deles.

## Revisitar quando

O repositório passar a ser público e for preciso decidir a redistribuição dos dados, ou se
a instituição quiser um repositório de dados próprio (institucional ou temático) ligado a
este.
