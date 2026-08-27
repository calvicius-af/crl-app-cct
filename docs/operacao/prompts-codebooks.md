# Criar e melhorar codebooks YAML (novos temas)

Cada tema é um ficheiro YAML em `codebooks/` — **não é preciso
tocar em código**. Este documento tem: (1) o formato, (2) prompts prontos
para gerar o YAML com um LLM, (3) o guia de melhoria com os dados de 2025.

---

## 1. Formato do YAML

```yaml
tema: "4.11 Teletrabalho"            # nome do tema (igual ao MaxQDA)
eixos: ["4.11.1", "4.11.2"]          # códigos-pai: recebem codificação
                                     # sempre que um subcódigo dispara
codigos:
  - id: "4.11.1.1"                   # id numérico igual ao do MaxQDA
    nome: "Acordo de teletrabalho"
    termos: [teletrabalho, trabalho remoto, acordo escrito]
    condicoes:                       # OPCIONAL — trava falsos positivos
      requer_algum: [acordo, escrito]   # a cláusula tem de conter um destes
      excluir: [comissão de teletrabalho] # se contém isto, não codifica
```

Regras práticas:
- `termos` são procurados sem distinção de maiúsculas; um prefixo apanha
  variantes ("candidat" apanha candidato/candidata/candidatura).
- Incluir as variantes morfológicas reais: "registo DE pessoal" E
  "registo DO pessoal" são termos diferentes.
- `condicoes` avaliam-se sobre a cláusula inteira — usar quando um termo é
  ambíguo (ex.: "quotas" só interessa se a cláusula falar de dados).

---

## 2. Prompt para GERAR um codebook novo

Colar num LLM (Claude, Copilot, gemma local), juntando o livro de códigos
do tema (o documento interno com DEFINIÇÃO/INCLUI/EXCLUI/TERMOS DE PESQUISA):

```
Vais converter um livro de códigos de análise qualitativa de convenções
coletivas de trabalho portuguesas num ficheiro YAML de configuração.

FORMATO EXATO (não inventes campos):
tema: "<número e nome do tema>"
eixos: [<lista dos códigos-pai, ex. "4.11.1">]
codigos:
  - id: "<id numérico do subcódigo, ex. 4.11.1.1>"
    nome: "<nome curto>"
    termos: [<termos de pesquisa do livro de códigos, em minúsculas>]
    condicoes:
      requer_algum: [<só se o livro indicar critérios de inclusão que
                      dependam de contexto; senão omitir esta secção>]
      excluir: [<só se o livro indicar exclusões lexicalizáveis>]

REGRAS:
1. Um item em "codigos" por cada subcódigo folha; os eixos agregadores
   vão apenas na lista "eixos".
2. Copia os TERMOS DE PESQUISA do livro de códigos tal como estão; junta
   variantes morfológicas óbvias do português jurídico (singular/plural,
   "de"/"do"/"dos", grafias AO90 e pré-AO90 como "atual"/"actual").
3. Para termos genéricos (uma palavra comum), acrescenta "condicoes:
   requer_algum" com 3-5 palavras que distingam o sentido do tema.
4. Não inventes termos que não estejam no livro de códigos nem nas regras
   acima. Devolve APENAS o YAML.

LIVRO DE CÓDIGOS:
<colar aqui>
```

Guardar o resultado como `codebooks/<numero>_<nome>.yaml` e validar:
`python -m cct.pipeline_tema --pdfs <2-3 PDFs de teste> --codebook <novo>.yaml --out /tmp/teste`

## 3. Prompt para REVER um codebook com feedback das peritas

```
Este é o YAML atual de um tema (abaixo) e uma lista de erros reportados
pelas peritas: falsos positivos (codificado mas não devia) e falsos
negativos (devia e não foi), cada um com o texto da cláusula.

Para cada erro propõe UMA alteração ao YAML: termo a acrescentar, termo a
remover, ou condição requer_algum/excluir a criar — citando o excerto que
a justifica. Não alteres ids nem a estrutura. Devolve o YAML completo
revisto seguido da lista de alterações com justificação.

YAML ATUAL:
<colar>
ERROS REPORTADOS:
<colar linhas do XLSX das peritas ou dos memos>
```

---

## 4. Melhorar termos com os dados de 2025 (mineração da amostra de referência)

Quando existe uma amostra de referência (export do MaxQDA com segmentos codificados à
mão, como o `4_08_ParaClaudeAppCCT.xlsx`), o processo é medido, não
adivinhado. Foi assim que o 4.08.5.1 subiu de F1 0.72 para 0.84.

### Passo 1 — medir a baseline
```
python -m cct.avaliar_baseline --xlsx <amostra-referencia>.xlsx --pdfs data/raw/bte/bte_2025 \
    --codebook codebooks/<tema>.yaml --out results/metricas/baseline_<tema>
```
O `relatorio.txt` mostra precisão/cobertura por subcódigo. Interpretar:
- **cobertura baixa** (muitos FN) → faltam termos → Passo 2;
- **precisão baixa** (muitos FP) → termos genéricos → Passo 3.

### Passo 2 — encontrar termos em falta (FN)
Os segmentos da amostra de referência que o lexical falhou contêm o vocabulário que
falta. Extraí-los e pedir a um LLM que proponha termos:

```
python - <<'FIM'
import json
from pathlib import Path
from cct.referencia import carregar_referencia
prev = json.load(open("results/metricas/baseline_<tema>/previstos.json"))
referencia = carregar_referencia(Path("<amostra-referencia>.xlsx"))
pares = {(p["doc_id"], p["codigo"]) for p in prev}
for g in gab:
    if (g["doc_id"], g["codigo"]) not in pares:
        print(f"[{g['codigo']}] {g['segmento'][:160]}")
FIM
```

Prompt com esse output:
```
Estes são segmentos de convenções coletivas que deviam ter sido apanhados
pelos códigos indicados entre parênteses retos, mas os termos de pesquisa
atuais (lista abaixo) não os encontraram. Para cada código, propõe os
termos ou expressões EXATAS presentes nos segmentos que os apanhariam
(2-4 palavras, tal como aparecem no texto). Ignora segmentos cuja ligação
ao código não seja óbvia.

TERMOS ATUAIS: <colar do YAML>
SEGMENTOS FALHADOS: <colar>
```

### Passo 3 — travar falsos positivos (FP)
Abrir o XLSX de sugestões, filtrar o subcódigo problemático, ler 10-20
segmentos codificados a mais e identificar o padrão (ex.: "quota sindical"
em cláusulas de pagamento). Traduzir o padrão numa condição:
`requer_algum` (palavras do sentido certo) ou `excluir` (expressão do
sentido errado).

### Passo 4 — remedir e fechar
Repetir o Passo 1. Se a precisão de um subcódigo ficar ≥ 0.85 com amostra de referência
suficiente (≥ 2 documentos), passa automaticamente para a faixa AUTO na
corrida seguinte (via `--metricas`). Guardar o YAML no git/backup — o
codebook é o ativo mais valioso do tema.
