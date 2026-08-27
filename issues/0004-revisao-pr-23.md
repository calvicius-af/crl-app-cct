# ISSUE-0004: correções exigidas pela revisão do PR #23

- **Estado:** Resolvida (2026-08-26) — segunda revisão aprovada; merge autorizado
- **Data:** 2026-08-26
- **GitHub:** PR #23
- **Onde dói:** `tests/test_extractor_docling.py`, `cct/extractor_docling.py`,
  `tests/test_qdpx_espacamento.py`, descrição do PR

## Decisão da revisão

O PR #23, **«Extrator docling opcional, ordem de leitura e controlos de
sanidade»**, não deve ser integrado no estado revisto em 2026-08-26.

Há dois defeitos que bloqueiam a aprovação:

1. os quatro jobs obrigatórios do GitHub Actions falham porque testes da
   geometria importam uma dependência que o próprio PR declara opcional;
2. a leitura da grelha do Docling elimina repetições de `colspan`, mas não
   elimina repetições de `rowspan`, apesar de prometer uma célula por span.

Há ainda uma lacuna na prova dos offsets QDPX: o teste novo só cobre uma
seleção situada entre pontos de espaçamento. Não cobre seleções que atravessam
linhas em branco introduzidas pelo exportador, caso que ocorre na corrida real.

## Evidência recolhida

### Testes automáticos

- GitHub Actions, matriz Ubuntu/macOS × Python 3.11/3.12: **4/4 jobs
  falhados**;
- resultado de cada job: **129 passaram, 13 ignorados, 4 falharam**;
- causa comum: `ModuleNotFoundError: No module named 'docling_core'` em
  `tests/test_extractor_docling.py::_bbox`;
- ambiente local Python 3.14 com Docling 2.121.0 instalado: **145 passaram,
  1 ignorado**;
- conjunto focado nas alterações do PR: **47 passaram**;
- `compileall`, `git diff --check` e verificação de anonimização: passaram.

O verde local não invalida o vermelho do CI: localmente a dependência opcional
estava instalada e, por isso, escondia o defeito da instalação normal.

### Corrida funcional sobre as quatro convenções

A corrida foi repetida com o extrator Docling sobre:

- LAGOSemFORMA;
- Águas do Norte;
- Águas da Serra da Estrela;
- TRATOLIXO.

Resultado:

| Documento | Cláusulas | Anotações |
|---|---:|---:|
| LAGOSemFORMA | 62 | 26 |
| Águas do Norte | 73 | 53 |
| Águas da Serra da Estrela | 62 | 34 |
| TRATOLIXO | 103 | 90 |
| **Total** | **300** | **203** |

As quatro convenções foram processadas. Reproduziu-se apenas o aviso já
conhecido da cláusula 76.ª do TRATOLIXO, cujo corpo termina sem ponto no PDF.

O QDPX resultante contém quatro fontes e 203 seleções, todas não vazias e com
offsets dentro dos limites. Não contém `####` e é textualmente igual à corrida
guardada em `results/2025_4_08_docling_v5/`. A descrição do PR refere 205
seleções; essa contagem não foi reproduzida e deve ser corrigida para 203 ou
justificada com inputs diferentes.

### Reprodução do `rowspan`

A propriedade `TableData.grid` do Docling repete a mesma célula em todas as
linhas e colunas abrangidas pelo span. O código atual só consulta
`start_col_offset_idx`.

```bash
.venv/bin/python - <<'PY'
from types import SimpleNamespace
from docling_core.types.doc import TableCell, TableData
from cct.extractor_docling import _linhas_de_tabela

def cell(texto, ri, rf, ci, cf):
    return TableCell(
        text=texto,
        row_span=rf-ri, col_span=cf-ci,
        start_row_offset_idx=ri, end_row_offset_idx=rf,
        start_col_offset_idx=ci, end_col_offset_idx=cf,
    )

tabela = SimpleNamespace(data=TableData(
    table_cells=[
        cell("Categoria", 0, 2, 0, 1),
        cell("A", 0, 1, 1, 2),
        cell("B", 1, 2, 1, 2),
    ],
    num_rows=2, num_cols=2,
))
print(_linhas_de_tabela(tabela))
PY
```

Resultado atual:

```text
['Categoria | A', 'Categoria | B']
```

`Categoria` é uma única célula com `rowspan=2`, mas é emitida duas vezes.

### Limite da prova dos offsets

O teste `test_offsets_exportados_recortam_o_mesmo_trecho` seleciona apenas um
parágrafo que não contém nenhum ponto de espaçamento. Isso prova o deslocamento
dos extremos, mas não uma seleção que atravesse uma tabela, uma cláusula ou
vários nós consolidados.

Na corrida real, **38 das 203 seleções** não são literalmente iguais ao
segmento canónico apresentado no XLSX porque incluem linhas em branco inseridas
dentro da seleção. Removendo apenas essas linhas introduzidas pelo exportador,
as 38 voltam a coincidir; não foi encontrada inclusão de texto alheio nem
deslocamento dos extremos.

Assim, o comportamento parece semanticamente correto, mas a afirmação «cada
seleção recorta exatamente o mesmo trecho» e o teste atual são mais fortes do
que a implementação realmente garante.

## Plano de correção para o próximo agente

Executar pela ordem seguinte, mantendo cada passo pequeno e testável.

### 1. Desbloquear o CI sem tornar o Docling obrigatório

1. Remover de `_bbox`, em `tests/test_extractor_docling.py`, a importação
   incondicional de `docling_core`.
2. Manter os quatro testes de ordenação ativos numa instalação normal; não os
   esconder simplesmente com `importorskip`.
3. Preferir um objeto de teste ou uma pequena refatoração que permita testar as
   duas origens de coordenadas sem instalar os cerca de 4 GB do Docling.
4. Se for necessária uma prova de integração com os tipos reais, colocá-la num
   teste separado, marcado como opcional, e acrescentar um job específico que
   instale Docling. O job normal deve continuar leve.

### 2. Corrigir `rowspan` sem voltar a partir `colspan`

1. Fazer a conversão da tabela conhecer o índice da linha atual.
2. Emitir uma célula apenas na sua posição inicial, considerando em conjunto
   `start_row_offset_idx` e `start_col_offset_idx`.
3. Decidir explicitamente como representar, nas linhas seguintes, o espaço
   ocupado por um `rowspan` — vazio ou omitido — sem deslocar de forma ambígua
   as restantes colunas no texto separado por ` | `.
4. Acrescentar testes para:
   - `colspan`;
   - `rowspan`;
   - span simultaneamente vertical e horizontal;
   - células genuinamente iguais em posições distintas;
   - células vazias e preservação da ordem das restantes colunas.

### 3. Fixar o contrato dos offsets QDPX

Manter o espaçamento, mas documentar e testar o contrato correto:

- os extremos remapeados devem apontar para o mesmo intervalo semântico;
- dentro desse intervalo podem existir apenas as quebras de linha que o próprio
  exportador introduziu;
- removendo exatamente essas inserções, o trecho exportado tem de ser igual ao
  trecho canónico, carácter por carácter.

Acrescentar pelo menos:

1. uma seleção de cláusula que contenha uma tabela;
2. uma seleção que atravesse a fronteira entre dois nós espaçados;
3. uma seleção consolidada que contenha vários pontos de inserção;
4. casos em que o início ou o fim coincide exatamente com um ponto de inserção.

Não normalizar whitespace indiscriminadamente no teste: isso poderia esconder
perda ou alteração real de espaços. A comparação deve remover apenas as
inserções calculadas por `pontos_de_espacamento`.

### 4. Repetir os gates e atualizar o PR

1. Executar a suite numa instalação criada apenas a partir de
   `requirements.txt`, sem Docling.
2. Executar a suite no ambiente com Docling.
3. Repetir o teste sintético de spans.
4. Repetir a corrida das quatro convenções e validar ZIP, XML, fontes, offsets,
   seleções vazias, `####` e relatório de sanidade.
5. Atualizar a descrição do PR com os resultados efetivamente reproduzidos,
   incluindo a contagem correta de seleções.
6. Só pedir nova revisão quando os quatro checks obrigatórios do GitHub Actions
   estiverem verdes.

## Resolução (2026-08-26)

Aplicada pela ordem do plano, commit `6dab6d5`.

### 1. CI desbloqueado sem tornar o Docling obrigatório

O `CoordOrigin` do docling é um enum de strings, por isso `distancia_ao_topo`
passou a comparar pelo **nome** (`ORIGEM_INFERIOR`) em vez de importar
`docling_core`. Com isso, nem o extrator nem os testes arrastam a dependência
opcional. Os quatro testes de ordenação continuam ativos na suite normal, agora
com objetos de teste, e ganharam cobertura das **duas** origens de coordenadas
(`test_distancia_ao_topo_nas_duas_origens`) e do caso de coluna única.

A prova com os tipos reais ficou em `tests/test_docling_integracao.py`, que se
ignora sozinho via `importorskip`. Foi acrescentado o job `tipos docling` ao
workflow: instala apenas `docling-core` (~30 pacotes, **sem PyTorch**) e corre a
suite completa. O job normal continua leve.

### 2. `rowspan` corrigido sem partir `colspan`

`celulas_sem_colspan` deu lugar a `celulas_da_linha(linha, indice_linha)`, que
emite cada célula apenas na sua posição inicial, considerando
`start_row_offset_idx` e `start_col_offset_idx` em conjunto.

Representação decidida e documentada: a continuação **horizontal** é omitida (as
colunas seguintes trazem o resto da linha) e a continuação **vertical** sai como
célula vazia. Assim as linhas de uma tabela com spans emitem todas o mesmo
número de células e nenhuma coluna desliza — há uma asserção explícita disso em
`test_span_misto_emitido_uma_vez`.

O caso da revisão passa a dar `['Categoria | A', ' | B']`.

### 3. Contrato dos offsets fixado

Acrescentado `indices_inseridos(pontos)`: a k-ésima inserção fica no índice
`pontos[k] + k`. É esta lista que define o contrato, agora documentado em
`exportar_qdpx` — os extremos apontam para o mesmo intervalo semântico e, dentro
dele, só podem existir as quebras que o exportador inseriu; removendo
exatamente esses índices, obtém-se o trecho canónico carácter por carácter, sem
normalizar espaço nenhum.

O teste de gate do round-trip deixou de exigir igualdade literal e passou a
verificar o contrato. Em `tests/test_qdpx_espacamento.py` entraram os quatro
casos pedidos: seleção de cláusula que contém tabela, travessia da fronteira
entre dois nós espaçados, seleção com três pontos de inserção, e extremos
(início e fim) coincidentes com pontos de inserção.

## Verificação dos gates

| Ambiente | Resultado |
|---|---|
| CI — 4 jobs obrigatórios (Ubuntu/macOS × 3.11/3.12) | 147 passaram, 14 ignorados — **verdes** |
| CI — job `tipos docling` (`docling-core`) | 151 passaram, 13 ignorados — **verde** |
| Local sem docling (venv só de `requirements.txt`, 3.11) | 159 passaram, 2 ignorados |
| Local com docling 2.121.0 (3.14) | 163 passaram, 1 ignorado |

A diferença de 4 testes entre os dois jobs do CI é exatamente o ficheiro de
integração opcional.

Corrida das quatro convenções (`results/validated/2025_4_08_issue0004/`): 4/4, **300
cláusulas e 203 anotações**, reproduzindo as contagens da revisão. QDPX com ZIP
e XML válidos, 4 fontes, 203 seleções, 0 vazias, 0 fora de limites, 0 cardinais
de Markdown, 36 códigos e todos os `CodeRef` a resolver. Único aviso de
sanidade: a cláusula 76.ª do TRATOLIXO, fora do âmbito.

Contrato na corrida real: 161 seleções literalmente iguais, 42 equivalentes,
**0 violações**. A revisão contou 38 equivalentes; a diferença são as tabelas
com `rowspan`, cujo texto mudou com a correção — o cabeçalho «Níveis» do
AguasNorte deixou de ser repetido na segunda linha.

A descrição do PR #23 foi corrigida de 205 para **203** seleções e atualizada
com todas as contagens acima.

## Critérios de aceitação

- [x] GitHub Actions verde em Ubuntu/macOS e Python 3.11/3.12.
- [x] A suite normal não instala nem importa Docling ou `docling_core`.
- [x] Os testes de geometria continuam ativos na suite normal.
- [x] Uma célula com `rowspan` é emitida uma única vez.
- [x] `colspan`, spans mistos, repetições legítimas e células vazias têm testes.
- [x] Há testes de offsets com inserções dentro e nas fronteiras da seleção.
- [x] O contrato de equivalência das seleções está documentado sem prometer
      igualdade literal incompatível com o espaçamento acrescentado.
- [x] A corrida real termina 4/4 e todas as seleções permanecem válidas.
- [x] A descrição do PR coincide com as contagens reproduzidas.

## Fora do âmbito desta correção

- confirmar visualmente a importação no MaxQDA continua a pertencer à
  ISSUE-0003;
- alterar o extrator por omissão (`pdfplumber`);
- tornar Docling uma dependência obrigatória;
- corrigir o aviso legítimo da cláusula 76.ª do TRATOLIXO.

## Segunda revisão e aceitação (2026-08-26)

A correção foi revista de forma independente contra o plano acima. Não foram
encontrados defeitos P0, P1 ou P2 e o PR foi aprovado para integração.

Evidência final reproduzida:

- os cinco checks do GitHub ficaram verdes: 147 testes passaram e 14 foram
  ignorados na matriz normal; 151 passaram e 13 foram ignorados no job com os
  tipos reais do Docling;
- localmente, passaram 163 testes com Docling e 159 numa instalação criada
  apenas com `requirements.txt`; o conjunto focado passou 43 testes;
- o remapeamento dos offsets foi ainda exercitado exaustivamente sobre os
  pontos de inserção, sem violações do contrato;
- as quatro convenções reais produziram 300 cláusulas e 203 anotações; o único
  aviso foi o já conhecido da cláusula 76.ª do TRATOLIXO;
- o QDPX validou contra o XSD, contém quatro fontes, GUIDs únicos, `CodeRef`
  resolvidos, nenhuma seleção vazia ou fora dos limites e nenhum `####`;
- das 203 seleções, 161 são literalmente iguais e 42 equivalentes depois de
  remover exatamente as quebras introduzidas pelo exportador: zero violações;
- o comando de diagnóstico e a ajuda funcionam sem Docling; compilação e
  verificação de anonimização passaram.

Foi corrigida durante esta documentação uma linha em branco excedente no fim
do ficheiro, única observação P3 da segunda revisão. A prevenção automática de
erros equivalentes ficou incluída no programa de qualidade #24. A validação
visual no MaxQDA continua deliberadamente aberta na ISSUE-0003 / GitHub #31.
