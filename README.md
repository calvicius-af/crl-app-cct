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

Fases 0 a 5 concluídas, **99 testes automáticos** a passar. Em uso real: o corpus de 2025
(89 convenções do tema 4.8, proteção de dados) foi processado e revisto por peritas em
cinco rondas sucessivas.

Qualidade medida contra codificação humana: cobertura 0,88, precisão 0,57 — e a faixa
`AUTO` só existe para códigos com precisão medida ≥ 0,85. Os números, e o que significam,
estão em [docs/validacao/](docs/validacao/README.md).

Por fazer: recolha automática do BTE, numeração de cláusulas por extenso, análise de
remissões entre documentos, prova com um segundo tema. Ver [specs/](specs/README.md) e
[issues/](issues/README.md).

## Instalação

Requer **Python 3.11 ou superior**. Quatro dependências, todas com licença permissiva.

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # Windows: .venv\Scripts\python
.venv/bin/python -m cct.doctor                        # verifica o ambiente, em português
```

Para instalação sem acesso à internet e para o resto dos requisitos de sistema, ver
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
    --out results/2026_4_08
```

Comparar duas versões de uma convenção:

```bash
python -m cct.comparar --pasta data/raw/textos_consolidados/ACIP_FESAHT \
    --out results/comparacoes/ACIP.xlsx
```

O guia de operação completo, com o que fazer quando algo corre mal, está em
[docs/operacao/guia-operacao.md](docs/operacao/guia-operacao.md).

## Estrutura do repositório

```text
cct/            código-fonte da aplicação
tests/          99 testes (pytest) — escritos antes da implementação
codebooks/      os temas de codificação, em YAML: configuração, não código
examples/       dois casos completos, PDF → TXT → QDPX (versionados)
scripts/        lançadores da aplicação gráfica
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
`results/` (saídas), `vendor/` (software de terceiros consultado) e `archive/`
(versões anteriores do projeto). Porquê, e como repor:
[docs/dados/README.md](docs/dados/README.md) e
[ADR-0009](docs/adr/0009-layout-do-repositorio.md).

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

A aplicação corre inteiramente na máquina local. Não faz pedidos de rede, com uma única
exceção opcional: se a camada semântica for ativada, fala com um modelo de linguagem em
`localhost` (por exemplo, LM Studio) — dentro da própria máquina, nunca para o exterior.
O código recusa URLs que não sejam de loopback. Essa camada está desligada por omissão
([ADR-0006](docs/adr/0006-semantica-llm-local-desligada-por-omissao.md),
[ADR-0012](docs/adr/0012-modelos-locais-obrigatorios.md)).

## Licença e citação

Código sob [MIT](LICENSE); documentação sob CC BY 4.0. A titularidade e a licença carecem
de confirmação institucional do CRL antes de qualquer publicação em acesso aberto.
Para citar, ver [CITATION.cff](CITATION.cff).
