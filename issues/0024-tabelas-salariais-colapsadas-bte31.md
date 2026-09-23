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
como auditor, e ausência de blocos de duas linhas no TXT.

**Atualização de 23-09-2026:** a equipa forneceu os nove PDFs PRI e o
manifesto, com hashes concordantes. O comando selecionou `pdfplumber`.
A causa da junção de linhas está em `_remover_cabecalhos_rodapes`:
apagava `\x02TABELA` e `\x03TABELA` por aparecerem em várias páginas.
Protegido todo o bloco, incluindo cabeçalhos/células repetidos, a execução
local recupera 13 linhas tabulares no
380, 64 em cada 384/385 e 58 no 386. Ainda é necessário conferir as
células no PDF, especialmente as tabelas largas divididas pela heurística
de duas colunas em 384/385. A correção não fecha esta issue sozinha.

Comparar as páginas originais com ambos os extratores antes de escolher
uma correção; validar grelha, categoria/valor e offsets no QDPX e depois
importar a amostra no MaxQDA. Critérios em
[intervenção BTE 31/2026](../docs/validacao/intervencao-extracao-bte31-2026-09-23.md).
