"""Percorre uma convenção convertida pelo Docling e lista a estrutura — sem regex.

Exercício da lição 02 da oficina `docs/formacao/aprender-docling/`.

Correr com o interpretador do ambiente virtual do Docling, não com o do AppCCT:

    .venv-docling/bin/python listar_clausulas.py 25_PR_003_BTE_02_ACIP_FESAHT.pdf

Verificado contra docling 2.121.0 / docling-core 2.92.0 por introspeção da API.
Não foi corrido ponta a ponta — ver NOTES.md, secção "Verificação do material".
"""
import sys
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DocItemLabel


def converter(caminho: Path):
    """Converte um PDF do BTE com o pipeline standard, sem OCR."""
    opcoes = PdfPipelineOptions(
        do_ocr=False,            # os PDFs do BTE são de origem digital
        do_table_structure=True,  # queremos as tabelas salariais reconhecidas
    )
    conversor = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opcoes)}
    )
    resultado = conversor.convert(caminho)
    if resultado.status not in (ConversionStatus.SUCCESS,
                               ConversionStatus.PARTIAL_SUCCESS):
        raise SystemExit(f"conversão falhou: {resultado.status} — {resultado.errors}")
    if resultado.status is ConversionStatus.PARTIAL_SUCCESS:
        print(f"[aviso] conversão parcial: {resultado.errors}", file=sys.stderr)
    return resultado


def listar_estrutura(doc) -> None:
    """Imprime cabeçalhos e tabelas na ordem de leitura, com a página de origem."""
    for item, nivel in doc.iterate_items():
        rotulo = getattr(item, "label", None)
        pagina = item.prov[0].page_no if getattr(item, "prov", None) else "?"

        if rotulo is DocItemLabel.SECTION_HEADER:
            print(f"p.{pagina:>3}  {'  ' * nivel}§ {item.text}")
        elif rotulo is DocItemLabel.TITLE:
            print(f"p.{pagina:>3}  ## {item.text}")
        elif rotulo is DocItemLabel.TABLE:
            linhas = item.data.num_rows if item.data else 0
            print(f"p.{pagina:>3}  {'  ' * nivel}[tabela: {linhas} linhas]")


def contar_rotulos(doc) -> None:
    """Quantos itens de cada tipo? É o retrato do que o modelo de layout viu."""
    from collections import Counter

    contagem = Counter(
        item.label.value
        for item, _ in doc.iterate_items()
        if getattr(item, "label", None) is not None
    )
    print("\n--- rótulos atribuídos pelo modelo de layout ---")
    for nome, n in contagem.most_common():
        print(f"{n:>5}  {nome}")


def exportar_tabelas(doc, destino: Path) -> None:
    """Grava cada tabela em CSV. As tabelas salariais dos anexos são o alvo."""
    destino.mkdir(parents=True, exist_ok=True)
    for i, tabela in enumerate(doc.tables):
        pagina = tabela.prov[0].page_no if tabela.prov else "sp"
        df = tabela.export_to_dataframe(doc=doc)
        ficheiro = destino / f"tabela_{i:02d}_p{pagina}.csv"
        df.to_csv(ficheiro, index=False)
        print(f"gravada {ficheiro}  ({df.shape[0]}x{df.shape[1]})")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    pdf = Path(sys.argv[1])
    resultado = converter(pdf)
    doc = resultado.document

    print(f"{pdf.name}: {len(doc.pages)} páginas, "
          f"{len(doc.texts)} itens de texto, {len(doc.tables)} tabelas\n")
    listar_estrutura(doc)
    contar_rotulos(doc)
    exportar_tabelas(doc, Path("saida-docling/tabelas"))


if __name__ == "__main__":
    main()
