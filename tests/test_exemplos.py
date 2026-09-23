"""Os exemplos publicados dizem o que o README diz que dizem (issues #4 e #7).

O README de `examples/` afirma números concretos (caracteres, nós, cláusulas,
segmentos, códigos) e que o texto dentro do QDPX é igual ao `.txt`. Nada os
verificava: regerar os exemplos e esquecer o README deixava a documentação a
afirmar o que já não era verdade. Os números são lidos do próprio README, pelo
que este teste não tem de ser editado quando os exemplos mudam — tem de ser o
README.
"""
import json
import re
import zipfile
from pathlib import Path

import pytest

EXEMPLOS = Path(__file__).resolve().parent.parent / "examples"
README = (EXEMPLOS / "README.md").read_text(encoding="utf-8")


def _numero(texto: str) -> int:
    return int(re.sub(r"\D", "", texto))


def _secao(ficheiro_txt: str) -> str:
    """A secção do README («## Exemplo …») que descreve este exemplo."""
    secoes = README.split("\n## ")
    secao = next((x for x in secoes if f"`saida/{ficheiro_txt}`" in x), None)
    assert secao, f"o README não descreve saida/{ficheiro_txt}"
    return secao


def _linha(secao: str, ficheiro: str) -> str:
    linha = next((l for l in secao.splitlines() if f"`saida/{ficheiro}`" in l), None)
    assert linha, f"a secção do README não tem linha para saida/{ficheiro}"
    return linha


def _exemplos():
    for pasta in sorted(p for p in EXEMPLOS.iterdir() if (p / "saida").is_dir()):
        docs = list((pasta / "saida").glob("*.doc.json"))
        if docs:
            yield pytest.param(pasta, docs[0], id=pasta.name)


@pytest.mark.parametrize("pasta,doc_json", list(_exemplos()))
def test_numeros_do_readme_batem_com_os_artefactos(pasta, doc_json):
    txt = doc_json.with_name(doc_json.name.replace(".doc.json", ".txt"))
    texto = txt.read_text(encoding="utf-8")
    doc = json.loads(doc_json.read_text(encoding="utf-8"))
    nos = doc["nos"]
    clausulas = [n for n in nos if n["tipo"] == "clausula"]

    secao = _secao(txt.name)
    linha_txt = _linha(secao, txt.name)
    assert _numero(re.search(r"([\d  ]+) caracteres", linha_txt).group(1)) == len(texto)

    linha_doc = _linha(secao, doc_json.name)
    assert _numero(re.search(r"([\d  ]+) nós", linha_doc).group(1)) == len(nos)
    assert _numero(re.search(r"\*?\*?(\d+) cláusulas", linha_doc).group(1)) == len(clausulas)

    with zipfile.ZipFile(pasta / "saida" / "projeto.qdpx") as zf:
        qde = zf.read("project.qde").decode("utf-8")
    linha_qdpx = _linha(secao, "projeto.qdpx")
    segmentos = len(re.findall(r"<PlainTextSelection\b", qde))
    assert _numero(re.search(r"(\d+) segmentos", linha_qdpx).group(1)) == segmentos
    if (m := re.search(r"(\d+) códigos", linha_qdpx)):
        assert int(m.group(1)) == len(re.findall(r"<Code\b", qde))


@pytest.mark.parametrize("pasta,doc_json", list(_exemplos()))
def test_offsets_apontam_para_o_rotulo(pasta, doc_json):
    """Cada cláusula ou artigo começa, no `.txt`, pelo próprio rótulo."""
    texto = doc_json.with_name(doc_json.name.replace(".doc.json", ".txt")).read_text(
        encoding="utf-8")
    for no in json.loads(doc_json.read_text(encoding="utf-8"))["nos"]:
        assert 0 <= no["char_start"] <= no["char_end"] <= len(texto), no["id"]
        if no["tipo"] in ("clausula", "artigo"):
            numero = no["rotulo"].split(" - ")[0]
            assert texto[no["char_start"]:].startswith(numero), no["rotulo"]


@pytest.mark.parametrize("pasta,doc_json", list(_exemplos()))
def test_o_texto_no_qdpx_e_o_txt_byte_a_byte(pasta, doc_json):
    """O README garante que as posições das codificações contam sobre este texto."""
    txt = doc_json.with_name(doc_json.name.replace(".doc.json", ".txt")).read_bytes()
    with zipfile.ZipFile(pasta / "saida" / "projeto.qdpx") as zf:
        fontes = [zf.read(n) for n in zf.namelist()
                  if n.startswith("Sources/") and n.endswith(".txt")]
    assert fontes == [txt]
