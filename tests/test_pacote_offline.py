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

def _capturar_comando(monkeypatch, tmp_path, alvos, constraints=None):
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
    preparar_pacote_offline.descarregar(alvos, ["pdfplumber>=0.11"], constraints)
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


def test_pip_download_aplica_as_constraints(monkeypatch, tmp_path):
    """Sem constraints o pacote traria a versão mais recente, não a testada."""
    fixacao = tmp_path / "runtime.txt"
    fixacao.write_text("pdfplumber==0.11.10\n", encoding="utf-8")
    comando = _capturar_comando(monkeypatch, tmp_path, [("win_amd64", "311")],
                                constraints=[fixacao])[0]
    assert "-c" in comando
    assert comando[comando.index("-c") + 1] == str(fixacao)
    # As constraints têm de vir antes dos pacotes, como qualquer opção do pip.
    assert comando.index("-c") < comando.index("pdfplumber>=0.11")


def test_constraints_em_falta_param_com_erro_claro(monkeypatch, tmp_path):
    monkeypatch.setattr(preparar_pacote_offline, "CONSTRAINTS_RUNTIME",
                        tmp_path / "nao-existe.txt")
    with pytest.raises(SystemExit):
        preparar_pacote_offline.ficheiros_de_constraints(False)


def test_manifesto_regista_as_constraints_usadas(monkeypatch, tmp_path):
    """Uma auditoria tem de poder dizer contra que versões o pacote foi feito."""
    destino = tmp_path / "wheels"
    destino.mkdir(parents=True)
    (destino / "exemplo-1.0-py3-none-any.whl").write_bytes(b"conteudo")
    fixacao = tmp_path / "requirements" / "runtime.txt"
    fixacao.parent.mkdir(parents=True)
    fixacao.write_text("pdfplumber==0.11.10\n", encoding="utf-8")
    monkeypatch.setattr(preparar_pacote_offline, "DESTINO", destino)
    monkeypatch.setattr(preparar_pacote_offline, "RAIZ", tmp_path)

    preparar_pacote_offline.escrever_manifesto([("win_amd64", "311")], [fixacao])
    dados = json.loads((destino / "manifesto.json").read_text(encoding="utf-8"))

    assert dados["schema_version"] == 2
    assert [c["ficheiro"] for c in dados["constraints"]] == [
        "requirements/runtime.txt"]
    assert len(dados["constraints"][0]["sha256"]) == 64


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


def test_integridade_deteta_wheel_a_mais(monkeypatch, tmp_path):
    """Uma wheel fora do manifesto podia ser instalada sem ser conferida.

    O pip resolve as dependências a partir de tudo o que está em --find-links,
    não só do que o manifesto lista.
    """
    wheels, _ = _preparar_wheels(monkeypatch, tmp_path)
    (wheels / "intrusa-9.9-py3-none-any.whl").write_bytes(b"nao-conferida")
    with pytest.raises(SystemExit):
        instalar_offline.verificar_integridade()


def test_sem_manifesto_para(monkeypatch, tmp_path):
    """Um pacote sem manifesto não é verificável, logo não se instala."""
    wheels, _ = _preparar_wheels(monkeypatch, tmp_path)
    (wheels / "manifesto.json").unlink()
    with pytest.raises(SystemExit):
        instalar_offline.verificar_integridade()


def test_sem_manifesto_com_saida_explicita_avisa_mas_nao_para(
        monkeypatch, tmp_path, capsys):
    """A saída existe para pacotes antigos, e obriga a dizê-lo por escrito."""
    wheels, _ = _preparar_wheels(monkeypatch, tmp_path)
    (wheels / "manifesto.json").unlink()
    instalar_offline.verificar_integridade(aceitar_sem_manifesto=True)
    assert "NÃO verificada" in capsys.readouterr().out


def test_manifesto_ilegivel_para(monkeypatch, tmp_path):
    wheels, _ = _preparar_wheels(monkeypatch, tmp_path)
    (wheels / "manifesto.json").write_text("{isto não é json", encoding="utf-8")
    with pytest.raises(SystemExit):
        instalar_offline.verificar_integridade()


# ---------- ISSUE-0009: caminhos de rede (UNC) ----------

def test_find_links_e_passado_como_uri(monkeypatch, tmp_path):
    """O pip perde o prefixo do servidor ao normalizar um caminho UNC.

    A forma file:/// passa intacta, pelo que o --find-links tem de ser um
    URI e não um caminho de sistema de ficheiros.
    """
    comandos = []

    class Resultado:
        returncode = 0
        stdout = "Successfully installed pdfplumber\n"

    def falso_run(comando, **_):
        comandos.append(comando)
        return Resultado()

    _preparar_wheels(monkeypatch, tmp_path)
    monkeypatch.setattr(instalar_offline.subprocess, "run", falso_run)
    instalar_offline.instalar()
    comando = comandos[0]
    i = comando.index("--find-links")
    assert comando[i + 1].startswith("file:///")
    assert str(instalar_offline.WHEELS) not in comando


def test_aviso_unc_aparece_com_caminho_de_rede(monkeypatch, capsys):
    """Um caminho UNC é conhecido por falhar: o aviso tem de sair antes."""
    monkeypatch.setattr(instalar_offline, "RAIZ",
                        __import__("pathlib").PureWindowsPath(
                            r"\\servidor\partilha\crl-app-cct"))
    instalar_offline.aviso_unc()
    out = capsys.readouterr().out
    assert "caminho de rede" in out


def test_aviso_unc_silencia_com_caminho_local(monkeypatch, capsys):
    monkeypatch.setattr(instalar_offline, "RAIZ",
                        __import__("pathlib").Path("/tmp/projeto"))
    instalar_offline.aviso_unc()
    assert capsys.readouterr().out == ""


# ---------- ISSUE-0009: diagnóstico da falha do pip ----------

@pytest.mark.parametrize("padrao,esperado", [
    ("ERROR: Could not install packages due to an OSError: "
     "[Errno 2] No such file or directory: '\\\\C$\\\\wheels'", "caminho"),
    ("ERROR: Could not find a version that satisfies the requirement "
     "(Access is denied)", "permiss"),
    ("ERROR: pdfplumber-0.11.10-cp311-win_amd64.whl is not a supported "
     "wheel on this platform", "outra versão"),
    ("ERROR: algo completamente diferente", "enviar a saída"),
])
def test_diagnostico_do_pip_distingue_familias_de_causa(padrao, esperado):
    solucao = instalar_offline.diagnostico_do_pip(padrao)
    assert esperado in solucao


# ---------- ISSUE-0009: .venv reaproveitado tem de ter pip ----------

def test_venv_sem_pip_e_refeito(monkeypatch, tmp_path, capsys):
    """Um .venv deixado a meio pode ter o python mas não o pip."""
    venv = tmp_path / ".venv"
    scripts = venv / ("Scripts" if __import__("os").name == "nt" else "bin")
    scripts.mkdir(parents=True)
    (scripts / ("python.exe" if __import__("os").name == "nt" else "python")) \
        .write_text("#!fake", encoding="utf-8")
    monkeypatch.setattr(instalar_offline, "VENV", venv)

    comandos = []

    class Resultado:
        returncode = 0
        stdout = ""

    def falso_run(comando, **_):
        comandos.append(comando)
        return Resultado()

    monkeypatch.setattr(instalar_offline.subprocess, "run", falso_run)
    instalar_offline.criar_venv(refazer=False)
    assert "a refazer" in capsys.readouterr().out
    assert comandos  # o venv foi recriado


def test_manifesto_regista_versao_e_commit_da_aplicacao(monkeypatch, tmp_path):
    """As estações não têm git: é daqui que a corrida tira o commit (ISSUE-0013)."""
    destino = tmp_path / "wheels"
    destino.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "appcct"\nversion = "9.9.9"\n', encoding="utf-8")
    monkeypatch.setattr(preparar_pacote_offline, "DESTINO", destino)
    monkeypatch.setattr(preparar_pacote_offline, "RAIZ", tmp_path)
    monkeypatch.setattr(preparar_pacote_offline, "estado_git",
                        lambda raiz: {"commit": "abc123", "dirty": False})

    preparar_pacote_offline.escrever_manifesto([("win_amd64", "311")], [])
    dados = json.loads((destino / "manifesto.json").read_text(encoding="utf-8"))

    assert dados["aplicacao"] == {"versao": "9.9.9", "commit": "abc123",
                                  "alteracoes_por_commitar": False}
