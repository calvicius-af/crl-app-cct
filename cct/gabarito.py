"""Leitor do gabarito MaxQDA (XLSX de segmentos codificados manualmente).

Colunas esperadas: Código, Segmento, Nome do documento, Tipo_conv,
SubTipo_conv, … O código vem como caminho hierárquico
"4.08 … > 4.08.5 … > 4.08.5.1 Nome"; normaliza-se para o id numérico
do nível mais específico ("4.08.5.1").
"""
import re
from pathlib import Path

RE_ID = re.compile(r"^(\d+(?:\.\d+)*)")


def normalizar_codigo(bruto: str) -> str:
    folha = bruto.split(">")[-1].strip()
    m = RE_ID.match(folha)
    return m.group(1) if m else folha


def carregar_gabarito(xlsx_path: Path) -> list[dict]:
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    ws = wb.active
    linhas = ws.iter_rows(values_only=True)
    cabecalho = [str(c).strip() if c else "" for c in next(linhas)]
    idx = {nome: i for i, nome in enumerate(cabecalho)}

    registos = []
    for row in linhas:
        codigo = row[idx["Código"]]
        segmento = row[idx["Segmento"]]
        doc = row[idx["Nome do documento"]]
        if not (codigo and segmento and doc):
            continue
        registos.append({
            "doc_id": str(doc).strip(),
            "codigo": normalizar_codigo(str(codigo)),
            "segmento": str(segmento).strip(),
            "tipo": str(row[idx.get("Tipo_conv", 3)] or "").strip(),
            "subtipo": str(row[idx.get("SubTipo_conv", 4)] or "").strip(),
        })
    return registos
