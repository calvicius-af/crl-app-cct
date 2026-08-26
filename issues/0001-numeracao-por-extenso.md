# ISSUE-0001: normalizar cláusulas com numeração por extenso

- **Estado:** Em curso — reconhecimento implementado no PR #23; falta normalização numérica para diacronia
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
