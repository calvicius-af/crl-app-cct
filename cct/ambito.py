"""Âmbito de um IRCT: PRI (privado), SPE (público empresarial), APU (Administração Pública).

Porque existe. A aplicação sabe processar convenções do sector privado e do
sector público empresarial. Não sabe ainda processar as da Administração
Pública — os ACT e ACEP celebrados ao abrigo da LTFP, que são depositados na
DGAEP e não na DGERT. Enquanto assim for, é preciso separar à entrada o que
entra no pipeline do que fica apenas recolhido e catalogado.

O número sequencial do BTE não serve para isso: é uma série única que atravessa
tudo. Daí um campo próprio, com vocabulário fechado de três valores.

Três letras e não duas, deliberadamente: o «PU» usado no ciclo de 2025
significava «público empresarial» mas lia-se como «público». `SPE` e `APU` não
se confundem.

Como se decide, por ordem de fiabilidade:

1. **Vocabulário** — `vocabularios/empregadores_ambito.csv`, lista editável de
   empregadores com âmbito conhecido. Tem prioridade sobre tudo o resto.
2. **Regra** — o tipo `ACEP` é sempre APU; a forma jurídica («, EPE», «, EM»,
   «Empresa Municipal») indica SPE; município, câmara, freguesia, universidade,
   politécnico ou direção-geral indicam APU.
3. **Omissão** — PRI, marcado como não verificado.

Tudo o que a *regra* classifique como SPE ou APU sai com aviso e fica por rever.
O módulo nunca decide um APU em silêncio: um falso APU retira um documento do
pipeline sem ninguém dar por isso.

Ver docs/rnc/README.md §5.2 e ADR-0016.
"""
import csv
import re
from pathlib import Path

from .localizador import _sem_acentos

VALORES = ("PRI", "SPE", "APU")
OMISSAO = "PRI"

VOCABULARIO_OMISSAO = (Path(__file__).resolve().parent.parent
                       / "vocabularios" / "empregadores_ambito.csv")

# Formas jurídicas que identificam uma entidade do sector público empresarial.
# Comparadas sobre o nome normalizado (sem acentos, minúsculas), com fronteira
# de palavra à esquerda para não apanhar «, EM» dentro de «ARMAZÉM».
RE_SPE = re.compile(
    r"(?:,\s*e\.?\s*p\.?\s*e\.?\b"          # , EPE  /  , E.P.E.
    r"|,\s*e\.?\s*m\.?\b"                   # , EM   /  , E.M.
    r"|,\s*e\.?\s*i\.?\s*m\.?\b"            # , EIM
    r"|,\s*s\.?\s*p\.?\s*a\.?\b"            # , SPA (sector público administrativo local)
    r"|\bempresa\s+municipal\b"
    r"|\bempresa\s+intermunicipal\b"
    r"|\bempresa\s+metropolitana\b"
    r"|\bservicos?\s+municipaliz\w*\b)")

# Entidades da Administração Pública em sentido estrito.
RE_APU = re.compile(
    r"(?:\bmunicipio\b|\bcamara\s+municipal\b|\bjunta\s+de\s+freguesia\b"
    r"|\bfreguesia\s+de\b|\bcomunidade\s+intermunicipal\b"
    r"|\buniversidade\b|\binstituto\s+politecnico\b|\bpolitecnico\b"
    r"|\bdirecao[- ]geral\b|\bsecretaria[- ]geral\b"
    r"|\badministracao\s+regional\b|\bgoverno\s+regional\b"
    r"|\binstituto\s+publico\b)")

TIPOS_APU = ("ACEP",)   # acordo coletivo de empregador público (LTFP)


def _normalizar(nome: str) -> str:
    return re.sub(r"\s+", " ", _sem_acentos(nome or "").lower()).strip()


def carregar_vocabulario(caminho: Path | None = None) -> dict[str, str]:
    """Lê `empregadores_ambito.csv` → {nome normalizado: âmbito}.

    Formato: `nome;ambito;fonte;data;responsavel`, separador `;`, UTF-8.
    Linhas com âmbito fora do vocabulário fechado são ignoradas com aviso — é
    preferível cair na regra do que classificar por um valor que ninguém definiu.
    """
    caminho = Path(caminho) if caminho else VOCABULARIO_OMISSAO
    tabela: dict[str, str] = {}
    if not caminho.exists():
        return tabela
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for linha in csv.reader(f, delimiter=";"):
            if len(linha) < 2 or not linha[0].strip():
                continue
            nome = _normalizar(linha[0])
            if nome in ("nome", "empregador", "denominacao"):
                continue            # cabeçalho
            valor = linha[1].strip().upper()
            if valor not in VALORES:
                print(f"AVISO — âmbito desconhecido em {caminho.name}: "
                      f"{linha[0]!r} → {valor!r} (ignorado)")
                continue
            tabela[nome] = valor
    return tabela


def classificar(empregador: str, tipo: str = "",
                vocabulario: dict[str, str] | None = None
                ) -> tuple[str, str, str | None]:
    """Devolve `(ambito, origem, aviso)`.

    `origem` é `vocabulario`, `regra` ou `omissao`. `aviso` vem preenchido
    sempre que a decisão precisa de confirmação humana — ou seja, sempre que o
    resultado não vem do vocabulário e não é o PRI por omissão.
    """
    tipo_norm = re.sub(r"[^A-Z]", "", (tipo or "").upper())
    nome = _normalizar(empregador)

    if vocabulario:
        if nome in vocabulario:
            return vocabulario[nome], "vocabulario", None
        for chave, valor in vocabulario.items():
            if chave and len(chave) >= 6 and chave in nome:
                return valor, "vocabulario", None

    if tipo_norm.startswith(TIPOS_APU):
        return "APU", "regra", f"tipo {tipo} → APU por regra — confirmar"
    if RE_APU.search(nome):
        return "APU", "regra", (f"«{empregador[:60]}» classificado APU por regra "
                                "— confirmar antes de excluir do pipeline")
    if RE_SPE.search(nome):
        return "SPE", "regra", (f"«{empregador[:60]}» classificado SPE por regra "
                                "— confirmar")
    return OMISSAO, "omissao", None


def processavel(ambito: str) -> bool:
    """O pipeline lê PRI e SPE. APU recolhe-se e cataloga-se; não se processa."""
    return (ambito or OMISSAO).upper() in ("PRI", "SPE")
