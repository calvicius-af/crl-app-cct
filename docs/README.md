# Documentação

Por onde começar, consoante o que precisas:

| Se queres… | Vai a |
|---|---|
| ver o sistema a funcionar, com ficheiros reais | [../examples/](../examples/README.md) |
| perceber como funciona | [arquitetura/arquitetura.md](arquitetura/arquitetura.md) |
| perceber **porque** é assim | [adr/](adr/README.md) — 11 decisões registadas |
| operá-lo | [operacao/guia-operacao.md](operacao/guia-operacao.md) |
| criar ou afinar um codebook | [operacao/prompts-codebooks.md](operacao/prompts-codebooks.md) |
| saber se é fiável | [validacao/](validacao/README.md) — gates, memos das peritas, métricas |
| instalar numa máquina nova | [dados/](dados/README.md) + [institucional/requisitos-tecnicos.md](institucional/requisitos-tecnicos.md) |
| apresentar o projeto | [institucional/](institucional/) — requisitos técnicos e proposta ao Instituto de Informática |
| o enquadramento teórico | [research/](research/README.md) — AKN4EU, ELI, FRBR, REFI-QDA |
| aprender a mexer no código | [formacao/](formacao/) |

## Como está organizada

- **arquitetura/** — o desenho do sistema: as quatro fases, os módulos, os fluxos de
  dados de e para o MaxQDA.
- **adr/** — uma página por decisão estruturante, escrita no momento em que se decide.
  Não se apaga nem se reescreve: se a decisão mudar, escreve-se outra que a substitui.
- **operacao/** — o que fazer, por que ordem, e o que fazer quando corre mal.
- **validacao/** — os gates de qualidade, os comentários das peritas exportados do
  MaxQDA, e as métricas contra codificação humana.
- **dados/** — proveniência de cada fonte, convenções de nomes, e como repor `data/`.
- **institucional/** — os documentos dirigidos ao Instituto de Informática.
- **research/** — estudos preparatórios; contexto, não especificação do que existe.
- **formacao/** — material didático produzido a partir deste projeto.

A documentação está sob CC BY 4.0 (ver [LICENSE](../LICENSE)).
