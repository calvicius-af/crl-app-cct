# Notas de trabalho — oficina "Aprender Docling"

Rascunho do professor. Preferências do formando, estado da oficina e dívidas por saldar.

## Preferências e contexto do formando

- Trabalha em português europeu. As lições, o glossário e os registos ficam em português.
- Já traz o modelo de domínio (convenções coletivas, BTE, cláusulas) e um pipeline a
  funcionar. A lacuna é técnica, não jurídica — nunca explicar o que é uma cláusula.
- A oficina liga-se ao [Processo de Formação Pragmática](../hub.md) já existente. Isto
  não é um curso paralelo: é o sub-processo *construir-expert* (fontes técnicas do
  Docling) que o hub tinha em aberto nos próximos passos.
- Avalia-se por desempenho, como no resto da formação: o código a funcionar é a prova.

## Estado da oficina

| Artefacto | Estado |
|---|---|
| `MISSION.md` | escrito, confirmado com o formando em 2026-08-21 |
| `RESOURCES.md` | primeira ronda, ancorada no repositório e na skill do pacote |
| `GLOSSARY.md` | **por criar** — só depois de o formando usar os termos corretamente (regra do formato) |
| `learning-records/` | vazio — ainda não há evidência de aprendizagem, só material coberto |
| Lições | 01, 02 e 03 escritas |

## Verificação do material — o que está e o que não está provado

Importante para a honestidade das lições:

- **Verificado por introspecção** do pacote instalado (`docling` 2.121.0, `docling-core`
  2.92.0): campos de `PdfPipelineOptions` e respetivos valores por omissão
  (`do_ocr=True`, `do_table_structure=True`, `TableFormerMode.ACCURATE`,
  `do_cell_matching=True`), valores de `DocItemLabel`, assinatura de
  `iterate_items` e de `download_models`, lista completa das flags de `docling convert`.
- **Verificado por leitura do código-fonte** no commit `06faa09`.
- **NÃO executado ponta a ponta.** O ambiente onde estas lições foram escritas tem o
  `huggingface.co` bloqueado por política de rede, e o pipeline standard precisa de
  descarregar os modelos de layout e de tabelas à primeira utilização. Nenhuma conversão
  foi corrida. Os tempos, contagens e excertos de output que as lições pedem para observar
  são o **exercício**, não um resultado copiado: quem os produz é o formando, na máquina
  dele. As afirmações sobre a API são verificáveis; as afirmações sobre resultados num PDF
  concreto do BTE são hipóteses a testar.
- O ambiente virtual limpo com `docling` mediu **5,5 GB** — esse número foi medido, não
  estimado.

## Dívidas e próximos passos

- [ ] Lição 04: comparar `pdfplumber` (o extractor actual) e Docling no mesmo PDF do BTE,
      contra o gabarito de `docs/validacao/`. É a lição que fecha a missão.
- [ ] Criar `GLOSSARY.md` assim que o formando usar corretamente `DoclingDocument`,
      *label*, proveniência e *backend* vs *pipeline*.
- [ ] Escrever registo de aprendizagem depois da lição 02 se houver evidência (código
      escrito pelo formando que percorra o documento sem regex).
- [ ] Decidir se o Docling entra como dependência opcional (`pip install cct[docling]`)
      ou fica como ferramenta de análise fora do pipeline. Depende da lição 04.
- [ ] Confirmar se as tabelas salariais que atravessam páginas ficam partidas em vários
      `TableItem` — não se encontrou fonte que responda; é experiência a fazer.
