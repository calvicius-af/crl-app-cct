# ADR-0013: anonimização dos exemplos publicados e exclusão dos PDFs originais

- **Estado:** Aceite
- **Data:** 2026-08-05
- **Decidido por:** CRL (António Fula)

## Contexto

Os exemplos demonstram o pipeline com convenções reais. Os PDFs de origem e algumas saídas
contêm nomes de pessoas signatárias. Embora os documentos tenham origem pública, a publicação
do repositório cria uma nova cópia pesquisável e reutilizável que não é necessária para
demonstrar o software.

## Decisão

- Não versionar os PDFs de entrada nem as versões históricas originais nos exemplos públicos.
- Substituir os nomes de signatários nos artefactos de saída por marcadores de igual
  comprimento, preservando os offsets do texto, `.doc.json` e QDPX.
- Aplicar e verificar a transformação com `scripts/anonimizar_exemplos.py`.
- Documentar a diferença como decisão de publicação, e não como falha de processamento.

## Consequências

- Os exemplos continuam a mostrar a estrutura e as saídas do pipeline, mas já não permitem
  reproduzir os PDFs originais apenas a partir do clone.
- Quem precisar de repetir a extração obtém os documentos na fonte oficial ou através do
  arquivo autorizado do CRL.
- Antes de publicar novos exemplos, deve-se executar a verificação de anonimização e confirmar
  que não foram acrescentados outros dados pessoais.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Publicar os PDFs por serem documentos oficiais | Não é necessário para demonstrar a aplicação e aumenta a exposição de dados pessoais. |
| Redigir visualmente os PDFs originais | Exige uma cadeia de redação PDF verificável; a exclusão é mais segura nesta fase. |
| Anonimizar só o README | Deixaria os nomes pesquisáveis nos textos, QDPX e Excel. |

## Revisitar quando

Existir autorização institucional explícita para redistribuir um conjunto de exemplos ou uma
ferramenta de redação PDF validada para produzir fontes anonimizadas.
