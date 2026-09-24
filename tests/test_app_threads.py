"""A app gráfica só mexe nos widgets a partir da thread principal (issue #45).

A thread de trabalho chamava `b_correr.configure(...)` no fim da corrida. O
Tkinter não é seguro para chamadas fora da thread do `mainloop`; em macOS isso
dá falhas intermitentes. Agora a thread só põe mensagens na fila, e é a thread
principal, ao despejá-la, que reativa o botão.

Os testes não abrem janelas: substituem o `tkinter` por módulos falsos (há
interpretadores, como o dos contentores de CI, sem ele) e criam a app sem
passar pelo `Tk.__init__`.
"""
import importlib
import sys
import threading
import time
import types

import pytest


class _Botao:
    def __init__(self):
        self.chamadas = []

    def configure(self, **opcoes):
        self.chamadas.append((threading.current_thread(), opcoes))


@pytest.fixture
def app_mod(monkeypatch):
    tk = types.ModuleType("tkinter")
    tk.Tk = type("Tk", (), {})
    for nome in ("filedialog", "messagebox", "ttk"):
        sub = types.ModuleType(f"tkinter.{nome}")
        setattr(tk, nome, sub)
        monkeypatch.setitem(sys.modules, f"tkinter.{nome}", sub)
    tk.messagebox.showinfo = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "tkinter", tk)
    monkeypatch.delitem(sys.modules, "cct.app", raising=False)
    return importlib.import_module("cct.app")


@pytest.fixture
def app(app_mod):
    import queue
    app = app_mod.AppCCT.__new__(app_mod.AppCCT)
    app.fila = queue.Queue()
    app.em_curso = False
    app.b_correr = _Botao()
    app.escrito = []
    app._escrever = app.escrito.append
    app.after = lambda *a: None
    return app


def _esperar_fim(app, app_mod, limite=30):
    """Espera que a thread de trabalho ponha o fim na fila, sem o consumir."""
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        if app_mod.FIM_DA_CORRIDA in list(app.fila.queue):
            return
        time.sleep(0.02)
    raise AssertionError("a corrida não terminou")


def test_a_thread_de_trabalho_nao_toca_nos_widgets(app, app_mod):
    principal = threading.current_thread()
    app._lancar(["json.tool", "--help"])
    _esperar_fim(app, app_mod)
    assert all(t is principal for t, _ in app.b_correr.chamadas), \
        "a thread de trabalho mexeu no botão"
    assert app.em_curso, "só a thread principal dá a corrida por terminada"

    app._despejar_fila()
    assert app.b_correr.chamadas[-1] == (principal, {"state": "normal"})
    assert not app.em_curso
    assert any("terminado com código 0" in t for t in app.escrito)


def test_segundo_clique_antes_do_arranque_nao_lanca_outra_corrida(app, app_mod, monkeypatch):
    """A corrida conta como em curso desde o clique, e não só depois de o
    subprocesso arrancar na outra thread."""
    lancadas = []
    monkeypatch.setattr(app_mod.threading, "Thread",
                        lambda target, daemon: types.SimpleNamespace(
                            start=lambda: lancadas.append(target)))
    app._lancar(["json.tool", "--help"])
    app._lancar(["json.tool", "--help"])
    assert len(lancadas) == 1
