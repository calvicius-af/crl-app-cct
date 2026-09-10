# SPEC-0002: instalação em estações sem acesso à internet

- **Estado:** Implementada
- **Data:** 2026-09-09
- **Autoria:** António Fula (com Claude Code)
- **Decisões relacionadas:** —
- **Nota de numeração:** o número 0001 está reservado para a spec da PR #35; se a
  ordem de integração se inverter, renumerar antes do merge.

## Problema

As três estações do CRL onde a AppCCT vai correr estão atrás de um proxy que bloqueia o
`pip`. A instalação normal (`pip install -r requirements.txt`) falha na primeira
dependência, e nenhuma das quatro bibliotecas necessárias chega à máquina.

A alternativa óbvia — pedir às comunicações uma excepção no proxy — foi ponderada e
posta de lado: teria de valer para as três máquinas, e deixaria a equipa dependente de
uma configuração de rede que ninguém no CRL sabe repor quando falhar. O atrito de
manutenção seria maior do que o problema que resolve.

## Objetivo

Instalar a AppCCT numa estação sem que a máquina faça um único pedido de rede, com um
procedimento que a equipa consegue repetir sozinha.

## Não-objetivos

- Não substitui a instalação normal onde há acesso à internet: `pip install -r
  requirements.txt` continua a ser a via corrente para quem tem rede aberta.
- Não resolve a ausência do próprio Python. A estação tem de ter Python 3.11 ou
  superior instalado; empacotar um interpretador portátil é outra decisão, para outra
  altura.
- Não cobre o extrator Docling (opcional, vários GB, com modelos que se descarregam à
  parte).
- Não faz gestão de versões: o pacote offline reflecte o `requirements.txt` do momento
  em que foi preparado.

## Comportamento

Duas fases, em máquinas diferentes.

**Fase 1, numa máquina com internet, uma vez:**

```
python scripts/preparar_pacote_offline.py [--alvos plataforma:versão,...] [--incluir-testes]
```

1. Lê as dependências de `requirements.txt` (fonte de verdade única). O `pytest` só
   entra com `--incluir-testes`.
2. Recria `vendor/wheels/` de raiz, apagando o conteúdo anterior.
3. Corre `pip download` por alvo, com `--platform`, `--python-version`, `--abi` e
   `--implementation` explícitos.
4. Escreve `MANIFESTO.txt` (leitura humana) e `manifesto.json` (leitura automática),
   ambos com o SHA-256 e o tamanho de cada wheel, de forma atómica.

Alvos por omissão: `win_amd64` para Python 3.11, 3.12 e 3.13. Sem `--alvos`, o script
avisa em texto que não está a cobrir macOS.

**Fase 2, na estação, uma vez por máquina:**

```
scripts/instalar_offline.bat        (Windows)
scripts/instalar_offline.command    (macOS)
```

1. Verifica pré-requisitos: Python 3.11+, módulo `venv`, wheels presentes.
2. Confere cada wheel contra `manifesto.json` e pára se alguma faltar ou não
   corresponder.
3. Cria `.venv` e instala com `pip --no-index --find-links vendor/wheels`.
4. Confirma que as bibliotecas carregam.

Casos-limite e o que deve acontecer:

| Situação | Comportamento esperado |
|---|---|
| `vendor/wheels/` ausente ou vazia | pára, a explicar que a pasta é preparada na fase 1 |
| wheel alterada ou truncada na cópia | pára, nomeando o ficheiro, e manda repetir a cópia |
| wheel do manifesto em falta | pára, nomeando o ficheiro |
| `manifesto.json` ausente | avisa que não verificou integridade e continua (compatível com pacotes preparados por versões anteriores) |
| Python da estação anterior a 3.11 | pára, a dizer que versão instalar |
| `--alvos` malformado | pára com o formato correcto, sem traceback |
| pacote preparado para outra versão de Python | o `pip` falha e a mensagem remete para a secção 5 da documentação |
| segunda corrida do preparador | a pasta é recriada, sem misturar versões |

## Critérios de aceitação

- [x] O instalador conclui com a rede cortada, a partir de uma `vendor/wheels/` preparada.
- [x] Nenhum dos dois scripts faz pedidos de rede na fase 2 (`--no-index`).
- [x] Uma wheel corrompida entre as duas fases é detectada antes de instalar.
- [x] Uma wheel em falta face ao manifesto é detectada antes de instalar.
- [x] Uma segunda corrida do preparador não deixa versões antigas na pasta.
- [x] Acrescentar ou mudar uma dependência em `requirements.txt` chega para que os dois
      scripts a passem a considerar, sem editar mais nenhum ficheiro.
- [x] `--incluir-testes` traz o `pytest` e a suite corre na estação.
- [x] Um `--alvos` malformado produz uma mensagem tratada, não um traceback.
- [x] As mensagens de erro nomeiam o caminho do `python` correcto para o sistema em uso.

## Plano de verificação

- **Testes automáticos**: `tests/test_pacote_offline.py` cobre o que é testável sem
  rede — a leitura de `requirements.txt` (com e sem `pytest`), a análise de `--alvos`,
  a construção do comando `pip download` com as quatro flags, e a verificação de
  integridade nos três desfechos (íntegro, alterado, em falta).
- **Verificação manual**: corrida completa das duas fases com a rede cortada; suite
  `pytest` a passar dentro do `.venv` assim criado.
- **Dados de ensaio**: as próprias wheels descarregadas; para os testes, ficheiros
  sintéticos numa pasta temporária.

## Riscos

- **O pacote é preparado para a versão de Python errada.** É a falha mais provável, e
  só se manifesta na estação. Mitigação: alvos por omissão a cobrir 3.11 a 3.13, flags
  de ABI explícitas, e uma mensagem de erro do instalador que remete para a secção
  certa da documentação.
- **Deriva entre `requirements.txt` e o que o pacote traz.** Mitigada por os dois
  scripts lerem o ficheiro em vez de terem listas próprias.
- **A política de segurança da estação bloqueia a execução de `.bat`/`.command`.** Não
  é contornável por código; nesse caso os mesmos passos correm à mão a partir da linha
  de comandos.
