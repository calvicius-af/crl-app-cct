"""Testes da barreira de segurança (scripts/verificar_seguranca.py).

Cada verificação é testada isoladamente, sobre listas de caminhos passadas
directamente — sem invocar o git — para que os testes sejam rápidos e não
dependam do estado real do repositório.
"""
import importlib.util
import sys
from pathlib import Path

_CAMINHO_MODULO = Path(__file__).resolve().parent.parent / "scripts" / "verificar_seguranca.py"
_ESPECIFICACAO = importlib.util.spec_from_file_location("verificar_seguranca", _CAMINHO_MODULO)
verificar_seguranca = importlib.util.module_from_spec(_ESPECIFICACAO)
sys.modules[_ESPECIFICACAO.name] = verificar_seguranca
_ESPECIFICACAO.loader.exec_module(verificar_seguranca)


CAMINHOS_LIMPOS = [
    "README.md",
    "cct/proveniencia.py",
    "scripts/limpar_cache.py",
    "examples/README.md",
    "examples/metricas_calibracao.json",
    "examples/acip_fesaht/saida/relatorio.txt",
]

CAMINHOS_ALLOWLIST_REAIS = [
    "examples/README.md",
    "examples/metricas_calibracao.json",
    "examples/acip_fesaht/saida/25_PR_003_BTE_02_ACIP_FESAHT.doc.json",
    "examples/acip_fesaht/saida/25_PR_003_BTE_02_ACIP_FESAHT.txt",
    "examples/acip_fesaht/saida/projeto.qdpx",
    "examples/acip_fesaht/saida/relatorio.txt",
    "examples/acip_fesaht/saida/sugestoes_peritas.xlsx",
    "examples/tinita_sitemaq/saida/25_PR_112_BTE_19_TINITA_SITEMAQ.doc.json",
    "examples/tinita_sitemaq/saida/25_PR_112_BTE_19_TINITA_SITEMAQ.txt",
    "examples/tinita_sitemaq/saida/comparacao_2020_2025.xlsx",
    "examples/tinita_sitemaq/saida/projeto.qdpx",
    "examples/tinita_sitemaq/saida/relatorio.txt",
    "examples/tinita_sitemaq/saida/sugestoes_peritas.xlsx",
]


# ---------- conjunto limpo: todas as verificações passam ----------

def test_dados_fora_do_sitio_vazio_em_conjunto_limpo():
    assert verificar_seguranca.verificar_dados_fora_do_sitio(CAMINHOS_LIMPOS) == []


def test_credenciais_vazio_em_conjunto_limpo():
    assert verificar_seguranca.verificar_credenciais(CAMINHOS_LIMPOS) == []


def test_allowlist_examples_vazio_em_conjunto_limpo():
    assert verificar_seguranca.verificar_allowlist_examples(CAMINHOS_LIMPOS) == []


def test_segredos_vazio_em_conjunto_limpo(tmp_path):
    for caminho in CAMINHOS_LIMPOS:
        destino = tmp_path / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("conteúdo normal em português, sem segredos.\n", encoding="utf-8")
    assert verificar_seguranca.verificar_segredos(CAMINHOS_LIMPOS, tmp_path) == []


# ---------- A: dados fora do sítio ----------

def test_deteta_pdf_versionado_fora_de_examples_e_tests():
    problemas = verificar_seguranca.verificar_dados_fora_do_sitio(["data/x.pdf"])
    assert len(problemas) == 1
    assert "data/x.pdf" in problemas[0]


def test_nao_se_queixa_de_xlsx_dentro_de_examples():
    problemas = verificar_seguranca.verificar_dados_fora_do_sitio(["examples/a/saida/b.xlsx"])
    assert problemas == []


def test_nao_se_queixa_de_dados_dentro_de_tests():
    problemas = verificar_seguranca.verificar_dados_fora_do_sitio(["tests/fixtures/x.qdpx"])
    assert problemas == []


# ---------- B: credenciais ----------

def test_deteta_env():
    problemas = verificar_seguranca.verificar_credenciais([".env"])
    assert len(problemas) == 1


def test_deteta_env_production():
    problemas = verificar_seguranca.verificar_credenciais([".env.production"])
    assert len(problemas) == 1


def test_aceita_env_example():
    problemas = verificar_seguranca.verificar_credenciais([".env.example"])
    assert problemas == []


# ---------- C: allowlist de examples/ ----------

def test_allowlist_aceita_os_caminhos_reais():
    assert verificar_seguranca.verificar_allowlist_examples(CAMINHOS_ALLOWLIST_REAIS) == []


def test_allowlist_rejeita_entrada_nao_redistribuida():
    problemas = verificar_seguranca.verificar_allowlist_examples(
        ["examples/acip_fesaht/entrada/x.pdf"])
    assert len(problemas) == 1
    assert "examples/acip_fesaht/entrada/x.pdf" in problemas[0]


def test_allowlist_rejeita_ficheiro_nao_previsto():
    problemas = verificar_seguranca.verificar_allowlist_examples(["examples/lixo.csv"])
    assert len(problemas) == 1
    assert "examples/lixo.csv" in problemas[0]


# ---------- D: segredos ----------

def test_deteta_chave_privada_pem(tmp_path):
    caminho = "segredo.txt"
    (tmp_path / caminho).write_text(
        "-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8")
    problemas = verificar_seguranca.verificar_segredos([caminho], tmp_path)
    assert any("chave privada PEM" in problema for problema in problemas)


def test_deteta_chave_aws(tmp_path):
    caminho = "config.py"
    (tmp_path / caminho).write_text(
        'AWS_ACCESS_KEY = "AKIAABCDEFGHIJKLMNOP"\n', encoding="utf-8")
    problemas = verificar_seguranca.verificar_segredos([caminho], tmp_path)
    assert any("chave de acesso AWS" in problema for problema in problemas)


def test_deteta_token_do_github_classico(tmp_path):
    caminho = "config.py"
    (tmp_path / caminho).write_text(
        'TOKEN = "ghp_' + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8" + '"\n',
        encoding="utf-8")
    problemas = verificar_seguranca.verificar_segredos([caminho], tmp_path)
    assert any("token do GitHub" in problema for problema in problemas)


def test_deteta_token_do_github_granularidade_fina(tmp_path):
    # Formato github_pat_: prefixo, 22 caracteres, underscore, 59 caracteres.
    # Não era apanhado pelo padrão clássico gh[pousr]_ — ver revisão do PR #52.
    caminho = "config.py"
    corpo = "11ABCDEFG0abcdefghijklm" + "_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2W3x4Y5z6A7b8C9"
    (tmp_path / caminho).write_text(
        'TOKEN = "github_pat_' + corpo + '"\n', encoding="utf-8")
    problemas = verificar_seguranca.verificar_segredos([caminho], tmp_path)
    assert any("token do GitHub" in problema for problema in problemas)


def test_nao_confunde_texto_com_token_do_github(tmp_path):
    caminho = "docs/nota.md"
    (tmp_path / caminho).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / caminho).write_text(
        "O github_pat_ é o prefixo dos tokens de granularidade fina.\n",
        encoding="utf-8")
    assert verificar_seguranca.verificar_segredos([caminho], tmp_path) == []


def test_deteta_password_atribuida_real(tmp_path):
    caminho = "config.py"
    (tmp_path / caminho).write_text(
        'password = "hunter2-super-secreto"\n', encoding="utf-8")
    problemas = verificar_seguranca.verificar_segredos([caminho], tmp_path)
    assert any("segredo genérico atribuído" in problema for problema in problemas)


def test_nao_deteta_password_changeme(tmp_path):
    caminho = "config.py"
    (tmp_path / caminho).write_text('password = "changeme"\n', encoding="utf-8")
    assert verificar_seguranca.verificar_segredos([caminho], tmp_path) == []


def test_nao_deteta_api_key_placeholder(tmp_path):
    caminho = "config.py"
    (tmp_path / caminho).write_text('api_key = "<a-tua-chave>"\n', encoding="utf-8")
    assert verificar_seguranca.verificar_segredos([caminho], tmp_path) == []


def test_nao_deteta_texto_normal_em_portugues(tmp_path):
    caminho = "notas.txt"
    (tmp_path / caminho).write_text(
        "A senha de acesso ao edifício é entregue na receção.\n", encoding="utf-8")
    assert verificar_seguranca.verificar_segredos([caminho], tmp_path) == []


def test_salta_ficheiros_binarios(tmp_path):
    caminho = "binario.bin"
    (tmp_path / caminho).write_bytes(b"AKIAABCDEFGHIJKLMNOP\x00lixo binario")
    assert verificar_seguranca.verificar_segredos([caminho], tmp_path) == []
