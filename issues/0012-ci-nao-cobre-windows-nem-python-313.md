# ISSUE-0012: o CI não corre em Windows nem em Python 3.13, que é o que as estações usam

- **Estado:** Resolvida — 2026-09-23 (verificação)
- **Data:** 2026-09-17
- **GitHub:** #61 (sub-issue de #58)
- **Onde dói:** `.github/workflows/testes.yml` (L26-27)

## O que acontece

Testamos num par de sistemas e entregamos noutro.

| | Testado no CI | Entregue nas estações |
|---|---|---|
| Sistema | Ubuntu, macOS | Windows 11 |
| Python | 3.11, 3.12 | 3.13.5 |

A matriz em `.github/workflows/testes.yml:26-27` é `os: [ubuntu-latest, macos-latest]` e
`python: ["3.11", "3.12"]`. Os restantes jobs fixam Python 3.12. **Windows não aparece em
nenhum job**, e 3.13 também não.

Ao mesmo tempo, `scripts/preparar_pacote_offline.py:41-45` prepara o pacote offline, por
omissão, para `win_amd64` em Python 3.11, 3.12 **e 3.13**, e `pyproject.toml:6` declara
`requires-python = ">=3.11"`, sem limite superior.

## Porque é que isto importa agora

O gate de instalação de 2026-09-17 encontrou sete problemas numa estação real. Os dois
mais graves — a falha em caminho de rede (ISSUE-0009) e a confusão do interpretador
(ISSUE-0010) — são específicos de Windows e nenhum deles podia ter sido apanhado pela
suite actual, por muito boa que fosse.

Não se trata de suspeitar que o código está errado em 3.13. Trata-se de não termos
nenhuma prova de que está certo, e de estarmos a afirmar suporte que não verificamos.

## O que devia acontecer

Pelo menos uma combinação Windows na matriz, e Python 3.13 coberto. A decisão de desenho a
tomar é quanto alargar sem tornar o CI lento:

1. **Mínimo defensável:** acrescentar `windows-latest` com Python 3.13. Fica uma matriz de
   cinco jobs de pytest em vez de quatro, e cobre as duas dimensões em falta de uma vez.
2. **Simétrico:** `os: [ubuntu-latest, macos-latest, windows-latest]` com
   `python: ["3.11", "3.12", "3.13"]`, que dá nove jobs. Mais lento e provavelmente
   desproporcionado.
3. **Intermédio:** matriz completa só em Ubuntu, e um job por sistema nas versões extremas.

A opção 1 parece o melhor equilíbrio, mas a decisão é de quem mantém o projeto.

## Notas

Há um limite honesto a reconhecer: um *runner* Windows do GitHub não reproduz uma estação
do CRL. Não tem unidades de rede mapeadas, nem a região portuguesa, nem as políticas de
proxy. O ISSUE-0009 continuaria por apanhar.

O que a cobertura dá é a camada de baixo: que o código corre em Windows e em 3.13. A
camada de cima — o ambiente institucional — continua a precisar de gates manuais como o
de 2026-09-17, e isso deve ficar escrito para que ninguém confunda CI verde com instalação
verificada.

## Verificação (2026-09-23)

Adotada a opção 1: `windows-latest` com Python 3.13 na matriz de
`.github/workflows/testes.yml`, além de Linux, macOS e Windows em 3.11 e 3.12. O CI do
PR #87 passou em todas as combinações. O limite registado nas notas mantém-se: CI verde
não é instalação verificada numa estação do CRL.
