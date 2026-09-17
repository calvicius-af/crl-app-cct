#!/usr/bin/env python3
"""Barreira única de segurança para o repositório.

Corre localmente e no CI para impedir que entrem no repositório dados
internos (PDFs de origem, exports de QDA, folhas de cálculo com informação
real), ficheiros não aprovados dentro de ``examples/`` e segredos (chaves,
tokens, palavras-passe) no conteúdo dos ficheiros versionados.

Substitui a verificação equivalente que hoje está escrita em bash no
workflow de CI, para que a mesma lógica possa ser corrida localmente antes
de um commit.

Uso:
    python scripts/verificar_seguranca.py
    python scripts/verificar_seguranca.py --apenas segredos
    python scripts/verificar_seguranca.py --apenas dados --apenas credenciais
    python scripts/verificar_seguranca.py --verboso
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

# Extensões que só devem existir dentro de examples/ ou tests/ (dados de
# origem, exports de ferramentas de QDA, folhas de cálculo). Fora dessas
# pastas, um ficheiro com uma destas extensões é quase sempre um sinal de
# que dados internos foram versionados por engano.
EXTENSOES_DADOS = (".pdf", ".qdpx", ".mqda", ".xlsx", ".qdc")

# Allowlist explícita do que é autorizado dentro de examples/. Qualquer
# ficheiro versionado sob examples/ que não corresponda a um destes padrões
# é reportado como problema. Padrões são avaliados com fnmatch sobre o
# caminho relativo à raiz do repositório (separadores "/").
ALLOWLIST_EXAMPLES = (
    "examples/README.md",  # nota introdutória do directório de exemplos
    "examples/metricas_calibracao.json",  # métricas agregadas, sem dados pessoais
    # Artefactos anonimizados de saída de cada caso de exemplo (ADR-0013):
    # os PDFs de origem em examples/*/entrada/ não são redistribuídos, só
    # os resultados já anonimizados em examples/*/saida/.
    "examples/*/saida/*.txt",
    "examples/*/saida/*.doc.json",
    "examples/*/saida/*.qdpx",
    "examples/*/saida/*.xlsx",
)

# Padrões de segredos. Cada entrada é (nome legível, padrão compilado).
# O nome é o que aparece no relatório — nunca o valor encontrado.
_VALOR_ASPAS = r'["\']([^"\']{12,})["\']'
_CHAVES_GENERICAS = (
    "password", "passwd", "senha", "secret", "token",
    "api_key", "apikey", "access_key",
)
PADROES_SEGREDOS = (
    ("chave privada PEM", re.compile(
        r"-----BEGIN (RSA |EC |OPENSSH |PGP |DSA )?PRIVATE KEY-----")),
    # Dois formatos em uso: o clássico (ghp_, gho_, ghu_, ghs_, ghr_) e o
    # token pessoal de granularidade fina (github_pat_), que é mais longo e
    # admite underscores no corpo. O prefixo "gh[pousr]_" exige underscore na
    # terceira posição, pelo que não colide com "github_pat_".
    ("token do GitHub", re.compile(
        r"gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}")),
    ("chave de acesso AWS", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("token do Slack", re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("chave da OpenAI/Anthropic", re.compile(r"sk-(ant-)?[A-Za-z0-9_-]{20,}")),
    ("segredo genérico atribuído", re.compile(
        r"(?i)\b(?:" + "|".join(_CHAVES_GENERICAS) + r")\b\s*[:=]\s*" + _VALOR_ASPAS)),
)

# Sub-padrões que, se presentes no valor de um "segredo genérico atribuído",
# indicam que se trata de um exemplo, placeholder ou marcador — não um
# segredo real.
_MARCADORES_INOFENSIVOS = (
    "example", "exemplo", "dummy", "xxx", "<", "${",
    "changeme", "placeholder", "redacted",
)

TAMANHO_MAXIMO_FICHEIRO = 2 * 1024 * 1024  # ~2 MB

# O próprio script e o seu ficheiro de testes contêm os padrões acima como
# texto literal (para os definir e para os testar) — têm de ser ignorados
# pela verificação de segredos, senão disparam contra si próprios.
FICHEIROS_IGNORADOS_SEGREDOS = (
    "scripts/verificar_seguranca.py",
    "tests/test_verificar_seguranca.py",
)


def _valor_e_placeholder(valor: str) -> bool:
    if valor.strip("*") == "":
        return True
    valor_lower = valor.lower()
    return any(marcador in valor_lower for marcador in _MARCADORES_INOFENSIVOS)


def listar_ficheiros_versionados(raiz: Path) -> list[str]:
    """Devolve os caminhos (relativos à raiz, com "/") dos ficheiros versionados."""
    resultado = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=raiz, capture_output=True, check=True)
    bruto = resultado.stdout.decode("utf-8")
    return [caminho for caminho in bruto.split("\0") if caminho]


def verificar_dados_fora_do_sitio(caminhos: list[str]) -> list[str]:
    """Ficheiros de dados (PDF, QDPX, MQDA, XLSX, QDC) fora de examples/ e tests/."""
    problemas = []
    for caminho in caminhos:
        sufixo = Path(caminho).suffix.lower()
        if sufixo not in EXTENSOES_DADOS:
            continue
        if caminho.startswith("examples/") or caminho.startswith("tests/"):
            continue
        problemas.append(
            f"{caminho}: ficheiro de dados ({sufixo}) fora de examples/ ou tests/")
    return problemas


def verificar_credenciais(caminhos: list[str]) -> list[str]:
    """Ficheiros .env versionados, excepto .env.example."""
    problemas = []
    for caminho in caminhos:
        nome = Path(caminho).name
        if nome == ".env.example":
            continue
        if nome == ".env" or nome.startswith(".env."):
            problemas.append(f"{caminho}: ficheiro de credenciais versionado")
    return problemas


def verificar_allowlist_examples(caminhos: list[str]) -> list[str]:
    """Ficheiros sob examples/ que não constam da allowlist deste script."""
    problemas = []
    for caminho in caminhos:
        if not (caminho == "examples" or caminho.startswith("examples/")):
            continue
        if any(fnmatch.fnmatch(caminho, padrao) for padrao in ALLOWLIST_EXAMPLES):
            continue
        problemas.append(
            f"{caminho}: não está na allowlist de examples/ deste script "
            "(scripts/verificar_seguranca.py); adiciona um padrão se for deliberado")
    return problemas


def _ficheiro_e_binario(dados: bytes) -> bool:
    return b"\x00" in dados


def _procurar_segredos_no_texto(caminho: str, texto: str) -> list[str]:
    problemas = []
    for numero_linha, linha in enumerate(texto.splitlines(), 1):
        for nome_padrao, padrao in PADROES_SEGREDOS:
            for correspondencia in padrao.finditer(linha):
                if nome_padrao == "segredo genérico atribuído":
                    valor = correspondencia.group(correspondencia.lastindex or 0)
                    if _valor_e_placeholder(valor):
                        continue
                problemas.append(f"{caminho}:{numero_linha}: possível {nome_padrao}")
    return problemas


def verificar_segredos(caminhos: list[str], raiz: Path) -> list[str]:
    """Varre o conteúdo dos ficheiros de texto versionados à procura de segredos."""
    problemas = []
    for caminho in caminhos:
        if caminho in FICHEIROS_IGNORADOS_SEGREDOS:
            continue
        caminho_absoluto = raiz / caminho
        try:
            if not caminho_absoluto.is_file():
                continue
            if caminho_absoluto.stat().st_size > TAMANHO_MAXIMO_FICHEIRO:
                continue
            dados = caminho_absoluto.read_bytes()
        except OSError:
            continue
        if _ficheiro_e_binario(dados):
            continue
        try:
            texto = dados.decode("utf-8")
        except UnicodeDecodeError:
            continue
        problemas.extend(_procurar_segredos_no_texto(caminho, texto))
    return problemas


VERIFICACOES = {
    "dados": ("Dados fora do sítio", lambda caminhos, raiz: verificar_dados_fora_do_sitio(caminhos)),
    "credenciais": ("Credenciais versionadas", lambda caminhos, raiz: verificar_credenciais(caminhos)),
    "exemplos": ("Allowlist de examples/", lambda caminhos, raiz: verificar_allowlist_examples(caminhos)),
    "segredos": ("Segredos no conteúdo", lambda caminhos, raiz: verificar_segredos(caminhos, raiz)),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apenas", action="append", choices=sorted(VERIFICACOES), default=None,
        help="corre só esta verificação (repetível); por omissão corre todas")
    parser.add_argument(
        "--verboso", action="store_true",
        help="mostra também as verificações que passaram")
    args = parser.parse_args()

    raiz = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, check=True, text=True).stdout.strip())
    caminhos = listar_ficheiros_versionados(raiz)

    chaves = args.apenas or list(VERIFICACOES)
    total_problemas = 0
    for chave in chaves:
        titulo, funcao = VERIFICACOES[chave]
        problemas = funcao(caminhos, raiz)
        if problemas:
            total_problemas += len(problemas)
            print(f"FALHOU — {titulo}:")
            for problema in problemas:
                print(f"  - {problema}")
        elif args.verboso:
            print(f"OK — {titulo}")

    if total_problemas:
        print(f"\n{total_problemas} problema(s) encontrado(s).")
        return 1
    print("OK — nenhum problema de segurança encontrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
