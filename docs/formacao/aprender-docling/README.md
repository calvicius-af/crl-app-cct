---
type: project
subtype: oficina-aprendizagem
created: 2026-08-21
tags:
  - formacao
  - python
  - docling
  - extracao
estado: ativo
projeto: "[[Processo de Formação Pragmática]]"
é-parte-de:
  - "[[Processo de Formação Pragmática]]"
norte:
  - "[[Referencial de competências — Python e pipeline CCT]]"
  - "[[Plano do tracer PDF — Python e pipeline CCT]]"
---

# Aprender Docling — oficina

Oficina de aprendizagem sobre o [Docling](https://github.com/docling-project/docling)
aplicado à extração de texto e estrutura de convenções coletivas publicadas no BTE.

É o sub-processo **construir-expert** que o [hub da formação](../hub.md) tinha em aberto
("investigar e atomizar as fontes técnicas — Python, PyMuPDF, Docling, LangExtract,
Ollama"), instanciado para uma dessas fontes. Segue o formato da skill `/teach`: estado
persistente em ficheiros, lições curtas em HTML, avaliação por desempenho.

## Como usar

1. Lê a [missão](MISSION.md). Tudo o resto se justifica por ela.
2. Faz as lições por ordem. Cada uma é curta e dá um ganho concreto.
3. Guarda o [cartão de referência](reference/cartao-docling.html) — é o documento a que
   vais voltar depois de as lições estarem esquecidas.
4. Pergunta. As lições são o andaime, não o professor.

```bash
open docs/formacao/aprender-docling/lessons/0001-primeira-conversao.html   # macOS
start docs\formacao\aprender-docling\lessons\0001-primeira-conversao.html  # Windows
```

## Lições

| # | Lição | Ganho |
|---|---|---|
| 01 | [A primeira conversão](lessons/0001-primeira-conversao.html) | Um PDF do BTE convertido, e a distinção entre backend, modelo de layout e pipeline |
| 02 | [Ler a estrutura, não o texto](lessons/0002-ler-a-estrutura.html) | Listar as cláusulas de uma convenção sem uma única regex |
| 03 | [Modelos offline](lessons/0003-modelos-offline.html) | O Docling a correr numa máquina do CRL sem internet |
| 04 | _por escrever_ | Docling contra o `cct/extractor.py`, no mesmo PDF, contra o gabarito de `docs/validacao/` |

A lição 04 precisa de números produzidos por ti — é assim que esta oficina funciona.

## Estado da oficina

| Ficheiro | O que é |
|---|---|
| [`MISSION.md`](MISSION.md) | Porque é que se está a aprender isto. Grava todas as decisões pedagógicas |
| [`RESOURCES.md`](RESOURCES.md) | As fontes de confiança, anotadas, e as lacunas conhecidas |
| [`NOTES.md`](NOTES.md) | Notas do professor, estado da oficina, e **o que está e o que não está verificado** |
| `learning-records/` | Registos de aprendizagem, ainda vazio: só se escreve com evidência |
| `assets/` | Componentes partilhados pelas lições — folha de estilo, quiz |
| `exemplos/` | Scripts para correr, não só para ler |

## Nota de honestidade

As lições foram escritas contra o Docling **2.121.0** instalado e introspecionado, mas
**nenhuma conversão foi executada ponta a ponta** — o ambiente onde foram escritas tem o
`huggingface.co` bloqueado, e o pipeline precisa de descarregar modelos à primeira
utilização. As afirmações sobre a API estão verificadas; as afirmações sobre o
comportamento num PDF concreto do BTE são hipóteses que os exercícios te mandam testar.
Ver [`NOTES.md`](NOTES.md), secção *Verificação do material*.
