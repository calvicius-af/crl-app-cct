# ISSUE-0024: tabelas salariais colapsadas no TXT do BTE 31/2026

- **Estado:** Resolvida — 2026-09-26
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

**Atualização de 25-09-2026 (corrida de 2025):** as «linhas longas» que restavam não eram
tabelas colapsadas: 177 eram linhas certas de tabelas com o conteúdo funcional numa
célula (CARRIS, RTP, LAGOS em Forma) ou cabeçalhos de grelhas largas. A medida passa a
não as contar quando a linha tem as mesmas células que a vizinha ou é longa só por uma
célula de texto (358 → 10 nos 277 PDF). Os defeitos reais eram três, todos corrigidos com
regra geral: letras que tocavam na fronteira entre zonas entravam nas duas, e a linha
saía entrelaçada (INOVA, «1.080400,,0000 €€»); tabelas dentro de outras liam-se duas
vezes (EPAL, 695 palavras a mais); camadas de texto recortadas ou fora da página
misturavam-se com o visível (MaiaAmbiente, GESAMB). Registo:
[avisos-2025-2026-09-25.md](../docs/validacao/avisos-2025-2026-09-25.md).

**Confirmação de 26-09-2026:** as grelhas largas do 384/385 saem inteiras, com as cinco
colunas (o corte em duas colunas das pp. 4–5 já não acontece). Os offsets do QDPX passam a
ser verificados no próprio QDPX, relido do zip como o MaxQDA o lê, com uma seleção por nó,
antes, dentro e depois das tabelas (`cct.qdpx.verificar_offsets`): 0 falhas nos 14 PDF do
corpus (1776 nós) e nos 277 de 2025 (84 844 nós). A métrica `offsets_qdpx` entra no corpus
de regressão, e o CI falha se uma seleção deixar de bater.
