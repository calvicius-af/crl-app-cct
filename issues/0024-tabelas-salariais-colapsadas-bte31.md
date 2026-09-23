# ISSUE-0024: tabelas salariais colapsadas no TXT do BTE 31/2026

- **Estado:** Aberta
- **Data:** 2026-09-23
- **GitHub:** [#84](https://github.com/calvicius-af/crl-app-cct/issues/84)
- **Onde dói:** `cct/extractor.py`, `cct/extractor_docling.py`, `cct/auditoria.py`

No QDPX de nove documentos, a tabela do 380 tem uma linha de 1371
caracteres; os anexos III e IV do 386 têm linhas de 933 e 1187; 384 e
385 apresentam linhas isoladas de células, incluindo uma de 3781
caracteres. Existem valores no TXT, mas a relação linha/coluna não está
demonstrada. O relatório indica grelhas detetadas por `pdfplumber`, usado
como auditor, e ausência de blocos de duas linhas no TXT. Os PDFs e o
comando/manifesto não foram fornecidos nesta ronda.

Comparar as páginas originais com ambos os extratores antes de escolher
uma correção; validar grelha, categoria/valor e offsets no QDPX e depois
importar a amostra no MaxQDA. Critérios em
[intervenção BTE 31/2026](../docs/validacao/intervencao-extracao-bte31-2026-09-23.md).
