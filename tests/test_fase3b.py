"""Testes da 2.ª ronda da Fase 3 — memos MaxQDA de 06/07 (4_08_triado).

- Memo 1: eixo-pai cobre a cláusula; subcódigo cobre só o número/alínea;
- Memos 2/5: Estrutura > Preâmbulo / Assinaturas, fora da codificação temática;
- Memo 3: códigos aninhados em árvore no QDPX (REVER > 4.08 > 4.08.4 > 4.08.4.1);
- Memo 4: continuação de alínea partida ("alíneas a), \n b) e c) do número");
- Memo 6: texto consolidado sinalizado e triado para a faixa CONSOLIDADO.
"""
import zipfile
import xml.etree.ElementTree as ET

from cct.extractor import estruturar, juntar_linhas
from cct.lexical import codificar
from cct.qdpx import exportar_qdpx, _caminho
from cct.triagem import triar

NS = {"q": "urn:QDA-XML:project:1.0"}

EXEMPLO = """Contrato coletivo entre a Empresa X e o Sindicato Y - Alteração salarial/texto consolidado.
Cláusula 1.ª
Avaliação
1- Cada trabalhador poderá efetuar a sua autoavaliação na plataforma.
2- Ao avaliado será remetida por email cópia do documento de avaliação.
Texto consolidado
Cláusula 2.ª
Processo individual
1- O empregador mantém um registo de pessoal de cada trabalhador.
Pela Empresa X:
António Silva, mandatário.
Pelo Sindicato Y:
José Costa, mandatário.
"""

CODEBOOK = {
    "tema": "t",
    "eixos": ["4.08.4", "4.08.5"],
    "codigos": [
        {"id": "4.08.4.1", "termos": ["email"]},
        {"id": "4.08.5.1", "termos": ["registo de pessoal"]},
    ],
}


def _doc():
    return estruturar(EXEMPLO, doc_id="t", subtipo="revisao_parcial_com_consolidado")


# memo 4 — continuação de alínea
def test_junta_continuacao_de_alinea():
    texto = ("pelos períodos estabelecidos nas alíneas a),\n"
             "b) e c) do número 3 da cláusula 55.ª, as férias não se iniciam.")
    assert "alíneas a), b) e c) do número 3" in juntar_linhas(texto)


def test_mantem_alinea_verdadeira():
    texto = "os seguintes deveres:\na) Cumprir o horário;\nb) Zelar pelos bens;"
    assert juntar_linhas(texto) == texto


# memo 1 — granularidade eixo/subcódigo
def test_eixo_na_clausula_subcodigo_no_paragrafo():
    doc, texto = _doc()
    anot = codificar(doc, texto, CODEBOOK)["anotacoes"]
    a_eixo = [a for a in anot if a["codigo"] == "4.08.4"]
    a_sub = [a for a in anot if a["codigo"] == "4.08.4.1"]
    assert len(a_eixo) == 1 and a_eixo[0]["nivel"] == "clausula"
    assert len(a_sub) == 1 and a_sub[0]["nivel"] == "paragrafo"
    assert texto[a_sub[0]["char_start"]:a_sub[0]["char_end"]].startswith("2- Ao avaliado")
    # o eixo cobre a cláusula inteira (inclui o n.º 1)
    trecho_eixo = texto[a_eixo[0]["char_start"]:a_eixo[0]["char_end"]]
    assert "1- Cada trabalhador" in trecho_eixo


# memos 2/5 — estrutura
def test_estrutura_preambulo_e_assinaturas():
    doc, texto = _doc()
    anot = codificar(doc, texto, CODEBOOK)["anotacoes"]
    estruturais = {a["codigo"] for a in anot if a["codigo"].startswith("Estrutura/")}
    assert "Estrutura/Preâmbulo" in estruturais
    assert "Estrutura/Assinaturas" in estruturais
    ass = next(a for a in anot if a["codigo"] == "Estrutura/Assinaturas")
    assert "Pela Empresa X" in texto[ass["char_start"]:ass["char_end"]]
    # sem codificação temática dentro do preâmbulo/assinaturas
    tematicas = [a for a in anot if not a["codigo"].startswith("Estrutura/")]
    no_ass = ass["no_id"]
    assert not any(a["no_id"] == no_ass for a in tematicas)


# memo 6 — consolidado
def test_nos_apos_marca_consolidado():
    doc, _ = _doc()
    cl2 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 2.ª"))
    cl1 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))
    assert cl2["origem"] == "consolidado"
    assert cl1["origem"] == "novo"


def test_triagem_consolidado():
    doc, texto = _doc()
    anot = codificar(doc, texto, CODEBOOK)
    t = triar(anot, aptos={"4.08.5.1", "4.08.4.1"}, doc=doc)
    codigos = {a["codigo"] for a in t["anotacoes"]}
    # 4.08.5.1 está no texto consolidado → faixa CONSOLIDADO, não AUTO
    assert any(c.startswith("CONSOLIDADO/4.08.5") for c in codigos)
    assert any(c.startswith("AUTO/4.08.4.1") for c in codigos)
    # estruturais não são prefixadas
    assert "Estrutura/Assinaturas" in codigos


EXEMPLO_ACIP = """Contrato coletivo entre X e Y - Alteração salarial e outras/texto consolidado
Artigo 1.º
O presente CCT altera a convenção coletiva publicada no BTE n.º 29.
Artigo 2.º
A tabela salarial produz efeitos a 1 de janeiro.
CAPÍTULO I - Âmbito
Cláusula 1.ª - Âmbito
1- O presente CCT obriga as empresas do setor.
"""


def test_consolidado_sem_marca_explicita_comeca_no_primeiro_capitulo():
    # padrão ACIP: artigos de alteração primeiro; a republicação (texto
    # consolidado) começa no primeiro capítulo/título
    doc, _ = estruturar(EXEMPLO_ACIP, doc_id="t",
                        subtipo="revisao_parcial_com_consolidado")
    art1 = next(n for n in doc["nos"] if n["rotulo"].startswith("Artigo 1.º"))
    cl1 = next(n for n in doc["nos"] if n["rotulo"].startswith("Cláusula 1.ª"))
    assert art1["origem"] == "novo"
    assert cl1["origem"] == "consolidado"


def test_titulo_reconhecido_como_nivel_estrutural():
    doc, texto = estruturar(
        "Preâmbulo.\nTexto consolidado\nTÍTULO I\nÁrea, âmbito e vigência\n"
        "Cláusula 1.ª - Âmbito\nTexto da cláusula.\n",
        doc_id="t", subtipo="revisao_parcial_com_consolidado")
    caps = [n for n in doc["nos"] if n["tipo"] == "capitulo"]
    assert caps and caps[0]["rotulo"].startswith("TÍTULO I - Área")
    cl = next(n for n in doc["nos"] if n["tipo"] == "clausula")
    assert cl["origem"] == "consolidado"


# memo 3 — árvore de códigos no QDPX
def test_caminho_hierarquico():
    assert _caminho("REVER/4.08.4.1") == ["REVER", "4.08", "4.08.4", "4.08.4.1"]
    assert _caminho("Estrutura/Assinaturas") == ["Estrutura", "Assinaturas"]
    assert _caminho("AUTO/Vigencia") == ["AUTO", "Vigencia"]


def test_qdpx_codigos_aninhados(tmp_path):
    doc, texto = _doc()
    anot = triar(codificar(doc, texto, CODEBOOK),
                 aptos={"4.08.4.1"}, doc=doc)
    destino = tmp_path / "t.qdpx"
    exportar_qdpx([(doc, texto, anot)], destino)
    with zipfile.ZipFile(destino) as zf:
        raiz = ET.fromstring(zf.read("project.qde").decode("utf-8"))
    codes = raiz.find(".//q:CodeBook/q:Codes", NS)
    topo = {c.get("name") for c in codes.findall("q:Code", NS)}
    assert "AUTO" in topo and "Estrutura" in topo
    auto = next(c for c in codes.findall("q:Code", NS) if c.get("name") == "AUTO")
    n408 = auto.find("q:Code", NS)
    assert n408.get("name").startswith("4.08")
    filho = n408.find("q:Code", NS)
    assert filho is not None  # 4.08.4 aninhado dentro de 4.08
