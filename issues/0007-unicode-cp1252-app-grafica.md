# ISSUE-0007: UnicodeEncodeError na app gráfica em estações Windows com cp1252

- **Estado:** Resolvida — 2026-09-15
- **Data:** 2026-09-14
- **GitHub:** #37
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
`cct/app.py` passa a usá-lo, com `encoding="utf-8"` e `errors="replace"` — a
app deixa de depender da região da máquina, e nenhuma mensagem a consegue
derrubar mesmo que traga um carácter inesperado.

Os lançadores `scripts/AppCCT.bat` e `scripts/instalar_offline.bat` fixam as
mesmas variáveis, para cobrir o instalador, que corre em consola e fora do
alcance da correção da app.

`tests/test_subprocesso_utf8.py` cobre o caso: um processo filho a imprimir
`✓ … → … ✗` por um pipe com `PYTHONIOENCODING=cp1252` no ambiente de partida.
O último teste é o controlo negativo — sem a correção, o mesmo cenário falha
com `UnicodeEncodeError`, o que garante que a reprodução continua fiel.

## Por confirmar

Falta a validação em máquina real do CRL (critério de aceitação do #37): correr
"Verificar instalação" e "Recolher do BTE…" numa estação com região portuguesa
e confirmar que terminam sem traceback.
