"""A saída dos subprocessos da app chega intacta, mesmo em região cp1252.

Reproduz o ISSUE #37: nas estações Windows do CRL, um processo Python cujo
stdout é um pipe codifica a saída na região da máquina (cp1252), que não tem
`✓`, `✗` nem `→`. Aqui simula-se a mesma condição em qualquer sistema,
impondo `PYTHONIOENCODING=cp1252` no ambiente de partida.
"""
import os
import subprocess
import sys

from cct.subprocesso import ambiente_utf8

# as mesmas marcas usadas em cct/doctor.py, cct/aquisicao.py e outros
PROGRAMA = "print('✓ pronto → 7 documentos ✗ 1 falhou')"
ESPERADO = "✓ pronto → 7 documentos ✗ 1 falhou"


def _correr(ambiente):
    return subprocess.run([sys.executable, "-u", "-c", PROGRAMA],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, encoding="utf-8", errors="replace",
                          env=ambiente)


def test_ambiente_forca_utf8():
    ambiente = ambiente_utf8({"PYTHONIOENCODING": "cp1252"})
    assert ambiente["PYTHONUTF8"] == "1"
    assert ambiente["PYTHONIOENCODING"] == "utf-8"


def test_nao_altera_o_ambiente_do_processo_atual():
    antes = os.environ.get("PYTHONIOENCODING")
    ambiente_utf8()
    assert os.environ.get("PYTHONIOENCODING") == antes


def test_ambiente_herdado_e_preservado():
    ambiente = ambiente_utf8({"CCT_MARCA": "valor"})
    assert ambiente["CCT_MARCA"] == "valor"


def test_saida_com_simbolos_sobrevive_ao_pipe():
    base = dict(os.environ)
    base["PYTHONIOENCODING"] = "cp1252"   # o que rebenta na estação do CRL
    r = _correr(ambiente_utf8(base))
    assert r.returncode == 0, r.stdout
    assert ESPERADO in r.stdout


def test_o_cenario_sem_correcao_e_mesmo_o_que_rebenta():
    """Guarda do teste anterior: sem `ambiente_utf8`, o filho falha."""
    base = dict(os.environ)
    base["PYTHONUTF8"] = "0"
    base["PYTHONIOENCODING"] = "cp1252"
    r = _correr(base)
    assert r.returncode != 0
    assert "UnicodeEncodeError" in r.stdout
