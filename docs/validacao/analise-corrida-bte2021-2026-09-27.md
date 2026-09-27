# Análise da corrida de 2021, 27-09-2026

Fonte: `manifest.json`, `relatorio.txt` e `diagnostico.md` enviados pela
equipa, relativos à corrida iniciada às 10:25 UTC de 27-09-2026, no commit
`53fd77c`. Não são incluídos no repositório: contêm caminhos locais e
extensos excertos dos documentos. Os PDFs de 2021, 2022 e 2025 da instalação
Mac não estavam acessíveis no ambiente de análise. As observações abaixo
são do diagnóstico automático; não constituem revisão das páginas originais.

## O que está confirmado

1. A corrida usou `--pdfs .../bte_2021` e `--out .../results/corrida`, com
   pdfplumber, sem variáveis MaxQDA, codebook master ou métricas de AUTO.
   O manifesto regista 48 entradas PDF, 48 saídas no QDPX, 8715 nós de
   cláusula e 3168 anotações. A completude classificou 36 PDFs como OK e
   12 como ATENÇÃO; nenhum ficou fora do QDPX. Isso não valida cada nó.
2. Os ficheiros `bte1_2021.pdf` a `bte48_2021.pdf` são **48 números completos
   do boletim**, não 48 convenções individuais. A documentação de dados já
   distingue estes dois tipos de fonte. A mensagem «Convenções processadas:
   48/48» e as contagens por cláusula/anotação são enganadoras neste corpus:
   um número completo contém vários instrumentos, outros textos e notas de
   depósito. A primeira nota não pode fechar o boletim. Isto explica os
   **48 avisos** de texto depois da nota de depósito como efeito do âmbito
   de entrada, sem provar que a ordem interna de cada convenção esteja boa.
3. Dos 86 problemas no manifesto, 28 são grupos de corpos de cláusulas sem
   frase terminada ou sem conteúdo, quatro referem anexos sem tabela, cinco
   são avisos de auditoria de tabelas rodadas e um agrupa os 14 documentos
   com texto consolidado sem subpastas de versões. Como cada ficheiro é um
   boletim inteiro, a atribuição de um anexo e de uma cláusula a uma única
   convenção tem de ser refeita antes de qualquer contagem substantiva.
4. Os relatórios da aquisição já tinham nomes com data, mas `manifest.json`
   era substituído. O pipeline temático reescrevia os quatro artefactos
   principais quando `--out` era reutilizado. Os relatórios de 2025 e 2022
   **não constam dos três anexos**. A sua recuperação depende de uma cópia
   anterior, Time Machine ou outro histórico local; o manifesto de 2021 não
   permite reconstruir os avisos dessas corridas.

## Casos que exigem o PDF antes de concluir

| Ficheiro do boletim | Sinal no diagnóstico | Verificação necessária |
|---|---|---|
| `bte16_2021` | cobertura 98,2%, 2751 palavras em falta, 670 a mais | localizar páginas e verificar se há imagem, grelha ou ordem de leitura que o PDFium e o pdfplumber tratam de modo distinto. |
| `bte6_2021` | cobertura 98,8%, 778 palavras em falta | conferir excertos e páginas; não converter a diferença de motores diretamente em perda confirmada. |
| `bte23_2021` | três trechos classificados como invertidos e avisos de tabelas altas nas páginas 18, 63, 64 e 86 | visualizar a orientação e comparar cada célula com o PDF. |
| `bte15_2021`, `bte11_2021`, `bte29_2021`, `bte33_2021`, `bte36_2021` | ordem de palavras inferior a 97% em pelo menos um caso; `bte15` tem 92,9% | localizar os blocos e comparar sequência de colunas e tabelas no PDF. |
| `bte13_2021`, `bte43_2021` | uma linha longa sinalizada em cada | conferir se são tabelas colapsadas ou linhas legítimas. |

O aviso de «tabelas em imagem» em páginas dispersas não demonstra, por si,
que as tabelas salariais do anexo indicado estejam nessas páginas. O
diagnóstico percorreu um boletim completo como se fosse um documento único.
Priorizar revisão visual dos segmentos sinalizados e, depois, repetir a
medição sobre PDFs individuais das convenções.

## Intervenção e critérios de aceitação

1. `cct.pipeline_tema` recusa nomes `bte<N>_<ANO>.pdf` e explica que é
   preciso um PDF por convenção. Não produzir QDPX temático ou métricas
   sobre um boletim inteiro. O boletim continua útil como fonte para o
   `cct.localizador` e como prova de publicação.
2. A primeira corrida continua a usar o `--out` escolhido. Se já houver
   manifesto, relatório, diagnóstico ou QDPX nessa pasta, uma nova corrida
   cria uma subpasta identificada por ano e instante UTC. Não move nem apaga
   a evidência anterior. O caminho efetivo aparece no log e em «Abrir
   resultados». As corridas de 2025, 2022 e 2021 futuras devem ter
   `manifest.json`, `relatorio.txt` e `diagnostico.md` separados.
3. A aquisição permite `--refazer-descarga` apenas com
   `--confirmar-rede --aplicar`, ou pelo botão «Descarregar de novo…» com
   confirmação explícita. Pede a cópia completa mesmo quando a versão
   intermédia está válida. Mantém registo e ordinais; se o conteúdo remoto
   divergir da cópia final já nomeada, esta não é substituída silenciosamente.
   Cada relatório de aquisição passa a ter um manifesto com o mesmo selo;
   `manifest.json` na raiz continua a apontar à última aquisição.
   Antes de registar os bytes, abre cada resposta com PDFium: uma resposta
   começada por `%PDF` mas cortada é repetida e, se continuar inválida,
   falha sem substituir a cópia anterior. O hash, isoladamente, não
   demonstrava que o PDF pudesse ser aberto.
4. Testar os dois percursos no Mac da equipa com uma **cópia** do índice,
   registo e PDFs: primeiro apagar apenas a cópia final e confirmar que a
   aquisição a repõe a partir de `data/interim/recolha/` com zero pedidos;
   depois pedir «Descarregar de novo…» e confirmar pedidos e hashes. Não
   apagar `data/registo/registo_bte.jsonl`. Guardar os relatórios antes e
   depois, anotando qualquer `conflito`.
5. Para análise temática, obter PDFs individuais das convenções dos anos
   pretendidos e verificar o inventário por ano, âmbito e família antes da
   corrida. Se não houver índice para 2021, a extração individual desse ano
   requer um procedimento de segmentação e conferência humana ainda por
   definir; não inferir 48 convenções a partir dos 48 boletins.

Falta executar o confronto página a página dos PDFs históricos, a medição
separada de 2025 e 2022 e o gate da app no Mac. A implementação e os testes
automatizados nesta mudança cobrem o comportamento de preservação,
repetição explícita da descarga e recusa de boletins completos.
