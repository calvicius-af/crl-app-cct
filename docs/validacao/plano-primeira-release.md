# Plano de validação da primeira release

Estado: **por executar e aprovar**. Este plano descreve a prova necessária;
uma suite verde ou um QDPX criado não constituem aprovação por si sós.
Preencher para cada ensaio: data, máquina/SO/Python, commit, operador,
comando, resultado esperado/observado, caminho da evidência, problema aberto
e decisão. Guardar evidências institucionais fora do Git, sem dados pessoais
em tickets públicos. Partir de um commit identificado e de uma cópia do corpus
e do registo; usar um `--out` novo por corrida.

## 1. Decisão de âmbito e bloqueios

Antes do selo, a equipa decide quais das capacidades opcionais entram na
primeira entrega: aquisição pela rede, Docling/OCR, camada semântica e
diacronia com versões anteriores. Uma capacidade anunciada como disponível
precisa do respetivo ensaio abaixo; caso contrário, identificá-la como
experimental/desligada na comunicação da release. Não usar como prova de
qualidade as métricas históricas 0,88/0,57: a revisão do gabarito humano
(GitHub #10) e a validação da faixa `AUTO` continuam pendentes.

Bloqueios para anunciar a operação base como validada: falha em qualquer job
obrigatório de CI, corpus real incompleto ou em regressão, documento esperado
ausente do QDPX, texto ou tabela materialmente errado sem solução e revisão,
importação MaxQDA falhada, ou instalação não reproduzida na estação alvo.
Avisos exigem triagem registada por documento; código de saída 0 não os aprova.
Problemas conhecidos devem ter decisão explícita de corrigir, restringir a
capacidade, ou adiar a release.

## 2. Matriz de ambientes

| Ambiente | Obrigatório para a base | Ensaios e evidência |
|---|---|---|
| CI GitHub em PR | Sim | `testes.yml`: pytest Linux/macOS/Windows 3.11/3.12 e Windows 3.13; segurança, referências, Ruff, mypy, pip-audit, docling-core e corpus real estrito. Anotar URLs e commit dos jobs, incluindo skips. |
| Runner Windows 3.13, partilha SMB | Sim | `instalacao-rede.yml` (pode ser iniciado manualmente): preparar pacote com `--incluir-testes`, instalar em `L:\`, `\\localhost\` e `\\NOME\`; guardar os logs. Só simula uma partilha local, não as políticas do CRL. |
| Estação institucional Windows 11, Python 3.13 | Sim | Instalação offline na localização efetiva (unidade mapeada e/ou UNC), app, `doctor`, aquisição simulada, confirmação de siglas, pipeline e importação MaxQDA. Repetir com a conta/permissões normais e proxy bloqueado. |
| Windows em disco local, Python 3.11/3.12 | Sim, pelo CI; ensaio manual se distribuído | Instalação e corrida de fumo com lançador; verificar caminhos, codificação e QDPX. |
| macOS arm64 e/ou Intel, Python 3.11/3.12 | Se distribuído | `AppCCT.command`, Tk, instalação offline para a arquitetura real, corrida e QDPX; Docling arm64 se incluído. O CI não valida a app visual nem o pacote offline para macOS. |
| Linux 3.11/3.12 | Sim, pelo CI; manual se distribuído | CLI, corpus, verificações estáticas; não prometer interface gráfica sem ensaio Tk. |
| MaxQDA 2022+ na versão institucional | Sim | Importar QDPX de Windows real; comparar textos, offsets, árvore, GUIDs e anotações com PDF e Excel. Reabrir e repetir importação de outra corrida. |

## 3. Preparação e verificações automáticas

1. Num checkout limpo do commit candidato, guardar `git rev-parse HEAD` e
   `git status --short`. Verificar os índices e os PDFs necessários, sem os
   versionar. Preparar cópia de segurança do índice, `data/registo/`, corpus,
   `siglas.csv` e resultados humanos antes de migrar ou renomear.
2. No macOS/Linux, criar `.venv` e instalar `requirements.txt` com as
   constraints de `requirements/runtime.txt` e `requirements/dev.txt`. Correr:

   ```bash
   .venv/bin/python -m pytest -q -rs
   .venv/bin/python scripts/verificar_seguranca.py --verboso
   .venv/bin/python scripts/verificar_referencias.py --verboso
   .venv/bin/python -m cct.doctor
   ```

   No PowerShell, substituir `.venv/bin/python` por
   `.\.venv\Scripts\python.exe`. Verificar que o `doctor` mostra esse
   interpretador; a ausência de fontes opcionais não é defeito de instalação.
3. Confirmar o CI do mesmo commit. O job `corpus` obtém PDFs com hashes
   esperados e usa `CCT_CORPUS_OBRIGATORIO=1`: não aceitar uma execução
   ignorada por falta de dados. Localmente, com corpus disponível, executar
   `.venv/bin/python -m cct.corpus obter --pasta <pasta-dos-PDF>` ou, se
   a rede pública estiver autorizada, `obter --rede`, seguido de
   `.venv/bin/python -m cct.corpus medir`. Comparar
   `results/corpus/comparacao.md` com `tests/corpus/referencia.json`;
   não atualizar a referência para encobrir uma regressão.
4. Se se alterou extração ou desempenho, correr
   `.venv/bin/python -m cct.desempenho medir --comparar` no mesmo ambiente
   da referência; registar segundos por página, memória, tamanho do corpus
   e diferenças. A falta de referência aprovada é uma decisão a documentar,
   não um resultado verde.

## 4. Instalação offline e caminhos Windows

1. Na máquina autorizada, preparar
   `python scripts/preparar_pacote_offline.py --alvos win_amd64:313 --incluir-testes`.
   Preservar `vendor/wheels/MANIFESTO.txt`, `manifesto.json`, constraints e
   commit. Copiar o pacote completo com escrita controlada na partilha.
2. Na estação CRL, a partir da **localização real** usada pela equipa,
   executar `scripts\instalar_offline.bat`. Repetir diretamente por UNC se
   esse caminho for usado. Confirmar hashes, `--no-index`, criação do `.venv`,
   permissões de escrita, e executar em PowerShell:

   ```powershell
   .\.venv\Scripts\python.exe -m cct.doctor
   .\.venv\Scripts\python.exe -m pytest -q -rs
   ```

3. Abrir `scripts\AppCCT.bat`, clicar **Verificar instalação** dentro da app
   (prova do subprocesso e UTF-8) e guardar o resultado. Confirmar que o
   Python, o Tk e os caminhos coincidem com a instalação. Repetir a corrida
   com uma pasta de resultados nova em caminho com espaços e acentos, e com
   caminho UNC se este for um modo de uso. Anotar qualquer diferença entre
   o runner SMB e a estação institucional (ISSUE-0009/GitHub #59).

## 5. Aquisição, nomeação e catálogo

1. Com um índice `.xlsx` real em `data/raw/indices/`, fazer simulação sem rede:
   `.\.venv\Scripts\python.exe -m cct.aquisicao --indices data\raw\indices`.
   Verificar número de linhas, famílias, `pedidos de rede: 0`, relatório e
   manifesto. Só autorizar `--confirmar-rede --aplicar` se a recolha pela
   rede fizer parte do âmbito aprovado; conferir URL permitido, hash do PDF,
   registo persistente, ordinal estável e segunda corrida idempotente.
2. Na app, abrir **Confirmar siglas…**, comparar cada sugestão e aviso com
   índice e ato publicado, corrigir e marcar individualmente. Verificar o
   `siglas.csv` local e uma nova simulação. Em CLI, usar `cct.nomeacao
   --siglas siglas.csv` sem `--aplicar` e `--confirmar CHAVE --aplicar` só
   para documento revisto. Testar uma sigla alterada depois de o PDF existir:
   deve produzir `conflito`, preservar o PDF e exigir decisão de migração.
3. Conferir no catálogo e no registo a correspondência 1:1 dos documentos,
   códigos e hashes; distinguir duas convenções com os mesmos outorgantes.
   Não aceitar nome de 63 caracteres cortado sem conferir a fonte. Se houver
   ficheiros de 2026 no esquema ADR-0016, ensaiar a migração
   `cct.nomeacao --migrar --correspondencia <CSV>` sem `--aplicar`, conferir
   todas as referências e só depois aplicar a passagem controlada descrita
   em [RNC §10](../rnc/README.md#10-migração-do-ciclo-anterior).

## 6. Extração, saída e revisão humana

1. Com `--pdfs data/raw/bte/bte_2026/convencoes`, correr
   `cct.pipeline_tema --codebook codebooks/4_08_protecao_dados.yaml
   --out results/runs/2026/<id-da-corrida>` com o Python do `.venv`.
   Contar PDFs de `PRI`, `SPE` e `APU`, comparar com os processados e
   excluídos; uma corrida apontada só para `PRI` não prova o ano todo.
   Confirmar que portarias e adesões ficam fora da análise temática.
2. Abrir `relatorio.txt`, `diagnostico.md`, `manifest.json`, QDPX e XLSX.
   Verificar hashes, parâmetros, commit, contagens, documentos excluídos,
   avisos por documento e ausência de sobrescrita da evidência anterior.
   Regenerar diagnóstico, se preciso, com `-m cct.completude --corrida
   results/runs/2026/<id-da-corrida>`.
3. Conferir PDF, TXT e QDPX página a página numa amostra representativa:
   duas colunas, cabeçalhos, rodapés, assinaturas, ordem de leitura, cláusulas
   por extenso, remissões, texto consolidado e versões anteriores. Nos anexos
   do BTE 31/2026, rever especialmente as tabelas de 380, 384, 385 e 386:
   cada linha, categoria e valor salarial deve coincidir com o PDF.
   Um aviso `nenhum bloco de tabela` ou código de saída 0 não valida valores.
4. Importar o QDPX no MaxQDA da equipa. Comparar todos os documentos
   esperados, os trechos e offsets das anotações, árvore de códigos, textos
   consolidados e Excel. Guardar memos de divergências ancorados no segmento.
   Repetir após correção numa nova corrida; registar aprovação das peritas.
5. Rever e corrigir o gabarito do tema 4.08, recalcular precisão/cobertura,
   examinar falsos positivos e negativos e aprovar explicitamente a faixa
   `AUTO` antes de a usar como resultado fiável (GitHub #10). Sem essa prova,
   operar com revisão humana integral ou delimitar a release.

## 7. Capacidades opcionais e falhas controladas

| Capacidade | Prova se incluída |
|---|---|
| Docling | Instalar separadamente e provisionar modelos com `cct.modelos_docling descarregar` numa máquina autorizada; na estação correr `verificar --pasta`, definir `CCT_DOCLING_MODELOS` e testar sem rede. Comparar texto, tabelas, memória e tempos com pdfplumber; importar o QDPX final no MaxQDA. A validação visual da ISSUE-0003 continua pendente. |
| OCR | Com modelos OCR completos e `CCT_DOCLING_OCR=1`, testar um PDF imagem conhecido e conferir todo o texto; não prometer cobertura de scans pelo extrator base. |
| Semântica | Apenas servidor loopback autorizado; confirmar que está desligada por omissão, sugestões em REVER, ausência de tráfego externo e comportamento sem LM Studio. |
| Diacronia | Incluir último texto completo em `data/raw/textos_consolidados/`; conferir `=`, alteração, nova e removida no Excel e no QDPX. Uma revisão parcial deve gerar aviso, não servir de base completa. |
| Falhas | PDF protegido, corrompido, demasiado grande, timeout Docling, modelo ausente, índice em falta, CSV de siglas ausente e pasta de PDFs vazia devem dar diagnóstico compreensível e preservar os restantes documentos. |

## 8. Fecho

Registar a decisão de cada área (técnica, operação e análise) com referência
às evidências do mesmo commit. Listar os defeitos abertos com impacto,
solução ou restrição de âmbito. Confirmar documentação e instruções de
instalação a partir de uma cópia limpa e só então criar a tag/entrega da
primeira release, mediante instrução explícita de publicação.
