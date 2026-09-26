# ISSUE-0009: a instalação offline falha quando o projeto está num caminho de rede

- **Estado:** Resolvida no código e verificada no CI com uma unidade de rede real — falta
  confirmar no próximo gate numa estação do CRL
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

## Verificação (2026-09-23)

Resolvido no código, com testes em `tests/test_pacote_offline.py` (secções «ISSUE-0009»):

1. `scripts/instalar_offline.py` usa `os.path.abspath` em vez de `resolve()`, que em
   Windows convertia a unidade mapeada (`L:`) no caminho UNC que o pip não abre.
2. Um projeto em caminho UNC é assinalado antes de instalar, com o que fazer.
3. A mensagem de falha do pip distingue permissões, caminho inacessível ou UNC, e
   versão ou plataforma, em vez de apontar sempre para a versão.
4. Um `.venv` reaproveitado tem de ter o pip, o que evita a instalação parcial silenciosa
   referida nas notas.

## Reprodução no CI (2026-09-26)

Um runner Windows *pode* ter unidades de rede: o workflow
`.github/workflows/instalacao-rede.yml` cria uma partilha SMB local, mapeia `L:` com
`net use` e instala o pacote offline verdadeiro (preparado no próprio job) sem rede para
o pip. Antes de instalar, prova que a condição do defeito está presente —
`Path("L:\\...").resolve()` devolve `\\localhost\crl\...` —, e um passo de controlo
com a forma antiga (`--find-links \\localhost\...` em texto) reproduz o erro da
estação letra a letra: `Processing \crl\unc\vendor\wheels\pdfplumber-...` e
`[Errno 2] No such file or directory`.

**A causa, confirmada:** o pip segue a RFC 8089, para a qual `file://localhost/x` é o
`/x` do disco local. O servidor da estação chamava-se precisamente `localhost`
(`L:` → `\\localhost\C$\...`); qualquer caminho para ele, em texto ou em URI, perdia o
servidor na conversão que o pip faz entre caminhos e URI. Por isso o `--find-links`
em URI da correção anterior não bastava para um projeto aberto diretamente por
`\\localhost\...`, e o CI mostrou-o.

**O que passou a fazer o instalador:** mantém a letra da unidade (`abspath`, já de
2026-09-23), e, quando a pasta é mesmo um caminho UNC, passa ao pip um URI com
`127.0.0.1` no lugar de `localhost` (`endereco_para_o_pip`), a mesma máquina, que o pip
trata como servidor. O diagnóstico reconhece também «neither a file nor a directory»
como um problema de caminho.

**Verificado no runner** (Windows, Python 3.13): a partir de `L:` pelo `.bat`, como na
estação, com o `doctor` e 91 testes a correr do `.venv` em `L:`; a partir de
`\\localhost\crl\...`; e a partir de `\\NOME-DA-MÁQUINA\crl\...`, o caso geral de
um servidor. O workflow corre nos PR que mexem no instalador, no preparador ou nas
dependências.

Falta a confirmação numa estação real, que o runner não substitui: região portuguesa,
políticas do proxy e a partilha institucional, com as suas permissões.
