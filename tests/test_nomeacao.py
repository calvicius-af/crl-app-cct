"""Testes da nomeação dos documentos recolhidos (SPEC-0001).

Correm inteiramente offline, sobre o índice real do BTE n.º 31 de 2026 definido
em `tests/test_recolha.py`. O que estes testes protegem é o contrato de nomes:
todo o resto do pipeline (localizador, comparador, cruzamento com as variáveis
do MaxQDA) lê o nome do ficheiro.
"""
import pytest

from cct.localizador import interpretar_doc_id
from cct.nomeacao import (MAX_NOME, MAX_SIGLA, carregar_siglas, e_sindical, nome_documento,
                          nomear, separar_outorgantes, sigla)
from cct.recolha import Registo, recolher

from .test_recolha import URL, AbridorFalso, escrever_indice

NOMES_ESPERADOS = [
    "26_PR_001_BTE_31_ACRAL_CESP",
    "26_PR_002_BTE_31_CNIS_FNSTFPS",
    "26_PR_003_BTE_31_AEVP_FESAHT",
    "26_PR_004_BTE_31_EmpresaMetropolitana_SINTAP",
    "26_PR_005_BTE_31_APSolutionsGMBH_STAS",
    "26_PR_006_BTE_31_CARRISTUR_Transportes",
]


@pytest.fixture()
def registo_com_recolha(tmp_path):
    """Registo com os seis documentos do BTE 31/2026 já 'descarregados'."""
    indice = escrever_indice(tmp_path)
    registo = Registo(tmp_path / "registo.jsonl")
    recolher([indice], tmp_path / "interim", registo, rede=True,
             abridor=AbridorFalso(), pausa=0)
    return registo, tmp_path


# ------------------------------------------------------------------- siglas

@pytest.mark.parametrize("nome,esperado", [
    ("Associação do Comércio e Serviços da Região do Algarve - ACRAL", "ACRAL"),
    ("CESP - Sindicato dos Trabalhadores do Comércio, Escritórios e Serviços", "CESP"),
    ("Associação das Empresas de Vinho do Porto (AEVP)", "AEVP"),
    ("Sindicato dos Trabalhadores da Actividade Seguradora (STAS)", "STAS"),
    ("Confederação Nacional das Instituições de Solidariedade - CNIS", "CNIS"),
    ("CARRISTUR - Inovação em Transportes Urbanos e Regionais, Sociedade "
     "Unipessoal L.da", "CARRISTUR"),
    # sigla a meio do nome, antes do sufixo da retificação
    ("Sindicato dos Trabalhadores dos Transportes - SITRA - Retificação", "SITRA"),
    ("Federação dos Sindicatos de Transportes e Comunicações - FECTRANS - "
     "Retificação", "FECTRANS"),
])
def test_sigla_declarada_no_nome(nome, esperado):
    s, aviso = sigla(nome)
    assert s == esperado
    assert aviso is None


@pytest.mark.parametrize("nome,esperado", [
    ("Empresa Metropolitana de Estacionamento da Maia, EM", "EmpresaMetropolitana"),
    # palavras genéricas cedem o lugar às distintivas
    ("Sindicato Nacional dos Motoristas", "Motoristas"),
    ("Associação Sindical das Trabalhadoras e Trabalhadores dos Transportes",
     "Transportes"),
    ("AP Solutions GMBH - Sucursal em Portugal", "APSolutionsGMBH"),
    ("Águas do Norte, S. A.", "AguasNorte"),
])
def test_sigla_derivada_por_recurso_traz_aviso(nome, esperado):
    s, aviso = sigla(nome)
    assert s == esperado
    assert aviso and "confirmar" in aviso


def test_tabela_de_siglas_sobrepoe_se_a_derivacao(tmp_path):
    csv = tmp_path / "siglas.csv"
    csv.write_text("nome;sigla\n"
                   "Empresa Metropolitana de Estacionamento da Maia, EM;EMEMaia\n",
                   encoding="utf-8")
    tabela = carregar_siglas(csv)
    s, aviso = sigla("Empresa Metropolitana de Estacionamento da Maia, EM", tabela)
    assert (s, aviso) == ("EMEMaia", None)


# ------------------------------------------------------------- lados da mesa

def test_cnis_e_patronal_e_fnstfps_e_sindical():
    assert not e_sindical("Confederação Nacional das Instituições de Solidariedade - CNIS")
    assert e_sindical("Federação Nacional dos Sindicatos dos Trabalhadores em "
                      "Funções Públicas e Sociais - FNSTFPS")


def test_outorgantes_separados_pelos_dois_lados():
    patronais, sindicais = separar_outorgantes(
        "Associação das Empresas de Vinho do Porto (AEVP); "
        "FESAHT - Federação dos Sindicatos da Agricultura")
    assert len(patronais) == 1 and len(sindicais) == 1
    assert "AEVP" in patronais[0]


def test_sem_outorgantes_usa_o_titulo():
    patronais, sindicais = separar_outorgantes("", (
        "Acordo de empresa entre a CARRISTUR - Inovação em Transportes Urbanos e "
        "Regionais, Sociedade Unipessoal L.da e a Associação Sindical das "
        "Trabalhadoras e Trabalhadores dos Transportes"))
    assert patronais[0].startswith("CARRISTUR")
    assert sindicais[0].startswith("Associação Sindical")


def test_varios_outorgantes_do_mesmo_lado_geram_aviso():
    entrada = {"ano": 2026, "num_bte": 31, "familia": "convencao",
               "titulo": "", "outorgantes":
               "Associação A - AAA; Associação B - BBB; Sindicato C - CCC"}
    nome, avisos = nome_documento(entrada, 7)
    assert nome == "26_PR_007_BTE_31_AAA_CCC"
    assert any("outorgantes patronals" in a or "outorgantes" in a for a in avisos)


# -------------------------------------------------------- contrato dos nomes

def test_nomes_do_bte31(registo_com_recolha):
    registo, tmp_path = registo_com_recolha
    resumo = nomear(registo, tmp_path / "bte", aplicar=True)
    assert [n for _, n in resumo["nomes"]] == NOMES_ESPERADOS
    assert resumo["por_estado"]["nomeado"] == 6


@pytest.mark.parametrize("nome", NOMES_ESPERADOS)
def test_nome_e_legivel_pelo_localizador(nome):
    ano, bte, tokens = interpretar_doc_id(nome)
    assert (ano, bte) == (26, 31)
    assert tokens


@pytest.mark.parametrize("nome", NOMES_ESPERADOS)
def test_nome_cabe_no_limite_do_maxqda(nome):
    assert len(nome) <= MAX_NOME


def test_nomes_de_partes_compridas_continuam_a_caber():
    """Cada sigla é cortada a 20 caracteres, pelo que o nome cabe sempre em 63."""
    entrada = {"ano": 2026, "num_bte": 31, "familia": "convencao", "titulo": "",
               "outorgantes": ("Associação Muito Comprida dos Industriais de "
                               "Qualquer Coisa Assim; Sindicato Igualmente "
                               "Comprido dos Trabalhadores Desse Setor")}
    nome, _avisos = nome_documento(entrada, 8)
    assert len(nome) <= MAX_NOME
    assert interpretar_doc_id(nome)
    assert all(len(parte) <= MAX_SIGLA for parte in nome.split("_")[5:])


# ---------------------------------------------------------------- ordinais

def test_ordinais_sao_estaveis_entre_corridas(registo_com_recolha):
    registo, tmp_path = registo_com_recolha
    primeiro = dict(nomear(registo, tmp_path / "bte", aplicar=True)["nomes"])
    segundo = dict(nomear(Registo.carregar(registo.caminho), tmp_path / "bte",
                          aplicar=True)["nomes"])
    assert primeiro == segundo


def test_documento_novo_recebe_o_ordinal_seguinte(registo_com_recolha, tmp_path):
    registo, pasta = registo_com_recolha
    nomear(registo, pasta / "bte", aplicar=True)

    # chega mais um documento, de um BTE anterior: não reordena o que já existe
    novo = {"chave": "2026/30/00010002", "ano": 2026, "num_bte": 30,
            "familia": "convencao", "posicao": 1, "titulo": "",
            "outorgantes": "Associação X - XXX; Sindicato Y - YYY",
            "descarga": {"estado": "descarregado", "caminho": "", "sha256": "x"}}
    registo.entradas[novo["chave"]] = novo
    nomear(registo, pasta / "bte", aplicar=False)
    assert novo["nomeacao"]["ordinal"] == 7
    assert registo.get("2026/31/00260057")["nomeacao"]["ordinal"] == 1


# ------------------------------------------------------- escrita e conflitos

def test_simulacao_nao_escreve_nada(registo_com_recolha):
    registo, tmp_path = registo_com_recolha
    resumo = nomear(registo, tmp_path / "bte", aplicar=False)
    assert resumo["por_estado"]["por_nomear"] == 6
    assert not list((tmp_path / "bte").rglob("*.pdf")) if (tmp_path / "bte").exists() else True


def test_segunda_corrida_nao_reescreve(registo_com_recolha):
    registo, tmp_path = registo_com_recolha
    nomear(registo, tmp_path / "bte", aplicar=True)
    resumo = nomear(Registo.carregar(registo.caminho), tmp_path / "bte", aplicar=True)
    assert resumo["por_estado"]["ja_existente"] == 6
    assert "nomeado" not in resumo["por_estado"]


def test_destino_ocupado_por_outro_conteudo_e_conflito(registo_com_recolha):
    registo, tmp_path = registo_com_recolha
    alvo = tmp_path / "bte" / "bte_2026" / f"{NOMES_ESPERADOS[0]}.pdf"
    alvo.parent.mkdir(parents=True)
    alvo.write_bytes(b"%PDF-1.4\noutra coisa qualquer\n")

    resumo = nomear(registo, tmp_path / "bte", aplicar=True)
    assert resumo["por_estado"]["conflito"] == 1
    assert alvo.read_bytes().startswith(b"%PDF-1.4\noutra")   # não foi tocado
    assert any("já existe" in p for p in resumo["problemas"])


def test_portarias_ficam_fora_da_pasta_que_o_pipeline_le(registo_com_recolha):
    registo, tmp_path = registo_com_recolha
    registo.entradas["2026/31/09990999"] = {
        "chave": "2026/31/09990999", "ano": 2026, "num_bte": 31,
        "familia": "extensao", "posicao": 20,
        "titulo": "Portaria de extensão do contrato coletivo entre a "
                  "Associação Nacional - ANX e o Sindicato Nacional - SNY",
        "outorgantes": "", "descarga": {"estado": "descarregado", "sha256": "z",
                                        "caminho": str(tmp_path / "interim" /
                                                       "2026" / "31" / "00260057.pdf")}}
    nomear(registo, tmp_path / "bte", aplicar=True)
    pasta_pipeline = tmp_path / "bte" / "bte_2026"
    assert (pasta_pipeline / "extensoes" / "26_PE_001_BTE_31_ANX_SNY.pdf").exists()
    assert len(sorted(pasta_pipeline.glob("*.pdf"))) == 6   # o glob do pipeline
