# Docling isolado e limitado (2026-09-26)

## Contexto

O #25 pedia que a execução do docling fosse offline, verificável e limitada: modelos
com proveniência, nenhum conteúdo enviado para fora, limites de tamanho, páginas e
tempo, e erros claros para PDF malformados, protegidos ou excessivos.

## O que ficou

| Pedido | Como | Teste |
|---|---|---|
| Hosts, artefactos, versões e checksums dos modelos | `python -m cct.modelos_docling inventariar` escreve `manifesto_modelos.json`, com a versão do docling e o caminho, o tamanho e o SHA-256 de cada ficheiro. Origem: `huggingface.co/docling-project` (revisão fixada pela versão do docling); o RapidOCR, a do pacote `rapidocr` | `test_manifesto_dos_modelos_apanha_ficheiros_alterados_em_falta_e_a_mais` |
| Prefetch e instalação offline verificável | `descarregar --destino` numa máquina com rede; `verificar --pasta` na estação, que falha se um ficheiro faltar, mudar ou sobrar | idem |
| Nenhum conteúdo enviado durante a extração | `enable_remote_services=False` e `allow_external_plugins=False` sempre; com `CCT_DOCLING_MODELOS`, o docling lê os modelos da pasta em modo offline (`HF_HUB_OFFLINE`) | `test_conversao_com_modelos_locais_nao_usa_a_rede`: converte com `socket.connect` bloqueado |
| Limites de tamanho, páginas e tempo | `cct/limites.py`: até 100 MB e 500 páginas (`CCT_MAX_MB`, `CCT_MAX_PAGINAS`), verificados com o PDFium antes de qualquer extrator; no docling, 900 s por documento (`CCT_DOCLING_TEMPO_MAX_S`), e uma conversão parcial é um erro | `test_pdf_com_paginas_ou_tamanho_a_mais`, `test_opcoes_do_docling_sem_servicos_remotos_e_com_tempo_maximo` |
| PDF malformado ou protegido | erro com o que fazer, antes de extrair; no pipeline, o documento fica fora do QDPX e a corrida continua | `test_pdf_corrompido_recusado_com_o_que_fazer`, `test_pdf_protegido_por_palavra_passe` |

## O OCR na via offline

O primeiro ensaio com a rede bloqueada falhou, e por uma razão que importa: o OCR
automático do docling escolhe o motor pelo que está instalado, não pelo que está na pasta
dos modelos. Sem o `onnxruntime`, escolhia o RapidOCR com PyTorch, cujos modelos não
estavam completos na pasta, e tentava ir buscá-los à rede. Na via offline, o OCR fica
desligado, e liga-se com `CCT_DOCLING_OCR=1` quando os modelos do OCR estiverem
completos.

Medido nos 14 PDF do corpus de regressão: o docling por omissão (com OCR) e o docling
offline (sem OCR) dão exatamente a mesma cobertura, as mesmas palavras a mais e os mesmos
nós em todos os documentos. Os PDF do BTE têm texto, e o OCR não acrescenta nada.

## Decisões

1. **Sem um subprocesso por documento.** O docling carrega os modelos em cerca de 10 s
   por processo (#26). Isolar cada documento custaria 10 s × documentos, e o limite de
   tempo por documento já existe dentro do docling (`document_timeout`), que termina a
   conversão de forma controlada. A extração não cria processos nem ficheiros temporários
   próprios que possam ficar órfãos.
2. **Sem limite de memória imposto.** O pico medido é de 4,4 GB (#26). Um limite do
   sistema (`RLIMIT_AS`) só existe no Linux, e as estações são Windows. O orçamento de
   memória fica no gate de desempenho do #26.
