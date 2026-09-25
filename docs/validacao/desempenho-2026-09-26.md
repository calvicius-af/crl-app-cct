# Desempenho dos extratores: baseline e orçamento (2026-09-26)

## Contexto

O #26 pedia uma baseline de desempenho reproduzível e limites que tornem uma regressão
visível. Até aqui havia só a estimativa do PR #23 (1 a 1,7 s por página no docling).

## Como se mede

`python -m cct.desempenho medir [--extrator docling]` sobre os 14 PDF do corpus de
regressão (BTE 31/2026, 159 páginas). Cada PDF corre num subprocesso novo, para que a
memória e as caches de um não contem no seguinte, e mede-se:

- **arranque:** importar o extrator;
- **a frio:** a primeira extração do PDF. No docling inclui o carregamento dos modelos a
  partir da cache local; sem rede (`HF_HUB_OFFLINE=1`) não há descarga, e o tempo de
  descarga fica de fora;
- **a quente:** a mesma extração, logo a seguir, no mesmo processo;
- **memória máxima:** o RSS máximo do subprocesso.

## Ambiente

macOS 27.0, arm64, 10 núcleos, Python 3.11.16. pdfplumber 0.11.10, pdfminer.six
20260107, pypdfium2 5.13.0, docling 2.128.0. Commit `7960395`.

## Resultados

| Extrator | s/página a quente | s/página a frio | Arranque | Memória máxima | Total a frio |
|---|---|---|---|---|---|
| pdfplumber | 0,19 | 0,19 | 0,05 s | 305 MB | 30 s |
| docling | 1,75 | 2,75 | 0,12 s | 4360 MB | 7 min |

Três medidas seguidas do pdfplumber variam menos de 1% (0,1913 a 0,1926 s/página): a
tolerância de 15% deixa folga ao ruído da máquina e apanha uma regressão a sério.

Por documento, o custo acompanha o número de páginas no pdfplumber (0,12 s no 378, com 2
páginas; 7,6 s no 382, com 35). No docling, o carregamento dos modelos custa cerca de 10
s por processo, e as páginas deitadas dos CARRISTUR custam cerca de 4 s cada, mais do
dobro das outras.

## Orçamento proposto (por aprovar)

| Extrator | s/página | Memória máxima |
|---|---|---|
| pdfplumber | 0,5 | 600 MB |
| docling | 4,5 | 8000 MB |

Cerca de 2,5 vezes a referência medida acima, para caber numa máquina do CI ou numa estação
mais lenta. O orçamento é absoluto e vale em qualquer ambiente; a referência + 15% vale
só no ambiente em que foi medida.

## Gate

- `python -m cct.desempenho medir --comparar` sai com 1 acima da referência + 15% ou do
  orçamento. Sem referência para o ambiente, só verifica o orçamento e diz como a criar.
- O workflow `Desempenho` (`.github/workflows/desempenho.yml`) corre-o todas as segundas-
  feiras sobre o corpus, só com o pdfplumber, e guarda as medidas como artefacto. Não
  corre em cada PR: os tempos de uma máquina partilhada variam demasiado para bloquear
  um PR.
- As contagens e o contrato QDPX continuam guardados pelo corpus de regressão, que corre
  em cada PR: uma otimização que os mude falha lá.

## O que fica

1. **Aprovar o orçamento.** Os valores acima são uma proposta.
2. **Referência do CI:** a primeira corrida do workflow dá as medidas de `linux-x86_64`,
   que se juntam à referência (artefacto `desempenho`).
3. **PDF com OCR.** O corpus só tem PDF com camada de texto, e o extrator clássico não faz
   OCR. Medir OCR precisa de um PDF digitalizado autorizado, que o corpus não tem.
