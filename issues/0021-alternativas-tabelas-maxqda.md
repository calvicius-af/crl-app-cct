# ISSUE-0021: alternativas para tabelas melhor formatadas no MAXQDA

- **Estado:** Aberta
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/qdpx.py` (exportação), `scripts/prova_richtext_qdpx.py`

## O que acontece

As tabelas chegam ao MAXQDA como texto plano com células separadas por ` | ` e isoladas
por linhas em branco. É legível e pesquisável (validado no gate F1b e na importação de
2026-09-17), mas não é uma tabela: não tem grelha, colunas alinhadas nem formatação.

A via `richTextPath` (DOCX embebido) foi testada e **falhou** — o MAXQDA ignorou o
`richTextPath` e mostrou o `plainTextPath` em duas rodadas independentes (ver
ISSUE-0003). Mas o MAXQDA importa ficheiros Word, o que sugere que exista outra via.

## O que devia acontecer

Uma avaliação das alternativas, com prova mínima para cada uma, antes de investir:

1. **`PDFSource` com o PDF original** — o MAXQDA mostra o layout perfeito; as seleções
   passam a retângulos por página (`PDFSelection`). O docling fornece as bbox de cada
   item, mas obrigaria a repensar o harness e as anotações, hoje todos por offsets de
   caracteres. **Prova**: um QDPX de 1 documento com `PDFSource` e uma codificação,
   importar e ver se a âncora cai no sítio.
2. **DOCX como fonte separada** (não `richTextPath`, mas um `TextSource` cujo conteúdo
   é DOCX) — verificar se o REFI-QDA o permite e se o MAXQDA o lê.
3. **Importação manual do DOCX no MAXQDA** (fora do QDPX): gerar um DOCX por convenção
   com tabelas verdadeiras e importá-lo à parte, mantendo o QDPX para as codificações.
   Perde-se a ligação automática, mas pode ser aceitável se as tabelas forem o que
   importa.
4. **Tabelas como imagens** (`PictureSource`?) — o MAXQDA suporta imagens; uma tabela
   renderizada como imagem preserva o layout mas perde a pesquisa.
5. **Melhorar o formato pipe** — alinhar colunas com espaços, usar `|` nas bordas
   (`| a | b |`), ou separadores visuais. Não é uma tabela, mas melhora a leitura.

## Como reproduzir

```bash
.venv/bin/python scripts/prova_richtext_qdpx.py   # a prova que falhou
# e, para cada alternativa, uma prova mínima análoga
```

## Notas

- A norma REFI-QDA 1.5 (XSD em `vendor/refi-qda/`) é a fonte para saber o que é
  permitido: `TextSource` aceita `plainTextPath` e `richTextPath`; há `PDFSource` e
  `PictureSource`. Verificar o XSD antes de desenhar.
- O resultado da prova richtext (falhou) está registado na ISSUE-0003 — não repetir.
- Esta issue é de **investigação**, não de implementação: o produto é uma decisão
  fundamentada sobre qual via seguir, com prova. Só depois se abre a implementação.
- Prioridade: média. O formato atual é funcional; isto é qualidade de apresentação.
