# ADR-0002: QDPX (REFI-QDA) como formato de troca com o MaxQDA

- **Estado:** Aceite
- **Data:** 2026-07-05
- **Decidido por:** CRL (António Fula)

## Contexto

O produto do pipeline tem de chegar ao MaxQDA, que é onde a equipa do CRL faz a análise.
A primeira versão do trabalho (o pré-processador, hoje em `archive/`) produzia ficheiros
de texto com marcas `#TEXT`/`#CODE` para importação estruturada. Funcionava, mas com dois
limites sérios: a codificação só chegava ao nível da cláusula, e a árvore de códigos
tinha de ser recriada à mão no MaxQDA.

Existe um formato aberto para isto: **REFI-QDA**, especificação publicada em refi-qda.net
e suportada por MaxQDA, ATLAS.ti, NVivo e QualCoder.

## Decisão

O formato de saída principal é **QDPX (REFI-QDA 1.5)**: um ZIP com `project.qde` (XML
com a árvore de códigos e as posições dos segmentos) e `Sources/` (o texto).

Daqui decorre uma regra crítica: o texto-fonte é **UTF-8 sem BOM, com quebras LF**, e os
offsets das seleções contam caracteres sobre esse texto exato. Um BOM ou um CRLF
desalinham todas as codificações.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Manter o formato `#TEXT`/`#CODE` | Não transporta a árvore de códigos nem permite codificar abaixo da cláusula (número, alínea) |
| Automação externa (n8n, KNIME) a escrever no MaxQDA | Estudado (ver [pesquisa](../research/autocoding-juridico-refi-qda-automacoes.md)); acrescenta uma plataforma inteira para resolver um problema de formato de ficheiro |
| Script de macro dentro do MaxQDA | Prende o trabalho a uma versão do programa e a uma máquina |

## Consequências

- Os projetos gerados abrem nativamente no MaxQDA 2022+ (*Importar → Projetos de outros
  programas QDA → REFI-QDA*), com a árvore de códigos já montada.
- O trabalho fica portável: se o CRL mudar de CAQDAS, os ficheiros continuam a ler-se.
- A propriedade **zero perda de texto** passa a ser obrigatória e testada: concatenar os
  nós do `doc.json` tem de reconstruir exatamente o `.txt` que vai dentro do QDPX.
- Ficamos dependentes da conformidade do MaxQDA com a especificação; cada gate incluiu,
  por isso, uma importação real e não apenas validação contra o XSD.

## Revisitar quando

A especificação REFI-QDA evoluir de forma incompatível, ou o MaxQDA deixar de a suportar.
