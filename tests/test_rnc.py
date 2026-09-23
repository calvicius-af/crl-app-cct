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
from cct.siglas import atribuir, candidatos, linhagem, palavras_distintivas
from cct.nomeacao import (AVISO_BASE_PELA_CADEIA, carregar_siglas, nome_documento, resolver_convencoes_base, sequencial_bte,
                          siglas_outorgantes, tipo_normalizado)
from cct.nomeacao import familia_do_nome
from cct.recolha import FAMILIAS_POR_OMISSAO, familia, ler_indice

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

def test_nome_rnc_comeca_por_ano_e_boletim(itens):
    """ADR-0022: cabeça {ANO}_BTE_{NN}_{AMBITO}_{SEQ}, cauda {CODIRCT}_{SIGLAS}."""
    nome, avisos = nome_documento(itens[0], 1, esquema="rnc")
    assert nome == "2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3"
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


def test_os_esquemas_antigos_continuam_a_ser_lidos():
    """2025 e ADR-0016: já não se escrevem, mas os ficheiros existem."""
    assert interpretar_doc_id("25_PR_016_BTE_04_EMARP_SINTAP") == (
        25, 4, ["emarp", "sintap"])
    assert interpretar_nome_rnc("25_PR_016_BTE_04_EMARP_SINTAP") is None
    assert interpretar_doc_id("2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2") == (
        26, 31, ["acral", "cesp", "strup"])


def test_metadados_que_o_nome_do_adr0016_leva():
    meta = interpretar_nome_rnc("2026_SPE_387_AE-ALT-RECT_47109_BTE_31_CARRISTUR-ASPTC")
    assert meta == {"esquema": "adr0016", "ano": 2026, "ambito": "SPE", "seq": 387,
                    "tipo": "AE-ALT-RECT", "cod_irct": "47109", "num_bte": 31,
                    "siglas": ["CARRISTUR", "ASPTC"], "outros_outorgantes": 0,
                    "familia": None, "portaria": None, "ano_dr": None}


def test_metadados_que_o_nome_do_adr0022_leva():
    meta = interpretar_nome_rnc("2026_BTE_01_PE_012_0452-2025_27251_ACRAL-CESP+1")
    assert meta == {"esquema": "adr0022", "ano": 2026, "ambito": None, "seq": 12,
                    "tipo": "PE", "cod_irct": "27251", "num_bte": 1,
                    "siglas": ["ACRAL", "CESP"], "outros_outorgantes": 1,
                    "familia": "extensao", "portaria": "0452", "ano_dr": 2025}


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


def test_siglas_um_de_cada_lado_e_o_resto_contado(itens):
    """ADR-0022: primeira patronal, primeira sindical, +N para as restantes."""
    siglas, restantes, avisos = siglas_outorgantes(itens[0])
    assert siglas == ["ACRAL", "CESP"]
    assert restantes == 3
    assert not avisos


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
    assert linha["familia"] == "convencao", "um ACEP é uma convenção, de âmbito APU"
    assert linha["processavel"] == "nao"
    assert linha["ficheiro_destino"].startswith("1_fontes/irct/convencoes/APU/")


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


# ------------------------------------------------ a regra das siglas (ADR-0017)

def _org(codigo, denominacao, base, concelho="", ultima="2020-01-01"):
    return dict(codigo_dgert=codigo, denominacao=denominacao, sigla_base=base,
                concelho=concelho, ultima_atividade=ultima)


def test_a_sigla_que_nao_colide_fica_como_esta():
    """A regra resolve duplicados; não corrige o registo da DGERT."""
    orgs = [_org("1.1.0", "SINDICATO DOS PESCADORES DE SETUBAL", "SPS"),
            _org("5.1.0", "ASSOCIACAO DOS ARMADORES DA PESCA", "ADAPLA")]
    assert atribuir(orgs) == {("1.1", "SPS"): "SPS", ("5.1", "ADAPLA"): "ADAPLA"}


def test_o_duplicado_sobe_a_escada_com_a_palavra_distintiva():
    """O caso que a coordenação pediu: SNM ocupado → SNMotoristas."""
    orgs = [_org("1.100.0", "SINDICATO NACIONAL DA MARINHA MERCANTE", "SNM"),
            _org("1.402.1", "SINDICATO NACIONAL DOS MOTORISTAS", "SNM")]
    resultado = atribuir(orgs)
    assert resultado[("1.100", "SNM")] == "SNM"
    assert resultado[("1.402", "SNM")] == "SNMotoristas"


def test_a_linhagem_mais_antiga_fica_com_a_sigla_curta():
    orgs = [_org("1.402.1", "SINDICATO NACIONAL DOS MOTORISTAS", "SNM"),
            _org("1.100.0", "SINDICATO NACIONAL DA MARINHA MERCANTE", "SNM")]
    assert atribuir(orgs)[("1.100", "SNM")] == "SNM", \
        "1.100 é mais antiga do que 1.402, e chegou em segundo lugar"


def test_o_resultado_nao_depende_da_ordem_de_chegada():
    orgs = [_org("5.1.0", "ASSOCIACAO COMERCIAL DE ESPINHO", "ACE", "ESPINHO"),
            _org("5.9.0", "ASSOCIACAO COMERCIAL DE ABRANTES", "ACE", "ABRANTES"),
            _org("1.402.1", "SINDICATO NACIONAL DOS MOTORISTAS", "SNM"),
            _org("1.100.0", "SINDICATO NACIONAL DA MARINHA", "SNM")]
    assert atribuir(orgs) == atribuir(list(reversed(orgs)))


def test_geracoes_da_mesma_organizacao_nao_sao_conflito():
    """O SITESE mudou de nome seis vezes e continua a ser o SITESE."""
    orgs = [_org("1.402.1", "SINDICATO DOS TRABALHADORES DE ESCRITORIO", "SITESE"),
            _org("1.402.3", "SINDICATO DOS TRABALHADORES E TECNICOS", "SITESE")]
    assert set(atribuir(orgs).values()) == {"SITESE"}


def test_uma_sigla_ja_atribuida_nao_se_reatribui():
    orgs = [_org("1.100.0", "SINDICATO NACIONAL DA MARINHA MERCANTE", "SNM"),
            _org("1.402.1", "SINDICATO NACIONAL DOS MOTORISTAS", "SNM")]
    resultado = atribuir(orgs, fixadas={("1.402", "SNM"): "SNM"})
    assert resultado[("1.402", "SNM")] == "SNM"
    assert resultado[("1.100", "SNM")] != "SNM"


def test_a_unicidade_ignora_maiusculas():
    """`SNMotoristas` e `SNMOTORISTAS` são o mesmo ficheiro no Windows."""
    orgs = [_org("1.1.0", "ALGUMA COISA", "SNMotoristas"),
            _org("2.1.0", "OUTRA COISA", "SNMOTORISTAS")]
    siglas = list(atribuir(orgs).values())
    assert len({s.upper() for s in siglas}) == 2


def test_nunca_sobram_duplicados_por_muitos_que_sejam():
    orgs = [_org(f"{i}.1.0", "ASSOCIACAO COMERCIAL DE ESPINHO", "ACE", "ESPINHO")
            for i in range(1, 9)]
    siglas = list(atribuir(orgs).values())
    assert len({s.upper() for s in siglas}) == len(orgs)


def test_encurta_se_a_base_e_nao_o_que_distingue():
    """`COMERCIALCONCELHOeir` não diz Oeiras nem se distingue de Oliveira."""
    orgs = [_org("5.1.0", "ASSOCIACAO COMERCIAL DO CONCELHO DE GONDOMAR",
                 "COMERCIALCONCELHO", "GONDOMAR"),
            _org("5.2.0", "ASSOCIACAO COMERCIAL DO CONCELHO DE OEIRAS",
                 "COMERCIALCONCELHO", "OEIRAS")]
    valores = atribuir(orgs)
    assert valores[("5.2", "COMERCIALCONCELHO")].endswith("Oeiras")
    assert all(len(v) <= 20 for v in valores.values())


def test_qualificador_fraco_fica_para_o_fim():
    assert palavras_distintivas(
        "ASSOCIACAO COMERCIAL DE ESPINHO E OUTROS CONCELHOS")[0] == "Espinho"


def test_a_escada_acaba_sempre_num_candidato_unico():
    escada = candidatos("ACE", "ASSOCIACAO COMERCIAL DE ESPINHO", "ESPINHO", "5.246.4")
    assert escada[0] == "ACE"
    assert "52464" in escada[-1], "o último degrau leva o código DGERT"


def test_linhagem():
    assert linhagem("1.402.1") == linhagem("1.402.3") == "1.402"
    assert linhagem("1.402.1") != linhagem("5.402.1")


# ----------------------------------- o dígito de família do COD: (IRCT)

def test_so_se_traduz_o_codigo_das_familias_verificadas():
    assert acto_negociacao("27251") == "7251"      # contrato coletivo
    assert acto_negociacao("47252") == "7252"      # acordo de empresa
    assert acto_negociacao("37000") == "", \
        "o dígito dos acordos coletivos está por determinar — não se adivinha"
    assert acto_negociacao("312") == "312"         # códigos curtos, intactos


# --------------------------- famílias: extensões, adesões e avisos (ADR-0018)

LINHAS_NAO_CONVENCAO = [
    # Portaria publicada no DR em 2025 e publicitada no BTE em 2026: conta
    # para os dados de 2026 (ADR-0022).
    dict(id="401/2026", tipo="PE", cod="27251", pdf="00010004.pdf",
         titulo="Portaria n.º 452/2025 - Portaria que estende o contrato coletivo "
                "entre a Associação do Comércio e Serviços da Região do Algarve - "
                "ACRAL e o CESP - Sindicato dos Trabalhadores do Comércio.",
         outorgantes="", altera="CCT.20260822.377/2026",
         sectores="COMÉRCIO A RETALHO", em_vigor=""),
    dict(id="402/2026", tipo="AA", cod="27251", pdf="00050006.pdf",
         titulo="Acordo de adesão entre a Algarve Retalho, L.da e o CESP - "
                "Sindicato dos Trabalhadores do Comércio ao contrato coletivo "
                "entre a ACRAL e o CESP.",
         outorgantes="Algarve Retalho, L.da - ALGRET; CESP - Sindicato dos "
                     "Trabalhadores do Comércio, Escritórios e Serviços de Portugal",
         altera="CCT.20260822.377/2026",
         sectores="SOLIDARIEDADE SOCIAL", em_vigor=""),
    dict(id="403/2026", tipo="AVISO", cod="26651", pdf="00070007.pdf",
         titulo="Aviso de projeto de portaria de extensão do contrato coletivo "
                "entre a AEVP e a FESAHT.",
         outorgantes="", altera="CCT-ALT.20260822.379/2026",
         sectores="VITICULTURA", em_vigor=""),
]


def _itens_de(*linhas_indice, pasta=None):
    """Lê um índice de ensaio feito só com as linhas indicadas."""
    import tempfile

    global LINHAS
    originais = LINHAS
    destino = Path(pasta or tempfile.mkdtemp())
    try:
        LINHAS = list(linhas_indice)
        return ler_indice(escrever_indice_tecnico(destino, "BTE33_2026.xlsx"))
    finally:
        LINHAS = originais


@pytest.fixture()
def itens_mistos(tmp_path):
    global LINHAS
    originais = LINHAS
    try:
        LINHAS = originais + LINHAS_NAO_CONVENCAO
        return ler_indice(escrever_indice_tecnico(tmp_path, "BTE33_2026.xlsx"))
    finally:
        LINHAS = originais


def test_o_vocabulario_de_tipos_cobre_as_quatro_familias():
    assert familia("CCT") == familia("AE") == familia("ACT") == "convencao"
    assert familia("ACEP") == "convencao", "um ACEP é uma convenção, de âmbito APU"
    assert familia("DA") == "convencao", "a decisão arbitral substitui a convenção"
    assert familia("PE") == familia("PCT") == familia("PRT") == "extensao"
    assert familia("AA") == familia("AA-ALT") == "adesao"
    assert familia("AVISO") == familia("AV") == "aviso"
    assert familia("ST") is None, "um tipo desconhecido não é adivinhado"


def test_as_adesoes_sao_recolhidas_por_omissao():
    """Estavam de fora, e uma adesão publicada não deixava rasto nenhum."""
    assert "adesao" in FAMILIAS_POR_OMISSAO
    assert set(FAMILIAS_POR_OMISSAO) == {"convencao", "extensao", "adesao", "aviso"}


def test_cada_familia_vai_para_a_sua_pasta(itens_mistos):
    destinos = {l["tipo_documento"]: l["ficheiro_destino"]
                for l in catalogo.linhas(itens_mistos)}
    assert destinos["CCT"].startswith("1_fontes/irct/convencoes/PRI/")
    assert destinos["PE"].startswith("1_fontes/irct/portarias_extensao/")
    assert destinos["AA"].startswith("1_fontes/irct/acordos_adesao/")
    assert destinos["AVISO"] == "", "um aviso não tem ficheiro — é metadado"


def test_so_as_convencoes_se_subdividem_por_ambito(itens_mistos):
    """Numa portaria o âmbito não decide nada: nenhuma entra no pipeline."""
    destinos = {l["tipo_documento"]: l["ficheiro_destino"]
                for l in catalogo.linhas(itens_mistos)}
    assert destinos["PE"].count("/") == 3, destinos["PE"]
    assert destinos["CCT"].count("/") == 4, destinos["CCT"]
    assert "/PRI/" not in destinos["PE"] and "/SPE/" not in destinos["PE"]


def test_o_aviso_fica_como_metadado_da_portaria():
    """«Registados apenas em metadados das portarias», sem perder a linha."""
    base = dict(LINHAS_NAO_CONVENCAO[0])          # a portaria
    aviso = dict(LINHAS_NAO_CONVENCAO[2], altera=base["altera"])
    linhas = catalogo.ligar_avisos(catalogo.linhas(_itens_de(base, aviso)))
    portaria = next(l for l in linhas if l["familia"] == "extensao")
    linha_aviso = next(l for l in linhas if l["familia"] == "aviso")
    assert portaria["avisos_projeto"], "a portaria tem de saber que houve projeto"
    assert linha_aviso["ficheiro_destino"] == ""
    assert linha_aviso["estado"] == "metadado", "a linha fica; o PDF é que não"


def test_so_as_convencoes_sao_processaveis(itens_mistos):
    por_familia = {l["familia"]: l["processavel"]
                   for l in catalogo.linhas(itens_mistos)}
    assert por_familia["convencao"] == "sim"
    assert por_familia["extensao"] == por_familia["adesao"] == "nao"
    assert por_familia["aviso"] == "nao"


def test_a_relacao_com_a_convencao_base_e_nomeada(itens_mistos):
    linhas = {l["tipo_documento"]: l for l in catalogo.linhas(itens_mistos)}
    assert linhas["PE"]["relacao"] == "estende"
    assert linhas["PE"]["relacao_alvo"] == "CCT.20260822.377/2026"
    assert linhas["AA"]["relacao"] == "adere"
    assert linhas["AVISO"]["relacao"] == "refere"
    assert linhas["CCT-ALT"]["relacao"] == "altera", \
        "uma revisão altera; uma portaria não — contá-las juntas é contar mal"


def test_a_portaria_herda_as_partes_do_titulo(itens_mistos):
    """Uma portaria não tem outorgantes: quem a emite é o Governo."""
    resolver_convencoes_base(itens_mistos)
    pe = next(i for i in itens_mistos if i["tipo"] == "PE")
    assert pe["outorgantes"] == ""
    nome, avisos = nome_documento(pe, 1, esquema="rnc")
    assert nome == "2026_BTE_31_PE_401_0452-2025_27251_ACRAL-CESP"
    assert any("título" in a for a in avisos)
    assert AVISO_BASE_PELA_CADEIA in avisos, \
        "até ao passo 0 da SPEC-0004, a base lida da cadeia fica por confirmar"


def test_a_familia_le_se_do_nome_nos_tres_esquemas():
    assert familia_do_nome("2026_BTE_01_PE_012_0452-2025_27251_ACRAL-CESP") == "extensao"
    assert familia_do_nome("2026_BTE_12_AA_412_27251_ABC-CESP") == "adesao"
    assert familia_do_nome("2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3") == "convencao"
    assert familia_do_nome("2026_BTE_31_SPE_387_AE-ALT-RECT_47109_CARRISTUR-ASPTC") \
        == "convencao"
    assert familia_do_nome("2026_PRI_401_PE_27251_BTE_33_ACRAL-CESP") == "extensao"
    assert familia_do_nome("2026_PRI_377_CCT_27251_BTE_31_ACRAL") == "convencao"
    assert familia_do_nome("26_PE_001_BTE_31_ACRAL_CESP") == "extensao"
    assert familia_do_nome("26_PR_003_BTE_31_ACRAL_CESP") == "convencao"
    assert familia_do_nome("um_ficheiro_qualquer") is None


def test_o_pipeline_recusa_o_que_nao_e_convencao(tmp_path, monkeypatch):
    """Uma portaria codificada como convenção não dá erro: dá números errados."""
    from cct import pipeline_tema

    pasta = tmp_path / "pdfs"
    pasta.mkdir()
    for nome in ("2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP.pdf",
                 "2026_BTE_33_PE_401_0452-2025_27251_ACRAL-CESP.pdf",
                 "2026_BTE_33_AA_402_27251_ALGRET-CESP.pdf",
                 "2026_PRI_401_PE_27251_BTE_33_ACRAL-CESP.pdf",
                 # renomeada à mão antes do ADR-0022: nenhum esquema a lê
                 "2026_001_BTE_01_PE_0452_ADCP_SETAAB.pdf"):
        (pasta / nome).write_bytes(b"%PDF-1.4\n")
    codebook = tmp_path / "cb.yaml"
    codebook.write_text("tema: ensaio\ncodigos: []\n", encoding="utf-8")

    monkeypatch.setattr("sys.argv",
                        ["cct.pipeline_tema", "--pdfs", str(pasta),
                         "--codebook", str(codebook),
                         "--out", str(tmp_path / "out")])
    with pytest.raises(SystemExit) as erro:
        pipeline_tema.main()
    mensagem = str(erro.value)
    assert "4 ficheiro(s)" in mensagem, mensagem
    assert "2026_001_BTE_01_PE_0452_ADCP_SETAAB.pdf  (extensao?)" in mensagem
    assert "_PE_" in mensagem and "_AA_" in mensagem
    assert "convencoes" in mensagem, "a mensagem tem de dizer para onde apontar"


def test_pdfs_da_pasta_encontra_direto_e_nas_subpastas_de_ambito(tmp_path):
    """`--pdfs` continua a aceitar a pasta do ano (ADR-0021, PR #69)."""
    from cct.pipeline_tema import _pdfs_da_pasta

    # esquema de 2025, ou já a pasta de um âmbito: direto, sem procurar mais
    direta = tmp_path / "direta"
    direta.mkdir()
    (direta / "26_PR_001_BTE_31_ACRAL_CESP.pdf").write_bytes(b"%PDF-1.4\n")
    assert _pdfs_da_pasta(direta) == [direta / "26_PR_001_BTE_31_ACRAL_CESP.pdf"]

    # esquema RNC: nada direto na pasta do ano, mas convencoes/PRI e SPE têm
    ano = tmp_path / "bte_2026"
    for sigla_ambito in ("PRI", "SPE", "APU"):
        (ano / "convencoes" / sigla_ambito).mkdir(parents=True)
    (ano / "convencoes" / "PRI" / "2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP.pdf"
     ).write_bytes(b"%PDF-1.4\n")
    (ano / "convencoes" / "SPE" / "2026_SPE_382_AE_47252_BTE_31_EMEM-SINTAP.pdf"
     ).write_bytes(b"%PDF-1.4\n")
    (ano / "convencoes" / "APU" / "2026_APU_999_ACEP_1_BTE_31_X-Y.pdf"
     ).write_bytes(b"%PDF-1.4\n")

    achados = _pdfs_da_pasta(ano)
    assert [f.name for f in achados] == [
        "2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP.pdf",
        "2026_SPE_382_AE_47252_BTE_31_EMEM-SINTAP.pdf",
    ], "APU não é processável (README §4.3) — não entra na descoberta automática"
    assert _pdfs_da_pasta(ano / "convencoes") == achados, (
        "a pasta convencoes também deve encontrar PRI e SPE sem duplicar o caminho")
    assert _pdfs_da_pasta(ano / "convencoes" / "PRI") == achados[:1]
    assert _pdfs_da_pasta(ano / "convencoes" / "SPE") == achados[1:]


def test_pdfs_da_pasta_sem_nada_devolve_lista_vazia(tmp_path):
    from cct.pipeline_tema import _pdfs_da_pasta

    vazia = tmp_path / "vazia"
    vazia.mkdir()
    assert _pdfs_da_pasta(vazia) == []


# ------------------------ a lista do INE como sinal, não como autoridade (ADR-0019)

INE = [
    # entidades com forma empresarial em S.13: empresas públicas reclassificadas
    ("Metropolitano de Lisboa, E.P.E.", "SPE_PROVAVEL", "S.13112"),
    ("Rádio e Televisão de Portugal, S.A.", "SPE_PROVAVEL", "S.13112"),
    ("TUB - Empresa de Transportes Urbanos de Braga, E.M.", "SPE_PROVAVEL", "S.131324"),
    # administração pública em sentido estrito
    ("Município de Vila Real", "APU", "S.131322"),
    ("União das freguesias de Real, Dume e Semelhe", "APU", "S.131323"),
    ("Instituto Nacional de Estatística", "APU", "S.13111"),
]


@pytest.fixture()
def tabela_ine(tmp_path):
    caminho = tmp_path / "ine.csv"
    linhas = ["nome;sinal;subsetor;subsetor_nome;forma_empresarial;fonte;ano"]
    linhas += [f"{n};{s};{sub};x;{'sim' if s == 'SPE_PROVAVEL' else 'nao'};"
               f"INE S.13 2025;2025" for n, s, sub in INE]
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return ambito.carregar_entidades_publicas(caminho)


def test_uma_empresa_publica_em_s13_nao_e_apu(tabela_ine):
    """O erro que esta lista podia causar, e que não pode causar.

    O Metropolitano de Lisboa está em S.13 por critério de contas nacionais,
    mas os seus trabalhadores estão sob o Código do Trabalho e o seu acordo de
    empresa sai no BTE. Classificá-lo APU retirava-o do pipeline em silêncio.
    """
    for nome in ("Metropolitano de Lisboa, E.P.E.",
                 "Rádio e Televisão de Portugal, S.A.",
                 "TUB - Empresa de Transportes Urbanos de Braga, E.M."):
        amb, origem, aviso = ambito.classificar_com_ine(
            nome, "AE", {}, tabela_ine)
        assert amb == "SPE", nome
        assert ambito.processavel(amb), f"{nome} tem de continuar processável"
        assert origem == "ine" and aviso


def test_municipios_e_freguesias_sao_apu(tabela_ine):
    for nome in ("Município de Vila Real",
                 "União das freguesias de Real, Dume e Semelhe"):
        amb, origem, aviso = ambito.classificar_com_ine(nome, "ACEP", {}, tabela_ine)
        assert (amb, origem) == ("APU", "ine"), nome
        assert not ambito.processavel(amb)
        assert aviso, "mesmo quando acerta, a lista não decide em silêncio"


def test_a_lista_do_ine_nunca_decide_sem_aviso(tabela_ine):
    """O critério do INE não é o do RNC: toda a proposta dela é para confirmar."""
    for nome, _sinal, _sub in INE:
        _amb, origem, aviso = ambito.classificar_com_ine(nome, "", {}, tabela_ine)
        assert origem == "ine" and aviso and "confirmado" in aviso


def test_o_vocabulario_da_equipa_ganha_a_lista_do_ine(tabela_ine):
    voc = {"metropolitano de lisboa, e.p.e.": "APU"}
    assert ambito.classificar_com_ine(
        "Metropolitano de Lisboa, E.P.E.", "AE", voc, tabela_ine) == (
        "APU", "vocabulario", None)


def test_ausencia_da_lista_nao_diz_nada(tabela_ine):
    """A CP, a Carris e a EPAL são SPE e não estão em S.13 — passam o teste de
    mercado. Cair fora da lista não pode significar «privado confirmado»."""
    amb, origem, aviso = ambito.classificar_com_ine(
        "CP - Comboios de Portugal, E.P.E.", "AE", {}, tabela_ine)
    assert origem != "ine"
    assert amb == "SPE", "apanhado pela regra da forma jurídica, não pela lista"


def test_nomes_curtos_nao_encaixam_por_acaso(tmp_path):
    """Com 4 241 entidades, uma chave curta encaixa dentro de outro nome."""
    caminho = tmp_path / "ine.csv"
    caminho.write_text("nome;sinal;subsetor;subsetor_nome;forma_empresarial;fonte;ano\n"
                       "Maia;APU;S.131322;x;nao;INE;2025\n"
                       "Município da Maia;APU;S.131322;x;nao;INE;2025\n",
                       encoding="utf-8")
    tabela = ambito.carregar_entidades_publicas(caminho)
    assert "maia" not in tabela, "chave demasiado curta para ser segura"
    assert "municipio da maia" in tabela


def test_a_lista_versionada_carrega_e_distingue_os_dois_sinais():
    caminho = (Path(__file__).resolve().parent.parent / "vocabularios"
               / "entidades_administracao_publica.csv")
    if not caminho.exists():
        pytest.skip("vocabulário não construído neste ambiente")
    tabela = ambito.carregar_entidades_publicas(caminho)
    assert len(tabela) > 4000
    ambitos = {a for a, _sub in tabela.values()}
    assert ambitos == {"APU", "SPE"}, \
        "as duas camadas têm de sobreviver ao ficheiro"
    metro = [v for k, v in tabela.items() if "metropolitano de lisboa" in k]
    assert metro and metro[0][0] == "SPE"
