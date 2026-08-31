# ADR-0010: na comparação diacrónica, o par de versões é escolhido pelo sistema

- **Estado:** Aceite
- **Data:** 2026-07-07
- **Decidido por:** CRL (António Fula)

## Contexto

A comparação entre versões de uma convenção (o que mudou de 2020 para 2025) foi
construída e validada contra as amostras de referência feitas à mão pela equipa: no caso ACIP
2009 → 2025, as quatro alterações da amostra de referência foram todas apanhadas.

Ao correr o lote completo — 44 pares — apareceu um problema que não era do comparador.
Em **36% dos pares**, a versão "anterior" escolhida era uma **revisão parcial**: um
documento de duas páginas que altera três cláusulas, não o texto completo da convenção.
Comparar contra isso produz centenas de falsas "cláusulas novas". Num caso (ADIPA), até o
documento de 2025 escolhido era ele próprio uma revisão parcial.

O erro estava na escolha do par, feita à mão, e era invisível: o comparador corria sem
queixas e produzia números plausíveis mas errados.

## Decisão

A escolha do par passa a ser **do sistema**, através da opção `--pasta`, que recebe a
pasta de versões de uma convenção e decide:

- **versão nova**: o documento de 2025 com mais texto;
- **versão anterior**: o texto **completo** mais recente que não seja de 2025;
- **revisão parcial**: qualquer documento com menos de 50% do texto do maior — excluído
  da escolha;
- **ano**: deduzido do nome do ficheiro (`2020_…`, `25112_BTE_19_…`, `NN_BTE_…`).

Se o utilizador forçar um par com `--antigo`/`--novo` e a versão antiga for uma revisão
parcial, a aplicação **avisa** em vez de comparar em silêncio.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Continuar a escolher à mão | Já se demonstrou que falha em mais de um terço dos casos, e falha em silêncio |
| Usar os metadados do MaxQDA para saber o subtipo | Existem e são usados noutros pontos, mas não cobrem as versões antigas do arquivo |
| Rejeitar automaticamente qualquer revisão parcial | Por vezes é o único documento disponível; melhor avisar do que impedir |

## Consequências

- Nas 21 pastas de textos consolidados, 21/21 passaram a escolher o par certo, com perfis
  de alteração plausíveis.
- Casos verificados manualmente como legítimos e não como erro: Ageas 2023→2025 (60
  alterações reais, quase todas de linguagem inclusiva), TINITA 2020→2025 (14
  renumerações), RTP (51 renumerações).
- Passa a haver uma dependência real dos **nomes dos ficheiros**: mudar o esquema de nomes
  parte a dedução do ano. Está documentado em [docs/dados](../dados/README.md).

## Revisitar quando

Houver uma fonte fiável de metadados de versão (por exemplo, identificadores ELI) que
dispense a heurística sobre nomes de ficheiro.
