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
 PDFs do BTE ────────┐                │ orquestra
 (data/raw/bte/)     │   ┌────────────▼─────────────────────────────┐
                     ├──►│ 1. EXTRAÇÃO        cct/extractor.py      │
 Variáveis MaxQDA ───┤   │  PDF → doc.json + doc.txt                │
 (.xlsx)             │   │  colunas duplas, tabelas, headers,       │
                     │   │  hierarquia, parágrafos, consolidado,    │
 Codebook master ────┤   │  assinaturas          [pdfplumber]       │
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

 TRANSVERSAIS
   cct/harness.py + avaliar_baseline.py  → métricas vs gabarito (calibração)
   cct/qdc.py / variaveis.py / gabarito.py → leitores dos exports MaxQDA
   cct/comparar.py                        → comparação avulsa de versões
   cct/doctor.py                          → verificação do ambiente
   cct/bench_llm.py                       → avaliação de modelos locais
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
   gabarito humano; a faixa AUTO só existe onde a precisão medida ≥ 0.85.
5. **Offline por omissão** — único tráfego de rede possível: o LLM local
   opcional em 127.0.0.1 (LM Studio).

## Módulos (`cct/`, ~3 000 linhas, 99 testes)
| Módulo | Responsabilidade |
|---|---|
| extractor.py | PDF → estrutura hierárquica com offsets (o módulo mais crítico) |
| schemas.py | contratos de dados (JSON Schema) |
| lexical.py | codificação por termos/condições; níveis cláusula/parágrafo |
| semantico.py | codificação LLM (backend plugável, cache, validação) |
| diacronia.py | alinhamento e classificação =/alteração/nova/removida |
| triagem.py | faixas AUTO/REVER/CONSOLIDADO calibradas |
| qdpx.py | exportador REFI-QDA (árvore de códigos, GUIDs determinísticos) |
| export_xlsx.py | Excel das peritas com contexto |
| qdc.py, variaveis.py, gabarito.py | leitores dos exports do MaxQDA |
| harness.py, avaliar_*.py | métricas contra gabarito |
| localizador.py | localizar convenções em números completos do BTE |
| pipeline_tema.py, comparar.py | orquestradores CLI |
| app.py, doctor.py | interface gráfica e verificação de ambiente |

## Fluxos de dados externos
- **MaxQDA → pipeline**: variáveis (.xlsx), codebook master (.qdc),
  gabaritos de segmentos (.xlsx) — todos exports nativos do MaxQDA.
- **Pipeline → MaxQDA**: projeto .qdpx (REFI-QDA 1.5, importação nativa
  no MaxQDA 2022+). GUIDs determinísticos garantem compatibilidade entre
  exports sucessivos.
- **Pipeline → peritas**: .xlsx autónomo (não requer MaxQDA).
