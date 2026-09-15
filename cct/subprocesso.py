"""Lançamento de subprocessos Python com a saída sempre em UTF-8.

A app gráfica (`cct.app`) corre cada ação como um subprocesso com o stdout
ligado a um pipe. Quando o stdout de um processo Python no Windows não é uma
consola real mas um pipe, a codificação segue a definição regional da máquina
(`cp1252` nas estações do CRL) — e os símbolos `✓`, `✗` e `→`, usados nas
mensagens de `cct.doctor`, `cct.aquisicao` e outros, rebentam com
`UnicodeEncodeError` ao serem impressos.

A correção é forçar UTF-8 no processo filho, independentemente da região
configurada na máquina. Ver ISSUE #37.
"""
import os


def ambiente_utf8(base=None):
    """Devolve uma cópia do ambiente com a saída do Python forçada a UTF-8.

    `base` permite passar um ambiente já preparado (por omissão, o do processo
    atual). Não altera `os.environ`.
    """
    ambiente = dict(os.environ if base is None else base)
    ambiente["PYTHONUTF8"] = "1"          # modo UTF-8 do interpretador
    ambiente["PYTHONIOENCODING"] = "utf-8"  # stdout/stderr, mesmo em pipe
    return ambiente
