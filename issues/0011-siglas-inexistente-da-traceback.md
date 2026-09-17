# ISSUE-0011: `--siglas` com ficheiro inexistente dá traceback em vez de mensagem

- **Estado:** Aberta
- **Data:** 2026-09-17
- **GitHub:** #62 (sub-issue de #58)
- **Onde dói:** `cct/nomeacao.py` (`carregar_siglas`, L399-417; `main`, L615-617)

## O que acontece

Na estação, a seguir a uma recolha que deixou sete siglas por confirmar, a nomeação
sugere corrigir com `--siglas`. Duas tentativas, dois *tracebacks*:

```
PS C:\...> .venv\Scripts\python.exe -m cct.nomeacao --destino data\raw\bte --siglas siglas.csv --aplicar
Traceback (most recent call last):
  ...
  File "...\cct\nomeacao.py", line 417, in carregar_siglas
    with open(caminho, encoding="utf-8-sig", newline="") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'siglas.csv'
```

E o mesmo com `--siglas siglas.exemplo.csv`.

Duas coisas correram mal aqui, e só uma é defeito de código.

**O defeito.** `carregar_siglas` abre o ficheiro (L417) sem verificar que existe, e `main`
chama-a (L615-617) sem capturar a excepção. O resultado é um *traceback* de seis linhas,
em inglês, que expõe caminhos internos. Todo o resto do projeto trata erros de utilizador
com mensagem em português e uma seta a dizer o que fazer — este caminho escapou ao padrão.

**O que não é defeito, mas confundiu.** O `siglas.csv` não existe no repositório de
propósito: é conhecimento da equipa, criado localmente, como está documentado em
`docs/dados/README.md:177-188`. O modelo existe e está versionado, em
`docs/operacao/siglas.exemplo.csv`. A segunda tentativa falhou porque esse modelo está em
`docs/operacao/` e não na raiz do projeto, que era de onde o comando corria.

## O que devia acontecer

Uma mensagem no formato do resto do projeto, a dizer que o ficheiro não existe, que não
vem no repositório, e onde está o modelo para copiar. Por exemplo:

```
PAROU AQUI: não encontrei o ficheiro de siglas 'siglas.csv'
  → o siglas.csv é conhecimento da equipa e não vem no repositório: copiar
    docs/operacao/siglas.exemplo.csv para a raiz do projeto, editar, e repetir
```

## Como reproduzir

```bash
python -m cct.nomeacao --destino data/raw/bte --siglas nao-existe.csv --aplicar
```

## Solução proposta

Validar a existência em `main`, antes de chamar `carregar_siglas`, e usar o mesmo padrão
de erro dos outros módulos. A validação pertence a `main` e não a `carregar_siglas`, para
que a função continue a poder ser usada em testes com caminhos construídos.

Vale a pena, na mesma correção, rever o exemplo em `docs/dados/README.md:188`
(`--siglas siglas.csv`): funciona se a pessoa copiar o modelo para a raiz, que é o que a
mensagem de erro deve passar a dizer.
