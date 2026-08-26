"""Verificador de ambiente: diz em português o que falta e como resolver.

Uso: python -m cct.doctor
"""
import sys
from pathlib import Path


def verificar() -> int:
    problemas = 0

    def ok(msg):
        print(f"  ✓ {msg}")

    def falha(msg, solucao):
        nonlocal problemas
        problemas += 1
        print(f"  ✗ {msg}\n    → {solucao}")

    print("== Python")
    if sys.version_info >= (3, 11):
        ok(f"Python {sys.version.split()[0]}")
    else:
        falha(f"Python {sys.version.split()[0]} é antigo",
              "instalar Python 3.11 ou superior (python.org)")

    print("== Bibliotecas")
    for mod, pacote in [("pdfplumber", "pdfplumber"), ("openpyxl", "openpyxl"),
                        ("yaml", "pyyaml"), ("jsonschema", "jsonschema")]:
        try:
            __import__(mod)
            ok(pacote)
        except ImportError:
            falha(f"falta a biblioteca {pacote}",
                  f"correr: python -m pip install {pacote}")
    try:
        import tkinter  # noqa: F401
        ok("tkinter (app gráfica)")
    except ImportError:
        falha("tkinter indisponível (app gráfica não abre; o resto funciona)",
              "Windows: reinstalar Python com a opção 'tcl/tk'; "
              "Mac: brew install python-tk")

    print("== Pastas e ficheiros")
    raiz = Path(__file__).resolve().parent.parent  # raiz do repositório
    dados = raiz / "data" / "raw"
    if (raiz / "codebooks").glob("*.yaml"):
        n = len(list((raiz / "codebooks").glob("*.yaml")))
        ok(f"codebooks/ com {n} tema(s)")
    else:
        falha("não há codebooks", "ver docs/operacao/PROMPTS_CODEBOOKS.md")
    pastas_bte = sorted((dados / "bte").glob("bte_*"))
    if pastas_bte:
        ok("pastas de PDFs: " + ", ".join(p.name for p in pastas_bte))
    else:
        falha("não existe data/raw/bte/bte_<ano>/ com PDFs",
              "criar a pasta e copiar os PDFs "
              "(ver docs/operacao/GUIA_OPERACAO.md §2 e docs/dados/README.md)")
    variaveis = sorted((dados / "maxqda").glob("VariaveisDocumento*.xlsx"))
    if variaveis:
        ok(f"variáveis do MaxQDA: {variaveis[-1].name}")
    else:
        falha("sem data/raw/maxqda/VariaveisDocumento*.xlsx (opcional mas recomendado)",
              "exportar do MaxQDA (GUIA §3.2)")
    if sorted((dados / "maxqda").glob("*.qdc")):
        ok("codebook master (.qdc) presente")
    else:
        print("  · sem .qdc do master (opcional — códigos sem descrições/cores)")
    if (dados / "textos_consolidados").is_dir():
        ok("data/raw/textos_consolidados/ presente (comparações diacrónicas ativas)")
    else:
        print("  · sem data/raw/textos_consolidados/ (comparações diacrónicas inativas)")
    if (raiz / "examples").is_dir():
        n = len([d for d in (raiz / "examples").iterdir() if d.is_dir()])
        ok(f"examples/ com {n} exemplo(s) completo(s) (PDF → TXT → QDPX)")

    print("== Docling (opcional, --extrator docling)")
    try:
        import docling  # noqa: F401
        ok("docling instalado (tabelas de anexos e layouts difíceis)")
    except ImportError:
        print("  · docling não instalado (só afeta a opção --extrator docling)")

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
        print(f"{problemas} problema(s) a resolver — ver as setas acima.")
    else:
        print("Tudo pronto. Podes correr o pipeline "
              "(docs/operacao/guia-operacao.md §4).")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(verificar())
