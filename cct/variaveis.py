"""Leitor das variáveis de documento exportadas do MaxQDA (2025).

Dá ao pipeline os metadados que a extração não consegue inferir do texto:
tipo/subtipo de convenção, CAE, entidades outorgantes, âmbito, etc.
Atenção: o export do MaxQDA trunca "Nome do documento" a ~30 caracteres,
pelo que o cruzamento com doc_ids completos é feito por prefixo.
"""
import unicodedata
from pathlib import Path


def _norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", str(s))
                if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def subtipo_pipeline(subtipo_reg: str, subtipo_conv: str) -> str:
    """Mapeia as variáveis do CRL para o enum do pipeline (routing art. 494.º/2 CT)."""
    reg = _norm(subtipo_reg or "")
    conv = _norm(subtipo_conv or "")
    if "1" in reg and "conven" in reg:
        return "primeira_convencao"
    if "global" in reg:
        return "revisao_global"
    if "parcial" in reg:
        if "texto consolidado" in conv:
            return "revisao_parcial_com_consolidado"
        return "revisao_parcial"
    if "texto consolidado" in conv:
        return "texto_consolidado"
    return "desconhecido"


def carregar_variaveis(xlsx_path: Path) -> list[dict]:
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    ws = wb.active
    linhas = ws.iter_rows(values_only=True)
    cab = [str(c).strip() if c is not None else "" for c in next(linhas)]
    idx = {nome: i for i, nome in enumerate(cab)}

    def col(row, nome, default=""):
        i = idx.get(nome)
        v = row[i] if i is not None else None
        return str(v).strip() if v is not None else default

    registos = []
    for row in linhas:
        nome = col(row, "Nome do documento")
        if not nome:
            continue
        registos.append({
            "nome_maxqda": nome,
            "num_bte": col(row, "Num_BTE"),
            "data_pub": col(row, "Data_pub"),
            "tipo_conv": col(row, "Tipo_conv"),
            "subtipo_conv": col(row, "SubTipo_conv"),
            "subtipo_reg": col(row, "SubTipo_conv_Reg"),
            "subtipo": subtipo_pipeline(col(row, "SubTipo_conv_Reg"),
                                        col(row, "SubTipo_conv")),
            "cae": col(row, "EtiquetaCAE_rev4"),
            "entidade_patronal": col(row, "Entidade_patronal_1"),
            "entidade_sindical": col(row, "Entidade_sindical_1"),
            "num_trabalhadores": col(row, "Num_trab_abrangidos"),
            "ambito_geografico": col(row, "Amb_Geografico"),
            "setor_publico_empresarial": col(row, "SetorPublicoEmpresarial"),
        })
    return registos


def procurar(variaveis: list[dict], doc_id: str) -> dict | None:
    """Cruza um doc_id completo com o nome truncado do MaxQDA (por prefixo)."""
    alvo = _norm(doc_id.removesuffix("_TXT"))
    melhor = None
    melhor_len = 0
    for v in variaveis:
        nome = _norm(v["nome_maxqda"].removesuffix("_txt"))
        pref = min(len(nome), len(alvo))
        if nome[:pref] == alvo[:pref] and pref > melhor_len:
            melhor, melhor_len = v, pref
    # exige um prefixo suficientemente longo para não cruzar documentos errados
    return melhor if melhor_len >= 20 else None
