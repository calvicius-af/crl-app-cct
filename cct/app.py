"""App gráfica local do pipeline CCT (tkinter — Mac e Windows, sem
dependências além do Python standard).

Uso: python -m cct.app
"""
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

RAIZ = Path(__file__).resolve().parent.parent      # raiz do repositório
DADOS = RAIZ / "data" / "raw"
RESULTADOS = RAIZ / "results"


class AppCCT(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pipeline CCT → MaxQDA")
        self.geometry("760x640")
        self.fila = queue.Queue()
        self.processo = None
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
                self._escrever(self.fila.get_nowait())
        except queue.Empty:
            pass
        self.after(150, self._despejar_fila)

    def _lancar(self, argumentos):
        if self.processo is not None:
            messagebox.showinfo("Em curso", "Já há uma corrida em curso.")
            return
        self._escrever("\n" + "=" * 60 + "\n$ " + " ".join(argumentos) + "\n")
        self.b_correr.configure(state="disabled")

        def trabalho():
            try:
                p = subprocess.Popen([sys.executable, "-u", "-m", *argumentos],
                                     cwd=str(RAIZ), stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True)
                self.processo = p
                for linha in p.stdout:
                    self.fila.put(linha)
                p.wait()
                self.fila.put(f"\n[terminado com código {p.returncode}]\n")
            except Exception as e:
                self.fila.put(f"\nERRO: {e}\n")
            finally:
                self.processo = None
                self.b_correr.configure(state="normal")

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


def main():
    AppCCT().mainloop()


if __name__ == "__main__":
    main()
