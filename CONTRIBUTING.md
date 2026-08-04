# Como contribuir

Este é um projeto pequeno, de uso institucional. Estas notas servem sobretudo para quem
se junta ao trabalho — pessoa ou agente — perceber como aqui se faz.

## Preparar o ambiente

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q      # 99 testes, ~5 segundos
.venv/bin/python -m cct.doctor     # verifica dados e dependências
```

Os testes correm **sem os dados**: os que precisam de PDFs ou de exports do MaxQDA
declaram-se `skipped` em vez de falhar. É por isso que a integração contínua passa num
repositório clonado de fresco.

## Testes antes do código

É a prática seguida desde a fase 0 e vale a pena manter: escrever primeiro o teste que
descreve o comportamento desejado, vê-lo falhar, e só então implementar. Quase todos os
testes deste repositório nasceram de um problema concreto encontrado num documento real —
quando corrigires algo, acrescenta o teste que impede o regresso do problema.

Casos difíceis vivem em `tests/fixtures/`; para verificação ponta a ponta há
[`examples/`](examples/README.md).

## As três regras que não se quebram

1. **UTF-8 sem BOM, quebras LF** no texto-fonte.
2. **Zero perda de texto**: concatenar os nós do `doc.json` reconstrói o `.txt`.
3. **O pipeline não conhece temas**: nenhum código de tema (4.08, …) dentro de `cct/`.

Se uma alteração tua obrigar a quebrar uma destas, para e escreve um ADR primeiro.

## Onde escrever o quê

| Tipo de trabalho | Onde |
|---|---|
| Uma decisão com consequências duradouras | [`docs/adr/`](docs/adr/README.md) — um ficheiro, meia página, no momento em que se decide |
| Uma funcionalidade nova, com desenho não trivial | [`specs/`](specs/README.md) — antes de programar |
| Algo partido, em falta, ou por afinar | [`issues/`](issues/README.md) + GitHub Issues |
| Como o sistema funciona | [`docs/arquitetura/`](docs/arquitetura/arquitetura.md) |
| Como se opera | [`docs/operacao/`](docs/operacao/guia-operacao.md) |

A regra prática: se daqui a um ano alguém puder perguntar *"porque é que isto está
assim?"* e a resposta não estiver no código, é um ADR.

## Antes de fazer commit

```bash
.venv/bin/python -m pytest -q

# nada de dados a escapar: só deve aparecer o que está em examples/ e tests/
git ls-files | grep -iE '\.(pdf|qdpx|mqda|xlsx|qdc)$'
```

Nunca versionar: PDFs do BTE fora de `examples/`, exports do MaxQDA, ficheiros `.mqda`,
resultados de corridas. O `.gitignore` cobre isto, mas convém confirmar — sobretudo antes
do primeiro *push* para um repositório remoto.

## Mensagens de commit

Em português, no imperativo, a dizer o efeito e não o mecanismo:

```
extractor: reconhecer cláusulas com numeração por extenso
docs: registar a decisão sobre o layout do repositório (ADR-0009)
```

## Codebooks

Os ficheiros em `codebooks/` são mantidos pela equipa de análise, não por quem programa.
O formato e o procedimento para acrescentar termos em falta (mineração dos falsos
negativos do gabarito) estão em
[docs/operacao/prompts-codebooks.md](docs/operacao/prompts-codebooks.md). Uma alteração de
codebook deve vir acompanhada da métrica antes e depois — é a única forma de saber se
melhorou.
