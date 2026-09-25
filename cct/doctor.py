"""Verificador de ambiente: diz em português o que falta e como resolver.

Uso: python -m cct.doctor
"""
import os
import sys
from pathlib import Path

# Mapeamento módulo -> pacote, partilhado com o instalador offline para não
# haver duas listas a divergir uma da outra (ISSUE-0010).
MODULOS = [("pdfplumber", "pdfplumber"), ("openpyxl", "openpyxl"),
           ("yaml", "pyyaml"), ("jsonschema", "jsonschema")]


def _python_do_venv() -> Path:
    raiz = Path(os.path.abspath(__file__)).parent.parent
    if os.name == "nt":
        return raiz / ".venv" / "Scripts" / "python.exe"
    return raiz / ".venv" / "bin" / "python"


def _venv_em_uso(venv: Path) -> bool:
    r"""Compara diretórios reais, incluindo UNC e unidades mapeadas no Windows.

    `sys.prefix` pode usar `\\localhost\C$` e a raiz do projeto `L:` para a
    mesma pasta. Comparar representações textuais dá um falso aviso.
    """
    if sys.prefix == sys.base_prefix or not venv.is_dir():
        return False
    try:
        return Path(sys.prefix).samefile(venv)
    except OSError:
        return os.path.normcase(os.path.abspath(sys.prefix)) == \
            os.path.normcase(os.path.abspath(venv))


def _solucao_tkinter() -> str:
    """Como obter o Tk para o Python em uso, por sistema e origem do Python."""
    versao = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.platform == "darwin":
        base = sys.base_prefix
        if "homebrew" in base.lower() or "/Cellar/" in base or base.startswith("/usr/local"):
            return (f"o Python {versao} veio do Homebrew, que traz o Tk à parte: "
                    f"brew install python-tk@{versao} (o .venv não precisa de ser refeito)")
        if base.startswith(("/Library/Developer", "/Applications/Xcode")) or base == "/usr":
            return ("é o Python da Apple (ferramentas de linha de comandos), com um Tk "
                    "antigo: instalar o Python 3.11 ou superior de python.org, que traz "
                    "o Tk 8.6, e refazer o .venv (scripts/instalar_offline.command)")
        return ("instalar o Python 3.11 ou superior de python.org, que traz o Tk 8.6, "
                "e refazer o .venv (scripts/instalar_offline.command)")
    if os.name == "nt":
        return "reinstalar o Python com a opção «tcl/tk and IDLE» ativa"
    return "instalar o pacote do Tk do sistema (Debian/Ubuntu: sudo apt install python3-tk)"


def problema_tkinter() -> str | None:
    """O que impede a app gráfica de abrir neste Python, ou `None`.

    Na corrida de 2025 em macOS a app não abriu e o terminal funcionou: é o
    sintoma de um Python sem o Tk (Homebrew) ou com um Tk antigo (o da Apple).
    """
    try:
        import tkinter
    except ImportError as e:
        return (f"o Python {sys.version.split()[0]} em {sys.executable} não tem o "
                f"tkinter ({e}); a app gráfica não abre, o resto funciona. Solução: "
                + _solucao_tkinter())
    if float(tkinter.TkVersion) < 8.6:
        return (f"o Tk {tkinter.TkVersion} deste Python é antigo e não abre janelas "
                "nas versões recentes do macOS. Solução: " + _solucao_tkinter())
    return None


def verificar() -> int:
    problemas = 0
    dados_pendentes = 0

    def ok(msg):
        print(f"  ✓ {msg}")

    def falha(msg, solucao):
        nonlocal problemas
        problemas += 1
        print(f"  ✗ {msg}\n    → {solucao}")

    def pendente(msg, solucao):
        nonlocal dados_pendentes
        dados_pendentes += 1
        print(f"  · {msg}\n    → {solucao}")

    print("== Python")
    if sys.version_info >= (3, 11):
        ok(f"Python {sys.version.split()[0]}")
    else:
        falha(f"Python {sys.version.split()[0]} é antigo",
              "instalar Python 3.11 ou superior (python.org)")
    # ISSUE-0010: dizer sempre com que interpretador se está a correr, e
    # detectar o .venv do projeto que não está a ser usado — sem isto, o
    # doctor corrido com o Python do sistema reporta como em falta
    # bibliotecas que estão instaladas no .venv.
    print(f"  · interpretador: {sys.executable}")
    raiz = Path(os.path.abspath(__file__)).parent.parent
    venv = raiz / ".venv"
    venv_em_uso = _venv_em_uso(venv)
    if venv.is_dir() and not venv_em_uso:
        print(f"  · o projeto tem um .venv ({venv}) que não está a ser usado")
        print(f"    → correr com o Python do projeto: "
              f"{_python_do_venv()} -m cct.doctor")

    print("== Bibliotecas")
    for mod, pacote in MODULOS:
        try:
            __import__(mod)
            ok(pacote)
        except ImportError:
            if venv.is_dir() and not venv_em_uso:
                falha(f"falta a biblioteca {pacote} (ou está no .venv que "
                      "não está a ser usado)",
                      f"correr com o Python do projeto: "
                      f"{_python_do_venv()} -m cct.doctor")
            else:
                falha(f"falta a biblioteca {pacote}",
                      "instalar as dependências: duplo clique em "
                      "scripts/instalar_offline.bat (Windows) ou "
                      "scripts/instalar_offline.command (macOS) — instalação sem internet, "
                      "ver docs/institucional/instalacao-offline.md; "
                      f"com acesso à internet basta: python -m pip install {pacote}")
    problema_tk = problema_tkinter()
    if problema_tk is None:
        import tkinter
        ok(f"tkinter com Tk {tkinter.TkVersion} (app gráfica)")
    else:
        texto, _, solucao = problema_tk.partition(" Solução: ")
        falha(texto, solucao)

    print("== Pastas e ficheiros")
    raiz = Path(__file__).resolve().parent.parent  # raiz do repositório
    dados = raiz / "data" / "raw"
    n = len(list((raiz / "codebooks").glob("*.yaml")))
    if n:
        ok(f"codebooks/ com {n} tema(s)")
    else:
        falha("não há codebooks", "ver docs/operacao/prompts-codebooks.md")
    pastas_bte = sorted((dados / "bte").glob("bte_*"))
    if pastas_bte:
        ok("pastas de PDFs: " + ", ".join(p.name for p in pastas_bte))
    else:
        pendente("ainda não há PDFs em data/raw/bte/bte_<ano>/",
                 "para a recolha automática, colocar índices .xlsx em "
                 "data/raw/indices/ e seguir docs/operacao/guia-operacao.md §2.1; "
                 "a ausência de PDFs antes da recolha é normal")
    variaveis = sorted((dados / "maxqda").glob("VariaveisDocumento*.xlsx"))
    if variaveis:
        ok(f"variáveis do MaxQDA: {variaveis[-1].name}")
    else:
        print("  · sem data/raw/maxqda/VariaveisDocumento*.xlsx "
              "(opcional; não impede a recolha — GUIA §3.2)")
    if sorted((dados / "maxqda").glob("*.qdc")):
        ok("codebook master (.qdc) presente")
    else:
        print("  · sem .qdc do master (opcional — códigos sem descrições/cores)")
    if (dados / "textos_consolidados").is_dir():
        ok("data/raw/textos_consolidados/ presente (comparações diacrónicas ativas)")
    else:
        print("  · sem data/raw/textos_consolidados/ (comparações diacrónicas inativas)")
    indices = sorted((dados / "indices").glob("*.xlsx")) \
        if (dados / "indices").is_dir() else []
    if indices:
        ok(f"data/raw/indices/ com {len(indices)} índice(s) do BTE "
           f"(recolha automática disponível)")
    else:
        pendente("sem data/raw/indices/*.xlsx — a recolha automática do BTE "
                 "não tem o que ler",
                 "copiar os índices fornecidos pela equipa antes de correr "
                 "cct.aquisicao (docs/operacao/guia-operacao.md §2.1)")
    registo = raiz / "data" / "registo" / "registo_bte.jsonl"
    if registo.exists():
        n = sum(1 for l in registo.read_text(encoding="utf-8").splitlines() if l.strip())
        ok(f"registo da recolha com {n} documento(s) "
           "(guarda os ordinais atribuídos — não apagar)")
    if (raiz / "examples").is_dir():
        n = len([d for d in (raiz / "examples").iterdir() if d.is_dir()])
        ok(f"examples/ com {n} exemplo(s) completo(s) (PDF → TXT → QDPX)")

    print("== Docling (opcional, --extrator docling)")
    try:
        import docling  # noqa: F401
        ok("docling instalado (tabelas de anexos e layouts difíceis)")
    except ImportError:
        print("  · docling não instalado (só afeta a opção --extrator docling)")

    print("== Rede (opcional — só a recolha do BTE, ADR-0015)")
    import os as _os
    if _os.environ.get("CCT_RECOLHA_REDE") == "1":
        print("  · CCT_RECOLHA_REDE=1: a recolha está autorizada a ligar-se ao BTE")
    else:
        print("  · desligada por omissão (a recolha só liga com --confirmar-rede)")

    print("== LM Studio (opcional, camada semântica)")
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:1234/v1/models",
                                    timeout=3) as r:
            import json
            modelos = [m["id"] for m in json.load(r)["data"]]
        ok(f"servidor ativo ({len(modelos)} modelos)")
    except Exception:
        print("  · LM Studio não está a correr (só afeta a opção semântica)")

    print()
    if problemas:
        print(f"{problemas} problema(s) da instalação — ver as setas acima.")
    elif dados_pendentes:
        print("Instalação pronta. Faltam dados de entrada para algumas operações "
              "— ver as setas acima.")
    else:
        print("Tudo pronto. Podes correr o pipeline "
              "(docs/operacao/guia-operacao.md §4).")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(verificar())
