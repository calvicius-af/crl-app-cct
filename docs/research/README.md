# Pesquisa

Estudos preparatórios e material de enquadramento reunido antes e durante o
desenvolvimento. São documentos de **contexto**, não especificações do que está
construído: para saber o que a aplicação faz hoje, ver
[../arquitetura/arquitetura.md](../arquitetura/arquitetura.md); para saber porque foi
construída assim, ver [../adr/](../adr/README.md).

| Ficheiro | Assunto |
|---|---|
| [requisitos-iniciais-app.md](requisitos-iniciais-app.md) | O pedido original: o que se pretendia da aplicação antes de existir código |
| [autocoding-juridico-refi-qda-automacoes.md](autocoding-juridico-refi-qda-automacoes.md) | Codificação automática de texto jurídico e integração com REFI-QDA (.qdpx) através de ferramentas de automação (n8n, KNIME) — a alternativa que foi ponderada e não seguida |
| [akn4eu-guia-tecnico.md](akn4eu-guia-tecnico.md) | AKN4EU (Akoma Ntoso for European Union): guia técnico |
| [akn4eu-guia-exaustivo.md](akn4eu-guia-exaustivo.md) | AKN4EU: versão longa, com o modelo de documento em detalhe |
| [irct-portugueses-eli-eli-dl-akn4eu.md](irct-portugueses-eli-eli-dl-akn4eu.md) | Como compatibilizar os IRCT portugueses com ELI, ELI-DL e AKN4EU |
| [frbr-guia-tecnico.md](frbr-guia-tecnico.md) · [frbr-guia-tecnico-v2.md](frbr-guia-tecnico-v2.md) | Modelo FRBR (obra / expressão / manifestação / item), duas versões do mesmo guia |
| [referencias-externas.md](referencias-externas.md) | Software de terceiros e especificações consultados, com licenças |

## Como isto se liga ao que existe

A linha AKN4EU / ELI / FRBR responde a uma pergunta de fundo: **uma convenção coletiva é
um documento ou uma sucessão de versões do mesmo instrumento?** É a distinção
obra/expressão do FRBR, e é ela que justifica duas decisões do pipeline — guardar
estrutura hierárquica com offsets em vez de texto plano, e tratar a diacronia
(2020 → 2025) como primeira classe em vez de comparação avulsa.

Nada disto está implementado como exportação normalizada. Se um dia for preciso publicar
os IRCT em formato europeu, o `doc.json` é o ponto de partida.
