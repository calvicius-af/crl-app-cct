# Arquitetura da aplicação — Pipeline CCT → MaxQDA

## Visão geral

Aplicação local em Python. Os comandos granulares podem guardar artefactos
intermédios por documento; `cct.pipeline_tema` encadeia as fases em memória
por PDF e escreve os resultados e o manifesto no destino da corrida.
A interface gráfica lança os módulos da CLI e também gere a confirmação
humana de siglas por documento, persistida em `siglas.csv` local.

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
        │ cct/qdpx.py      │ │ export_xlsx.py   │ │                │
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
1. **Entradas e saídas verificáveis** — os comandos granulares suportam
   inspeção por fase; a corrida temática processa em memória por documento
   e emite saídas, relatório, diagnóstico e manifesto. A UI lança módulos
   em subprocesso e usa a lógica de confirmação de `cct.nomeacao`.
2. **Configuração é dados, não código** — os temas de codificação são YAML;
   a equipa de análise mantém-nos sem intervenção informática.
3. **Contratos validados** — doc.json e anotacoes.json têm JSON Schema;
   a propriedade "zero perda de texto" é verificada por teste.
4. **Qualidade medida e revista** — o harness compara com a amostra de
   referência humana; a interpretação das métricas históricas aguarda revisão
   do gabarito (GitHub #10), inclusive para decisões sobre AUTO.
5. **Offline por omissão** — o LLM opcional só aceita loopback. A aquisição
   exige autorização de rede, e o Docling pode descarregar modelos na primeira
   execução; provisionar modelos antes de usar em redes fechadas.

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
| corpus.py, desempenho.py | regressão em PDF reais e medições por extrator |
| completude.py, modelos_docling.py | diagnóstico da corrida e gestão de modelos verificados |
| limites.py, subprocesso.py | limites de PDFs e isolamento de conversões Docling |

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
