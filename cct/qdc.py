"""Leitor do codebook master do MaxQDA (.qdc, REFI-QDA codebook).

Fonte de compatibilidade entre outputs: GUIDs, nomes de exibição, cores e
descrições dos códigos usados no projeto master de 2025. Os códigos do
pipeline cruzam-se com o master pelo id numérico inicial do nome
("4.08.1 Direitos de Personalidade" → id "4.08.1") ou pelo nome exato.
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS_QDC = "urn:QDA-XML:codebook:0:4"
RE_ID_NUM = re.compile(r"^(\d+(?:\.\d+)*)\s")


def _limpar_guid(guid: str) -> str:
    return guid.strip("{}").lower()


def carregar_qdc(qdc_path: Path) -> dict[str, dict]:
    """Devolve {chave: {guid, nome, descricao, cor}}.

    Cada código do master fica acessível por duas chaves: o id numérico
    inicial (se existir, normalizado sem zeros à esquerda ambíguos) e o
    nome completo.
    """
    raiz = ET.parse(qdc_path).getroot()
    registos: dict[str, dict] = {}

    def visitar(el):
        for code in el.findall(f"{{{NS_QDC}}}Code"):
            nome = code.get("name", "")
            desc_el = code.find(f"{{{NS_QDC}}}Description")
            reg = {
                "guid": _limpar_guid(code.get("guid", "")),
                "nome": nome,
                "descricao": (desc_el.text or "").strip() if desc_el is not None else "",
                "cor": code.get("color", ""),
            }
            registos.setdefault(nome, reg)
            # "00 Estrutura" também acessível como "Estrutura"
            m_pref = re.match(r"^\d+\s+(.+)$", nome)
            if m_pref:
                registos.setdefault(m_pref.group(1), reg)
            m = RE_ID_NUM.match(nome)
            if m:
                registos.setdefault(m.group(1), reg)
                # "4.3.01" e "4.03.1" são grafias alternativas do mesmo id
                alt = ".".join(str(int(p)) if p.isdigit() else p
                               for p in m.group(1).split("."))
                registos.setdefault(alt, reg)
            visitar(code)

    codes = raiz.find(f"{{{NS_QDC}}}Codes")
    if codes is not None:
        visitar(codes)
    return registos


def procurar_codigo(registos: dict[str, dict], segmento: str) -> dict | None:
    """Procura um segmento de caminho do pipeline no master.

    Tenta: nome exato → id numérico exato → id com zeros normalizados.
    """
    if segmento in registos:
        return registos[segmento]
    if re.fullmatch(r"\d+(?:\.\d+)*", segmento):
        alt = ".".join(str(int(p)) for p in segmento.split("."))
        if alt in registos:
            return registos[alt]
    return None
