# AppCCT — pré-codificação de convenções coletivas para o MaxQDA

Aplicação local do **Centro de Relações Laborais** que pega nas convenções coletivas
publicadas no *Boletim do Trabalho e Emprego*, extrai o texto com a estrutura preservada,
sugere a codificação temática das cláusulas, compara cada convenção com a sua versão
anterior, e entrega um projeto pronto a abrir no **MaxQDA**.

O objetivo não é substituir a análise humana. É evitar que, num corpus de quase três
centenas de convenções por ano, alguma coisa passe despercebida — e poupar às analistas o
trabalho mecânico de localizar, no meio de centenas de páginas, as cláusulas que
interessam a cada tema.

**Ver a funcionar em dois minutos:** [`examples/`](examples/README.md) tem artefactos de
dois casos reais — texto extraído, projeto MaxQDA e instruções para obter os PDFs de origem.

## O que faz, em quatro passos

```
PDF do BTE  →  1. EXTRAÇÃO      texto + estrutura (capítulo, cláusula, número, alínea)
            →  2. CODIFICAÇÃO   codebook do tema → cláusulas candidatas
            →  3. DIACRONIA     o que mudou face à versão anterior
            →  4. TRIAGEM       AUTO / REVER / CONSOLIDADO
                                → projeto.qdpx (MaxQDA) + sugestoes_peritas.xlsx
```

Detalhe em [docs/arquitetura/arquitetura.md](docs/arquitetura/arquitetura.md).

## Estado

Fases 0 a 5 concluídas, com uma suite automática executada no CI em Linux e macOS,
Python 3.11 e 3.12. Em uso real: o corpus de 2025
(89 convenções do tema 4.8, proteção de dados) foi processado e revisto por peritas em
cinco rondas sucessivas.

Qualidade medida contra codificação humana: cobertura 0,88, precisão 0,57 — e a faixa
`AUTO` só existe para códigos com precisão medida ≥ 0,85. Os números, e o que significam,
estão em [docs/validacao/](docs/validacao/README.md).

Por fazer: recolha automática do BTE, numeração de cláusulas por extenso, análise de
remissões entre documentos, prova com um segundo tema. Ver [specs/](specs/README.md) e
[issues/](issues/README.md).

## Instalação

Requer **Python 3.11 ou superior**. A instalação base tem quatro dependências diretas,
todas com licença permissiva. O extrator Docling é opcional e significativamente mais
pesado.

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # Windows: .venv\Scripts\python
.venv/bin/python -m cct.doctor                        # verifica o ambiente, em português
```

**Em rede fechada** (o caso das estações do CRL, onde o proxy bloqueia o pip): as
bibliotecas preparam-se uma vez numa máquina com acesso e instalam-se sem qualquer pedido
de rede.

```bash
python scripts/preparar_pacote_offline.py   # máquina com internet, uma vez
scripts/instalar_offline.bat                # em cada estação (macOS: .command)
```

O procedimento completo, incluindo o que fazer quando falha, está em
[docs/institucional/instalacao-offline.md](docs/institucional/instalacao-offline.md). O
resto dos requisitos de sistema está em
[docs/institucional/requisitos-tecnicos.md](docs/institucional/requisitos-tecnicos.md).

## Utilização

**Com interface gráfica** (a via normal): duplo clique em `scripts/AppCCT.command`
(macOS) ou `scripts/AppCCT.bat` (Windows). Os campos aparecem pré-preenchidos; basta
carregar em *Correr pipeline*.

**Por linha de comandos** — a corrida completa de um tema:

```bash
python -m cct.pipeline_tema \
    --pdfs data/raw/bte/bte_2026 \
    --codebook codebooks/4_08_protecao_dados.yaml \
    --pasta-versoes data/raw/textos_consolidados \
    --out results/runs/2026/2026_4_08
```

Cada corrida cria também `manifest.json`, com o comando, commit, versões, hashes dos
inputs/outputs, contagens e problemas encontrados.

Comparar duas versões de uma convenção:

```bash
python -m cct.comparar --pasta data/raw/textos_consolidados/ACIP_FESAHT \
    --out results/benchmarks/tema-4.08/comparacoes/ACIP.xlsx
```

O guia de operação completo, com o que fazer quando algo corre mal, está em
[docs/operacao/guia-operacao.md](docs/operacao/guia-operacao.md).

## Estrutura do repositório

```text
cct/            código-fonte da aplicação
tests/          testes pytest: unidade, integração, corpus e formatos
codebooks/      os temas de codificação, em YAML: configuração, não código
examples/       dois casos completos, PDF → TXT → QDPX (versionados)
scripts/        lançadores da aplicação gráfica e instalação offline
docs/
  arquitetura/  como o sistema funciona
  adr/          porque é assim — registo das decisões tomadas
  operacao/     como se opera, e como se escrevem codebooks
  validacao/    os gates, os memos das peritas, as métricas
  dados/        de onde vêm os dados e como repor
  institucional/ requisitos técnicos e proposta ao Instituto de Informática
  research/     estudos preparatórios (AKN4EU, ELI, FRBR, REFI-QDA)
  formacao/     material de formação
specs/          o que se vai construir a seguir
issues/         o que está partido ou em falta
```

Não versionadas, mas presentes numa instalação de trabalho: `data/` (fontes),
`results/` (saídas), `vendor/` (bibliotecas para instalação offline e software
de terceiros consultado) e `archive/`
(versões anteriores do projeto). Porquê, e como repor:
[docs/dados/README.md](docs/dados/README.md) e
[ADR-0009](docs/adr/0009-layout-do-repositorio.md). O ciclo de vida de fontes, caches,
corridas e resultados humanos está em
[organização do workspace](docs/dados/organizacao-workspace.md).

## Regras que não se quebram

Três invariantes sustentam tudo o resto. Estão cobertas por testes, mas convém saber
porquê antes de mexer:

1. **Texto-fonte em UTF-8 sem BOM, quebras LF.** Os offsets das codificações contam
   caracteres sobre esse texto exato — um BOM desalinha todas as marcações.
2. **Zero perda de texto.** Concatenar os nós de um `doc.json` reconstrói integralmente o
   `.txt`, carácter a carácter.
3. **O pipeline não conhece temas.** Um tema novo é um ficheiro YAML em `codebooks/`,
   nunca uma alteração ao código.

## Privacidade e funcionamento offline

A aplicação corre localmente. A instalação base não faz pedidos de rede em operação. Há
duas exceções opcionais a preparar antes de usar numa rede fechada: o Docling pode
descarregar modelos na primeira execução, e a camada semântica, se ativada, fala com um
modelo de linguagem em
`localhost` (por exemplo, LM Studio) — dentro da própria máquina, nunca para o exterior.
Os modelos do Docling podem ser pré-instalados para funcionamento offline. O código da
camada semântica recusa URLs que não sejam de loopback e essa camada está desligada por omissão
([ADR-0006](docs/adr/0006-semantica-llm-local-desligada-por-omissao.md),
[ADR-0012](docs/adr/0012-modelos-locais-obrigatorios.md)).

## Licença e citação

Trabalho pessoal de António Fula, oferecido para uso do CRL sem lhe atribuir a
titularidade. Dedicado ao domínio público — ver [LICENSE](LICENSE): pode ser usado,
copiado, modificado e distribuído por qualquer pessoa ou entidade, para qualquer fim,
sem restrições e sem necessidade de atribuição. Citação disponível, mas opcional, em
[CITATION.cff](CITATION.cff).
