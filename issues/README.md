# Issues

Problemas conhecidos e trabalho pequeno por fazer, em Markdown, dentro do repositório.

## Porque existe esta pasta

O **GitHub Issues é a fonte de verdade** para discussão, atribuição e estado. Esta pasta
é o espelho legível de dentro do repositório: quem clona o código — ou um agente que só
vê ficheiros — encontra aqui o que está partido e o que falta, sem precisar de acesso à
plataforma.

Não substitui o GitHub. Complementa-o.

## Como usar

1. Copiar `0000-template.md` para `NNNN-titulo-curto.md`.
2. Se houver issue correspondente no GitHub, referir o número (`#42`) no cabeçalho, e
   vice-versa.
3. Quando ficar resolvido, marcar `Estado: Resolvido` com a data e o que foi feito —
   não apagar. O histórico de problemas é informação útil sobre o sistema.

Issue *versus* [spec](../specs/README.md): se para resolver é preciso desenhar
comportamento novo, é spec. Se é corrigir, ajustar ou completar algo que já existe,
é issue.

## Índice

| # | Título | Estado |
|---|---|---|
| [0001](0001-numeracao-por-extenso.md) | Normalizar cláusulas com numeração por extenso | Em curso |
| [0002](0002-quebras-de-linha-em-titulos-multilinha.md) | Quebras de linha nos blocos de título do início dos documentos | Aberta |
| [0003](0003-qdpx-perde-ganhos-do-docling.md) | O QDPX perde os ganhos de legibilidade do extrator Docling | Em curso |
| [0004](0004-revisao-pr-23.md) | Correções exigidas pela revisão do PR #23 | Resolvida |
| [0005](0005-programa-qualidade-tecnica.md) | Programa de qualidade técnica pós-PR #23 | Aberta |
| [0006](0006-colunas-cortam-cabecalhos-centrados.md) | O corte em duas colunas parte cabeçalhos centrados (pdfplumber) | Aberta |
| [0007](0007-unicode-cp1252-app-grafica.md) | UnicodeEncodeError na app gráfica em estações Windows com cp1252 | Resolvida |
| [0008](0008-clausula-previa-nao-reconhecida.md) | O extrator não reconhece "Cláusula prévia" como cabeçalho | Resolvida |
| [0009](0009-instalacao-offline-falha-em-caminho-unc.md) | A instalação offline falha quando o projeto está num caminho de rede | Aberta |
| [0010](0010-python-do-projeto-em-windows.md) | Em Windows, não é claro qual o Python do projeto, e o doctor não ajuda | Aberta |
| [0011](0011-siglas-inexistente-da-traceback.md) | `--siglas` com ficheiro inexistente dá traceback em vez de mensagem | Aberta |
| [0012](0012-ci-nao-cobre-windows-nem-python-313.md) | O CI não corre em Windows nem em Python 3.13 | Aberta |
| [0013](0013-proveniencia-sem-git-na-estacao.md) | A proveniência perde o commit quando não há git na estação | Aberta |
| [0014](0014-carristur-sem-clausulas-nem-nota-de-deposito.md) | Quatro documentos CARRISTUR produzem zero cláusulas | Aberta |
