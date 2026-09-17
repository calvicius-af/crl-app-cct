# Segurança

## Superfície de exposição

A aplicação corre na máquina local, não abre portas, não escuta ligações e não envia
telemetria. A instalação base não faz pedidos de rede durante o processamento.

A única exceção é opcional e local: se a camada semântica for ativada (`--semantica`), a
aplicação fala com um servidor de modelo de linguagem em `http://127.0.0.1:1234`
(por exemplo, LM Studio), na própria máquina. Está desligada por omissão. O backend aceita
somente `localhost`, `127.0.0.1` ou `::1`; uma URL remota falha antes de qualquer pedido de
rede. Não existe backend para serviços externos — ver
[ADR-0012](docs/adr/0012-modelos-locais-obrigatorios.md).

O extrator Docling opcional pode descarregar modelos na primeira execução. Em ambientes
fechados, os modelos devem ser pré-instalados a partir de uma origem aprovada; a execução
normal usa apenas os ficheiros locais.

O produto não requer credenciais, chaves ou segredos. Ficheiros `.env` não devem ser
guardados no repositório nem dentro das cópias locais em `vendor/`.

## Barreiras automáticas no repositório

Três camadas, todas verificáveis:

1. **`.gitignore`** — ignora `data/`, `results/`, `vendor/`, `archive/`, os ficheiros de
   projeto QDA e `.env` com todas as variantes (`.env.*`), com uma única excepção
   explícita para `.env.example`.
2. **`scripts/verificar_seguranca.py`** — corre localmente antes de um commit e no CI (job
   *segurança*). Sobre os ficheiros já versionados, verifica que não entraram ficheiros de
   dados fora de `examples/` e `tests/`, que não há `.env` versionado, que tudo o que está
   em `examples/` consta de uma *allowlist* explícita, e varre o conteúdo à procura de
   segredos (chaves PEM, tokens do GitHub e do Slack, chaves AWS, chaves de API,
   atribuições do género `password = "…"`). O relatório indica ficheiro e linha, nunca o
   valor encontrado. Só usa a biblioteca padrão.
3. **Definições do GitHub** — *secret scanning* com *push protection* e alertas do
   Dependabot devem ficar activos no repositório. São gratuitos em repositórios públicos e
   privados, e apanham o que uma verificação local não apanha (histórico já enviado,
   padrões de fornecedores conhecidos). Esta parte não se configura por ficheiro: faz-se em
   *Settings → Code security*.

A *allowlist* de `examples/` é deliberadamente estreita: passam o `README.md`, as métricas
de calibração e os artefactos de saída anonimizados em `examples/*/saida/`. Os PDFs de
origem em `examples/*/entrada/` não são redistribuídos
([ADR-0013](docs/adr/0013-anonimizacao-dos-exemplos-publicados.md)). Acrescentar um tipo
novo de ficheiro exige acrescentar o padrão ao script, no mesmo commit — é esse o momento
de revisão.

## Cadeia de fornecimento e permissões do CI

O workflow declara `permissions: contents: read` ao nível do ficheiro: nenhum job escreve
no repositório, publica pacotes ou comenta em issues. Uma permissão adicional, se vier a
ser precisa, declara-se no job que a usa, não globalmente.

As GitHub Actions estão fixadas por SHA, com a versão em comentário ao lado. Uma tag como
`v4` pode ser reapontada para outro commit entre duas corridas; um SHA não. O Dependabot
propõe o SHA seguinte por *pull request*, que passa pelos mesmos jobs.

As versões instaladas estão fixadas em `requirements/runtime.txt`, `requirements/dev.txt` e
`requirements/docling.txt`, usados como *constraints*. O `requirements.txt` continua a
declarar mínimos, para que a instalação local se mantenha leve. O procedimento de
actualização está em [CONTRIBUTING.md](CONTRIBUTING.md), secção *Actualizar versões*.

**Hashes de artefactos.** A prova de integridade por hashes já existe neste projeto, no
pacote offline: `scripts/preparar_pacote_offline.py` calcula o SHA-256 de cada *wheel* e
escreve `vendor/wheels/MANIFESTO.txt` e `vendor/wheels/manifesto.json`;
`scripts/instalar_offline.py` recalcula todos os hashes e recusa instalar se um ficheiro
faltar ou não corresponder. O procedimento está em
[`docs/institucional/instalacao-offline.md`](docs/institucional/instalacao-offline.md).

O que esta verificação garante, dito com precisão: **integridade**, isto é, que os ficheiros
chegaram intactos desde a preparação, apanhando corrupção, truncagem e cópia incompleta. Não
garante, por si só, **autenticidade**: o manifesto viaja dentro da mesma pasta que verifica e
não é assinado, pelo que quem consiga escrever nessa pasta altera a *wheel* e o manifesto no
mesmo gesto.

A autenticidade é assegurada fora do instalador, por **controlo de acesso**: a pasta da
partilha de rede onde o pacote é publicado tem escrita restrita a quem prepara o pacote e
leitura para as estações, configurada pelo Instituto de Informática, que assegura a
transferência dessa responsabilidade quando a pessoa que a detém deixar o organismo. A
decisão, o que cobre e o que não cobre estão no
[ADR-0020](docs/adr/0020-integridade-dos-artefactos-de-instalacao.md).

A garantia a declarar, perante uma auditoria, é integridade verificada por hashes sobre um
canal de distribuição com controlo de acesso. Não é prova criptográfica de autenticidade, e
depende de essas permissões estarem efectivamente configuradas.

No CI não se usa `--require-hashes`, por decisão registada no
[ADR-0020](docs/adr/0020-integridade-dos-artefactos-de-instalacao.md): obrigaria a fixar a
árvore transitiva por plataforma para as quatro combinações da matriz, e a garantia que
acrescenta (bytes idênticos) não é a que falta ao CI (versões conhecidas), que as
*constraints* já dão.

Das lacunas que esse ADR identificou, ficaram fechadas as que dependiam só de código: o
preparador e o instalador aplicam agora as *constraints*, pelo que a estação recebe as
versões que o CI testou; um pacote sem `manifesto.json` deixou de instalar, salvo saída
explícita; e uma *wheel* que esteja na pasta sem constar do manifesto faz parar, porque o
pip a resolveria como dependência sem nunca a ter conferido.

A que não dependia de código, a autenticação do manifesto, foi fechada por decisão
institucional: controlo de acesso à partilha, como descrito acima. As alternativas
criptográficas foram ponderadas e rejeitadas por não serem operáveis com regularidade neste
contexto, o que está fundamentado no ADR-0020.

## Auditoria de dependências

O CI corre `pip-audit --strict` sobre os ficheiros de *constraints* (job *auditoria*), o
que inclui as dependências transitivas resolvidas. Audita o que o projeto declara, não o
que vem pré-instalado na imagem do runner.

Política de resposta a um alerta:

1. se houver versão corrigida e ela mantiver a matriz 3.11/3.12, sobe-se a versão no
   ficheiro de *constraints* e o *pull request* segue o caminho normal;
2. se não houver correção, avalia-se a exposição real — a aplicação corre localmente, sem
   portas abertas e sem rede no processamento, pelo que muitas vulnerabilidades de rede não
   são alcançáveis aqui. A conclusão fica escrita num issue;
3. só depois disso se acrescenta uma excepção `--ignore-vuln GHSA-…` ao job, sempre com o
   número do issue em comentário ao lado, para que a excepção tenha dono e data;
4. uma excepção sem issue associado é para remover.

## Dados tratados

- **Convenções coletivas** publicadas no Boletim do Trabalho e Emprego — documentos
  públicos. Contêm nomes de signatários, que constam da publicação oficial.
- **Exports do MaxQDA** — trabalho interno do CRL, não público. Ficam em `data/raw/`,
  fora do controlo de versões, e não devem ser publicados sem decisão da instituição.

Nada disto é enviado para fora da máquina.

## Reportar uma vulnerabilidade

Se encontrar um problema de segurança, **não abra um issue público**. Contacte
diretamente a equipa do projeto no Centro de Relações Laborais, descrevendo o problema, o
impacto e como reproduzi-lo. A resposta é dada com a maior brevidade possível e a
correção é publicada com o devido crédito, se assim for desejado.

Em contexto institucional, aplica-se cumulativamente a política de segurança da informação
da entidade responsável pelos sistemas.

## Dependências

Quatro bibliotecas diretas na instalação base, todas com licença permissiva:
`pdfplumber`, `openpyxl`, `pyyaml`, `jsonschema` (mais `pytest` em desenvolvimento). A
interface gráfica usa `tkinter`, da biblioteca padrão do Python. O Docling é opcional e
tem uma cadeia de dependências distinta, que deve ser inventariada e fixada antes de uma
instalação institucional.

O Dependabot está configurado em [`.github/dependabot.yml`](.github/dependabot.yml) para as
dependências Python e para as GitHub Actions. Os alertas do Dependabot e o *secret
scanning* activam-se nas definições do repositório, como descrito acima.
