# Docling Resources

Fontes de confiança para esta oficina. Tudo o que é afirmado nas lições sai daqui, não do
conhecimento paramétrico do modelo. A versão de referência é **Docling 2.121.0** /
**docling-core 2.92.0** (commit `06faa09`, 20-08-2026).

## Knowledge

- [Repositório `docling-project/docling`](https://github.com/docling-project/docling)
  A fonte primária. Projeto da IBM Research Zurique, hoje alojado na LF AI & Data
  Foundation, licença MIT. **Usar para:** confirmar o comportamento real de qualquer opção
  — a documentação publicada atrasa-se em relação ao código.
- [Documentação oficial — Concepts › Docling Document](https://docling-project.github.io/docling/concepts/docling_document/)
  Define o `DoclingDocument`: `texts`, `tables`, `pictures`, a árvore `body`, a
  `furniture` (cabeçalhos e rodapés de página) e a ordem de leitura.
  **Usar para:** perceber o modelo de dados antes de escrever código que o percorre.
- [Documentação oficial — Usage › Advanced options](https://docling-project.github.io/docling/usage/advanced_options/)
  Pré-fetch de modelos, `artifacts_path`, `enable_remote_services`, modos do TableFormer,
  limites de tamanho. **Usar para:** tudo o que toque a instalação offline do CRL.
- [Skill de agente que o Docling traz no próprio pacote](https://docling-project.github.io/docling/usage/agent_skills/)
  Depois de instalado, `docling/.agents/skills/docling/` traz `SKILL.md` e
  `references/{cli,python-sdk,extraction,rag,service-client,slim-packaging}.md`, escritos
  pela equipa do projeto. **Usar para:** a referência mais densa e mais actual da API;
  instala-se com `uvx library-skills --claude`.
- [Docling Technical Report (arXiv 2408.09869)](https://arxiv.org/abs/2408.09869)
  O artigo que descreve a arquitetura e os modelos de layout e de tabelas.
  **Usar para:** perceber *porque* é que a segmentação funciona, e onde falha.
- [`docling convert --help`](https://docling-project.github.io/docling/reference/cli/)
  **Usar para:** a lista de flags da versão que está mesmo instalada. Já se confirmou
  nesta sessão que a documentação e a skill do pacote descrevem `--force-ocr`, que a
  2.121.0 marca como *deprecated* a favor de `--ocr-mode full_page`.
- [`docling-project/docling-core`](https://github.com/docling-project/docling-core)
  Os tipos Pydantic (`DocItemLabel`, `ProvenanceItem`, `TableItem`).
  **Usar para:** saber que campos existem mesmo num item, em vez de adivinhar.
- [`krrome/docling-hierarchical-pdf`](https://github.com/krrome/docling-hierarchical-pdf)
  Pós-processador de terceiros (MIT) que reordena a árvore do `DoclingDocument`, aninhando
  o corpo dentro do cabeçalho a que pertence — coisa que o Docling explicitamente não faz.
  **Usar para:** o motor de reestruturação. Os seus *parsers* de numeração não reconhecem
  cabeçalhos portugueses; ver a
  [avaliação completa, com medições](avaliacao-docling-hierarchical-pdf.md).

## Wisdom (Communities)

- [Discussões do repositório Docling](https://github.com/docling-project/docling/discussions)
  Onde a equipa responde. **Usar para:** confirmar se um comportamento estranho num PDF é
  bug conhecido antes de contornar com heurística.
- [Issues com o rótulo de layout/tabelas](https://github.com/docling-project/docling/issues)
  **Usar para:** procurar casos parecidos com os PDFs do BTE (duas colunas, tabelas
  salariais compridas) antes de abrir um relato novo.

## Gaps

- **Nenhuma fonte trata PDFs jurídicos portugueses.** O corpus do BTE — duas colunas,
  `Cláusula 1.ª` centrada em linha própria, tabelas salariais que atravessam páginas — não
  está representado em nenhum *benchmark* do Docling. Aqui a evidência tem de ser
  produzida localmente: o AppCCT já tem uma amostra de referência humana em `docs/validacao/`, e é essa a
  única medida que conta.
- Não há material publicado a comparar `pdfplumber` com Docling em documentos de duas
  colunas. A comparação da lição 04 é original.
