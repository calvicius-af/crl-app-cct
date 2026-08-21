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
- **Actualização de 2026-08-21 — primeira execução real, feita pelo formando.** Correu a
  lição 1 num PDF real do BTE (`3_BTE_2_ACIP_FESAHT.pdf`), em macOS, com Python 3.14, sem
  `--no-ocr`. Conversão bem-sucedida em 78,4 s. Confirmou-se algo que as lições ainda não
  cobriam: **o motor de OCR por omissão (RapidOCR) descarrega os seus pesos de
  `modelscope.cn`, não de `huggingface.co`** — um segundo host que a lição 03 e o cartão
  de referência não mencionavam. Corrigido nas duas páginas. É a primeira vez que uma
  afirmação desta oficina deixa de ser hipótese e passa a facto confirmado por execução.
- **Actualização de 2026-08-21 — níveis de hierarquia e AKN4EU.** O formando perguntou
  porque é que o Markdown não mostra níveis distintos entre capítulo e cláusula, e se o
  Docling se aproxima do AKN4EU. Verificado por leitura do código-fonte
  (`docling/models/stages/heading_hierarchy/heading_hierarchy_model.py`):
  - `PdfPipelineOptions.heading_hierarchy_options.enabled` é `False` por omissão — **todos**
    os `SECTION_HEADER` ficam em `level=1`. Isto explica o sintoma exactamente.
  - Ligada, a opção tenta 3 sinais em ordem: marcadores do PDF (raros no BTE), numeração
    jurídica (mas os regex de palavra-chave são só em inglês — `chapter`, `article`,
    `clause`… — "CAPÍTULO"/"Cláusula" em português **não** disparam esta via), e estilo
    visual (tamanho/negrito — este sim, independente de língua, e o caminho mais provável
    de funcionar nas convenções).
  - Confirmado por `grep` no pacote inteiro: **não existe exportador para AKN4EU/Akoma
    Ntoso**. A tradução `level` numérico → `AKN4EU chapter/clause` continua a ser código a
    escrever — mais simples do que hoje, porque aplica-se a um título já isolado, não a
    texto corrido.
  - Sobre a necessidade de *linting* pós-extração que o formando levantou: confirmado como
    expectativa correcta, não sintoma de falha do Docling — é o mesmo papel que
    `docs/validacao/` já cumpre para o extractor actual.
  - **Não testado em execução** (precisaria de converter um PDF real com a opção ligada,
    o que este ambiente não permite — ver nota acima sobre rede). Registado como hipótese
    fundamentada em código-fonte, não como facto confirmado por execução.

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
