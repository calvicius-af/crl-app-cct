"""Testes do pacote de instalação offline (SPEC-0002).

Cobrem o que é verificável sem rede: a leitura das dependências, a análise dos
alvos, a forma do comando `pip download` e a verificação de integridade. A
corrida real dos dois scripts fica para a verificação manual descrita na spec.
"""
import json

import pytest

from scripts import instalar_offline, preparar_pacote_offline


# ---------- dependências lidas de requirements.txt ----------

def test_pacotes_vem_de_requirements_sem_pytest():
    pacotes = preparar_pacote_offline.pacotes_de_requirements(incluir_testes=False)
    nomes = [p.split(">")[0].split("=")[0].lower() for p in pacotes]
    assert nomes == ["pdfplumber", "openpyxl", "pyyaml", "jsonschema"]


def test_incluir_testes_acrescenta_o_pytest():
    pacotes = preparar_pacote_offline.pacotes_de_requirements(incluir_testes=True)
    assert any(p.lower().startswith("pytest") for p in pacotes)


def test_comentarios_do_requirements_nao_entram():
    # requirements.txt tem linhas comentadas com nomes de pacotes reais
    # (docling, docling-hierarchical-pdf) que não devem ser descarregados.
    pacotes = preparar_pacote_offline.pacotes_de_requirements(incluir_testes=True)
    assert not any("docling" in p.lower() for p in pacotes)


# ---------- análise dos alvos ----------

def test_alvo_valido():
    assert preparar_pacote_offline._analisar_alvo("win_amd64:311") == ("win_amd64", "311")


@pytest.mark.parametrize("texto", ["win_amd64", "win_amd64:", ":311", "win_amd64:3.11"])
def test_alvo_invalido_levanta_value_error(texto):
    with pytest.raises(ValueError):
        preparar_pacote_offline._analisar_alvo(texto)


# ---------- comando pip download ----------

def _capturar_comando(monkeypatch, tmp_path, alvos):
    """Corre descarregar() sem rede, devolvendo os comandos que teria corrido."""
    comandos = []

    class Resultado:
        returncode = 0
        stdout = ""

    def falso_run(comando, **_):
        comandos.append(comando)
        return Resultado()

    monkeypatch.setattr(preparar_pacote_offline, "DESTINO", tmp_path / "wheels")
    monkeypatch.setattr(preparar_pacote_offline, "RAIZ", tmp_path)
    monkeypatch.setattr(preparar_pacote_offline.subprocess, "run", falso_run)
    preparar_pacote_offline.descarregar(alvos, ["pdfplumber>=0.11"])
    return comandos


def test_pip_download_fixa_abi_e_implementacao(monkeypatch, tmp_path):
    """Sem estas flags o pip pode filtrar pelo ABI do interpretador em uso."""
    comando = _capturar_comando(monkeypatch, tmp_path, [("win_amd64", "313")])[0]
    for flag, valor in [("--platform", "win_amd64"), ("--python-version", "313"),
                        ("--abi", "cp313"), ("--implementation", "cp")]:
        assert flag in comando, f"falta {flag}"
        assert comando[comando.index(flag) + 1] == valor


def test_um_comando_por_alvo(monkeypatch, tmp_path):
    comandos = _capturar_comando(
        monkeypatch, tmp_path, [("win_amd64", "311"), ("win_amd64", "312")])
    assert len(comandos) == 2
    assert [c[c.index("--abi") + 1] for c in comandos] == ["cp311", "cp312"]


def test_pasta_e_recriada_a_cada_corrida(monkeypatch, tmp_path):
    """Uma wheel de uma versão anterior não pode sobreviver à nova corrida."""
    destino = tmp_path / "wheels"
    destino.mkdir(parents=True)
    antiga = destino / "pdfplumber-0.0.1-py3-none-any.whl"
    antiga.write_text("versão antiga", encoding="utf-8")

    _capturar_comando(monkeypatch, tmp_path, [("win_amd64", "311")])
    assert not antiga.exists()
    assert destino.is_dir()


# ---------- verificação de integridade ----------

def _preparar_wheels(monkeypatch, tmp_path, conteudo=b"conteudo-da-wheel"):
    from cct.proveniencia import sha256

    wheels = tmp_path / "wheels"
    wheels.mkdir(parents=True)
    wheel = wheels / "exemplo-1.0-py3-none-any.whl"
    wheel.write_bytes(conteudo)
    (wheels / "manifesto.json").write_text(json.dumps({
        "schema_version": 1,
        "gerado": "2026-09-09T00:00:00+00:00",
        "alvos": ["win_amd64/py311"],
        "wheels": [{"ficheiro": wheel.name, "sha256": sha256(wheel),
                    "bytes": wheel.stat().st_size}],
    }), encoding="utf-8")
    monkeypatch.setattr(instalar_offline, "WHEELS", wheels)
    return wheels, wheel


def test_integridade_aceita_pacote_intacto(monkeypatch, tmp_path):
    _preparar_wheels(monkeypatch, tmp_path)
    instalar_offline.verificar_integridade()  # não levanta


def test_integridade_deteta_wheel_alterada(monkeypatch, tmp_path):
    _, wheel = _preparar_wheels(monkeypatch, tmp_path)
    wheel.write_bytes(b"conteudo-adulterado")
    with pytest.raises(SystemExit):
        instalar_offline.verificar_integridade()


def test_integridade_deteta_wheel_em_falta(monkeypatch, tmp_path):
    _, wheel = _preparar_wheels(monkeypatch, tmp_path)
    wheel.unlink()
    with pytest.raises(SystemExit):
        instalar_offline.verificar_integridade()


def test_sem_manifesto_avisa_mas_nao_para(monkeypatch, tmp_path, capsys):
    """Pacotes preparados por versões anteriores não têm manifesto.json."""
    wheels, _ = _preparar_wheels(monkeypatch, tmp_path)
    (wheels / "manifesto.json").unlink()
    instalar_offline.verificar_integridade()
    assert "não verificada" in capsys.readouterr().out


def test_manifesto_ilegivel_para(monkeypatch, tmp_path):
    wheels, _ = _preparar_wheels(monkeypatch, tmp_path)
    (wheels / "manifesto.json").write_text("{isto não é json", encoding="utf-8")
    with pytest.raises(SystemExit):
        instalar_offline.verificar_integridade()
