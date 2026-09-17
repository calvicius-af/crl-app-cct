# `0_gestao/`

## O que vive aqui

As decisões e as listas que governam o resto do ciclo: o roteiro do relatório, o livro de códigos, o catálogo, os vocabulários controlados, as atas e os procedimentos.

## O que não vive aqui

Documentos que entram de fora, mesmo que sejam de referência, ficam em `1_fontes/externas/`. As saídas da aplicação ficam em `2_processamento/`. As versões superadas de qualquer destes ficheiros vão para `9_arquivo/`.

## Como se chamam os ficheiros

O catálogo é `catalogo_irct_AAAA.csv`, por exemplo `catalogo_irct_2026.csv`.

Os vocabulários têm nome descritivo em minúsculas e sem data: `siglas_organizacoes.csv`, `siglas_ambiguas.csv`, `actos_negociacao.csv`, `entidades_administracao_publica.csv`, `empregadores_ambito.csv`, `tipos_documento.csv`, `estados.csv` e `temas.csv`. A versão ativa é a que está aqui; as anteriores estão em `9_arquivo/` com data no nome.

As atas seguem `AAAAMMDD_assunto.md`, por exemplo `20260916_decisao_sectores.md`.

## Quem escreve e quem lê

Escrevem a coordenação, no roteiro, nas atas e nos procedimentos, e quem resolve avisos, nos vocabulários. O catálogo é escrito pela aplicação e anotado pelos técnicos nas cinco colunas da equipa.

Lê toda a gente, e lê a aplicação: as bandeiras `--siglas`, `--ambitos` e `--codebook` apontam para aqui.

## Quando sai daqui

Não sai, porque é a camada de governo do ciclo. O que sai são as versões anteriores: sempre que um destes ficheiros é substituído, a versão antiga vai para `9_arquivo/0_gestao/` com data no nome.

A regra de uma versão ativa por documento é mais importante aqui do que em qualquer outra pasta, porque duas versões de um vocabulário em uso produzem duas nomeações diferentes para o mesmo documento.
