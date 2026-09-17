"""Testes do verificador de referências documentais (scripts/verificar_referencias.py).

Cada verificação é testada isoladamente, sobre ficheiros escritos num
directório temporário — sem invocar o git — para que os testes sejam rápidos
e não dependam do estado real do repositório.
"""
import importlib.util
import sys
from pathlib import Path

_CAMINHO_MODULO = Path(__file__).resolve().parent.parent / "scripts" / "verificar_referencias.py"
_ESPECIFICACAO = importlib.util.spec_from_file_location("verificar_referencias", _CAMINHO_MODULO)
verificar_referencias = importlib.util.module_from_spec(_ESPECIFICACAO)
sys.modules[_ESPECIFICACAO.name] = verificar_referencias
_ESPECIFICACAO.loader.exec_module(verificar_referencias)


def _escrever(tmp_path: Path, caminho: str, conteudo: str) -> None:
    destino = tmp_path / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")


# ---------- links Markdown ----------

def test_link_valido_nao_reporta_problema(tmp_path):
    _escrever(tmp_path, "docs/guia.md", "conteúdo")
    _escrever(tmp_path, "docs/hub.md", "[guia](guia.md)\n")
    caminhos = ["docs/guia.md", "docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert quebrados == []
    assert caixa_errada == []


def test_link_quebrado_e_reportado(tmp_path):
    _escrever(tmp_path, "docs/hub.md", "[inexistente](nao-existe.md)\n")
    caminhos = ["docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert len(quebrados) == 1
    assert "nao-existe.md" in quebrados[0]
    assert caixa_errada == []


def test_link_com_caixa_errada_e_reportado_separadamente(tmp_path):
    _escrever(tmp_path, "docs/GUIA.md", "conteúdo")
    _escrever(tmp_path, "docs/hub.md", "[guia](guia.md)\n")
    caminhos = ["docs/GUIA.md", "docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert quebrados == []
    assert len(caixa_errada) == 1
    assert "guia.md" in caixa_errada[0]


def test_url_externo_e_ignorado(tmp_path):
    _escrever(tmp_path, "docs/hub.md", "[site](https://exemplo.org/pagina)\n")
    caminhos = ["docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert quebrados == []
    assert caixa_errada == []


def test_ancora_pura_e_ignorada(tmp_path):
    _escrever(tmp_path, "docs/hub.md", "[secção](#introdução)\n")
    caminhos = ["docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert quebrados == []
    assert caixa_errada == []


def test_ficheiro_com_ancora_valida_pela_parte_do_ficheiro(tmp_path):
    _escrever(tmp_path, "docs/guia.md", "# Guia\n\n## Secção\n")
    _escrever(tmp_path, "docs/hub.md", "[secção do guia](guia.md#secção)\n")
    caminhos = ["docs/guia.md", "docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert quebrados == []
    assert caixa_errada == []


def test_ficheiro_com_ancora_e_ficheiro_inexistente_e_quebrado(tmp_path):
    _escrever(tmp_path, "docs/hub.md", "[secção](nao-existe.md#secção)\n")
    caminhos = ["docs/hub.md"]
    quebrados, caixa_errada = verificar_referencias.verificar_links_markdown(caminhos, tmp_path)
    assert len(quebrados) == 1
    assert "nao-existe.md#secção" in quebrados[0]


# ---------- caminhos de documentação em código Python ----------

def test_caminho_doc_valido_em_codigo_nao_reporta_problema(tmp_path):
    _escrever(tmp_path, "docs/operacao/guia-operacao.md", "conteúdo")
    _escrever(tmp_path, "cct/doctor.py", 'falha("erro", "ver docs/operacao/guia-operacao.md")\n')
    caminhos = ["docs/operacao/guia-operacao.md", "cct/doctor.py"]
    quebrados, caixa_errada = verificar_referencias.verificar_caminhos_em_codigo(caminhos, tmp_path)
    assert quebrados == []
    assert caixa_errada == []


def test_caminho_doc_quebrado_em_codigo_e_reportado(tmp_path):
    _escrever(tmp_path, "cct/doctor.py", 'falha("erro", "ver docs/operacao/GUIA_OPERACAO.md")\n')
    caminhos = ["cct/doctor.py"]
    quebrados, caixa_errada = verificar_referencias.verificar_caminhos_em_codigo(caminhos, tmp_path)
    assert len(quebrados) == 1
    assert "docs/operacao/GUIA_OPERACAO.md" in quebrados[0]


def test_caminho_doc_com_caixa_errada_em_codigo_e_reportado_separadamente(tmp_path):
    _escrever(tmp_path, "docs/operacao/guia-operacao.md", "conteúdo")
    _escrever(tmp_path, "cct/doctor.py", 'falha("erro", "ver docs/operacao/GUIA-OPERACAO.md")\n')
    caminhos = ["docs/operacao/guia-operacao.md", "cct/doctor.py"]
    quebrados, caixa_errada = verificar_referencias.verificar_caminhos_em_codigo(caminhos, tmp_path)
    assert quebrados == []
    assert len(caixa_errada) == 1
    assert "docs/operacao/GUIA-OPERACAO.md" in caixa_errada[0]


def test_caminho_ignorado_fora_das_pastas_de_codigo(tmp_path):
    _escrever(tmp_path, "outro/lugar.py", 'x = "docs/nao-existe.md"\n')
    caminhos = ["outro/lugar.py"]
    quebrados, caixa_errada = verificar_referencias.verificar_caminhos_em_codigo(caminhos, tmp_path)
    assert quebrados == []
    assert caixa_errada == []
