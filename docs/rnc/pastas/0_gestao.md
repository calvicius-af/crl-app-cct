# `0_gestao/` — o que governa o ciclo

## O que vive aqui
As decisões e as listas que mandam no resto: o roteiro do relatório, o livro de
códigos, o catálogo, os vocabulários controlados, as atas e os procedimentos.

## O que não vive aqui
Documentos que entram de fora, mesmo que sejam de referência → `1_fontes/externas/`.
Saídas da aplicação → `2_processamento/`. Versões superadas de qualquer destes
ficheiros → `9_arquivo/`.

## Como se chamam os ficheiros
Cada subpasta tem o seu padrão. O catálogo é `catalogo_irct_AAAA.csv`
(`catalogo_irct_2026.csv`). Os vocabulários têm nome descritivo em minúsculas,
sem data: `siglas_organizacoes.csv`, `empregadores_ambito.csv`, `temas.csv`,
`tipos_documento.csv`, `estados.csv`. As atas são `AAAAMMDD_assunto.md`
(`20260916_decisao_sectores.md`). Nenhum vocabulário leva data no nome: a versão
ativa é a que está aqui, as anteriores estão em `9_arquivo/`.

## Quem escreve e quem lê
Escrevem a coordenação (roteiro, atas, procedimentos) e quem resolve avisos
(vocabulários). O catálogo é escrito pela aplicação e anotado pelos técnicos nas
cinco colunas da equipa. Lê toda a gente, e lê a aplicação: `--siglas`,
`--ambitos` e `--codebook` apontam para aqui.

## Quando sai daqui
Não sai — é a camada de governo do ciclo. O que sai são as *versões anteriores*:
sempre que um destes ficheiros é substituído, a versão antiga vai para
`9_arquivo/0_gestao/` com data no nome. A regra é «uma versão ativa por
documento», e é aqui que ela é mais importante: duas versões de um vocabulário a
conviver produzem duas nomeações diferentes para o mesmo documento.
