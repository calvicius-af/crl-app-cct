# Teste em Windows: correções do gate de instalação de 2026-09-17

**Data:** 2026-09-19
**Branch:** `fix/instalacao-windows-gate-2026-09-17` (commit `c736440`)
**Issues cobertos:** 0009 (caminho UNC), 0010 (doctor/interpretador), 0012 (CI), 0013 (proveniência), 0007 remanescente

Este guia verifica, numa máquina Windows real, que as correções feitas para os
problemas do gate de 2026-09-17 funcionam. Segue o protocolo de
[instalacao-estacao-crl-2026-09-17.md](instalacao-estacao-crl-2026-09-17.md).

---

## 1. Obter o código

**Opção A — zip (recomendado para a estação, inclui o pacote offline):**

O ficheiro `crl-app-cct-windows-teste.zip` (40 MB) está no Desktop do Mac.
Copiá-lo para a máquina Windows por pen, partilha ou download. Contém o projeto
completo **incluindo `vendor/wheels/`** (31 wheels, 40.7 MB, alvos
`win_amd64` para Python 3.11, 3.12 e 3.13, com `manifesto.json` verificado).

**Opção B — git (se a máquina de teste tiver git e acesso):**

```bat
git clone -b fix/instalacao-windows-gate-2026-09-17 https://github.com/calvicius-af/crl-app-cct.git
```

⚠ Neste caso o `vendor/wheels/` **não vem** (está no `.gitignore`): copiar a
pasta à parte do zip, ou correr na máquina com internet
`python scripts\preparar_pacote_offline.py --incluir-testes`.

## 2. Dependências necessárias na máquina Windows

| O quê | Versão | Notas |
|---|---|---|
| Windows | 10 ou 11 | o gate anterior usou Windows 11 |
| Python | 3.11, 3.12 ou 3.13 | **3.13.5 é o das estações do CRL** — testar com este se possível; instalar de python.org com "Add python.exe to PATH" e tcl/tk |
| Espaço em disco | ~200 MB | projeto + wheels + .venv |
| git | **não é necessário** | o teste do ISSUE-0013 depende de o git **não** estar instalado; se estiver, o teste 6.4 continua válido (commit aparece em vez do motivo) |
| Internet | **não é necessária** | toda a instalação é offline (`--no-index`) |

## 3. Instalação (ISSUE-0009 — o teste principal)

### 3.1 Caso base: caminho local

1. Extrair o zip para `C:\profiles\<utilizador>\crl-app-cct` (ou qualquer caminho local).
2. Duplo clique em `scripts\instalar_offline.bat`.
3. **Esperado:** termina com `✓ Successfully installed` para as distribuições e
   `✓ as 4 bibliotecas carregam`, sem qualquer erro do pip.

### 3.2 Caso de rede: unidade mapeada (o caso que falhava)

1. Colocar/mapear o projeto numa unidade de rede (na estação do CRL era `L:`
   apontando a `\\localhost\C$\...`; qualquer partilha serve para reproduzir).
2. Correr `scripts\instalar_offline.bat` a partir daí.
3. **Esperado:** a instalação **completa sem o erro `OSError: [Errno 2]`** que
   derrubava o pip antes. É este o critério de fecho do ISSUE-0009.
4. Se falhar (não devia): a mensagem `PAROU AQUI` tem de apontar para
   **caminho/rede** ("copiá-lo para um disco local"), não para versão/plataforma.

### 3.3 Caso de rede: caminho UNC direto

1. Correr a partir de `\\servidor\partilha\crl-app-cct` (sem letra mapeada).
2. **Esperado:** aparece o aviso `· atenção: o projeto está num caminho de rede`
   **antes** da instalação, e a instalação prossegue. Se falhar, o aviso já
   disse o que fazer — isso é aceitável e deve ser registado no relatório.

### 3.4 .venv deixado a meio

1. Apagar `C:\...\crl-app-cct\.venv\Scripts\pip.exe` (deixando o `python.exe`).
2. Correr `scripts\instalar_offline.bat`.
3. **Esperado:** `· .venv existente está incompleto — a refazer` e instalação
   completa (antes disto, um .venv sem pip era reaproveitado em silêncio).

## 4. Doctor (ISSUE-0010)

### 4.1 Doctor com o Python do sistema (o caso que confundia)

1. Abrir PowerShell **sem** activar o `.venv`.
2. `python -m cct.doctor`
3. **Esperado:**
   - a secção `== Python` mostra `· interpretador: C:\...python.exe` (o do sistema);
   - aparece `· o projeto tem um .venv (...) que não está a ser usado` com a
     seta `→ correr com o Python do projeto: ...\.venv\Scripts\python.exe -m cct.doctor`;
   - as bibliotecas que falham dizem **"correr com o Python do projeto"**, e
     **não** "instalar as dependências" (que fechava o ciclo inútil).

### 4.2 Doctor com o Python do projeto

1. `.\.venv\Scripts\python.exe -m cct.doctor`
2. **Esperado:** `✓ pdfplumber`, `✓ openpyxl`, `✓ yaml`, `✓ jsonschema`, sem
   o aviso de .venv, e `Tudo pronto` no fim (com os dados da estação).

## 5. App gráfica (ISSUE-0007 remanescente — fecha o #37)

1. Duplo clique em `scripts\AppCCT.bat`.
2. Clicar no botão **"Verificar instalação"**.
3. **Esperado:** a saída do doctor aparece na janela **sem**
   `UnicodeEncodeError: 'charmap' codec can't encode character '✓'` — este
   botão nunca tinha sido exercitado pela app (correu sempre no terminal, onde
   o problema não se manifesta). É o último critério de aceitação do #37.

## 6. Proveniência (ISSUE-0013)

### 6.1 Manifesto sem git

1. Correr qualquer acção que produza manifesto (ex.: "Correr pipeline" na app,
   ou `cct.pipeline_tema` com um codebook de teste).
2. Abrir o `manifest.json` resultante (em `results/...`).
3. **Esperado:** `"git": {"commit": null, "dirty": null, "motivo": "git_ausente"}`
   — o `motivo` é o campo novo; antes era `null` sem explicação.

### 6.2 Com git instalado (se a máquina de teste tiver)

O manifesto mostra `"commit": "<sha>"` como antes — sem regressão.

## 7. Suite de testes na estação (opcional mas recomendado)

O pacote offline inclui o pytest (`--incluir-testes` foi usado):

```bat
cd C:\...\crl-app-cct
.venv\Scripts\python -m pytest -q
```

**Esperado:** todos passam ou skip (os que exigem dados declarados skip).
Isto é a mesma suite que o CI novo vai correr em `windows-latest`/3.13.

## 8. O que registar no relatório

Para cada teste acima: passou / falhou, e a saída relevante (copiar do
terminal). Em caso de falha do 3.2 (o caso principal), copiar **toda** a
saída do pip — é essa a evidência para o diagnóstico.

---

## Após os testes

1. Se tudo passar: marcar os issues 0009, 0010, 0012, 0013 como
   `Estado: Resolvido` com a data, e fechar o #37 (teste 5).
2. O CI (ISSUE-0012) valida-se sozinho: o push do branch já despoletou a
   matriz nova — verificar em GitHub → Actions que o job
   `pytest (windows-latest, Python 3.13)` passa.
3. Merge do branch `fix/instalacao-windows-gate-2026-09-17` para `main`.
