# Como contribuir

Este é um projeto pequeno, de uso institucional. Estas notas servem sobretudo para quem
se junta ao trabalho — pessoa ou agente — perceber como aqui se faz.

## Preparar o ambiente

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q      # suite completa; a contagem cresce com o projeto
.venv/bin/python -m cct.doctor     # verifica dados e dependências
```

Em Windows (o sistema das estações do CRL) o interpretador do ambiente é
`.venv\Scripts\python.exe`:

```bat
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m cct.doctor
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

O mapa e a estrutura de destino da suite estão em [`tests/README.md`](tests/README.md).

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
.venv/bin/python -m pytest -q        # Windows: .venv\Scripts\python -m pytest -q

# nada de dados, credenciais ou segredos a escapar
python scripts/verificar_seguranca.py --verboso

# nada de links ou caminhos documentais quebrados (nem sensíveis a maiúsculas/minúsculas)
python scripts/verificar_referencias.py --verboso

# lint e tipos, os mesmos do job "análise estática" do CI (issue #27);
# instalar uma vez com: python -m pip install -c requirements/dev.txt ruff mypy types-PyYAML
python -m ruff check cct scripts tests
python -m mypy cct
```

Os testes tratam como falha um aviso de depreciação ou um ficheiro por fechar no
código do projeto (`pytest.ini`, issue #8). Os avisos das bibliotecas externas
continuam visíveis, mas não fazem falhar a corrida.

`scripts/verificar_seguranca.py` é a mesma barreira que corre no CI (job
*segurança*) e só usa a biblioteca padrão, pelo que corre em qualquer máquina sem
instalar nada. Faz quatro verificações sobre os ficheiros versionados:

1. ficheiros de dados (`.pdf`, `.qdpx`, `.mqda`, `.xlsx`, `.qdc`) fora de
   `examples/` e `tests/`;
2. ficheiros `.env` e variantes (`.env.production`, …), com excepção de
   `.env.example`;
3. *allowlist* de `examples/`: só passam o `README.md`, as métricas de calibração
   e os artefactos de saída anonimizados em `examples/*/saida/`. Nada de
   `examples/*/entrada/` é redistribuído ([ADR-0013](docs/adr/0013-anonimizacao-dos-exemplos-publicados.md));
4. varrimento de segredos no conteúdo (chaves PEM, tokens do GitHub e do Slack,
   chaves AWS, chaves de API, atribuições do género `password = "…"`). O relatório
   indica ficheiro e linha, nunca o valor encontrado.

Se um ficheiro novo em `examples/` for deliberado, acrescenta o padrão à
`ALLOWLIST_EXAMPLES` do script, no mesmo commit — é essa a revisão.

`scripts/verificar_referencias.py` corre a par, também localmente e no CI
(job *segurança*): apanha links Markdown locais e caminhos de documentação em
código Python que apontem para um destino inexistente, incluindo o caso
traiçoeiro de um destino que só existe com outra caixa (passa em
macOS/Windows, falha em Linux).

Nunca versionar: PDFs do BTE fora de `examples/`, exports do MaxQDA, ficheiros `.mqda`,
resultados de corridas. O `.gitignore` cobre isto, mas convém confirmar — sobretudo antes
do primeiro *push* para um repositório remoto.

Uma nova corrida deve conservar o `manifest.json` que o pipeline gera. Antes de mover ou
limpar ficheiros locais, correr `python scripts/inventariar_workspace.py` e seguir
[a política do workspace](docs/dados/organizacao-workspace.md). Nunca guardar `.env` ou
credenciais dentro de `vendor/`, mesmo sendo uma pasta ignorada pelo Git.

## Actualizar versões

As dependências vivem em dois registos, de propósito — mínimos para quem
instala, versões exactas para quem verifica:

| Ficheiro | O que declara | Para quê |
|---|---|---|
| `requirements.txt` | mínimos (`>=`) | instalação local leve, tolerante, sem Docling |
| `requirements/runtime.txt` | versões exactas | o que o CI testa e o que uma release instala |
| `requirements/dev.txt` | versões exactas | `pytest` e `pip-audit` |
| `requirements/docling.txt` | versão exacta | `docling-core`, só os tipos, para o job opcional |

Os ficheiros em `requirements/` usam-se como *constraints*, não como lista de
instalação:

```bash
python -m pip install -r requirements.txt \
    -c requirements/runtime.txt -c requirements/dev.txt
```

Para subir uma versão:

1. altera o `==` no ficheiro de *constraints* correspondente (e o `>=` em
   `requirements.txt` apenas se o mínimo deixar de ser suportado);
2. corre a suite nas **duas** versões do Python da matriz, 3.11 e 3.12 — uma
   versão nova que já não suporte 3.11 parte o CI em metade dos jobs;
3. confirma que a instalação leve continua a funcionar sem Docling: a suite tem
   de passar sem `docling-core` instalado (os testes respectivos declaram-se
   `skipped`);
4. corre `pip-audit --strict -r requirements/runtime.txt -r requirements/dev.txt`.

O Dependabot ([`.github/dependabot.yml`](.github/dependabot.yml)) abre estes
*pull requests* automaticamente, às segundas-feiras, para as dependências Python
e para as GitHub Actions. Nenhum entra sem passar os jobs.

As GitHub Actions estão fixadas por SHA no workflow, com a versão em comentário
ao lado (`actions/checkout@11d5960… # v4.4.0`). Uma tag como `v4` pode ser
reapontada para outro commit entre duas corridas; um SHA não. Ao actualizar à
mão, actualiza também o comentário.

Só `docling-core` é que está fixado sem a sua árvore transitiva: é uma
dependência opcional, fora da instalação base, e fixar toda a árvore traria
dezenas de pacotes que o produto não distribui.

A instalação institucional não passa por aqui: passa pelo pacote offline, que já
verifica o SHA-256 de cada *wheel* antes de instalar — ver
[`docs/institucional/instalacao-offline.md`](docs/institucional/instalacao-offline.md)
e o [ADR-0020](docs/adr/0020-integridade-dos-artefactos-de-instalacao.md).
O pacote offline é preparado e instalado com estas mesmas *constraints*, pelo que
uma estação institucional recebe as versões que o CI testou. Se acrescentares um
ficheiro de *constraints* novo, liga-o também a `ficheiros_de_constraints` em
`scripts/preparar_pacote_offline.py`, senão as duas vias divergem em silêncio.

## Mensagens de commit

Em português, no imperativo, a dizer o efeito e não o mecanismo:

```
extractor: reconhecer cláusulas com numeração por extenso
docs: registar a decisão sobre o layout do repositório (ADR-0009)
```

## Codebooks

Os ficheiros em `codebooks/` são mantidos pela equipa de análise, não por quem programa.
O formato e o procedimento para acrescentar termos em falta (mineração dos falsos
negativos da amostra de referência) estão em
[docs/operacao/prompts-codebooks.md](docs/operacao/prompts-codebooks.md). Uma alteração de
codebook deve vir acompanhada da métrica antes e depois — é a única forma de saber se
melhorou.
