# ISSUE-0009: a instalação offline falha quando o projeto está num caminho de rede

- **Estado:** Aberta
- **Data:** 2026-09-17
- **GitHub:** #59 (sub-issue de #58)
- **Onde dói:** `scripts/instalar_offline.py` (`instalar()`, L180-196), `scripts/instalar_offline.bat`

## O que acontece

Numa estação do CRL, com o projeto numa unidade mapeada `L:` que aponta para
`\\localhost\C$\profiles\CRL044628\pessoal\crl-app-cct-...`, o instalador chega à
instalação e o pip falha:

```
== Instalação das bibliotecas (sem rede)
Looking in links: \\localhost\C$\profiles\CRL044628\pessoal\...\vendor\wheels
Processing l:\c$\profiles\crl044628\pessoal\...\vendor\wheels\pdfplumber-0.11.10-py3-none-any.whl
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory:
'\\C$\\profiles\\CRL044628\\pessoal\\...\\vendor\\wheels\\pdfplumber-0.11.10-py3-none-any.whl'
```

Repare-se em três caminhos diferentes para o mesmo ficheiro, na mesma mensagem: o que o
pip recebeu (`\\localhost\C$\...`), o que ele diz estar a processar (`l:\c$\...`) e o que
tentou abrir (`\C$\...`, sem o `\\localhost`). O prefixo do servidor desapareceu.

Correr exactamente o mesmo `scripts/instalar_offline.bat` a partir de
`C:\profiles\CRL044628\pessoal\crl-app-cct-...` funciona à primeira, com
`✓ Successfully installed` para as 16 distribuições.

Isto é um bloqueador: uma estação institucional com o perfil em unidade de rede não
consegue instalar, e a saída teve de ser descoberta pela pessoa que instalava.

## O que devia acontecer

A instalação deve funcionar independentemente de o projeto estar num caminho local, numa
unidade mapeada ou num caminho UNC. Se houver um caso que genuinamente não possa
funcionar, o instalador deve dizê-lo antes de tentar, e dizer o que fazer.

## Como reproduzir

```bat
rem Numa estação Windows, com o projeto acessível por unidade mapeada de rede:
L:
cd \crl-app-cct-...
scripts\instalar_offline.bat
```

## Causa provável

Não está confirmada e precisa de verificação na estação, porque não há Windows no
ambiente de desenvolvimento nem no CI (ver ISSUE-0012).

O que está confirmado no código:

1. `scripts/instalar_offline.bat:3` faz `cd /d "%~dp0.."`, ficando com o directório de
   trabalho na unidade mapeada, `L:`;
2. `scripts/instalar_offline.py:28` define `RAIZ = Path(__file__).resolve().parent.parent`.
   Em Windows, `resolve()` sobre um ficheiro numa unidade mapeada de rede devolve o
   **caminho UNC de destino**, não a letra de unidade. É aqui que `L:` vira
   `\\localhost\C$\...`;
3. `scripts/instalar_offline.py:182` passa `"--find-links", str(WHEELS)`, isto é, um
   caminho de sistema de ficheiros e não uma URL `file:`. Não há normalização do prefixo
   UNC.

A hipótese é que o pip, ao normalizar um valor de `--find-links` em forma UNC, perca o
componente do servidor. O erro mostra isso mesmo: procura `\C$\...` em vez de
`\\localhost\C$\...`.

## Soluções a avaliar

Por ordem de preferência, todas por confirmar na estação:

1. **Não resolver mapeamentos de rede.** Usar `os.path.abspath` em vez de `resolve()` para
   `RAIZ`, preservando `L:\...`, que o pip trata sem ambiguidade. É a correção mais
   pequena e ataca a origem.
2. **Passar `--find-links` como URL**, com `WHEELS.as_uri()`, em vez de um caminho. Evita
   a normalização de caminhos do pip.
3. **Detectar e avisar.** Se o caminho resolvido começar por `\\`, dizer antes de tentar
   que a instalação a partir de um caminho de rede é conhecida por falhar, e indicar a
   saída: correr a partir da letra de unidade local.

As três não são exclusivas. A 3 tem valor por si, porque transforma uma falha obscura num
aviso accionável, mesmo que a 1 ou a 2 resolvam o caso comum.

## Problema associado: a mensagem de erro aponta a causa errada

Quando o pip falha, `instalar()` (L190-196) diz sempre a mesma coisa:

> se a mensagem falar em versão de Python ou plataforma, o pacote offline foi preparado
> para outra versão: voltar a correr preparar_pacote_offline.py com o alvo certo

Neste caso a causa não tinha nada que ver com versão nem plataforma. A *wheel* que falhou,
`pdfplumber-0.11.10-py3-none-any.whl`, é universal: não podia ter sido excluída por
incompatibilidade. A mensagem mandou procurar no sítio errado.

A sugestão deve passar a distinguir pelo menos três famílias de causa: incompatibilidade
de versão ou plataforma; caminho inacessível ou em forma UNC; e permissões. O `stdout` do
pip já é impresso antes (L191), pelo que a informação está lá — falta a orientação estar
alinhada com ela.

## Notas

O `.venv` criado pela tentativa falhada foi reaproveitado pela corrida seguinte
(`✓ já existe (a reaproveitar)`) e a instalação completou-se sem problema. Não há defeito
aqui, mas vale a pena confirmar que um `.venv` deixado a meio por uma falha anterior nunca
pode conduzir a uma instalação parcial silenciosa.
