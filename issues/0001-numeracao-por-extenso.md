# ISSUE-0001: cláusulas com numeração por extenso não são reconhecidas

- **Estado:** Em curso — reconhecimento implementado no PR #23; falta normalização numérica para diacronia
- **Data:** 2026-07-07
- **GitHub:** #28 (sub-issue de #24)
- **Onde dói:** `cct/extractor.py`

## O que acontece

O extrator reconhece cláusulas numeradas em algarismos (`Cláusula 12.ª`, `Artigo 5.º`),
mas não as que estão escritas por extenso (`Cláusula décima segunda`, `Cláusula primeira`).
Nessas convenções, o texto é extraído corretamente mas fica agregado no nó anterior em vez
de dar origem a um nó de cláusula próprio.

## O que devia acontecer

Uma cláusula com numeração por extenso deve produzir um nó `clausula` com o número
correspondente, indistinguível de uma numerada em algarismos — incluindo para efeitos de
comparação diacrónica, onde o emparelhamento por número deixa de funcionar.

## Como reproduzir

```bash
python -m cct.cli extrair --pdf <PDF com numeração por extenso> --out-dir /tmp/probe
# no .doc.json: os nós "clausula" ficam abaixo do número real de cláusulas do documento
```

Falta identificar uma convenção concreta do corpus onde isto aconteça, para servir de caso
de teste. É o primeiro passo para resolver.

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
