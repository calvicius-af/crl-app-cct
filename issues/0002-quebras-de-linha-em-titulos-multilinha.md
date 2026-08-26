# ISSUE-0002: quebras de linha nos blocos de título do início dos documentos

- **Estado:** Aberta
- **Data:** 2026-07-06
- **GitHub:** #29 (sub-issue de #24)
- **Onde dói:** `cct/extractor.py` (junção de linhas)

## O que acontece

Nos blocos de título que abrem as convenções — o cabeçalho longo que identifica as partes
outorgantes, muitas vezes em três ou quatro linhas — a junção de linhas não se aplica, e o
texto extraído fica partido a meio de frase.

O resto do documento não tem este problema: a regra que junta continuações de linha
funciona bem no corpo das cláusulas. São os blocos de título iniciais, com formatação
própria e linhas curtas centradas, que escapam.

## O que devia acontecer

O bloco de título deve sair como texto corrido, tal como um parágrafo normal do corpo.

## Como reproduzir

Ver o início de qualquer um dos exemplos:

```bash
head -5 examples/acip_fesaht/saida/25_PR_003_BTE_02_ACIP_FESAHT.txt
```

## Notas

Reportado pela equipa nos memos do MaxQDA da ronda de 6 de julho de 2026 (memos 21 e 23,
em [docs/validacao/memos-peritas-4_08-v3.html](../docs/validacao/memos-peritas-4_08-v3.html)).

Cuidado ao corrigir: as linhas de título são protegidas de propósito da junção de linhas,
para não fundir o título de uma cláusula com o do capítulo — foi um problema reportado
numa ronda anterior. A correção tem de distinguir os dois casos, e ambos têm de continuar
cobertos por teste.

**Impacto:** cosmético na leitura, sem efeito nas codificações (o bloco de título fica
fora da análise temática, em `00 Estrutura`).

## Progresso no PR #23

O PR #23 melhorou a identificação do preâmbulo e dos limites dos subtipos
oficiais, mas não apresentou uma prova suficiente de que todos os títulos
iniciais centrados e multilinha ficam unidos sem fundir títulos estruturais.
O problema mantém-se aberto como #29, com casos de regressão explícitos para os
dois comportamentos.
