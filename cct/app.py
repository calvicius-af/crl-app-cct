"""App gráfica local do pipeline CCT (tkinter — Mac e Windows, sem
dependências além do Python standard).

Uso: python -m cct.app
"""
import queue
import subprocess
import sys
import threading
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    _JANELA = tk.Tk
except ImportError:      # sem o Tk: main() explica o que falta e como resolver
    tk = filedialog = messagebox = ttk = None  # type: ignore[assignment]
    _JANELA = object  # type: ignore[misc, assignment]

from cct.subprocesso import ambiente_utf8

RAIZ = Path(__file__).resolve().parent.parent      # raiz do repositório
DADOS = RAIZ / "data" / "raw"
RESULTADOS = RAIZ / "results"
# Posto na fila pela thread de trabalho quando o subprocesso termina. Só a
# thread principal mexe nos widgets (issue #45): o Tkinter não é seguro para
# chamadas de outras threads, e em macOS isso dá falhas intermitentes.
FIM_DA_CORRIDA = object()


def decisoes_confirmadas(lista: list[dict], marcados: set[str],
                         valores: dict[tuple[str, str], str]) -> tuple[dict[str, str], list[str]]:
    """O que a janela de confirmação grava e que documentos manda nomear (#38).

    `lista` vem de `nomeacao.pendentes`; `marcados` são as chaves dos
    documentos que a pessoa confirmou; `valores[(chave, outorgante)]` é a sigla
    escrita na janela (a sugerida, ou a corrigida). Devolve as siglas a gravar
    no siglas.csv, `{outorgante: sigla}`, e as chaves a nomear.
    """
    siglas: dict[str, str] = {}
    chaves = []
    for p in lista:
        if p["chave"] not in marcados:
            continue
        escritas = {nome: (valores.get((p["chave"], nome)) or sugerida).strip()
                    for nome, sugerida in p["siglas"]}
        if any(not s for s in escritas.values()):
            continue                     # uma sigla apagada: não se confirma
        siglas.update(escritas)
        chaves.append(p["chave"])
    return siglas, chaves


class AppCCT(_JANELA):
    def __init__(self):
        super().__init__()
        self.title("Pipeline CCT → MaxQDA")
        self.geometry("760x640")
        self.fila = queue.Queue()
        self.em_curso = False
        self._construir()
        self._preencher_defaults()
        self.after(150, self._despejar_fila)

    # ---------- interface ----------
    def _construir(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        linha = 0

        def campo(rotulo, var, escolher, dica=""):
            nonlocal linha
            ttk.Label(frm, text=rotulo).grid(row=linha, column=0, sticky="w", pady=3)
            ttk.Entry(frm, textvariable=var).grid(row=linha, column=1, sticky="ew", padx=6)
            ttk.Button(frm, text="Escolher…", command=escolher, width=10)\
                .grid(row=linha, column=2)
            if dica:
                linha += 1
                ttk.Label(frm, text=dica, foreground="gray")\
                    .grid(row=linha, column=1, sticky="w", padx=6)
            linha += 1

        self.v_pdfs = tk.StringVar()
        campo("Pasta de PDFs *", self.v_pdfs,
              lambda: self._dir(self.v_pdfs),
              "um PDF por convenção (ex.: data/raw/bte/bte_2026)")

        self.v_indices = tk.StringVar()
        campo("Índices do BTE", self.v_indices,
              lambda: self._dir(self.v_indices),
              "pasta com os .xlsx da DGERT, para a recolha automática")

        ttk.Label(frm, text="Tema (codebook) *").grid(row=linha, column=0, sticky="w", pady=3)
        self.v_codebook = tk.StringVar()
        self.cb_codebook = ttk.Combobox(frm, textvariable=self.v_codebook, state="readonly")
        self.cb_codebook.grid(row=linha, column=1, sticky="ew", padx=6)
        linha += 1

        self.v_variaveis = tk.StringVar()
        campo("Variáveis MaxQDA", self.v_variaveis,
              lambda: self._fich(self.v_variaveis, [("Excel", "*.xlsx")]))
        self.v_master = tk.StringVar()
        campo("Codebook master (.qdc)", self.v_master,
              lambda: self._fich(self.v_master, [("QDC", "*.qdc")]))
        self.v_metricas = tk.StringVar()
        campo("Métricas (calibração AUTO)", self.v_metricas,
              lambda: self._fich(self.v_metricas, [("JSON", "*.json")]))
        self.v_versoes = tk.StringVar()
        campo("Versões anteriores", self.v_versoes,
              lambda: self._dir(self.v_versoes),
              "pasta tipo data/raw/textos_consolidados (comparações diacrónicas)")
        self.v_out = tk.StringVar()
        campo("Pasta de resultados *", self.v_out, lambda: self._dir(self.v_out))

        self.v_semantica = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Camada semântica (LM Studio ligado, modelo gemma)",
                        variable=self.v_semantica).grid(row=linha, column=1, sticky="w", padx=6)
        linha += 1

        botoes = ttk.Frame(frm)
        botoes.grid(row=linha, column=0, columnspan=3, pady=8, sticky="ew")
        self.b_correr = ttk.Button(botoes, text="▶  Correr pipeline", command=self._correr)
        self.b_correr.pack(side="left")
        ttk.Button(botoes, text="Recolher do BTE…",
                   command=self._recolher).pack(side="left", padx=8)
        ttk.Button(botoes, text="Confirmar siglas…",
                   command=self._confirmar_siglas).pack(side="left")
        ttk.Button(botoes, text="Comparar versões (pasta)…",
                   command=self._comparar).pack(side="left", padx=8)
        ttk.Button(botoes, text="Verificar instalação",
                   command=self._doctor).pack(side="left")
        ttk.Button(botoes, text="Abrir resultados",
                   command=self._abrir_out).pack(side="right")
        linha += 1

        self.log = tk.Text(frm, height=16, state="disabled", wrap="word")
        self.log.grid(row=linha, column=0, columnspan=3, sticky="nsew", pady=(6, 0))
        frm.rowconfigure(linha, weight=1)

    def _preencher_defaults(self):
        yamls = sorted((RAIZ / "codebooks").glob("*.yaml"))
        self.cb_codebook["values"] = [str(y.relative_to(RAIZ)) for y in yamls]
        if yamls:
            self.v_codebook.set(str(yamls[0].relative_to(RAIZ)))
        self.v_indices.set(str(DADOS / "indices"))
        pastas = sorted((DADOS / "bte").glob("bte_*"))
        if pastas:
            self.v_pdfs.set(str(pastas[-1]))
        variaveis = sorted((DADOS / "maxqda").glob("VariaveisDocumento*.xlsx"))
        if variaveis:
            self.v_variaveis.set(str(variaveis[-1]))
        qdc = sorted((DADOS / "maxqda").glob("*.qdc"))
        if qdc:
            self.v_master.set(str(qdc[-1]))
        metricas = sorted((RESULTADOS / "metricas").glob("baseline_*/metricas.json"))
        if metricas:
            self.v_metricas.set(str(metricas[-1]))
        if (DADOS / "textos_consolidados").is_dir():
            self.v_versoes.set(str(DADOS / "textos_consolidados"))
        self.v_out.set(str(RESULTADOS / "corrida"))

    # ---------- utilitários ----------
    def _dir(self, var):
        d = filedialog.askdirectory(initialdir=str(RAIZ))
        if d:
            var.set(d)

    def _fich(self, var, tipos):
        f = filedialog.askopenfilename(initialdir=str(RAIZ), filetypes=tipos)
        if f:
            var.set(f)

    def _escrever(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", texto)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _despejar_fila(self):
        try:
            while True:
                mensagem = self.fila.get_nowait()
                if mensagem is FIM_DA_CORRIDA:
                    self.em_curso = False
                    self.b_correr.configure(state="normal")
                    # o que a ação pediu para fazer no fim, já na thread principal
                    depois, self._depois = getattr(self, "_depois", None), None
                    if depois:
                        depois()
                else:
                    self._escrever(mensagem)
        except queue.Empty:
            pass
        self.after(150, self._despejar_fila)

    def _lancar(self, argumentos, depois=None):
        if self.em_curso:
            messagebox.showinfo("Em curso", "Já há uma corrida em curso.")
            return
        self._depois = depois
        # marcado aqui, na thread principal, e não depois de o subprocesso
        # arrancar: um segundo clique nesse intervalo lançava outra corrida
        self.em_curso = True
        self._escrever("\n" + "=" * 60 + "\n$ " + " ".join(argumentos) + "\n")
        self.b_correr.configure(state="disabled")

        def trabalho():
            try:
                # As mensagens do pipeline usam símbolos fora da tabela de
                # caracteres por omissão do Windows (cp1252, ex.: ✓ ✗ →). Sem
                # forçar UTF-8 aqui, o processo filho rebenta com
                # UnicodeEncodeError ao escrever para este pipe (que, ao
                # contrário de uma consola, não tem o tratamento especial do
                # Windows para Unicode) — foi o que aconteceu em estações do
                # CRL com a codificação regional portuguesa. Ver ISSUE-0007 e
                # tests/test_subprocesso_utf8.py.
                # o `with` fecha o pipe e espera pelo processo
                with subprocess.Popen([sys.executable, "-u", "-m", *argumentos],
                                      cwd=str(RAIZ), stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True,
                                      encoding="utf-8", errors="replace",
                                      env=ambiente_utf8()) as p:
                    for linha in p.stdout:
                        self.fila.put(linha)
                self.fila.put(f"\n[terminado com código {p.returncode}]\n")
            except Exception as e:
                self.fila.put(f"\nERRO: {e}\n")
            finally:
                self.fila.put(FIM_DA_CORRIDA)

        threading.Thread(target=trabalho, daemon=True).start()

    # ---------- ações ----------
    def _correr(self):
        if not self.v_pdfs.get() or not self.v_codebook.get() or not self.v_out.get():
            messagebox.showwarning("Campos em falta",
                                   "Preenche a pasta de PDFs, o tema e a pasta de resultados.")
            return
        args = ["cct.pipeline_tema", "--pdfs", self.v_pdfs.get(),
                "--codebook", self.v_codebook.get(), "--out", self.v_out.get()]
        if self.v_variaveis.get():
            args += ["--variaveis", self.v_variaveis.get()]
        if self.v_master.get():
            args += ["--master", self.v_master.get()]
        if self.v_metricas.get():
            args += ["--metricas", self.v_metricas.get()]
        if self.v_versoes.get():
            args += ["--pasta-versoes", self.v_versoes.get()]
        if self.v_semantica.get():
            args += ["--semantica"]
        self._lancar(args)

    def _recolher(self):
        """Recolha do BTE + nomeação. É a única ação que liga à internet."""
        indices = Path(self.v_indices.get() or (DADOS / "indices"))
        if not indices.exists() or not list(indices.glob("*.xlsx")):
            messagebox.showwarning(
                "Sem índices",
                f"Não há ficheiros .xlsx em\n{indices}\n\n"
                "A recolha lê a lista de documentos dos índices que a DGERT "
                "fornece por número do BTE.")
            return
        autorizar = messagebox.askyesno(
            "Ligar à internet?",
            "A recolha vai descarregar os documentos listados nos índices a "
            "partir de bte.dgcp.mtsss.gov.pt.\n\n"
            "É a única parte da aplicação que usa a rede, e só descarrega "
            "documentos públicos do Boletim do Trabalho e Emprego.\n\n"
            "Sim — descarregar e renomear.\n"
            "Não — apenas simular e mostrar o que seria feito.")
        args = ["cct.aquisicao", "--indices", str(indices),
                "--destino", str(DADOS / "bte")]
        if autorizar:
            args += ["--confirmar-rede", "--aplicar"]
        # no fim, as siglas que ficaram por confirmar (#38)
        self._lancar(args, depois=lambda: self._confirmar_siglas(aplicar=autorizar,
                                                                 so_se_houver=True))

    def _confirmar_siglas(self, aplicar: bool = True, so_se_houver: bool = False):
        """A janela de confirmação das siglas adivinhadas, documento a documento (#38).

        Mostra cada documento por confirmar, com a sigla sugerida de cada
        outorgante, que se pode aceitar ou corrigir, e os outros avisos. As
        siglas confirmadas ficam no siglas.csv da equipa, para não voltarem a
        ser perguntadas; a seguir corre só a nomeação dos documentos
        confirmados (offline, sem descarregar nada).
        """
        from cct.nomeacao import SIGLAS_EQUIPA, gravar_siglas, pendentes, tabela_de_siglas
        from cct.recolha import REGISTO_OMISSAO, Registo

        registo = Registo.carregar(REGISTO_OMISSAO)
        lista = pendentes(registo, tabela_de_siglas([]))
        if not lista:
            if not so_se_houver:
                messagebox.showinfo("Siglas", "Não há documentos por confirmar.")
            return
        janela = tk.Toplevel(self)
        janela.title(f"Confirmar siglas — {len(lista)} documento(s)")
        janela.geometry("820x520")
        ttk.Label(janela, padding=8, wraplength=780, text=(
            "Estas siglas foram adivinhadas a partir do nome do outorgante. "
            "Confirmar cada documento, corrigindo a sigla se for preciso. As "
            "siglas confirmadas ficam gravadas e não voltam a ser perguntadas; "
            "com vários outorgantes do mesmo lado, o nome usa sempre o primeiro."
        )).pack(fill="x")
        # os botões antes da lista: o `pack` dá o espaço por ordem, e uma lista
        # longa empurrava-os para fora da janela
        botoes = ttk.Frame(janela, padding=8)
        botoes.pack(side="bottom", fill="x")
        tela = tk.Canvas(janela, highlightthickness=0)
        barra = ttk.Scrollbar(janela, orient="vertical", command=tela.yview)
        corpo = ttk.Frame(tela, padding=8)
        corpo.bind("<Configure>", lambda _e: tela.configure(scrollregion=tela.bbox("all")))
        tela.create_window((0, 0), window=corpo, anchor="nw")
        tela.configure(yscrollcommand=barra.set)
        tela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        marcas: dict[str, tk.BooleanVar] = {}
        campos: dict[tuple[str, str], tk.StringVar] = {}
        for p in lista:
            marcas[p["chave"]] = tk.BooleanVar(value=bool(p["siglas"]))
            ttk.Checkbutton(corpo, variable=marcas[p["chave"]],
                            text=f"{p['doc_id'] or p['chave']}").pack(anchor="w", pady=(8, 0))
            ttk.Label(corpo, text=p["titulo"], foreground="gray",
                      wraplength=740).pack(anchor="w", padx=24)
            for nome, sugerida in p["siglas"]:
                linha = ttk.Frame(corpo)
                linha.pack(anchor="w", padx=24, fill="x")
                campos[(p["chave"], nome)] = tk.StringVar(value=sugerida)
                ttk.Entry(linha, width=18,
                          textvariable=campos[(p["chave"], nome)]).pack(side="left")
                ttk.Label(linha, text=nome[:90]).pack(side="left", padx=6)
            for aviso in p["outros_avisos"]:
                ttk.Label(corpo, text=f"• {aviso}", foreground="gray",
                          wraplength=720).pack(anchor="w", padx=24)

        def gravar():
            siglas, chaves = decisoes_confirmadas(
                lista, {c for c, v in marcas.items() if v.get()},
                {k: v.get() for k, v in campos.items()})
            if not chaves:
                messagebox.showinfo("Siglas", "Nenhum documento confirmado.", parent=janela)
                return
            if siglas:
                gravar_siglas(SIGLAS_EQUIPA, siglas)
            janela.destroy()
            if aplicar:
                args = ["cct.nomeacao", "--aplicar"]
                for chave in chaves:
                    args += ["--confirmar", chave]
                self._lancar(args)
            else:
                self._escrever(f"\nSiglas gravadas em {SIGLAS_EQUIPA}. A recolha foi "
                               "uma simulação: os documentos são nomeados na próxima "
                               "recolha com escrita.\n")

        ttk.Button(botoes, text="Gravar e nomear", command=gravar).pack(side="right")
        ttk.Button(botoes, text="Agora não", command=janela.destroy).pack(side="right", padx=8)

    def _comparar(self):
        pasta = filedialog.askdirectory(
            initialdir=self.v_versoes.get() or str(DADOS / "textos_consolidados"),
            title="Pasta com as versões de UMA convenção")
        if not pasta:
            return
        out = Path(self.v_out.get() or RESULTADOS) / \
            f"comparacao_{Path(pasta).name}.xlsx"
        out.parent.mkdir(parents=True, exist_ok=True)
        self._lancar(["cct.comparar", "--pasta", pasta, "--out", str(out)])

    def _doctor(self):
        self._lancar(["cct.doctor"])

    def _abrir_out(self):
        out = Path(self.v_out.get() or RESULTADOS)
        out.mkdir(parents=True, exist_ok=True)
        if sys.platform == "darwin":
            subprocess.run(["open", str(out)])
        elif sys.platform.startswith("win"):
            import os
            os.startfile(str(out))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(out)])


def main() -> int:
    """Abre a janela; sem o Tk, diz no terminal porquê e como resolver.

    No macOS a app fechava sem mensagem quando o Python não tinha o Tk
    (corrida de 2025): o lançador fechava a janela do terminal com o erro.
    """
    from cct.doctor import problema_tkinter

    problema = problema_tkinter()
    if problema:
        print(f"A app gráfica não pode abrir: {problema}\n"
              "O pipeline continua a funcionar no terminal "
              "(docs/operacao/guia-operacao.md).", file=sys.stderr)
        return 1
    try:
        app = AppCCT()
    except tk.TclError as e:
        print(f"O Tk não conseguiu abrir a janela: {e}\n"
              "Correr «python -m cct.doctor» e enviar o resultado.", file=sys.stderr)
        return 1
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
