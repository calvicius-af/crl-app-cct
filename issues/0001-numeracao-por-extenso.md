# ISSUE-0001: normalizar cláusulas com numeração por extenso

- **Estado:** Em curso — normalização implementada a 2026-09-23 (`cct/numeracao.py`); falta o gate com uma convenção real
- **Data:** 2026-07-07
- **GitHub:** #28 (sub-issue de #24)
- **Onde dói:** `cct/diacronia.py` e representação canónica do número

## O que acontece

Desde o PR #23, o extrator reconhece cláusulas escritas por extenso (`Cláusula décima
segunda`, `Cláusula primeira`) e cria o nó estrutural correto. Contudo, o ordinal ainda
não é convertido para um número canónico. A comparação diacrónica reconhece diretamente
apenas algarismos, pelo que o emparelhamento por número não beneficia destes cabeçalhos.

## O que devia acontecer

Uma cláusula por extenso deve conservar o rótulo original e expor o número canónico
correspondente, indistinguível de uma numerada em algarismos para efeitos de comparação
diacrónica.

## Como reproduzir

```bash
python -m cct.cli extrair --pdf <PDF com numeração por extenso> --out-dir /tmp/probe
# o nó existe; falta confirmar que a diacronia o emparelha pelo número canónico
```

O caso `Cláusula décima segunda` já está coberto na extração. Falta um par de versões que
prove o emparelhamento diacrónico entre ordinal por extenso e numeração canónica.

## Notas

Implica converter numerais ordinais por extenso em português (`primeira` → 1,
`décima segunda` → 12), incluindo formas compostas. Afeta também o `cct/diacronia.py`,
que emparelha cláusulas por número antes de recorrer à semelhança de conteúdo.

Identificado como limitação conhecida no fecho da fase 5.

## Progresso no PR #23

O PR #23 passou a reconhecer cabeçalhos como `Cláusula décima segunda` e
corrigiu os falsos positivos encontrados durante a revisão. A extração
estrutural deixou, portanto, de estar bloqueada.

Continua por resolver a normalização do ordinal para um número canónico. O
emparelhamento em `cct/diacronia.py` ainda reconhece apenas algarismos, pelo que
esta parte permanece aberta no GitHub como #28, dentro do programa #24.

## Normalização (2026-09-23)

`cct/numeracao.py` dá a cada cláusula ou artigo uma chave canónica, sem tocar no
rótulo, que fica como está no documento:

| Rótulo | Chave |
|---|---|
| `Cláusula 12.ª - Horário` | `cl12` |
| `Cláusula décima segunda - Horário` | `cl12` |
| `Cláusula 16.ª-A - Férias` | `cl16A` |
| `Artigo único - Âmbito` | `arunico` |
| `Cláusula prévia - Âmbito da revisão` | `clprevia` |

`cct/diacronia.py` passa a emparelhar por esta chave. Converte ordinais simples e
compostos até 199, só em ordem decrescente, e recusa o todo se uma palavra não for
ordinal (`Cláusula geral e transitória` continua sem número).

Corrigido de caminho um defeito da chave antiga, que só lia os algarismos: a
`16.ª-A`, inserida por uma revisão, tinha a mesma chave que a `16.ª` e podia ser
emparelhada com ela. A letra passa a fazer parte da chave.

Testes em `tests/test_numeracao.py`, incluindo o critério de aceitação (a mesma
cláusula escrita como `12.ª` e como `décima segunda`, com o texto reescrito, é
emparelhada pelo número). Os dois testes de emparelhamento falham com o código
anterior.

**Gate real, parcial (revisão do PR #88, 2026-09-23):** LPFP e SJPF, BTE 29/2025
(`25_PR_194_BTE_29_LPFP_SJPfutebol`). A extração produz «Cláusula primeira» e «Cláusula
segunda», normalizadas para `cl1` e `cl2`. Não há versão anterior local desta convenção,
pelo que o emparelhamento diacrónico com dados reais continua por testar. Falta: uma
versão anterior da LPFP/SJPF, ou outro par real, para fechar o critério do #28.
