# ISSUE-0007: UnicodeEncodeError na app gráfica em estações Windows com cp1252

- **Estado:** Resolvida — 2026-09-15
- **Data:** 2026-09-14
- **GitHub:** #37 (corrigida no PR #39)
- **Onde dói:** `cct/app.py` (lançamento dos subprocessos), lançadores `.bat`

## O que acontecia

Numa estação do CRL (Windows, Python 3.13.5, região portuguesa), tanto
"Verificar instalação" (`cct.doctor`) como "Recolher do BTE…" (`cct.aquisicao`)
terminavam com:

```
UnicodeEncodeError: 'charmap' codec can't encode character '✓' ...
```

O mesmo comando corrido numa consola, fora da app gráfica, não falhava.

## Causa

A app lança cada ação como subprocesso com o stdout ligado a um pipe. Quando o
stdout de um processo Python no Windows não é uma consola real mas um pipe, a
codificação segue a definição regional da máquina (`cp1252` nas estações do
CRL), que não tem `✓`, `✗` nem `→` — os símbolos usados nas mensagens de
`doctor.py`, `aquisicao.py`, `comparar.py`, `pipeline_tema.py`, `bench_llm.py`
e `scripts/instalar_offline.py`.

Impacto prático: numa corrida real de 14 documentos, todo o trabalho tinha
terminado corretamente e o processo rebentou só na última linha do resumo — mas
o traceback fazia parecer que a corrida inteira tinha falhado.

## Resolução aplicada (2026-09-15)

`cct/subprocesso.py` (novo) expõe `ambiente_utf8()`, que devolve uma cópia do
ambiente com `PYTHONUTF8=1` e `PYTHONIOENCODING=utf-8`. O `Popen` de
`cct/app.py` passa a usá-lo, com `encoding="utf-8"` e `errors="replace"`: a
app deixa de depender da região da máquina, e nenhuma mensagem a consegue
derrubar mesmo que traga um carácter inesperado.

A construção do ambiente vive num módulo próprio por duas razões. A primeira é
que `cct/app.py` importa `tkinter`, que não existe em todas as instalações de
Python (nem em todos os contentores de CI), pelo que um teste que o importasse
seria frágil. A segunda é que o teste passa a exercitar exactamente o código
que a app corre, em vez de uma réplica das mesmas três linhas.

Os lançadores `scripts/AppCCT.bat` e `scripts/instalar_offline.bat` fixam as
mesmas variáveis, para cobrir o instalador, que corre em consola e fora do
alcance da correção da app.

`tests/test_subprocesso_utf8.py` cobre o caso: um processo filho a imprimir
`✓ … → … ✗` por um pipe com `PYTHONIOENCODING=cp1252` no ambiente de partida.
O último teste é o controlo negativo — sem a correção, o mesmo cenário falha
com `UnicodeEncodeError`, o que garante que a reprodução continua fiel.

## Confirmação em máquina real (2026-09-17)

O [gate de instalação numa estação do CRL](../docs/validacao/instalacao-estacao-crl-2026-09-17.md)
exercitou o caso. Windows 11, Python 3.13.5, região portuguesa. O registo da app mostra
`cct.aquisicao` ("Recolher do BTE…") e `cct.pipeline_tema` ("Correr pipeline") a correrem
pela interface gráfica, portanto com o stdout ligado a um pipe, e a imprimirem `→` e `⚠`.
Nenhum destes caracteres existe em cp1252. As duas acções terminaram com código 0, sem
`UnicodeEncodeError`.

Falta um pedaço do critério de aceitação do #37: a acção **"Verificar instalação"** não foi
exercitada pela app — nesse teste, o `cct.doctor` correu no terminal, onde o problema não
se manifesta. Basta clicar nesse botão dentro da aplicação para fechar o #37 sem margem.
