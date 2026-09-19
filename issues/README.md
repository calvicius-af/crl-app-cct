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
| [0015](0015-assinaturas-sem-quebra-nomes-deslocados.md) | O bloco de assinaturas sai sem quebra, com nomes deslocados e sem destaque | Em curso |
| [0016](0016-marcadores-paragrafo-alinea-perdidos.md) | Marcadores de parágrafo e alínea perdidos ou trocados por hífens | Resolvida |
| [0017](0017-titulo-clausula-68-nao-apanhado.md) | O título da Cláusula 68.ª não é apanhado | Aberta |
| [0018](0018-titulo-anexo-depois-da-tabela.md) | O título do último anexo sai depois dos dados da tabela | Aberta |
| [0019](0019-residuo-be-do-cabecalho.md) | Resíduo "BE" do cabeçalho do BTE no corpo do texto | Resolvida |
| [0020](0020-tabelas-carristur-rodadas.md) | As tabelas dos CARRISTUR estão rodadas 90º e saem invertidas | Aberta |
| [0021](0021-alternativas-tabelas-maxqda.md) | Alternativas para tabelas melhor formatadas no MAXQDA | Aberta |
| [0022](0022-nomes-nao-seguem-esquema-rnc.md) | Os nomes dos ficheiros não seguem o esquema definido em docs/rnc/README.md | Resolvida |

## Ronda de 2026-09-18: qualidade da extração (linting e renomeação)

Oito issues (0015-0022) levantadas na revisão dos 14 documentos do BTE 31/2026, depois
da importação para MAXQDA. Nenhuma impede a leitura qualitativa; todas reduzem a
credibilidade da extração, que é o que se quer demonstrar. Foram escritas para poderem
ser executadas **independentemente por modelos diferentes** — cada uma tem o documento
concreto, o excerto errado, o módulo afetado e a hipótese de causa.

### Como pegar numa destas issues

1. Ler a issue inteira — o excerto do "O que acontece" é a evidência, não uma paráfrase.
2. Reproduzir com o comando da secção "Como reproduzir" (usa `--extrator docling` e o
   codebook `codebooks/demo_fase0.yaml`, que não faz pré-codificação).
3. Confirmar a hipótese da secção "Notas" **antes** de corrigir — várias apontam duas
   causas possíveis e a correção difere.
4. Corrigir com teste que falha primeiro (o repo usa `pytest`; ver `tests/`).
5. Não alterar nomes de ficheiros já atribuídos (ver ISSUE-0022 e `docs/rnc/README.md` §7).

### Agrupamento por causa raiz

| Grupo | Issues | Módulo principal |
|---|---|---|
| Assinaturas | 0015, 0018 (data de outorga) | `extractor.py`, `extractor_docling.py` |
| Marcadores de lista | 0016 | `extractor_docling.py` (`RE_MARCADOR_PROPRIO`) |
| Títulos | 0017, 0018 | `extractor.py` (`estruturar`) |
| Mobiliário do BTE | 0019 | `extractor_docling.py` (`limpar_texto_item`) |
| Tabelas | 0020, 0021 | `extractor.py`, `qdpx.py` |
| Nomeação | 0022 | `nomeacao.py`, `docs/rnc/README.md` |

### Ordem sugerida

As de menor risco e maior retorno primeiro: **0019** (resíduo BE, correção estreita),
**0016** (marcadores, afeta muitos documentos), **0015** (assinaturas, três sintomas
mas um só bloco), **0017**/**0018** (títulos), **0020** (tabelas rodadas), **0022**
(decisão de equipa, não só código), **0021** (investigação, sem implementação imediata).
