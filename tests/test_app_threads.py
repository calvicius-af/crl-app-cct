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


# ---------- confirmação das siglas (#38) ----------

PENDENTES = [
    {"chave": "a", "doc_id": "D1", "titulo": "", "outros_avisos": [],
     "siglas": [("Sindicato Nacional dos Motoristas", "Motoristas")]},
    {"chave": "b", "doc_id": "D2", "titulo": "", "outros_avisos": ["2 outorgantes do lado sindical"],
     "siglas": [("Empresa Metropolitana de Estacionamento da Maia, EM", "EmpresaMetropolitana")]},
    {"chave": "c", "doc_id": "D3", "titulo": "", "outros_avisos": [], "siglas": []},
]


def test_decisoes_gravam_so_os_documentos_confirmados(app_mod):
    siglas, chaves, motivos, ajustes = app_mod.decisoes_confirmadas(
        PENDENTES, {"a", "b"},
        {("b", "Empresa Metropolitana de Estacionamento da Maia, EM"): " EMEM "})
    assert chaves == ["a", "b"] and motivos == ajustes == []
    assert siglas == {"Sindicato Nacional dos Motoristas": "Motoristas",
                      "Empresa Metropolitana de Estacionamento da Maia, EM": "EMEM"}


@pytest.mark.parametrize("apagada", ["", "  "])
def test_sigla_apagada_impede_a_confirmacao_e_diz_porque(app_mod, apagada):
    """Revisão do PR #96: um campo esvaziado ("") não volta à sugestão; nada
    se grava, nem os outros documentos marcados, e o motivo é dito."""
    siglas, chaves, motivos, _ = app_mod.decisoes_confirmadas(
        PENDENTES, {"a", "c"}, {("a", "Sindicato Nacional dos Motoristas"): apagada})
    assert (siglas, chaves) == ({}, [])
    assert motivos == ["D1: sigla vazia para «Sindicato Nacional dos Motoristas»"]


def test_sigla_so_com_pontuacao_impede_a_confirmacao(app_mod):
    """Revisão do PR #96: «!!!» passava na janela e desaparecia na gravação,
    e o documento era nomeado com a sigla adivinhada."""
    siglas, chaves, motivos, _ = app_mod.decisoes_confirmadas(
        PENDENTES, {"a"}, {("a", "Sindicato Nacional dos Motoristas"): " !!! "})
    assert (siglas, chaves) == ({}, [])
    assert motivos == ["D1: «!!!» não tem letras nem algarismos "
                       "(sigla de «Sindicato Nacional dos Motoristas»)"]


def test_sigla_normalizada_como_no_nome_e_mostrada_antes(app_mod):
    siglas, chaves, motivos, ajustes = app_mod.decisoes_confirmadas(
        PENDENTES, {"a"}, {("a", "Sindicato Nacional dos Motoristas"): "S.N.Mó."})
    assert chaves == ["a"] and motivos == []
    assert siglas == {"Sindicato Nacional dos Motoristas": "SNMo"}
    assert ajustes == ["«S.N.Mó.» fica SNMo"]


MESMA_ENTIDADE = [
    {"chave": k, "doc_id": d, "titulo": "", "outros_avisos": [],
     "siglas": [(nome, "EmpresaMetropolitana")]}
    for k, d, nome in (("x", "D1", "Empresa Metropolitana"),
                       ("y", "D2", "Empresa Metropolitana."),
                       ("z", "D3", "EMPRESA METROPOLITANA"))]


def test_a_mesma_entidade_com_siglas_diferentes_impede_a_confirmacao(app_mod):
    """Revisão do PR #96: EMM num documento e a sugerida no outro davam as duas
    chaves confirmadas e só uma sigla gravada; o primeiro saía com um nome
    diferente do confirmado. A entidade compara-se como no siglas.csv."""
    siglas, chaves, motivos, _ = app_mod.decisoes_confirmadas(
        MESMA_ENTIDADE, {"x", "z"}, {("x", "Empresa Metropolitana"): "EMM"})
    assert (siglas, chaves) == ({}, [])
    assert motivos == ["«Empresa Metropolitana» tem siglas diferentes "
                       "(EMM em D1; EmpresaMetropolitana em D3): a entidade tem uma só "
                       "sigla, escrever a mesma em todos"]
    # a mesma sigla em todos: confirma, uma linha no siglas.csv por entidade
    siglas, chaves, motivos, _ = app_mod.decisoes_confirmadas(
        MESMA_ENTIDADE, {"x", "z"}, {("x", "Empresa Metropolitana"): "EMM",
                                     ("z", "EMPRESA METROPOLITANA"): "emm".upper()})
    assert chaves == ["x", "z"] and motivos == []
    assert set(siglas.values()) == {"EMM"}


class _Var:
    def __init__(self, value=None):
        self.valor = value

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor


class _Widget:
    criados: list = []

    def __init__(self, *_a, **opcoes):
        self.opcoes = opcoes
        _Widget.criados.append(self)

    def __getattr__(self, _nome):             # pack, bind, title, destroy, …
        return lambda *a, **k: None


def test_janela_das_siglas_comeca_desmarcada_e_exige_cada_confirmacao(app, app_mod, monkeypatch):
    """Revisão do PR #96: com os documentos já marcados, um clique em «Gravar
    e nomear» confirmava-os todos sem revisão. Começam desmarcados."""
    from cct import nomeacao, recolha
    tk = sys.modules["tkinter"]
    _Widget.criados = []
    for nome in ("Toplevel", "Canvas"):
        monkeypatch.setattr(tk, nome, _Widget, raising=False)
    for nome in ("Frame", "Label", "Scrollbar", "Checkbutton", "Entry", "Button"):
        monkeypatch.setattr(tk.ttk, nome, _Widget, raising=False)
    monkeypatch.setattr(tk, "BooleanVar", _Var, raising=False)
    monkeypatch.setattr(tk, "StringVar", _Var, raising=False)
    avisos = []
    monkeypatch.setattr(tk.messagebox, "showinfo", lambda *a, **k: avisos.append(a[1]))
    monkeypatch.setattr(tk.messagebox, "showwarning", lambda *a, **k: avisos.append(a[1]),
                        raising=False)
    respostas = []
    monkeypatch.setattr(tk.messagebox, "askyesno",
                        lambda *a, **k: avisos.append(a[1]) or respostas.pop(0), raising=False)
    monkeypatch.setattr(recolha.Registo, "carregar", classmethod(lambda cls, *_a: None))
    monkeypatch.setattr(nomeacao, "tabela_de_siglas", lambda *_a: {})
    monkeypatch.setattr(nomeacao, "pendentes", lambda *_a: PENDENTES)
    gravadas = []
    monkeypatch.setattr(nomeacao, "gravar_siglas", lambda _f, s: gravadas.append(s))
    lancados = []
    app._lancar = lambda args, depois=None: lancados.append(args)

    app._confirmar_siglas()
    marcas = [w.opcoes["variable"] for w in _Widget.criados if "variable" in w.opcoes]
    campos = [w.opcoes["textvariable"] for w in _Widget.criados if "textvariable" in w.opcoes]
    gravar = next(w.opcoes["command"] for w in _Widget.criados
                  if w.opcoes.get("text") == "Gravar e nomear")
    assert len(marcas) == 3 and not any(m.get() for m in marcas)

    gravar()                                   # nada revisto: nada gravado
    assert avisos == ["Nenhum documento confirmado."] and gravadas == lancados == []

    marcas[0].set(True)
    campos[0].set("")                          # sigla apagada por inteiro
    gravar()
    assert "sigla vazia" in avisos[-1] and gravadas == lancados == []

    campos[0].set("!!!")                       # só pontuação
    gravar()
    assert "não tem letras nem algarismos" in avisos[-1] and gravadas == lancados == []

    campos[0].set("S.N.M.")                    # a normalização muda: pergunta antes
    respostas.append(False)
    gravar()
    assert "«S.N.M.» fica SNM" in avisos[-1] and gravadas == lancados == []
    respostas.append(True)
    gravar()
    assert gravadas == [{"Sindicato Nacional dos Motoristas": "SNM"}]
    assert lancados == [["cct.nomeacao", "--aplicar", "--confirmar", "a"]]


def test_janela_partilha_a_caixa_da_mesma_entidade(app, app_mod, monkeypatch):
    """Revisão do PR #96: uma correção num documento vale para os outros da
    mesma entidade, como no siglas.csv, que guarda uma sigla por entidade."""
    from cct import nomeacao, recolha
    tk = sys.modules["tkinter"]
    _Widget.criados = []
    for nome in ("Toplevel", "Canvas"):
        monkeypatch.setattr(tk, nome, _Widget, raising=False)
    for nome in ("Frame", "Label", "Scrollbar", "Checkbutton", "Entry", "Button"):
        monkeypatch.setattr(tk.ttk, nome, _Widget, raising=False)
    monkeypatch.setattr(tk, "BooleanVar", _Var, raising=False)
    monkeypatch.setattr(tk, "StringVar", _Var, raising=False)
    monkeypatch.setattr(recolha.Registo, "carregar", classmethod(lambda cls, *_a: None))
    monkeypatch.setattr(nomeacao, "tabela_de_siglas", lambda *_a: {})
    monkeypatch.setattr(nomeacao, "pendentes", lambda *_a: MESMA_ENTIDADE)
    app._confirmar_siglas()
    campos = [w.opcoes["textvariable"] for w in _Widget.criados if "textvariable" in w.opcoes]
    assert len(campos) == 3 and campos[0] is campos[1] is campos[2]


def test_a_acao_do_fim_corre_na_thread_principal(app, app_mod):
    """A janela das siglas abre-se quando a recolha acaba, na thread principal."""
    chamadas = []
    app._depois = lambda: chamadas.append(threading.current_thread())
    app.fila.put(app_mod.FIM_DA_CORRIDA)
    app._despejar_fila()
    assert chamadas == [threading.main_thread()] and app._depois is None
