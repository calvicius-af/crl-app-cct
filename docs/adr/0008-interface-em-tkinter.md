# ADR-0008: interface gráfica em tkinter, sem dependências adicionais

- **Estado:** Aceite
- **Data:** 2026-07-07
- **Decidido por:** CRL (António Fula)

## Contexto

O pipeline é operado por pessoas da área das relações laborais, não por informáticos.
Pedir-lhes que escrevam comandos com seis argumentos, em máquinas Windows geridas pelo
Instituto de Informática, era um obstáculo real à adoção.

Ao mesmo tempo, qualquer dependência nova (Electron, PyQt, um servidor web local) é mais
uma coisa a justificar num parecer de segurança e a instalar em máquinas onde o
utilizador não é administrador.

## Decisão

A interface é uma janela **tkinter**, que faz parte da biblioteca padrão do Python: zero
dependências além do que já é preciso para o pipeline. Funciona em macOS e em Windows, e
lança-se por duplo clique (`scripts/AppCCT.command`, `scripts/AppCCT.bat`).

A aplicação é uma **casca fina**: descobre sozinha os caminhos habituais (pasta de PDFs,
codebooks, exports do MaxQDA), monta o comando e lança-o em subprocesso, mostrando o
registo ao vivo. Não tem lógica própria — o que ela faz é exatamente o que a linha de
comandos faz.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| PyQt / wxPython | Melhor aspeto, mas é uma dependência grande a instalar e a licenciar |
| Aplicação web local (Flask + navegador) | Abre uma porta local — pergunta desnecessária a fazer a um serviço de segurança informática |
| Só linha de comandos | Barreira de adoção para quem faz o trabalho |
| Electron | Centenas de megabytes e um ecossistema inteiro para uma janela com sete campos |

## Consequências

- A instalação é: Python, `pip install -r requirements.txt`, duplo clique. Nada mais.
- O aspeto é o do sistema operativo, sem polimento. Aceitável para uma ferramenta interna.
- Como a interface não tem lógica, não pode divergir da linha de comandos — o que se
  testa na CLI vale para a aplicação.
- Em Linux e nalgumas instalações de Python, `tkinter` não vem incluído; o
  `python -m cct.doctor` deteta e explica como resolver.

## Revisitar quando

For preciso uso simultâneo por várias pessoas, ou acesso remoto — aí a resposta certa
passa a ser uma aplicação servidor, e esta decisão deixa de servir.
