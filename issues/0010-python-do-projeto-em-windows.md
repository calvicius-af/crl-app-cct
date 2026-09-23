# ISSUE-0010: em Windows, não é claro qual o Python do projeto, e o doctor não ajuda

- **Estado:** Resolvida — 2026-09-23 (verificação)
- **Data:** 2026-09-17
- **GitHub:** #60 (sub-issue de #58)
- **Onde dói:** `cct/doctor.py` (L28-39), `README.md` (L54), `CONTRIBUTING.md`, `docs/operacao/guia-operacao.md` (L118, L134, L141)

## O que acontece

São dois sintomas com a mesma raiz, e no teste da estação apareceram encadeados.

**Primeiro, a documentação manda escrever um comando que não existe em Windows.**

```
PS C:\...> .venv/bin/python -m cct.doctor
.venv/bin/python : The term '.venv/bin/python' is not recognized as the name of a cmdlet...
```

Em Windows o interpretador do ambiente é `.venv\Scripts\python.exe`. Há sítios onde a
documentação acerta, com as duas formas lado a lado e rotuladas
(`docs/institucional/instalacao-offline.md:110-111`,
`docs/operacao/guia-operacao.md:89-90`). Mas o mesmo guia de operação, mais à frente
(L118, L134, L141), só traz a forma POSIX, sem rótulo. O `README.md:54` e todo o
`CONTRIBUTING.md` idem.

**Segundo, o `doctor` corrido com o Python errado diz que falta tudo.**

Logo a seguir a uma instalação bem sucedida, que terminou com `✓ as 4 bibliotecas
carregam`:

```
PS C:\...> python -m cct.doctor
== Bibliotecas
  ✗ falta a biblioteca pdfplumber
    → instalar as dependências: duplo clique em scripts/instalar_offline.bat ...
  ✗ falta a biblioteca openpyxl
  ✗ falta a biblioteca pyyaml
  ✗ falta a biblioteca jsonschema
```

As bibliotecas estão instaladas. O que está errado é o interpretador: `python` é o do
sistema, e as bibliotecas vivem no `.venv`. O `doctor` não sabe distinguir os dois casos e
manda instalar outra vez o que já está instalado, o que fecha um ciclo em que a pessoa
repete uma instalação que já correu bem.

## O que devia acontecer

1. O `doctor` deve dizer, sempre, **com que interpretador está a correr**, e detectar que
   existe um `.venv` no projeto do qual não está a ser executado. Nesse caso, a sugestão
   não deve ser "instalar as dependências", mas "correr com o Python do projeto", com o
   comando certo para o sistema em uso.
2. Todos os comandos na documentação dirigida a quem opera devem trazer a forma de Windows,
   por ser esse o sistema das estações do CRL. Onde já há as duas, manter; onde só há a
   POSIX, acrescentar.

## Como reproduzir

```bat
scripts\instalar_offline.bat
python -m cct.doctor
rem reporta as 4 bibliotecas como em falta, logo apos as ter instalado com sucesso
```

## Causa

`cct/doctor.py` verifica as bibliotecas com `__import__(mod)` (L28-31) no interpretador
que já está a correr, e reporta `ImportError` como biblioteca em falta (L33-39). Não
compara `sys.executable`, `sys.prefix` ou `sys.base_prefix` com o `.venv` do projeto, nem
imprime o interpretador em uso em ponto nenhum da saída — `sys.executable` não aparece no
ficheiro.

## Notas

O impacto real é de confiança, não de funcionamento: a aplicação corre bem, porque os
lançadores `scripts/AppCCT.bat:8-9` usam correctamente `.venv\Scripts\python.exe`. O
problema aparece a quem sai dos lançadores e segue a documentação à mão, que é
exactamente o que se faz quando alguma coisa corre mal.

## Verificação (2026-09-23)

1. `cct/doctor.py` imprime sempre o interpretador em uso e deteta um `.venv` do projeto
   que não está a ser usado, comparando os diretórios reais (também com UNC e unidades
   mapeadas, `_venv_em_uso`). Nesse caso sugere correr com o Python do projeto, e não
   reinstalar. Testes em `tests/test_doctor.py`.
2. O README e o guia de operação trazem os comandos na forma de Windows
   (`.\.venv\Scripts\python.exe`).
