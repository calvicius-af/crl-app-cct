"""Testes do doctor (ISSUE-0010).

O doctor corrido com o Python do sistema, numa estação com .venv instalado,
reportava as bibliotecas como em falta — quando o erro era o interpretador.
Estes testes verificam que a saída identifica o interpretador em uso e
distingue os dois casos. O doctor usa só stdlib, pelo que corre em qualquer SO.
"""
import sys
from pathlib import Path

import pytest

from cct import doctor


def _correr_doctor(monkeypatch, tmp_path, capsys, venv_existe=True,
                   executavel=None, sem_bibliotecas=False):
    """Corre verificar() com a raiz do projeto apontada a tmp_path."""
    raiz = tmp_path / "projeto"
    raiz.mkdir(parents=True, exist_ok=True)
    if venv_existe:
        (raiz / ".venv").mkdir(exist_ok=True)
    ficheiro_doctor = raiz / "cct" / "doctor.py"
    ficheiro_doctor.parent.mkdir(exist_ok=True)
    ficheiro_doctor.write_text("# placeholder para abspath", encoding="utf-8")
    (raiz / "codebooks").mkdir(exist_ok=True)
    (raiz / "codebooks" / "teste.yaml").write_text("tema: teste\n", encoding="utf-8")

    def falso_abspath(caminho):
        # devolver o caminho do doctor dentro do projeto fake
        return str(ficheiro_doctor)

    monkeypatch.setattr(doctor.os.path, "abspath", falso_abspath)
    if executavel is not None:
        monkeypatch.setattr(doctor.sys, "executable", executavel)
    if sem_bibliotecas:
        # simular a estação: nenhuma das bibliotecas carrega neste
        # interpretador (estão no .venv, não no Python do sistema)
        monkeypatch.setattr(
            doctor, "MODULOS",
            [("modulo_inexistente_xyz", "pacote-fake")])
    # sys.prefix/base_prefix: simular que NÃO estamos num venv do projeto
    monkeypatch.setattr(doctor.sys, "prefix", "/usr")
    monkeypatch.setattr(doctor.sys, "base_prefix", "/usr")
    codigo = doctor.verificar()
    out = capsys.readouterr().out
    return codigo, out


def test_doctor_imprime_o_interpretador(monkeypatch, tmp_path, capsys):
    """Sem o interpretador na saída, não há como diagnosticar o erro #60."""
    _, out = _correr_doctor(monkeypatch, tmp_path, capsys,
                            executavel="/usr/bin/python3")
    assert "/usr/bin/python3" in out


def test_com_venv_nao_usado_a_falha_aponta_o_interpretador(
        monkeypatch, tmp_path, capsys):
    """Com .venv presente e fora de uso, a causa provável é o interpretador,
    não a falta de instalação — repetir a instalação fecha um ciclo inútil."""
    _, out = _correr_doctor(monkeypatch, tmp_path, capsys,
                            executavel="/usr/bin/python3",
                            sem_bibliotecas=True)
    assert "não está a ser usado" in out
    assert "correr com o Python do projeto" in out
    # a sugestão não pode ser "instalar as dependências"
    assert "instalar as dependências" not in out


def test_sem_venv_mantem_a_sugestao_de_instalar(
        monkeypatch, tmp_path, capsys):
    _, out = _correr_doctor(monkeypatch, tmp_path, capsys, venv_existe=False,
                            executavel="/usr/bin/python3",
                            sem_bibliotecas=True)
    assert "instalar as dependências" in out
    assert "não está a ser usado" not in out


def test_modulos_partilhados_com_o_instalador():
    """A lista de bibliotecas não pode divergir entre doctor e instalador."""
    from scripts import instalar_offline
    assert doctor.MODULOS == instalar_offline.MODULOS


def test_doctor_reconhece_venv_pelo_diretorio_real(monkeypatch, tmp_path):
    """O prefixo de Python e o diretório do projeto são a mesma pasta."""
    venv = tmp_path / "projeto" / ".venv"
    venv.mkdir(parents=True)
    monkeypatch.setattr(doctor.sys, "prefix", str(venv))
    monkeypatch.setattr(doctor.sys, "base_prefix", str(tmp_path))
    assert doctor._venv_em_uso(venv)


def test_doctor_distingue_dados_em_falta_de_instalacao(monkeypatch, tmp_path, capsys):
    codigo, out = _correr_doctor(monkeypatch, tmp_path, capsys,
                                 venv_existe=False)
    assert codigo == 0
    assert "Instalação pronta. Faltam dados de entrada" in out
    assert "a ausência de PDFs antes da recolha é normal" in out
    assert "não impede a recolha" in out
