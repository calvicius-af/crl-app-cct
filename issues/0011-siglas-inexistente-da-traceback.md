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
propósito: é conhecimento da equipa, criado localmente. Isto foi **decidido e documentado
no PR #39** (2026-09-15), que acrescentou o modelo `docs/operacao/siglas.exemplo.csv` e
escreveu em `docs/dados/README.md:177-188` que não existe um `siglas.csv` "oficial" para
copiar. A segunda tentativa do teste falhou porque esse modelo está em `docs/operacao/` e
o comando corria a partir da raiz do projeto.

Ou seja, metade deste problema já foi resolvida noutra ronda, e bem. O que resta é mais
estreito do que parece à primeira vista, e são duas coisas pequenas:

1. o erro sai como *traceback* em vez de mensagem;
2. a documentação diz que o ficheiro tem de ser criado, mas não diz **onde** o pôr, e o
   exemplo em `docs/dados/README.md:188` usa `--siglas siglas.csv`, um caminho relativo
   que só funciona se o ficheiro estiver na raiz — o que em lado nenhum está escrito.

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

Na mesma correção, dizer no `docs/dados/README.md` onde colocar o ficheiro, já que o
exemplo da L188 assume a raiz do projeto sem o declarar. É a peça que faltou ao trabalho
do PR #39, não um erro dele.
