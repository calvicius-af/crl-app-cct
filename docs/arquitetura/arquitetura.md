# Arquitetura da aplicação — Pipeline CCT → MaxQDA

## Visão geral

Aplicação local em Python, organizada como um pipeline de fases que
comunicam **apenas por ficheiros** (inspecionáveis e reexecutáveis).
A interface gráfica é uma casca fina: invoca os mesmos comandos da linha
de comandos e não contém lógica própria.

```
                       ┌─────────────────────────────┐
 ENTRADAS              │   App gráfica (cct/app.py)  │   tkinter, stdlib
                       │   ou linha de comandos      │
                       └──────────────┬──────────────┘
 Índices do BTE ─────┐                │ orquestra
 (data/raw/indices/) │   ┌────────────▼─────────────────────────────┐
                     ├──►│ 0. AQUISIÇÃO (opcional)                  │
                     │   │  cct/recolha.py  → descarrega (só aqui   │
                     │   │  há rede; desligada por omissão)         │
                     │   │  cct/nomeacao.py → AA_PR_NNN_BTE_NN_…    │
                     │   └────────────┬─────────────────────────────┘
                     │                │ PDFs em data/raw/bte/bte_<ano>/
 PDFs do BTE ────────┤                │
 (data/raw/bte/)     │   ┌────────────▼─────────────────────────────┐
                     ├──►│ 1. EXTRAÇÃO        extractor.py ou       │
                     │   │                    extractor_docling.py  │
 Variáveis MaxQDA ───┤   │  PDF → doc.json + doc.txt                │
 (.xlsx)             │   │  colunas duplas, tabelas, headers,       │
                     │   │  hierarquia, parágrafos, consolidado,    │
 Codebook master ────┤   │  assinaturas   [pdfplumber | Docling]    │
 (.qdc)              │   └────────────┬─────────────────────────────┘
                     │                │ doc.json (JSON Schema)
 Codebooks YAML ─────┤   ┌────────────▼─────────────────────────────┐
 (codebooks/*.yaml)  ├──►│ 2. CODIFICAÇÃO     cct/lexical.py        │
                     │   │  termos + condições de contexto →        │
 Versões anteriores ─┤   │  anotações {código, confiança, nível}    │
 (data/raw/textos_   │   │  + opcional: cct/semantico.py (LLM local)│
  consolidados/)     │   └────────────┬─────────────────────────────┘
                     │                │ anotacoes.json
                     │   ┌────────────▼─────────────────────────────┐
                     └──►│ 3. DIACRONIA       cct/diacronia.py      │
                         │  versão anterior vs atual → =/alteração/ │
                         │  nova/removida → novidades do consolidado│
                         └────────────┬─────────────────────────────┘
                                      │ novidades (ids de cláusulas)
                         ┌────────────▼─────────────────────────────┐
                         │ 4. TRIAGEM         cct/triagem.py        │
                         │  AUTO (precisão calibrada ≥0.85) /       │
                         │  REVER / CONSOLIDADO (sem novidade)      │
                         └────────────┬─────────────────────────────┘
                                      │
                    ┌─────────────────┼──────────────────┐
        ┌───────────▼──────┐ ┌────────▼────────┐ ┌───────▼────────┐
 SAÍDAS │ projeto.qdpx     │ │ sugestoes_      │ │ relatorio.txt  │
        │ (REFI-QDA, árvore│ │ peritas.xlsx    │ │ (problemas por │
        │  de códigos c/   │ │ (segmentos c/   │ │  documento)    │
        │  GUIDs estáveis) │ │  contexto)      │ │                │
        │ cct/qdpx.py      │ │ cct/export_xlsx │ │                │
        └──────────────────┘ └─────────────────┘ └────────────────┘
                                      │
                             manifest.json
                     proveniência, hashes, versões e contagens

 TRANSVERSAIS
   cct/harness.py + avaliar_baseline.py  → métricas vs amostra de referência (calibração)
   cct/qdc.py / variaveis.py / referencia.py → leitores dos exports MaxQDA
   cct/comparar.py                        → comparação avulsa de versões
   cct/doctor.py                          → verificação do ambiente
   cct/bench_llm.py                       → avaliação de modelos locais
   cct/sanidade.py                        → avisos estruturais por documento
   cct/proveniencia.py                    → manifesto verificável da corrida
```

## Princípios de desenho
1. **Fases desacopladas por ficheiros** — cada passo pode ser corrido,
   inspecionado e repetido isoladamente; a UI e a CLI partilham 100% da
   lógica (a UI lança os módulos em subprocesso).
2. **Configuração é dados, não código** — os temas de codificação são YAML;
   a equipa de análise mantém-nos sem intervenção informática.
3. **Contratos validados** — doc.json e anotacoes.json têm JSON Schema;
   a propriedade "zero perda de texto" é verificada por teste.
4. **Qualidade medida, não presumida** — o harness compara sempre com o
   amostra de referência humana; a faixa AUTO só existe onde a precisão medida ≥ 0.85.
5. **Offline por omissão** — o LLM opcional só aceita loopback. O Docling pode
   descarregar modelos na primeira execução e deve ser pré-provisionado em redes fechadas.

## Módulos (`cct/`)
| Módulo | Responsabilidade |
|---|---|
| extractor.py | PDF → estrutura hierárquica com offsets (o módulo mais crítico) |
| extractor_docling.py | extrator alternativo para tabelas e layouts difíceis |
| schemas.py | contratos de dados (JSON Schema) |
| lexical.py | codificação por termos/condições; níveis cláusula/parágrafo |
| semantico.py | codificação LLM (backend plugável, cache, validação) |
| diacronia.py | alinhamento e classificação =/alteração/nova/removida |
| triagem.py | faixas AUTO/REVER/CONSOLIDADO calibradas |
| qdpx.py | exportador REFI-QDA (árvore de códigos, GUIDs determinísticos) |
| sanidade.py | controlos estruturais e avisos antes da exportação |
| proveniencia.py | manifesto da corrida com hashes, ambiente e contagens |
| export_xlsx.py | Excel das peritas com contexto |
| qdc.py, variaveis.py, referencia.py | leitores dos exports do MaxQDA |
| harness.py, avaliar_*.py | métricas contra a amostra de referência |
| localizador.py | localizar convenções em números completos do BTE |
| recolha.py | ler os índices do BTE e descarregar os documentos (única fase com rede) |
| nomeacao.py | siglas dos outorgantes, ordinais estáveis e nomes do esquema do pipeline |
| aquisicao.py | encadeia recolha + nomeação numa corrida |
| pipeline_tema.py, comparar.py | orquestradores CLI |
| app.py, doctor.py | interface gráfica e verificação de ambiente |

O QDPX pode inserir linhas em branco para legibilidade. Os offsets são remapeados e o
contrato é de equivalência semântica: removendo exatamente as inserções calculadas pelo
exportador, recupera-se o trecho canónico carácter por carácter.

## Fluxos de dados externos
- **MaxQDA → pipeline**: variáveis (.xlsx), codebook master (.qdc),
  amostras de referência de segmentos (.xlsx) — todos exports nativos do MaxQDA.
- **Pipeline → MaxQDA**: projeto .qdpx (REFI-QDA 1.5, importação nativa
  no MaxQDA 2022+). GUIDs determinísticos garantem compatibilidade entre
  exports sucessivos.
- **Pipeline → peritas**: .xlsx autónomo (não requer MaxQDA).
- **BTE → pipeline** (opcional): índices .xlsx da DGERT e PDFs públicos de
  `bte.dgcp.mtsss.gov.pt`, descarregados apenas com autorização explícita
  ([ADR-0015](../adr/0015-recolha-em-rede-desligada-por-omissao.md)).
