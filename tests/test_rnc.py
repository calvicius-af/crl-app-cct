"""Testes da compatibilização com a gestão documental do RNC (SPEC-0003).

Três coisas: que o índice do BTE é lido nos dois dialetos que a DGERT
distribui, que o esquema de nomes do RNC produz nomes que o resto do pipeline
continua a saber ler, e que o catálogo separa o que o índice mistura.

O índice de ensaio é o do BTE n.º 31 de 2026, no dialeto técnico — cabeçalho e
linhas reais, reconstruídos com openpyxl para não versionar binários.
"""
import csv
from pathlib import Path

import pytest

from cct import ambito, catalogo
from cct.catalogo import (acto_negociacao, paginas, separar_alteracoes,
                          separar_sectores)
from cct.localizador import interpretar_doc_id, interpretar_nome_rnc
from cct.nomeacao import (carregar_siglas, nome_documento, sequencial_bte,
                          siglas_outorgantes, tipo_normalizado)
from cct.recolha import ler_indice

# Cabeçalho técnico: o que vem nos índices de 2026. O de 2025 usava rótulos
# ("TIPO DE DOCUMENTO:", "COD:\n(IRCT)") e está coberto em tests/test_recolha.py.
CABECALHO_TECNICO = [
    "Ano", "IDDocumento", "Titulo", "TipoSubTipoDoc", "NVolumeBTE", "NBTE",
    "DataBTE", "DataDistribuicaoBTE", "PagVersaoEscrita", "CAE",
    "CodigoGEPDGERT", "DocumentosEmVigor", "LinkDocEmVigor",
    "DocAlteradosPorEste", "DocAlteradosPorEste2", "DocAlterameste",
    "SetoresAtividade", "Outorgantes", "FormulaPDF", "NomePDF", "URLPDF",
]

URL = "https://bte.dgcp.mtsss.gov.pt/documentos/2026/31"

LINHAS = [
    dict(id="377/2026", tipo="CCT", cod="27251", pdf="00260057.pdf",
         titulo="Contrato coletivo entre a Associação do Comércio e Serviços da "
                "Região do Algarve - ACRAL e o CESP - Sindicato dos Trabalhadores "
                "do Comércio - Revisão global.",
         outorgantes="Associação do Comércio e Serviços da Região do Algarve - ACRAL; "
                     "CESP - Sindicato dos Trabalhadores do Comércio, Escritórios e "
                     "Serviços de Portugal; STRUP - Sindicato dos Trabalhadores de "
                     "Transportes Rodoviários e Urbanos de Portugal; Sindicato das "
                     "Indústrias Eléctricas do Sul e Ilhas - SIESI; Sindicato Nacional "
                     "dos Trabalhadores das Telecomunicações e Audiovisual - SINTTAV",
         altera="CCT-ALT.20250708.321/2025",
         sectores="COMÉRCIO A RETALHO; ATIVIDADES VETERINÁRIAS",
         em_vigor=""),
    dict(id="379/2026", tipo="CCT-ALT", cod="26651", pdf="00600062.pdf",
         titulo="Contrato coletivo entre a Associação das Empresas de Vinho do "
                "Porto (AEVP) e a FESAHT - Federação dos Sindicatos da Agricultura "
                "- Alteração.",
         outorgantes="Associação das Empresas de Vinho do Porto (AEVP); FESAHT - "
                     "Federação dos Sindicatos da Agricultura, Alimentação, Bebidas, "
                     "Hotelaria e Turismo de Portugal",
         altera="CCT-ALT.20251209.520/2025",
         sectores="VITICULTURA; REMUNERAÇÕES; SUBSÍDIO DE REFEIÇÃO",
         em_vigor="BTE 3, 22/01/2025, pág. 21 (16/2025)"),
    dict(id="382/2026", tipo="AE", cod="47252", pdf="00880122.pdf",
         titulo="Acordo de empresa entre a Empresa Metropolitana de Estacionamento "
                "da Maia, EM e o Sindicato dos Trabalhadores da Administração Pública "
                "- Revisão global.",
         outorgantes="Empresa Metropolitana de Estacionamento da Maia, EM; Sindicato "
                     "dos Trabalhadores da Administração Pública e de Entidades com "
                     "Fins Públicos - SINTAP",
         altera="AE.20230308.76/2023",
         sectores="ACTIVIDADES AUXILIARES DOS TRANSPORTES TERRESTRES",
         em_vigor=""),
    # retificação: a coluna de outorgantes vem vazia no índice real
    dict(id="387/2026", tipo="AE-ALT-RECT", cod="47109", pdf="01680170.pdf",
         titulo="Acordo de empresa entre a CARRISTUR - Inovação em Transportes "
                "Urbanos e Regionais, Sociedade Unipessoal L.da e a Associação "
                "Sindical dos Trabalhadores da Carris e Participadas, (ASPTC) "
                "- Retificação.",
         outorgantes="", altera="AE-ALT.20260722.323/2026",
         sectores="TRANSPORTES TERRESTRES",
         em_vigor="BTE 27, 22/07/2026, pág. 222 (323/2026)"),
]


def escrever_indice_tecnico(pasta: Path, nome="BTE31_2026.xlsx") -> Path:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "31"
    ws.append(CABECALHO_TECNICO)
    for l in LINHAS:
        linha = [None] * len(CABECALHO_TECNICO)
        linha[0], linha[1], linha[2], linha[3] = 2026, l["id"], l["titulo"], l["tipo"]
        linha[4], linha[5] = 93, 31
        linha[6], linha[7] = "2026-08-22 00:00:00", "2026-08-24 00:00:00"
        linha[10], linha[11] = l["cod"], l["em_vigor"]
        linha[13] = l["altera"]
        linha[16], linha[17] = l["sectores"], l["outorgantes"]
        linha[19], linha[20] = l["pdf"], f"{URL}/{l['pdf']}"
        ws.append(linha)
    caminho = pasta / nome
    wb.save(caminho)
    return caminho


@pytest.fixture()
def itens(tmp_path):
    return ler_indice(escrever_indice_tecnico(tmp_path))


# ------------------------------------------------- o dialeto técnico do índice

def test_le_o_dialeto_tecnico_do_indice(itens):
    """O índice de 2026 não traz um único cabeçalho igual ao de 2025."""
    assert len(itens) == len(LINHAS)
    primeiro = itens[0]
    assert primeiro["id_dgert"] == "377/2026"
    assert primeiro["tipo"] == "CCT"
    assert primeiro["cod_irct"] == "27251"
    assert primeiro["num_bte"] == 31
    assert primeiro["ficheiro"] == "00260057.pdf"
    assert primeiro["url"].endswith("/00260057.pdf")
    assert primeiro["altera"] == "CCT-ALT.20250708.321/2025"
    assert "ACRAL" in primeiro["outorgantes"]


def test_cadeia_de_alteracoes_junta_as_duas_colunas(tmp_path):
    """DocAlteradosPorEste e …2 são partes da mesma cadeia, não alternativas."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(CABECALHO_TECNICO)
    linha = [None] * len(CABECALHO_TECNICO)
    linha[0], linha[1], linha[2], linha[3] = 2026, "400/2026", "Contrato", "CCT-ALT"
    linha[5], linha[13], linha[14] = 31, "CCT-ALT.20250708.321/2025", \
        "CCT-ALT.20240101.10/2024"
    linha[19], linha[20] = "00010002.pdf", f"{URL}/00010002.pdf"
    ws.append(linha)
    caminho = tmp_path / "BTE31_2026.xlsx"
    wb.save(caminho)

    item = ler_indice(caminho)[0]
    assert item["altera"] == ("CCT-ALT.20250708.321/2025; CCT-ALT.20240101.10/2024")


# ------------------------------------------------------------- esquema de nome

def test_nome_rnc_tem_os_seis_campos_e_o_numero_do_bte(itens):
    nome, avisos = nome_documento(itens[0], 1, esquema="rnc")
    assert nome == "2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2"
    assert not avisos


def test_todo_o_nome_rnc_e_lido_pelo_localizador(itens):
    """O critério que não se negoceia: o pipeline continua a ler o nome."""
    for i, item in enumerate(itens, 1):
        nome, _ = nome_documento(item, i, esquema="rnc")
        assert len(nome) <= 63, nome
        ano, bte, tokens = interpretar_doc_id(nome)
        assert (ano, bte) == (26, 31), nome
        assert tokens, nome
        assert interpretar_doc_id(nome + "_TXT") == (ano, bte, tokens)


def test_o_esquema_antigo_continua_a_ser_lido():
    assert interpretar_doc_id("25_PR_016_BTE_04_EMARP_SINTAP") == (
        25, 4, ["emarp", "sintap"])
    assert interpretar_nome_rnc("25_PR_016_BTE_04_EMARP_SINTAP") is None


def test_metadados_que_o_nome_rnc_leva():
    meta = interpretar_nome_rnc("2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-ASPTC")
    assert meta == {"ano": 2026, "ambito": "SPE", "seq": 387,
                    "tipo": "AE-ALT-RECT", "cod_irct": "47109", "num_bte": 31,
                    "siglas": ["CARRISTUR", "ASPTC"], "outros_outorgantes": 0}


def test_retificacao_sem_outorgantes_resolve_se_pelo_titulo(itens):
    """Sem precisar do catálogo acumulado do ano: as partes estão no título."""
    rect = next(i for i in itens if i["tipo"] == "AE-ALT-RECT")
    assert rect["outorgantes"] == ""
    nome, avisos = nome_documento(rect, 4, esquema="rnc")
    assert "CARRISTUR" in nome and "ASPTC" in nome
    assert any("título" in a for a in avisos), "a herança tem de ficar assinalada"


def test_o_numero_sequencial_e_o_do_boletim_nao_o_ordinal_interno(itens):
    assert sequencial_bte(itens[0]) == 377
    nome, _ = nome_documento(itens[0], 99, esquema="rnc")
    assert "_377_" in nome and "_099_" not in nome


def test_sem_id_no_indice_cai_no_ordinal_e_avisa(itens):
    item = dict(itens[0], id_dgert="")
    nome, avisos = nome_documento(item, 7, esquema="rnc")
    assert "_007_" in nome
    assert any("ordinal interno" in a for a in avisos)


def test_esquema_desconhecido_e_recusado(itens):
    with pytest.raises(ValueError, match="esquema"):
        nome_documento(itens[0], 1, esquema="sharepoint")


def test_siglas_pela_ordem_do_indice_e_o_resto_contado(itens):
    siglas, restantes, _ = siglas_outorgantes(itens[0])
    assert siglas == ["ACRAL", "CESP", "STRUP"]
    assert restantes == 2


def test_tipo_normalizado():
    assert tipo_normalizado("CCT-ALT") == "CCT-ALT"
    assert tipo_normalizado("ae-alt-rect") == "AE-ALT-RECT"
    assert tipo_normalizado(" ") == "SEMTIPO"


# ------------------------------------------------------------------- âmbito

def test_empresa_municipal_e_spe_e_fica_por_rever():
    amb, origem, aviso = ambito.classificar(
        "Empresa Metropolitana de Estacionamento da Maia, EM", "AE")
    assert (amb, origem) == ("SPE", "regra")
    assert aviso, "a regra nunca decide em silêncio"


def test_acep_e_apu_e_nao_e_processavel():
    amb, _, aviso = ambito.classificar("Município de Lisboa", "ACEP")
    assert amb == "APU" and aviso
    assert not ambito.processavel("APU")
    assert ambito.processavel("PRI") and ambito.processavel("SPE")


def test_o_vocabulario_ganha_a_regra():
    voc = {"empresa metropolitana de estacionamento da maia, em": "PRI"}
    assert ambito.classificar("Empresa Metropolitana de Estacionamento da Maia, EM",
                              "AE", voc) == ("PRI", "vocabulario", None)


def test_privado_por_omissao_nao_gera_aviso():
    assert ambito.classificar("IBERCOURIER - Serviço de Transporte Urgente, "
                              "Unipessoal L.da", "AE") == ("PRI", "omissao", None)


def test_forma_juridica_dentro_de_palavra_nao_conta():
    """«, EM» é forma jurídica; o «ém» de «Armazém» não é."""
    assert ambito.classificar("Armazém Central, L.da", "AE")[0] == "PRI"


def test_vocabulario_recusa_valor_fora_do_fechado(tmp_path, capsys):
    csv_ = tmp_path / "amb.csv"
    csv_.write_text("nome;ambito\nAlguma Empresa;PUBLICO\nOutra;SPE\n",
                    encoding="utf-8")
    voc = ambito.carregar_vocabulario(csv_)
    assert voc == {"outra": "SPE"}
    assert "PUBLICO" in capsys.readouterr().out


# ------------------------------------------------------------------ catálogo

def test_paginas_saem_do_nome_de_origem():
    assert paginas("00260057.pdf") == (26, 57)
    assert paginas("01680170.pdf") == (168, 170)
    assert paginas("qualquer.pdf") == (None, None)
    assert paginas("00570026.pdf") == (None, None)      # fim antes do início


def test_acto_de_negociacao_sai_do_codigo_irct():
    """27251 é o acto 7251 com o dígito de família do contrato coletivo."""
    assert acto_negociacao("27251") == "7251"
    assert acto_negociacao("47252") == "7252"
    assert acto_negociacao("312") == "312"      # códigos curtos ficam intactos


def test_cadeia_de_alteracoes_separada():
    estruturado, resto = separar_alteracoes(
        "CCT-ALT.20250708.321/2025; alterado pelo BTE 3 de 2024")
    assert estruturado == [{"tipo": "CCT-ALT", "data": "20250708",
                            "seq": "321", "ano": "2025"}]
    assert resto == ["alterado pelo BTE 3 de 2024"]


def test_sectores_e_materias_saem_separados():
    materias, sectores = separar_sectores(
        "VINHOS E BEBIDAS ESPIRITUOSAS; VITICULTURA; REMUNERAÇÕES; "
        "SUBSÍDIO DE REFEIÇÃO")
    assert materias == ["REMUNERAÇÕES", "SUBSÍDIO DE REFEIÇÃO"]
    assert sectores == ["VINHOS E BEBIDAS ESPIRITUOSAS", "VITICULTURA"]


def test_nada_se_perde_na_separacao_dos_sectores():
    bruto = "SEGUROS; RESSEGUROS; TELETRABALHO; ALGO QUE NINGUÉM CLASSIFICOU"
    materias, sectores = separar_sectores(bruto)
    assert sorted(materias + sectores) == sorted(
        p.strip() for p in bruto.split(";"))


def test_catalogo_tem_uma_linha_por_documento(tmp_path, itens):
    linhas = catalogo.linhas(itens)
    assert len(linhas) == len(LINHAS)
    assert [l["seq_anual"] for l in linhas] == [377, 379, 382, 387]
    assert {l["nome_canonico"] for l in linhas}.__len__() == len(LINHAS)
    assert all(set(l) >= set(catalogo.COLUNAS) for l in linhas)


def test_apu_fica_catalogado_mas_nao_processavel(itens):
    item = dict(itens[0], tipo="ACEP",
                outorgantes="Município de Lisboa; SINTAP")
    linha = catalogo.linhas([item])[0]
    assert linha["ambito"] == "APU"
    assert linha["estado"] == "nao_processavel"
    assert linha["ficheiro_destino"].startswith("1_fontes/irct/APU/")


def test_regerar_o_catalogo_preserva_o_que_a_equipa_escreveu(tmp_path, itens):
    saida = tmp_path / "catalogo.csv"
    catalogo.escrever(catalogo.linhas(itens), saida)

    with open(saida, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    linhas[0]["perita"] = "AF"
    linhas[0]["temas_atribuidos"] = "4.08"
    linhas[0]["estado"] = "validado"
    catalogo.escrever(linhas, saida)

    catalogo.escrever(catalogo.fundir(catalogo.linhas(itens), saida), saida)
    with open(saida, encoding="utf-8", newline="") as f:
        refeitas = list(csv.DictReader(f, delimiter=";"))
    assert len(refeitas) == len(LINHAS)
    assert refeitas[0]["perita"] == "AF"
    assert refeitas[0]["temas_atribuidos"] == "4.08"
    assert refeitas[0]["estado"] == "validado"


def test_linha_que_desaparece_do_indice_e_assinalada_nao_apagada(tmp_path, itens):
    saida = tmp_path / "catalogo.csv"
    catalogo.escrever(catalogo.linhas(itens), saida)
    catalogo.escrever(catalogo.fundir(catalogo.linhas(itens[:1]), saida), saida)
    with open(saida, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    assert len(linhas) == len(LINHAS)
    orfas = [l for l in linhas if "já não consta" in l["avisos"]]
    assert len(orfas) == len(LINHAS) - 1


# ----------------------------------------------------- tabela de siglas

def test_tabela_de_siglas_nos_dois_formatos(tmp_path):
    sem_cabecalho = tmp_path / "curta.csv"
    sem_cabecalho.write_text("Sindicato Nacional dos Motoristas;SNM\n",
                             encoding="utf-8")
    assert carregar_siglas(sem_cabecalho) == {
        "sindicato nacional dos motoristas": "SNM"}

    com_cabecalho = tmp_path / "registo.csv"
    com_cabecalho.write_text(
        "codigo_dgert;denominacao;sigla;origem_sigla\n"
        "1.1.0;SINDICATO NACIONAL DOS MOTORISTAS;MOTORISTAS;recurso\n"
        "1.2.0;FESAHT - FEDERACAO DOS SINDICATOS DA AGRICULTURA;FESAHT;registo\n",
        encoding="utf-8")
    tabela = carregar_siglas(com_cabecalho)
    assert tabela == {"fesaht - federacao dos sindicatos da agricultura": "FESAHT"}, \
        "uma sigla inventada pelo script não é uma sigla confirmada"


def test_siglas_do_repositorio_carregam(tmp_path):
    """O vocabulário versionado tem de ser legível pela bandeira --siglas."""
    caminho = Path(__file__).resolve().parent.parent / "vocabularios" \
        / "siglas_organizacoes.csv"
    if not caminho.exists():
        pytest.skip("vocabulário não construído neste ambiente")
    tabela = carregar_siglas(caminho)
    assert len(tabela) > 1000
    assert all(s and s.isascii() for s in tabela.values())
