# ADR-0014: distinguir caches, corridas e artefactos humanos fora do Git

- **Estado:** Aceite
- **Data:** 2026-08-26
- **Decidido por:** CRL (António Fula)
- **Refina:** ADR-0009

## Contexto

O ADR-0009 decidiu corretamente manter `data/` e `results/` fora do Git, mas
classificou `data/interim/` e todo o `results/` como descartáveis. A utilização
real acumulou projetos MQDA importados, Excel possivelmente revisto por peritas,
provas de MaxQDA, benchmarks e experiências sem manifesto. Alguns destes
ficheiros podem conter trabalho humano que o código não consegue regenerar.

Pastas chamadas `v2`, `v3` ou `teste` também não fixam o commit, os inputs, o
ambiente nem a decisão que produziram a saída. A exclusão do Git resolve volume e
privacidade, mas não resolve proveniência, retenção ou cópia de segurança.

## Decisão

- Manter `data/`, `results/`, `archive/` e `vendor/` fora do Git.
- Classificar artefactos locais por ciclo de vida: fonte, referência humana,
  validado, reproduzível, experiência, intermédio, cache e terceiro.
- Só cache explicitamente classificada pode ser eliminada automaticamente.
- Tratar MQDA, resultados anotados/triados e Excel potencialmente revisto como
  trabalho humano até confirmação em contrário.
- Fazer cada nova corrida produzir um `manifest.json` com comando, commit,
  ambiente, hashes, contagens e problemas.
- Inventariar com SHA-256 antes de migrar pastas antigas.
- Separar progressivamente corridas, benchmarks, experiências, resultados
  validados e entregáveis segundo
  [a organização do workspace](../dados/organizacao-workspace.md).
- Nunca guardar credenciais ou `.env` nas cópias de terceiros em `vendor/`.

## Consequências

- `results/` deixa de poder ser apagada em bloco.
- Uma saída só é considerada reproduzível quando o manifesto fixa os inputs e o
  código; estar fora do Git não é prova de regenerabilidade.
- A migração atual é deliberadamente conservadora: primeiro inventário e cópia de
  segurança, depois movimentos validados por hash.
- O pipeline passa a produzir um ficheiro adicional, `manifest.json`.
- O inventário local contém nomes e hashes de ficheiros internos e, por isso,
  continua fora do Git.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Continuar a usar sufixos `v2`, `v3`, … | Não fornecem proveniência nem distinguem resultado humano de cache |
| Versionar tudo no Git/LFS | Mantém os problemas de privacidade, licenças e volume do ADR-0009 |
| Apagar e regenerar `results/` | Pode destruir revisões humanas e experiências não reproduzíveis |
| Mover tudo imediatamente | Os caminhos atuais ainda são usados e os artefactos antigos não estão classificados |

## Revisitar quando

A instituição disponibilizar armazenamento de artefactos com controlo de acesso,
retenção, checksums e cópias de segurança, ou quando a migração dos caminhos atuais
estiver concluída.
