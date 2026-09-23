"""Testes do esquema de nomes comum às três famílias (ADR-0022, SPEC-0004).

Um só esquema para convenções, portarias de extensão e acordos de adesão:

    {ANO}_BTE_{NN}_{X}_{SEQ}_{miolo}_{CODIRCT}_{SIGLA1}-{SIGLA2}[+N]

O que se protege aqui é o contrato do nome — que o resto da aplicação o lê, que
um campo estrutural em falta nunca dá um nome, e que a migração única dos nomes
do ADR-0016 não perde nem ficheiros nem o trabalho da equipa no catálogo.
Correm offline, sobre o índice de ensaio de `tests/test_rnc.py`.
"""
import csv
import fnmatch
import hashlib

import pytest

from cct import catalogo
from cct.localizador import (RE_DOC_ID_CONVENCAO, RE_DOC_ID_RNC,
                             interpretar_doc_id, interpretar_nome_rnc)
from cct.nomeacao import (AVISO_BASE_PELA_CADEIA, MAX_NOME, NomeRNCInvalido,
                          escrever_correspondencia, familia_do_nome,
                          nome_documento, nomear, referencia_portaria,
                          resolver_convencoes_base, siglas_outorgantes)
from cct.recolha import Registo

from .test_rnc import LINHAS, LINHAS_NAO_CONVENCAO, _itens_de

ACRAL_CCT = LINHAS[0]                       # 377/2026, CCT, 27251
AEVP_ALT = LINHAS[1]                        # 379/2026, CCT-ALT, 26651
PE, AA, AVISO = LINHAS_NAO_CONVENCAO


def _nomes(*linhas_indice):
    """Nomes do esquema RNC para um índice de ensaio, com a base resolvida."""
    itens = _itens_de(*linhas_indice)
    resolver_convencoes_base(itens)
    return {i["tipo"]: nome_documento(i, n, esquema="rnc")
            for n, i in enumerate(itens, 1)}


# --------------------------------------------------------- forma do nome

def test_ida_e_volta_nas_tres_familias():
    nomes = _nomes(ACRAL_CCT, PE, AA)
    familias = {"CCT": "convencao", "PE": "extensao", "AA": "adesao"}
    for tipo, (nome, _avisos) in nomes.items():
        assert len(nome) <= MAX_NOME, nome
        assert interpretar_doc_id(nome)[:2] == (26, 31), nome
        meta = interpretar_nome_rnc(nome)
        assert meta and meta["esquema"] == "adr0022", nome
        assert meta["familia"] == familias[tipo]
        assert familia_do_nome(nome) == familias[tipo]


def test_cabeca_comum_e_agrupamento_por_ano_e_boletim():
    nomes = sorted(n for n, _ in _nomes(ACRAL_CCT, AEVP_ALT, PE, AA).values())
    assert all(n.startswith("2026_BTE_31_") for n in nomes)
    # dentro do boletim, o quarto campo agrupa antes do sequencial: a ordem
    # integral de publicação está no catálogo, não no nome (ADR-0022, regra 1)
    assert [n.split("_")[3] for n in nomes] == ["AA", "PE", "PRI", "PRI"]


def test_o_quarto_campo_e_ambito_ou_tipo_nunca_o_contrario():
    nomes = _nomes(ACRAL_CCT, PE, AA)
    assert nomes["CCT"][0].split("_")[3] in ("PRI", "SPE", "APU")
    assert nomes["PE"][0].split("_")[3] == "PE"
    assert nomes["AA"][0].split("_")[3] == "AA"
    # e as expressões regulares não se confundem entre esquemas
    for nome, _ in nomes.values():
        assert not RE_DOC_ID_RNC.match(nome), nome
    assert not RE_DOC_ID_CONVENCAO.match(nomes["PE"][0])
    assert not RE_DOC_ID_CONVENCAO.match("2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP")


def test_nenhuma_contagem_interna_entra_no_nome():
    nome, _ = _nomes(ACRAL_CCT, PE)["PE"]
    assert "_401_" in nome, "o sequencial é o da DGCP (IDDocumento 401/2026)"
    nome, _ = nome_documento(_itens_de(ACRAL_CCT)[0], 999, esquema="rnc")
    assert "999" not in nome


# ------------------------------------------------------ portarias de extensão

def test_portaria_do_dr_de_2025_no_bte_de_2026():
    nome, _ = _nomes(ACRAL_CCT, PE)["PE"]
    assert nome.startswith("2026_BTE_31_PE_401_0452-2025_"), \
        "ANO é o do BTE (dados de 2026); o ano do DR fica no miolo"


@pytest.mark.parametrize("titulo,esperado", [
    ("Portaria n.º 452/2025 - Portaria de extensão", (452, "", 2025)),
    ("Portaria n.º 50-A/2025, de 3 de fevereiro", (50, "A", 2025)),
    ("Portaria nº 7/2026 - extensão do CCT", (7, "", 2026)),
    ("Portaria de extensão do contrato coletivo entre a X e o Y", None),
    ("Portaria n.º 12/2027", None),        # DR posterior ao BTE: leitura errada
])
def test_referencia_da_portaria(titulo, esperado):
    assert referencia_portaria({"ano": 2026, "titulo": titulo}) == esperado


def test_portaria_com_sufixo():
    pe = dict(PE, titulo="Portaria n.º 50-A/2025 - " + PE["titulo"].split(" - ", 1)[1])
    nome, _ = _nomes(ACRAL_CCT, pe)["PE"]
    assert "_PE_401_0050A-2025_27251_" in nome


def test_a_coluna_do_indice_ganha_ao_titulo():
    entrada = {"ano": 2026, "portaria_dr": "33/2026",
               "titulo": "Portaria n.º 452/2025 - extensão"}
    assert referencia_portaria(entrada) == (33, "", 2026)


# --------------------------------------------------- convenção de base

def test_o_codigo_e_o_da_convencao_de_base():
    """`*_27251_*` junta a convenção, a portaria que a estende e a adesão."""
    nomes = [n for n, _ in _nomes(ACRAL_CCT, AEVP_ALT, PE, AA).values()]
    familia_27251 = fnmatch.filter(nomes, "*_27251_*")
    assert sorted(n.split("_")[3] for n in familia_27251) == ["AA", "PE", "PRI"]


def test_a_base_nao_se_adivinha_pelo_cod_irct_da_propria_portaria():
    """Sem a convenção de base entre as entradas, a PE não tem nome — mesmo
    que o COD: (IRCT) da portaria coincida com o da convenção."""
    pe = _itens_de(PE)[0]
    resolver_convencoes_base([pe])
    assert pe["cod_irct"] == "27251"
    with pytest.raises(NomeRNCInvalido, match="convenção de base"):
        nome_documento(pe, 1, esquema="rnc")


def test_adesao_sem_base_nao_tem_nome():
    aa = dict(AA, altera="CCT.20190301.55/2019")      # convenção de anos anteriores
    itens = _itens_de(ACRAL_CCT, aa)
    resolver_convencoes_base(itens)
    adesao = next(i for i in itens if i["tipo"] == "AA")
    assert adesao["cod_irct_base_por_resolver"] == "CCT.20190301.55/2019"
    with pytest.raises(NomeRNCInvalido):
        nome_documento(adesao, 1, esquema="rnc")


def test_uma_coluna_do_indice_nao_e_substituida_pela_cadeia():
    aa = _itens_de(AA)[0]
    aa["cod_irct_base"] = "11111"
    resolver_convencoes_base([aa])
    assert aa["cod_irct_base"] == "11111"
    assert aa["cod_irct_base_origem"] == "indice"
    nome, avisos = nome_documento(aa, 1, esquema="rnc")
    assert "_AA_402_11111_" in nome
    assert AVISO_BASE_PELA_CADEIA not in avisos


def test_portaria_de_varias_convencoes():
    pe = dict(PE, altera="CCT.20260822.377/2026; CCT-ALT.20260822.379/2026")
    nome, avisos = _nomes(ACRAL_CCT, AEVP_ALT, pe)["PE"]
    assert "_27251_" in nome and "_26651_" not in nome
    assert any("2 convenções" in a for a in avisos)

    linhas = {l["tipo_documento"]: l
              for l in catalogo.linhas(_itens_de(ACRAL_CCT, AEVP_ALT, pe))}
    assert linhas["PE"]["cod_irct_base"] == "27251"
    assert linhas["PE"]["cod_irct_base_adicionais"] == "26651"
    assert linhas["PE"]["relacao_alvo"] == ("CCT.20260822.377/2026; "
                                           "CCT-ALT.20260822.379/2026")


# --------------------------------------------------------------- siglas

def test_ae_fica_empresa_sindicato():
    entrada = {"outorgantes": "Empresa Metropolitana de Estacionamento da Maia, "
                              "EM - EMEM; Sindicato dos Trabalhadores da "
                              "Administração Pública - SINTAP"}
    assert siglas_outorgantes(entrada)[:2] == (["EMEM", "SINTAP"], 0)


def test_so_partes_de_um_lado_gera_aviso():
    siglas, restantes, avisos = siglas_outorgantes(
        {"outorgantes": "Associação A - AAA; Associação B - BBB; Associação C - CCC"})
    assert (siglas, restantes) == (["AAA", "BBB"], 1)
    assert any("só há partes do lado patronal" in a for a in avisos)


def test_o_lado_sindical_vem_depois_mesmo_fora_de_ordem_no_indice():
    siglas, restantes, _ = siglas_outorgantes(
        {"outorgantes": "Sindicato X - SX; Associação A - AAA; Sindicato Y - SY"})
    assert (siglas, restantes) == (["AAA", "SX"], 1)


# ------------------------------------------------------------- catálogo

def test_o_catalogo_tem_as_colunas_novas():
    linhas = {l["tipo_documento"]: l
              for l in catalogo.linhas(_itens_de(ACRAL_CCT, PE, AA))}
    assert linhas["CCT"]["cod_irct_base"] == "27251"
    assert linhas["PE"]["portaria_dr"] == "452/2025"
    assert linhas["AA"]["portaria_dr"] == ""
    assert linhas["PE"]["ficheiro_destino"] == (
        "1_fontes/irct/portarias_extensao/2026_BTE_31_PE_401_0452-2025_27251_ACRAL-CESP.pdf")


def test_documento_sem_nome_fica_no_catalogo_por_confirmar(tmp_path):
    """Uma portaria sem referência do DR não parte o catálogo: fica sem nome,
    com o motivo, e as colunas da equipa são guardadas pelo ficheiro de origem."""
    pe = dict(PE, titulo="Portaria que estende o contrato coletivo da ACRAL.")
    linhas = catalogo.linhas(_itens_de(ACRAL_CCT, pe))
    portaria = next(l for l in linhas if l["familia"] == "extensao")
    assert portaria["nome_canonico"] == ""
    assert portaria["ficheiro_destino"] == ""
    assert portaria["estado"] == "por_confirmar"
    assert "Diário da República" in portaria["avisos"]

    anterior = tmp_path / "catalogo.csv"
    portaria["observacoes"] = "pedir o número da portaria à DGERT"
    catalogo.escrever(linhas, anterior)
    novas = catalogo.fundir(catalogo.linhas(_itens_de(ACRAL_CCT, pe)), anterior)
    assert next(l for l in novas if l["familia"] == "extensao")["observacoes"] \
        == "pedir o número da portaria à DGERT"
    assert len(novas) == 2, "a linha sem nome não pode aparecer como órfã"


# ------------------------------------------------------ nomeação e escrita

def _registo_com(tmp_path, *linhas_indice):
    """Registo com os documentos do índice de ensaio já «descarregados»."""
    registo = Registo(tmp_path / "registo.jsonl")
    for n, item in enumerate(_itens_de(*linhas_indice, pasta=tmp_path), 1):
        pdf = tmp_path / "interim" / f"{n:08d}.pdf"
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(b"%PDF-1.4\n" + item["id_dgert"].encode())
        item["chave"] = f"2026/31/{n:08d}"
        registo.actualizar(item, descarga={
            "estado": "descarregado", "caminho": str(pdf),
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest()})
    return registo


def test_sem_campo_estrutural_nao_se_escreve_nem_com_aceitar_heuristicas(tmp_path):
    pe = dict(PE, titulo="Portaria que estende o contrato coletivo da ACRAL.")
    aa = dict(AA, altera="")
    registo = _registo_com(tmp_path, ACRAL_CCT, pe, aa)
    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc",
                    aceitar_heuristicas=True)
    assert resumo["por_estado"] == {"nomeado": 1, "por_confirmar": 2}
    escritos = [p.name for p in (tmp_path / "bte").rglob("*.pdf")]
    assert escritos == ["2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf"]
    assert any("Diário da República" in p for p in resumo["problemas"])
    assert any("convenção de base" in p for p in resumo["problemas"])


def test_base_pela_cadeia_fica_por_confirmar_ate_ao_passo_0(tmp_path):
    registo = _registo_com(tmp_path, ACRAL_CCT, PE, AA)
    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc")
    assert resumo["por_estado"] == {"nomeado": 1, "por_confirmar": 2}

    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc",
                    aceitar_heuristicas=True)
    escritos = sorted(p.relative_to(tmp_path / "bte" / "bte_2026").as_posix()
                      for p in (tmp_path / "bte").rglob("*.pdf"))
    assert escritos == [
        "acordos_adesao/2026_BTE_31_AA_402_27251_ALGRET-CESP.pdf",
        "convencoes/PRI/2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf",
        "portarias_extensao/2026_BTE_31_PE_401_0452-2025_27251_ACRAL-CESP.pdf",
    ]


# ---------------------------------------------- migração única do ADR-0016

def _nomeado_no_adr0016(tmp_path):
    """Um registo com a convenção já escrita com o nome do ADR-0016."""
    registo = _registo_com(tmp_path, ACRAL_CCT)
    entrada = next(iter(registo.entradas.values()))
    antigo = (tmp_path / "bte" / "bte_2026" / "convencoes" / "PRI"
              / "2026_PRI_377_CCT_27251_BTE_31_ACRAL-CESP-STRUP+2.pdf")
    antigo.parent.mkdir(parents=True)
    antigo.write_bytes(open(entrada["descarga"]["caminho"], "rb").read())
    entrada["nomeacao"] = {"ordinal": 1, "estado": "nomeado",
                           "doc_id": antigo.stem, "caminho": str(antigo)}
    return registo, entrada, antigo


def test_sem_migrar_um_nome_antigo_e_conflito(tmp_path):
    registo, entrada, antigo = _nomeado_no_adr0016(tmp_path)
    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc")
    assert entrada["nomeacao"]["estado"] == "conflito"
    assert antigo.exists()
    assert any("migração controlada" in p for p in resumo["problemas"])


def test_migrar_escreve_o_novo_apaga_o_antigo_e_regista(tmp_path):
    registo, entrada, antigo = _nomeado_no_adr0016(tmp_path)
    novo = antigo.with_name("2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf")

    simulacao = nomear(registo, tmp_path / "bte", aplicar=False, esquema="rnc",
                       migrar=True)
    assert simulacao["por_estado"] == {"por_migrar": 1}
    assert antigo.exists() and not novo.exists()

    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc",
                    migrar=True)
    assert novo.exists() and not antigo.exists()
    assert entrada["nomeacao"]["migrado_de"] == antigo.stem
    assert resumo["migracoes"] == [{
        "nome_anterior": antigo.stem, "nome_novo": novo.stem,
        "sha256": entrada["descarga"]["sha256"], "id_dgert": "377/2026",
        "chave": entrada["chave"]}]

    # uma segunda corrida já não tem nada a migrar
    segunda = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc",
                     migrar=True)
    assert segunda["por_estado"] == {"ja_existente": 1}
    assert not segunda["migracoes"]


def test_migrar_sem_o_pdf_intermedio_usa_a_copia_ja_nomeada(tmp_path):
    """O PDF da recolha é descartável (ADR-0014); o já nomeado serve de origem."""
    registo, entrada, antigo = _nomeado_no_adr0016(tmp_path)
    import os
    os.remove(entrada["descarga"]["caminho"])
    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc",
                    migrar=True)
    assert resumo["por_estado"] == {"nomeado": 1}
    assert not antigo.exists()
    assert antigo.with_name("2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3.pdf").exists()


def test_a_correspondencia_leva_as_colunas_da_equipa_para_o_nome_novo(tmp_path):
    registo, entrada, antigo = _nomeado_no_adr0016(tmp_path)
    resumo = nomear(registo, tmp_path / "bte", aplicar=True, esquema="rnc",
                    migrar=True)
    tabela = tmp_path / "correspondencia.csv"
    escrever_correspondencia(resumo["migracoes"], tabela)
    escrever_correspondencia([], tabela)          # acrescenta, não substitui
    with open(tabela, encoding="utf-8") as f:
        assert len(list(csv.DictReader(f, delimiter=";"))) == 1

    anterior = tmp_path / "catalogo_antigo.csv"
    velha = {c: "" for c in catalogo.COLUNAS}
    velha.update(nome_canonico=antigo.stem, perita="Dra. X", temas_atribuidos="C9")
    catalogo.escrever([velha], anterior)

    novas = catalogo.fundir(catalogo.linhas(_itens_de(ACRAL_CCT)), anterior,
                            catalogo.carregar_correspondencia(tabela))
    assert len(novas) == 1, "sem órfãs: a linha antiga passou para o nome novo"
    assert novas[0]["nome_canonico"] == "2026_BTE_31_PRI_377_CCT_27251_ACRAL-CESP+3"
    assert (novas[0]["perita"], novas[0]["temas_atribuidos"]) == ("Dra. X", "C9")


def test_migrar_exige_a_tabela_de_correspondencia(tmp_path):
    from cct.nomeacao import main

    registo = _registo_com(tmp_path, ACRAL_CCT)
    registo.guardar()
    with pytest.raises(SystemExit):
        main(["--registo", str(registo.caminho), "--destino", str(tmp_path / "bte"),
              "--migrar"])


# ------------------------------- chave das linhas sem nome (revisão do PR #87)

def _sem_nome(**campos):
    linha = {c: "" for c in catalogo.COLUNAS}
    linha.update({"familia": "extensao", "tipo_documento": "PE",
                  "estado": "por_confirmar", "ficheiro_origem": "00010004.pdf",
                  **campos})
    return linha


def test_linhas_sem_nome_com_a_mesma_origem_em_boletins_diferentes(tmp_path):
    """`00010004.pdf` repete-se entre boletins: a chave não pode ser só a origem."""
    anterior = tmp_path / "catalogo.csv"
    catalogo.escrever([
        _sem_nome(ano="2026", bte_numero="31", seq_anual="401", perita="Dra. A"),
        _sem_nome(ano="2026", bte_numero="33", seq_anual="415", perita="Dra. B"),
    ], anterior)
    novas = catalogo.fundir([
        _sem_nome(ano=2026, bte_numero=33, seq_anual=415),
        _sem_nome(ano=2026, bte_numero=31, seq_anual=401),
    ], anterior)
    assert [(l["bte_numero"], l["perita"]) for l in novas] == [
        (33, "Dra. B"), (31, "Dra. A")]


def test_sem_identificador_a_chave_usa_ano_boletim_e_origem(tmp_path):
    anterior = tmp_path / "catalogo.csv"
    catalogo.escrever([
        _sem_nome(ano="2026", bte_numero="31", perita="Dra. A"),
        _sem_nome(ano="2026", bte_numero="33", perita="Dra. B"),
    ], anterior)
    novas = catalogo.fundir([_sem_nome(ano=2026, bte_numero=31),
                             _sem_nome(ano=2026, bte_numero=33)], anterior)
    assert [l["perita"] for l in novas] == ["Dra. A", "Dra. B"]


def test_chave_ambigua_nao_repoe_nem_perde_o_trabalho_da_equipa(tmp_path):
    """Duas linhas antigas com a mesma chave: nenhuma é escolhida às cegas, e as
    duas ficam no catálogo, assinaladas, para uma pessoa decidir."""
    anterior = tmp_path / "catalogo.csv"
    catalogo.escrever([
        _sem_nome(ano="2026", bte_numero="31", ficheiro_origem="", perita="Dra. A"),
        _sem_nome(ano="2026", bte_numero="31", ficheiro_origem="", perita="Dra. B"),
    ], anterior)
    novas = catalogo.fundir([_sem_nome(ano=2026, bte_numero=31, ficheiro_origem="")],
                            anterior)
    assert novas[0]["perita"] == ""
    assert "chave repetida" in novas[0]["avisos"]
    assert sorted(l["perita"] for l in novas[1:]) == ["Dra. A", "Dra. B"]
    assert all("chave repetida" in l["avisos"] for l in novas[1:])
