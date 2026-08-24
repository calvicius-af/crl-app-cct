# ISSUE-0003: o QDPX perde os ganhos de legibilidade do extrator docling

- **Estado:** Aberta
- **Data:** 2026-08-24
- **Onde dói:** `cct/extractor_docling.py`, `cct/extractor.py` (estruturar), `cct/qdpx.py`

## O que acontece

Na importação para MaxQDA do QDPX gerado com `--extrator docling`
(`results/2025_4_08_docling_teste/projeto.qdpx`, verificação do utilizador
de 2026-08-24), as melhorias vistas no Markdown do docling não chegam ao
texto final:

1. **`########` sobreviventes** — nos perfis de função do TRATOLIXO
   aparecem linhas como `######## Missão/finalidade da função …`. A
   limpeza usa `^#{1,6}\s+`, mas o pós-processador hierárquico pode
   produzir níveis >6; com 7+ cardinais a regex não casa e os `#` ficam.
2. **Células de colspan duplicadas** — as tabelas de perfil de função
   saem com repetições (`Competência | Competência | Competência`,
   `Nível 3 | Nível 3 | Nível 3`): o `export_to_markdown` do docling
   repete o conteúdo de células fundidas por cada coluna abrangida.
3. **Sem respiração vertical** — a linha em branco antes de cada
   cláusula/artigo e à volta das tabelas (bem visível no Markdown) não
   existe no TXT do QDPX: o `estruturar` descarta todas as linhas vazias
   ao construir o texto final, e o QDPX herda esse texto denso.

## O que devia acontecer

O TXT dentro do QDPX devia refletir a legibilidade do Markdown: sem
artefactos `#`, tabelas sem células repetidas e uma linha em branco a
separar cláusulas/artigos e tabelas do texto corrido.

## Como reproduzir

```bash
.venv/bin/python -m cct.pipeline_tema \
    --pdfs <pasta com 25_PR_247_BTE_40_TRATOLIXO_STAL.pdf> \
    --codebook codebooks/4_08_protecao_dados.yaml \
    --extrator docling --out results/teste_docling
# importar projeto.qdpx no MaxQDA e abrir o TRATOLIXO nos perfis de função
```

## Notas

Proposta de resolução, por ponto:

1. Trocar `RE_HEADING_MD` para `^#+\s+` (qualquer profundidade) em
   `extractor_docling.py`. Correção de uma linha + teste.
2. Em `_celulas`/`markdown_para_texto`, colapsar células consecutivas
   idênticas numa linha de tabela (`a | a | a | b` → `a | b`). O risco de
   perder repetições legítimas em tabelas salariais é baixo (valores
   iguais lado a lado são raros e o colapso só se aplica a texto igual
   carácter a carácter), mas validar com o Anexo I do LAGOSemFORMA e a
   tabela do AguasNorte.
3. A quebra vertical não pode entrar no `estruturar` sem partir a
   propriedade zero-perda e os offsets dos nós (char_start/char_end são
   usados pelo harness e pelas anotações). Duas vias possíveis:
   a) **na exportação** (`qdpx.py`): inserir `\n` extra antes de cada
      `char_start` de nó clausula/artigo/capitulo/anexo ao escrever o
      TXT, recalculando os offsets das anotações no mesmo passo — é
      onde a legibilidade importa e mantém o modelo interno intacto;
   b) **no estruturar**: emitir a linha em branco como parte do texto
      canónico — mais simples, mas mexe em todos os offsets, gabaritos
      e comparações existentes; exigiria revalidar o harness completo.
   A via (a) é a recomendada.

Relacionada com a limitação já conhecida das tabelas partidas na mudança
de página (merge por continuação sem cabeçalho, AguasNorte G-M).
