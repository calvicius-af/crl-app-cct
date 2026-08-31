---
type: project
created: 2026-06-04
tags:
  - formacao
  - design-instrucional
  - meta-processo
  - andragogia
estado: ativo
prazo:
norte:
  - "[[Conversational Framework]]"
  - "[[3 Cs dos objetivos de aprendizagem]]"
  - "[[Referenciais de competências]]"
sul:
  - "[[Decisão — Formação envolve o blueprint CCT em vez de duplicar]]"
  - "[[Decisão — v1 do processo de formação não inclui camada LMS]]"
  - "[[Decisão — Domain expert é sub-processo de construção de contexto]]"
oeste:
  - "[[blueprint_cct_maxqda_pipeline]]"
  - "[[MOC — Aprendizagem e Design Instrucional]]"
este: []
---

# Processo de Formação Pragmática

## Objectivo

Um **meta-processo reutilizável** que, dado um objetivo de aprendizagem ligado a um problema real, orquestra agentes e skills para produzir uma formação estruturada (análise, desenho, desenvolvimento, avaliação, capitalização). Aprende-se enquanto se resolve um problema concreto, e cada formação alimenta de forma consolidada o vault como Personal Knowledge Management System.

## Porquê

Até agora a aprendizagem tem sido avulsa, sem consolidação nem apropriação dos conceitos. Este processo torna-a estruturada e cumulativa: **orquestra e fecha lacunas sobre o que já existe no vault, em vez de construir tudo de raiz**. A formação é o instrumento; o problema real é o motor.

## Estratégia de construção

Desenham-se as 6 etapas no papel (design abstrato), mas a validação faz-se **implementando um subconjunto num caso-âncora real** — não no vazio. Walking skeleton: uma fatia fina mas completa primeiro, e o processo emerge como sedimento da fricção observada.

## Bases de trabalho

- [[Processo de Formação Pragmática — Base operacional]] — contrato operacional da v1, ciclo de trabalho, definição de pronto e riscos vivos.
- [[Processo de Formação Pragmática — Mapa de artefactos]] — inventário dos artefactos mínimos do processo e da primeira instância Python+CCT.
- [[Análise de necessidades — Python e blueprint CCT]] — primeira análise da instância Python+CCT, ainda em rascunho.
- [[Referencial de competências — Python e pipeline CCT]] — competência de saída da primeira instância Python+CCT.
- [[Plano do tracer PDF — Python e pipeline CCT]] — primeiro ciclo curto da v1: PDF real → texto/Markdown → avaliação → capitalização.
- [[Rubrica de avaliação — tracer PDF Python+CCT]] — critérios mínimos de desempenho para fechar o primeiro tracer.
- [Aprender Docling — oficina](aprender-docling/README.md) — primeira instância do sub-processo `construir-expert`, sobre a fonte técnica Docling: missão, fontes anotadas, lições e cartão de referência.
- Base dinâmica do projeto — vive no vault Obsidian e não é distribuída neste repositório.
- [[AGENTS|AGENTS local]] — regras específicas para trabalho futuro nesta pasta.

## As 6 etapas (ciclo ISD / ADDIE) e o âmbito da v1

| Etapa | Método (ancorado no vault) | v1 |
|---|---|---|
| 1 · Análise de necessidades | Map It → objetivo, lacunas, contexto | ✅ |
| 2 · Desenho | programa + referencial + competências de saída (3 Cs + Bouterf + níveis + `esco::` leve + EQF) | ✅ |
| 3 · Desenvolvimento | conteúdos + exercícios ([[Conversational Framework|6 tipos de Laurillard]]) + sub-processo *construir-expert* | ✅ |
| 4 · Implementação (LMS) | Moodle (NAS) + SCORM + H5P | ⏸ v2 |
| 5 · Avaliação | INOFOR + Kirkpatrick + [[Transferência de aprendizagem|avaliação por desempenho]] | ✅ |
| 6 · Capitalização | `atomic-notes` / `atomize-report` → vault | ✅ |

O **design universal** e as **boas práticas DGERT** são restrições *transversais* de qualidade (linguagem clara, estrutura acessível), não etapas.

## Caso-âncora (v1)

> Aprender **Python** enquanto se implementa o `blueprint_cct_maxqda_pipeline` v2, sobre o corpus das **[[convenções coletivas]]** (CC + AC + AE; tracer inicial = 1 contrato coletivo end-to-end).

- **Reaproveita, não duplica:** o blueprint já decompõe o trabalho em etapas atómicas (A1.1 … F3), cada uma com *Inputs / Outputs / Critério de Sucesso*.
- **Sacada da avaliação:** o *Critério de Sucesso* de cada etapa do blueprint **é** o critério do objetivo de aprendizagem (o "C" dos 3 Cs) **e** a evidência de competência. O código a funcionar é a prova de aprendizagem.
- **Modelos locais já no blueprint:** Ollama + LangExtract — o requisito "local" já é decisão tomada, não algo a inventar.

## Os experts (domain knowledge expert)

Não é um sistema de retrieval nem confiança no conhecimento paramétrico do LLM. É um **sub-processo reutilizável de construção de contexto**:

1. **Investigar** fontes autorizadas (critérios: privilegiar experiência UE, fundamentar tudo, melhor conhecimento como contexto).
2. **Ingerir** → atomizar no vault via `atomic-notes` / `atomize-report` (sem duplicar).
3. **Instanciar** uma skill-expert ancorada nesse contexto, à imagem das personas existentes ([[catarina-varga]], [[helena-rodrigues]], [[miguel-andersen]], [[paulo-nielsen]], [[rui-takahashi]], [[sandra-ferreira]]).

Na v1 constrói-se o **expert técnico/Python** (lacuna no vault). O domínio CCT/laboral já está modelado (Glossário CRL, 200+ conceitos) e serve de *contexto de aplicação*.

## Inventário de skills/agentes (design abstrato — a reutilizar)

- `gestor-de-formacao` — orquestrador; faz as questões iniciais de âmbito (persona de gestor de formação experiente).
- `diagnostico-necessidades` — análise Map It.
- `desenho-formacao` — programa + referencial + competências (3 Cs / ESCO / EQF).
- `construir-expert` — sub-processo investigar → ingerir → instanciar (reusa `atomic-notes`/`atomize-report`).
- `desenho-exercicios` — variedade técnica segundo os 6 tipos de Laurillard.
- `avaliacao-formacao` — INOFOR + Kirkpatrick + avaliação por desempenho; sinaliza pontos de dor para reformulação.
- **Reuso directo:** `atomic-notes`, `atomize-report`, `obsidian-cli`, `tool-contract-design`.

## Token efficiency (propriedade emergente)

Reusar artefactos > regenerar · Ollama local para extração em massa · Claude reservado para raciocínio de alto valor (andaimes, avaliação) · cada ingestão torna a sessão seguinte mais barata.

## Próximos passos

- [ ] Etapa 1 (Análise): redigir o objetivo de aprendizagem da v1 com os 3 Cs e mapear lacunas Python vs blueprint.
- [x] Etapa 2 (Desenho): iniciar o referencial de competências de saída com campo `esco::` leve.
- [ ] Sub-processo `construir-expert`: investigar e atomizar as fontes técnicas (Python, PyMuPDF, Docling, LangExtract, Ollama) no vault depois do primeiro tracer.
- [x] Etapa 3: desenhar o 1.º conjunto de exercícios (tracer = PDF → texto/Markdown) cobrindo vários tipos de Laurillard.
- [ ] Decidir a localização do código (repo próprio em `3 Projetos/Processo de Formação Pragmática/codigo/` vs separado) e excluir `.git/` no Obsidian.
- [ ] Resolver o alias sobreposto "CCT" no glossário (ver Notas relacionadas).

## Decisões recentes

- [[Decisão — v1 por tracers curtos com evidência executável]] — validada em 2026-06-07.

## Backlog de formações futuras

- R + análise de dados de CCTs (a jusante deste pipeline).
- GraphRAG jurídico multi-camada ([[MOC — Modelo conceptual de GraphRAG jurídico multi-camada]]) — bom projeto de aprendizagem de dados/IA por si só.
- Agente de feedback sobre prática deliberada em terapia familiar — **bloqueado** até resolver a barreira de `4 Clínica/` (CLAUDE.md §3).

## v2 (diferido)

Camada LMS: montar Moodle na NAS UGREEN (Docker), empacotamento SCORM, exercícios H5P, look via ágora design system, abertura a outros alunos e documentação para terceiros.

## Notas relacionadas

- [[MOC — Aprendizagem e Design Instrucional]] — fundamentos (Laurillard, 3 Cs, referenciais).
- [[blueprint_cct_maxqda_pipeline]] — a espinha técnica do caso-âncora (projeto CRL legado, só leitura).
- Aberto: o alias **"CCT"** está sobreposto entre [[contrato coletivo]] (sigla CC/CCT) e [[convenções coletivas]] (CCT de trabalho) — decisão terminológica vinculativa por tomar.
