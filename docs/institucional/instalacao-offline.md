# Instalação sem internet — AppCCT

## 1. O problema que isto resolve

A AppCCT precisa de quatro bibliotecas Python que, numa instalação normal, se
descarregam da internet no momento em que se instala. Nas estações do CRL essa
descarga é bloqueada pelo proxy da rede interna.

Este documento descreve a alternativa: preparar as bibliotecas **uma vez**, numa
máquina com acesso, e instalá-las nas estações **sem qualquer pedido de rede**.
Não é um contorno da política de segurança nem exige exceção no proxy. É o
procedimento normal do Python para redes fechadas, e é o mesmo mecanismo que o
próprio `pip` documenta.

Consequência prática: não é preciso abrir pedido às comunicações, e a
instalação deixa de depender de a rede se portar bem no dia em que se instala.

## 2. Como funciona, em duas frases

As bibliotecas Python distribuem-se em ficheiros chamados *wheels* (extensão
`.whl`). São ficheiros comuns: copiam-se, guardam-se, conferem-se. O que se faz
aqui é guardar essas wheels dentro da própria pasta do projeto, em
`vendor/wheels/`, e mandar o instalador ir buscá-las lá em vez de à internet.

```
Máquina com internet              Partilha de rede            Estação do CRL
   preparar_pacote_offline.py  →  pasta do projeto     →   instalar_offline.bat
   (descarrega as wheels)         com vendor/wheels/       (instala sem rede)
```

## 3. Preparar o pacote (uma vez, na máquina com acesso)

Na pasta do projeto, com internet disponível:

```
python scripts/preparar_pacote_offline.py
```

Isto descarrega para `vendor/wheels/` as bibliotecas necessárias para Windows
64 bits e Python 3.11, 3.12 e 3.13, e escreve dois ficheiros de conferência:
`MANIFESTO.txt` (legível, com os hashes SHA-256 de cada ficheiro) e
`manifesto.json` (o mesmo, para leitura automática).

As dependências vêm de `requirements.txt`, que é a única lista a manter: acrescentar
lá uma biblioteca chega para que ela passe a entrar no pacote offline.

**A pasta `vendor/wheels/` é recriada de raiz a cada corrida.** É deliberado: se as
wheels novas ficassem ao lado das antigas, a instalação na estação poderia escolher uma
versão que já não é a pretendida, sem aviso nenhum.

Espaço ocupado: cerca de 25 MB por versão de Python coberta.

Para incluir também o `pytest`, e assim poder correr a suite de testes na
estação:

```
python scripts/preparar_pacote_offline.py --incluir-testes
```

Se as estações forem macOS, ou de outra arquitetura, indicar os alvos:

```
python scripts/preparar_pacote_offline.py --alvos macosx_11_0_arm64:311
```

## 4. Instalar na estação (uma vez por máquina)

1. Copiar a pasta do projeto completa da partilha de rede para a estação,
   incluindo a pasta `vendor/wheels/`.
2. Duplo clique em `scripts/instalar_offline.bat` (Windows) ou
   `scripts/instalar_offline.command` (macOS).
3. A janela mostra a verificação prévia, a conferência dos hashes contra o
   manifesto, a instalação e a confirmação final. Ao terminar com "Instalado",
   está pronta.
4. Abrir a aplicação com duplo clique em `scripts/AppCCT.bat`.

O instalador chama o `pip` com a opção `--no-index`, que o impede de contactar
o PyPI ou o proxy. Se a rede estiver completamente cortada, a instalação
corre na mesma.

## 5. Quando alguma coisa corre mal

O instalador não falha em silêncio: pára, diz onde parou e o que fazer. As três
situações previsíveis:

**"não há bibliotecas em vendor/wheels"** — a pasta foi copiada sem o
`vendor/wheels/`. Copiar de novo a pasta completa. Isto acontece sobretudo
quando se copia a partir de uma cópia obtida por `git clone`, porque o
`vendor/` não é versionado (é conteúdo binário, não código).

**"o pip não conseguiu instalar", com menção a versão ou plataforma** — o
pacote foi preparado para uma versão de Python diferente da que a estação tem.
Confirmar a versão na estação com `python -V` e voltar a correr o preparador
com o alvo certo, por exemplo `--alvos win_amd64:312`.

**"a biblioteca X não corresponde ao manifesto"** ou **"falta a biblioteca X"**
— a cópia de `vendor/wheels/` ficou incompleta ou corrompeu-se pelo caminho. Repetir
a cópia a partir da origem. O instalador confere isto antes de instalar seja o que
for, precisamente para que o problema apareça aqui e não mais tarde.

**"esta máquina tem Python X, que é antigo"** — a estação precisa de Python
3.11 ou superior. É a única coisa que continua a depender de uma instalação
autorizada; o instalador oficial do python.org é um ficheiro único e não
requer acesso ao proxy depois de descarregado.

Em qualquer outro caso, correr o diagnóstico e guardar o resultado, usando o
`python` que está dentro do `.venv` criado:

```
.venv\Scripts\python -m cct.doctor      (Windows)
.venv/bin/python -m cct.doctor           (macOS)
```

## 6. Actualizar a aplicação mais tarde

Alterações ao código da aplicação não exigem repetir nada disto: substitui-se a
pasta do projeto (ou faz-se `git pull`) e o `.venv` existente continua a servir.

Só é preciso voltar a correr o preparador quando as dependências mudarem, o que
está registado em `requirements.txt`. Nesse caso, correr o preparador de novo (a
pasta `vendor/wheels/` é recriada de raiz, sem restos da versão anterior), copiar a
pasta para a partilha, e na estação correr o instalador com `--refazer`.

## 7. O que isto significa para a segurança

O procedimento não aumenta a superfície de risco face à instalação normal — pelo
contrário, reduz o número de momentos em que a estação fala com o exterior, que
passa a ser zero. Os pontos que uma auditoria interna tenderá a perguntar:

1. **Origem das bibliotecas.** As mesmas do PyPI oficial, todas com licença
   permissiva (MIT, Apache-2.0, BSD, MIT-CMU), listadas em
   [requisitos-tecnicos.md](requisitos-tecnicos.md) §3.
2. **Integridade.** O `MANIFESTO.txt` regista o SHA-256 de cada ficheiro, e o
   `manifesto.json` guarda o mesmo em formato lido pela máquina. O instalador
   confere todos os hashes automaticamente antes de instalar: uma wheel alterada
   ou truncada entre a preparação e a instalação faz o procedimento parar, com o
   nome do ficheiro.
3. **Momento da descarga.** Uma vez, numa máquina identificada, e não em cada
   estação.
4. **Ausência de tráfego posterior.** A aplicação não faz pedidos de rede em
   operação (ver [requisitos-tecnicos.md](requisitos-tecnicos.md) §4). As duas
   exceções opcionais, Docling e camada semântica local, estão desligadas por
   omissão.
