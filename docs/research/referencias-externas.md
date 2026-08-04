# Referências externas: software e especificações consultados

Durante o desenho da aplicação foram estudados vários projetos de terceiros e
especificações técnicas, sobretudo para perceber como outras equipas leem e escrevem o
formato REFI-QDA e como se representa legislação em XML.

**Nenhum destes projetos está incluído no repositório.** As cópias de trabalho ficam na
pasta local `vendor/`, excluída do Git: é código com autoria e licenças próprias, que não
nos cabe redistribuir. Esta página serve de registo do que foi consultado, com que
licença, e o que daí resultou para o projeto.

## Ferramentas REFI-QDA

| Projeto | Origem | Licença | O que se retirou |
|---|---|---|---|
| `pyqdpx` | github.com/…/pyqdpx | MIT (© 2025 Pethő Gergely) | Leitura de ficheiros QDPX em Python; confirmou a estrutura `project.qde` + `Sources/` que o nosso exportador produz |
| `pyrefiqda` | PyPI / GitHub (`pyrefiqda`) | MIT (© 2026 Constantin Brîncoveanu) | Modelo de objetos REFI-QDA; comparação com o nosso `cct/qdpx.py` |
| `portableQDA` | github.com/…/portableQDA | LGPL | Round-trip de informação entre programas QDA; referência para a compatibilidade de GUIDs |
| `atlas-qdpx` | github.com/…/atlas-qdpx | MIT (© 2025 Boris Bachmann) | Tratamento de exports QDPX do ATLAS.ti; casos-limite de codificação de caracteres |
| `refi-qda` (especificação) | refi-qda.net | Especificação pública | **A referência normativa**: XSD do projeto REFI-QDA, diagrama de classes e especificação completa. É contra isto que o `.qdpx` gerado é validado |

## Ferramentas de análise qualitativa e codificação assistida

| Projeto | Licença | O que se retirou |
|---|---|---|
| `maxqda-codebook-builder` | MIT (© 2026 DrAndrey75) | Construção offline de codebooks para MaxQDA; inspirou o formato YAML dos nossos codebooks |
| `paper_themes` | sem ficheiro de licença — **não reutilizável sem autorização** | Codificação temática com LLM local via LM Studio e conversão para projeto MaxQDA; foi daqui que veio a ideia do backend LM Studio (ver [ADR-0006](../adr/0006-semantica-llm-local-desligada-por-omissao.md)) |
| `fastQDA` | sem ficheiro de licença — **não reutilizável sem autorização** | Alternativa leve a CAQDAS; comparação de abordagens |
| `phdbuddy` | sem ficheiro de licença — **não reutilizável sem autorização** | CAQDAS web com IA; referência de interface |
| `qualitative-analysis-toolkit` | proprietária (*All Rights Reserved*) — **apenas consulta** | Análise fenomenológica e temática em Python |
| `QC-Report-Generator` | GPL — **copyleft, incompatível com reutilização direta** | Geração de relatórios a partir de análise qualitativa |

## Normalização de texto jurídico

| Referência | O que é | Relevância |
|---|---|---|
| AKN4EU 4.2 (publicação de 2024-10-29) | Perfil europeu do Akoma Ntoso para atos jurídicos | Caminho possível para representar IRCT em XML normalizado; ver `akn4eu-guia-tecnico.md` e `akn4eu-guia-exaustivo.md` |
| ELI / ELI-DL | *European Legislation Identifier* e o seu vocabulário de dados | Identificação persistente de instrumentos; ver `irct-portugueses-eli-eli-dl-akn4eu.md` |
| FRBR | Modelo obra/expressão/manifestação/item | Base conceptual para distinguir uma convenção (obra) das suas versões e publicações; ver `frbr-guia-tecnico.md` |

Estas três linhas de trabalho **não estão implementadas** — são o enquadramento para uma
eventual fase de interoperabilidade com sistemas europeus, e a razão pela qual o
`doc.json` guarda estrutura hierárquica em vez de texto plano.

## Nota sobre licenças

Antes de reutilizar código de qualquer um destes projetos (e não apenas de o consultar),
verificar a licença na origem: cinco deles não têm ficheiro de licença, o que em direito
de autor significa **todos os direitos reservados** por omissão, e dois têm licenças
(GPL, proprietária) incompatíveis com a licença deste repositório.
