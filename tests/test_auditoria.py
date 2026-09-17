"""Testes da auditoria cruzada de tabelas (guardiões de 2026-09-17).

O que se protege aqui: uma tabela perdida na extração tem de ser
visível no relatório — como divergência entre extratores ou como anexo
de remuneração sem tabela — em vez de desaparecer em silêncio.
"""
from cct.auditoria import contar_blocos_tabela, divergencias, tabelas_esperadas
from cct.extractor import estruturar


# ------------------------------------------------------- contagem de blocos

def test_conta_blocos_de_tabela():
    texto = ("Antes.\n"
             "A | B | C\n"
             "1 | 2 | 3\n"
             "4 | 5 | 6\n"
             "Meio.\n"
             "X | Y\n"
             "Z | W\n"
             "Fim.\n")
    assert contar_blocos_tabela(texto) == 2


def test_linha_isolada_com_pipe_nao_e_bloco():
    texto = "Uma frase | outra parte da frase\nFim.\n"
    assert contar_blocos_tabela(texto) == 0


def test_texto_sem_tabelas_devolve_zero():
    assert contar_blocos_tabela("Cláusula 1.ª\nCorpo da cláusula.") == 0


# ---------------------------------------------------------- divergências

def test_pdfplumber_ve_e_o_texto_nao():
    avisos = divergencias(n_pdfplumber=3, n_texto=0)
    assert len(avisos) == 1
    assert "pdfplumber deteta 3" in avisos[0]
    assert "perda" in avisos[0]


def test_docling_ve_e_o_texto_nao():
    avisos = divergencias(n_pdfplumber=0, n_texto=0, n_docling=2)
    assert any("docling deteta 2" in a for a in avisos)


def test_sem_divergencia_quando_coincidem():
    assert divergencias(2, 2) == []
    assert divergencias(0, 0) == []
    assert divergencias(2, 3) == []  # contagens não precisam de ser iguais


def test_docling_nao_ve_o_que_o_pdfplumber_ve():
    avisos = divergencias(n_pdfplumber=1, n_texto=1, n_docling=0)
    assert any("sem grelha" in a for a in avisos)


# ------------------------------------------- anexos sem tabela (canário)

def _doc_com_anexo(rotulo: str, corpo: str,
                   tabela_fora: str = "") -> tuple[dict, str]:
    """Documento mínimo com um anexo, para o canário da sanidade.

    `tabela_fora` acrescenta linhas DEPOIS do anexo — o caso em que a
    tabela existe no documento mas cai fora do corpo do nó.
    """
    texto, nos = [], []

    def _add(tipo: str, rot: str, linhas_do_no: list[str]):
        start = sum(len(l) + 1 for l in texto)
        texto.extend(linhas_do_no)
        nos.append({"id": f"{tipo}{len(nos)}", "tipo": tipo, "rotulo": rot,
                    "char_start": start,
                    "char_end": start + sum(len(l) + 1 for l in linhas_do_no),
                    "pai": None, "origem": "novo", "folha": True})

    _add("clausula", "Cláusula 1.ª - Âmbito",
         ["Cláusula 1.ª - Âmbito", "1- A convenção aplica-se à empresa."])
    _add("anexo", rotulo, [rotulo] + corpo.split("\n"))
    if tabela_fora:
        texto.extend(tabela_fora.split("\n"))
    doc = {"versao_schema": "0.1", "doc_id": "teste", "tipo": "CCT",
           "subtipo": "desconhecido", "nos": nos}
    return doc, "\n".join(texto)


def test_anexo_de_remuneracao_sem_tabela_da_aviso():
    doc, texto = _doc_com_anexo(
        "Anexo I - Mapa de remunerações",
        "Texto corrido sem tabela.")
    avisos = tabelas_esperadas(doc, texto)
    assert len(avisos) == 1
    assert "Mapa de remunerações" in avisos[0]
    assert "sem nenhuma tabela" in avisos[0]


def test_anexo_com_tabela_fora_do_no_diz_fora_do_no():
    """A tabela existe no documento mas cai fora do corpo do anexo.

    É o caso real do estruturar com o docling: o anexo fecha no
    cabeçalho e as linhas de grelha ficam órfãs a seguir. A mensagem
    tem de distingui-lo da perda real.
    """
    doc, texto = _doc_com_anexo(
        "Anexo I - Mapa de remunerações",
        "Sem tabela no corpo do nó.",
        tabela_fora="Nível | Escalão\nI | 1 000,00")
    avisos = tabelas_esperadas(doc, texto)
    assert len(avisos) == 1
    assert "fora do corpo do nó" in avisos[0]
    assert "perdida" not in avisos[0]


def test_anexo_de_remuneracao_com_tabela_nao_da_aviso():
    doc, texto = _doc_com_anexo(
        "Anexo I - Mapa de remunerações",
        "Nível | Escalão 1\nI | 1 234,56")
    assert tabelas_esperadas(doc, texto) == []


def test_anexo_sem_termos_de_tabela_nao_da_aviso():
    doc, texto = _doc_com_anexo(
        "Anexo II - Regulamento interno",
        "Parágrafo primeiro.")
    assert tabelas_esperadas(doc, texto) == []


# --------------------------------------- integração: sanidade chama canário

def test_sanidade_inclui_o_canario_de_tabelas():
    from cct.sanidade import verificar
    doc, texto = _doc_com_anexo(
        "Anexo I - Mapa de remunerações",
        "Sem tabela aqui.")
    avisos = verificar(doc, texto)
    assert any("Mapa de remunerações" in a and "tabela" in a for a in avisos)


# ------------------- integração: a auditoria nunca custa o documento (PR #67)

def test_auditoria_a_rebentar_nao_exclui_o_documento(tmp_path, monkeypatch):
    """Uma exceção na auditoria pdfplumber é um aviso, não perda de documento.

    O caso real: com --extrator docling, o docling extrai bem um PDF que
    o auditor pdfplumber não consegue abrir. Se a exceção caísse no
    `except` geral do loop, o documento válido era excluído do QDPX por
    causa de uma verificação opcional — a degradação da auditoria não
    pode custar o resultado (bloqueante apontado na revisão do PR #67).
    """
    from cct import pipeline_tema
    from cct.auditoria import contar_tabelas_pdfplumber

    pasta = tmp_path / "pdfs"
    pasta.mkdir()
    # nome de convenção (passa ao gate de famílias); conteúdo irrelevante
    # porque a extração é substituída por um duplo
    pdf = pasta / "26_PR_001_BTE_31_TESTE_X_Y.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    codebook = tmp_path / "cb.yaml"
    codebook.write_text("tema: ensaio\ncodigos: []\n", encoding="utf-8")
    out = tmp_path / "out"

    DOC, TEXTO = estruturar(
        "Cláusula 1.ª - Âmbito\n1- Aplica-se à empresa.\n"
        "Depositado em 23 de janeiro de 2025, a fl. 87.\n", "teste")

    def _extrair_falso(pdf_path, **kw):
        return {"**DOC**": None}  # nunca chega a ser usado

    def _extrair_duplo(pdf_path, paginas=None, doc_id=None, subtipo="desconhecido"):
        import copy
        return copy.deepcopy(DOC), TEXTO

    def _auditoria_rebenta(pdf_path):
        raise OSError("PDF corrompido para o auditor")

    monkeypatch.setattr(pipeline_tema, "extrair_pdf", _extrair_duplo)
    monkeypatch.setattr("cct.auditoria.contar_tabelas_pdfplumber",
                        _auditoria_rebenta)
    monkeypatch.setattr("sys.argv",
                        ["cct.pipeline_tema", "--pdfs", str(pasta),
                         "--codebook", str(codebook), "--out", str(out)])

    pipeline_tema.main()

    # o documento TEM de estar no QDPX apesar da auditoria rebentada
    import zipfile
    zf = zipfile.ZipFile(out / "projeto.qdpx")
    fontes = [n for n in zf.namelist()
              if n.startswith("Sources/") and n.endswith(".txt")]
    assert len(fontes) == 1, "o documento foi excluído do QDPX pela auditoria"
    # e o relatório regista a falha como aviso, não como erro do documento
    rel = (out / "relatorio.txt").read_text(encoding="utf-8")
    assert "[auditoria] não foi possível verificar" in rel
    assert "Convenções processadas: 1/1" in rel
