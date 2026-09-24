# Docling sem modelos: avaliação da hipótese (2026-09-24)

## Pergunta

A maioria dos PDF do BTE tem texto digital e não precisa de OCR. É possível usar o
Docling sem descarregar modelos, e ganhar com isso o que ele faz melhor do que o
pdfplumber (tabelas e texto rodado)?

## O que foi verificado

Tudo foi medido neste ambiente, sem acesso ao `huggingface.co` (onde estão os
modelos) nem ao BTE. Os ensaios usaram PDF sintéticos (`tests/pdf_sintetico.py`).

| # | Verificação | Resultado |
|---|---|---|
| 1 | Instalar `docling-slim[format-pdf]` (a distribuição modular do Docling, só com o leitor de PDF) | Instala sem PyTorch: `docling-parse`, `docling-core`, `pypdfium2` |
| 2 | Converter um PDF com `DocumentConverter`, OCR e tabelas desligados | **Não funciona.** O pipeline normal de PDF carrega sempre o modelo de layout, que precisa de PyTorch e dos pesos |
| 3 | Usar só o leitor, `docling-parse` | Funciona sem modelos: devolve linhas de texto com coordenadas e as linhas gráficas (as grelhas das tabelas) |
| 4 | Texto rodado 90º numa página sem rotação declarada (o defeito do TINITA e dos CARRISTUR) | pdfplumber: `sagloF`, `oçivreS` (invertido). PDFium e `docling-parse`: `Folgas Serviço Semana 1` (correto) |
| 5 | Peso do Docling completo com modelos locais para Windows e Python 3.13 | 72 pacotes, **222 MB** em wheels (124 MB são o PyTorch sem GPU). O valor de 4 GB em `requirements.txt` é da instalação Linux com CUDA |

## Interpretação

1. **Sem modelos, o Docling é só um leitor de PDF.** O que o tornou melhor nas tabelas
   (reconhecer a estrutura das células) e nos títulos (classificar blocos) vem
   precisamente dos modelos: o de layout e o TableFormer. Sem eles, o `docling-parse`
   dá o mesmo tipo de informação que o pdfplumber: texto e posições.
2. **O texto rodado não precisa do Docling.** O PDFium, que já vem instalado com o
   pdfplumber, lê-o corretamente. É a correção mais barata para a ISSUE-0020 e o #42:
   não acrescenta nenhuma dependência.
3. **O Docling com modelos é menos pesado do que se pensava.** 222 MB de pacotes, mais
   os modelos, que não foi possível medir aqui. Os modelos têm de ser descarregados uma
   vez numa máquina com internet e copiados para a partilha. O Docling lê-os de uma
   pasta local (`artifacts_path`).

## Recomendação

Por ordem, cada passo medido no corpus de regressão (`python -m cct.corpus medir`) antes
de avançar:

1. **Texto rodado.** Feito no mesmo dia, e sem o PDFium: o próprio pdfplumber 0.11 lê
   o texto rodado no sentido certo com `char_dir_rotated`, e o extrator põe as tabelas
   rodadas de pé. O teste `test_extrator_le_bem_o_texto_rodado` deixou de ser `xfail`.
   Nas tabelas rodadas dos CARRISTUR o corpus mostrou que o PDFium não lê texto nenhum,
   o que confirma a escolha.
2. **Docling com modelos numa máquina preparada.** Medir no corpus a completude e as
   tabelas dos dois extratores lado a lado (`medir --extrator docling`). Se ganhar,
   decidir entre instalá-lo nas estações (cerca de 222 MB mais os modelos) ou extrair
   uma vez e distribuir o resultado.
3. **Não seguir** a via «Docling sem modelos»: não traz o que se procurava.

## Limites

1. Os ensaios são sintéticos. A conclusão 1 decorre da arquitetura do Docling e não
   depende dos PDF. As conclusões 2 e 3 precisam de ser confirmadas no corpus real.
2. O tamanho dos modelos e o tempo de conversão por documento ficam por medir: é
   preciso acesso ao `huggingface.co`.
