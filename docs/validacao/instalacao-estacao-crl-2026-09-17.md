# Gate de instalação numa estação do CRL — 2026-09-17

- **Estação:** Windows 11 (10.0.26200), Python 3.13.5, região portuguesa
- **Projeto em:** unidade mapeada `L:`, que resolve para `\\localhost\C$\profiles\CRL044628\pessoal\crl-app-cct-...`
- **Registo original:** histórico do terminal e da app, mais `manifest.json` e `relatorio.txt` da corrida
- **Resultado:** a instalação **completou-se**, mas só depois de a pessoa que instalava
  descobrir por si uma saída não documentada. A corrida do pipeline produziu os três
  artefactos esperados.

Este é o primeiro gate feito numa estação real, fora do ambiente de desenvolvimento. Vale
mais do que qualquer teste automático que tenhamos: encontrou sete problemas em menos de
uma hora, e nenhum deles aparece em CI.

## O que correu bem

| O quê | Evidência |
|---|---|
| Preparação do pacote offline | 26 *wheels*, 38,9 MB, para `win_amd64` em Python 3.11, 3.12 e 3.13 |
| Verificação de integridade | `✓ 26 ficheiro(s) conferidos contra o manifesto`, nas duas tentativas |
| Instalação, a partir de um caminho local | `✓ Successfully installed` com as 16 distribuições, e `✓ as 4 bibliotecas carregam` |
| Recolha do BTE pela app | 14 documentos descarregados, 14 nomeados |
| Pipeline pela app | 14/14 convenções, 292 cláusulas, 101 anotações, QDPX e XLSX gerados |
| **Codificação UTF-8 nos subprocessos da app (ISSUE-0007, #37)** | Ver a secção seguinte |

## O ISSUE-0007 ficou verificado em máquina real, quase por inteiro

O registo da app mostra `cct.aquisicao` e `cct.pipeline_tema` a correrem através da
interface gráfica — portanto com o *stdout* ligado a um *pipe*, que era a condição da
falha — e a imprimirem `→` e `⚠`. Nenhum destes caracteres existe em cp1252. Ambas as
acções terminaram com código 0, sem `UnicodeEncodeError`.

É exactamente o cenário que rebentava antes da correção. Falta um pedaço do critério de
aceitação do #37: a acção **"Verificar instalação"** não foi exercitada *pela app*. No
teste, o `cct.doctor` foi corrido no terminal, onde o problema não se manifesta. Para
fechar o #37 sem margem, basta clicar nesse botão dentro da aplicação.

## Os problemas encontrados

Sete, por ordem de impacto, agrupados no issue #58. Cada um tem issue próprio; a coluna
*Onde dói* aponta o ficheiro e a linha confirmados no código.

| # | Problema | Onde dói | Issue |
|---|---|---|---|
| 1 | A instalação offline falha quando o projeto está num caminho de rede (UNC) | `scripts/instalar_offline.py:182` | [0009](../../issues/0009-instalacao-offline-falha-em-caminho-unc.md) |
| 2 | A mensagem de falha do instalador aponta uma causa que não é a real | `scripts/instalar_offline.py:190-196` | [0009](../../issues/0009-instalacao-offline-falha-em-caminho-unc.md) |
| 3 | O `doctor` diz que faltam bibliotecas que estão instaladas no `.venv` | `cct/doctor.py:28-39` | [0010](../../issues/0010-python-do-projeto-em-windows.md) |
| 4 | A documentação manda correr `.venv/bin/python` em Windows | `README.md:54`, `CONTRIBUTING.md`, `docs/operacao/guia-operacao.md:118,134,141` | [0010](../../issues/0010-python-do-projeto-em-windows.md) |
| 5 | `--siglas` com ficheiro inexistente dá *traceback* cru | `cct/nomeacao.py:417,615-617` | [0011](../../issues/0011-siglas-inexistente-da-traceback.md) |
| 6 | O CI não corre em Windows nem em Python 3.13, que é o que as estações usam | `.github/workflows/testes.yml:26-27` | [0012](../../issues/0012-ci-nao-cobre-windows-nem-python-313.md) |
| 7 | A proveniência perde o *commit* quando não há git na estação | `cct/proveniencia.py:41-51` | [0013](../../issues/0013-proveniencia-sem-git-na-estacao.md) |

Há ainda um problema de extração, sem relação com a instalação, registado à parte em
[ISSUE-0014](../../issues/0014-carristur-sem-clausulas-nem-nota-de-deposito.md): quatro
documentos CARRISTUR produziram **zero cláusulas** e sinalizaram falta de nota de depósito.

## O que não é problema, e porque é importante dizê-lo

A primeira corrida do pipeline falhou com `Sem PDFs em //localhost/C$/.../data/raw/bte/bte_2026`.
Isto estava **correto**: nessa altura a pasta estava vazia, como o próprio `doctor` tinha
dito (`✗ não existe data/raw/bte/bte_<ano>/ com PDFs`). Só depois a aquisição descarregou
os 14 documentos, e aí o pipeline correu. Não há aqui defeito nenhum, e registá-lo como
problema custaria tempo a quem viesse a investigar.

As nove linhas "a confirmar" da nomeação também **não são problema**. Quatro dizem que há
vários outorgantes do mesmo lado e que o nome usa o primeiro: é comportamento deliberado,
documentado em `docs/dados/README.md` pelo PR #39, que escreve que "o aviso fica no
relatório para confirmação, mas não há escolha a fazer entre outorgantes". As outras cinco
são siglas derivadas por heurística, assinaladas precisamente para serem confirmadas por
uma pessoa. O sistema está a fazer o que deve: a pedir confirmação, não a falhar.

## Relação com o PR #39

Parte do que este gate encontrou já tinha sido trabalhada na ronda anterior, no PR #39
(*branch* `claude/sharp-ptolemy-e6ursw`, integrada em 2026-09-15 e entretanto apagada).
Vale a pena registar o que lhe pertence, para que o histórico se leia:

| O que o PR #39 fez | Como aparece neste gate |
|---|---|
| Correção UTF-8 nos subprocessos da app, mais os lançadores `.bat` | **Funcionou.** É a confirmação em máquina real descrita acima |
| `docs/operacao/siglas.exemplo.csv` e a explicação de que o `siglas.csv` é local | **Metade do ISSUE-0011 já estava feita.** O que resta é o *traceback* cru e dizer onde pôr o ficheiro |
| Documentou que, com vários outorgantes do mesmo lado, entra o primeiro no nome | Explica quatro das nove linhas "a confirmar" do teste, que **não são problema** |

O PR #39 tocou `scripts/instalar_offline.bat` para fixar as variáveis de UTF-8. É o mesmo
ficheiro envolvido no ISSUE-0009, mas o problema do caminho de rede não era conhecido
nessa altura e nada no PR #39 o podia ter apanhado.

## A lição de método

Seis dos sete problemas são de **primeira utilização**: não partem o código, partem a
pessoa que está a instalar. Nenhum deles seria apanhado pela suite de testes, porque todos
vivem na fronteira entre o produto e o ambiente real — o sistema de ficheiros da
instituição, o interpretador que está no PATH, a consola do Windows, o que a documentação
manda escrever.

A conclusão prática está no [ISSUE-0012](../../issues/0012-ci-nao-cobre-windows-nem-python-313.md):
testar em Linux e macOS, em Python 3.11 e 3.12, e entregar em Windows com Python 3.13, é
uma lacuna de cobertura que este gate tornou impossível de ignorar.
