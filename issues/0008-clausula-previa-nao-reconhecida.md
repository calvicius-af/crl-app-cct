# ISSUE-0008: o extrator não reconhece "Cláusula prévia" como cabeçalho

- **Estado:** Resolvida no código — 2026-09-15; falta a confirmação no corpus
- **Data:** 2026-09-14
- **GitHub:** #40
- **Onde dói:** `cct/extractor.py` (`_NUMERACAO`, `RE_CLAUSULA`, `RE_ARTIGO`)

## O que acontecia

`RE_CLAUSULA` exigia que "Cláusula" fosse seguida de uma numeração reconhecida:
algarismos (`12.ª`), `único`/`única`, ou um ordinal por extenso. "Cláusula
prévia" não é nenhum destes casos, pelo que a linha não era cabeçalho.

Caso real: o contrato coletivo entre a AEVP e a FESAHT, BTE n.º 31/2026
(revisão salarial parcial), abre com:

```text
Cláusula prévia Âmbito de revisão
1- O presente contrato coletivo de trabalho revê parcialmente o anteriormente
   acordado pelas partes outorgantes e publicado no Boletim do Trabalho e
   Emprego, n.º 3, de 22 de janeiro de 2025 […]
```

O título e os três números eram absorvidos pelo nó anterior (o preâmbulo), sem
código nem hierarquia próprios. O texto não desaparecia — a propriedade
zero-perda mantinha-se — mas a estrutura ficava errada logo no início do
documento, e os números não eram subsegmentados em nós `paragrafo`, porque
`_subsegmentar_paragrafos` só atua sobre nós já classificados como
`clausula`/`artigo`.

Nas revisões parciais, esta é justamente a cláusula que diz o que a revisão
altera, portanto é das que mais interessa ter delimitada.

## Resolução aplicada (2026-09-15)

`_DESIGNADOR` acrescenta à numeração uma **lista fechada** de designadores de
posição (`prévia`/`prévio`, `preliminar`), pela mesma razão que levou a
restringir os ordinais: aceitar "qualquer palavra" a seguir a "Cláusula" fazia
do título do CAPÍTULO XV do AguasNorte ("Cláusula geral e transitória") uma
cláusula vazia.

O designador leva um guarda próprio: só conta se for seguido de fim de linha ou
de uma maiúscula (o título da cláusula). Sem acento, `previa` é a forma verbal
de "prever", e uma linha de prosa como "Cláusula previa o pagamento em
duodécimos" passaria a cabeçalho, roubando o corpo à cláusula real. O guarda usa
`(?-i:…)` porque o grupo da numeração é aplicado dentro de `(?i:…)`, que de
outro modo tornaria a exigência de maiúscula inútil.

A subsegmentação em parágrafos passa a aplicar-se por consequência direta, sem
alteração própria: o nó já é do tipo `clausula`.

Testes em `tests/test_extractor_nuances.py`: o cabeçalho, os três números como
nós `paragrafo`, os designadores aceites e recusados, e o caso de prosa que o
guarda trava.

## Por confirmar

O corpus vive fora do repositório e não estava disponível quando isto foi
escrito, pelo que fica por fazer o primeiro ponto do #40: confirmar noutros
documentos (sobretudo revisões parciais, sufixo `-ALT`) se "Cláusula prévia" é
fórmula recorrente e se há outras variantes além de "preliminar". A lista é
fechada de propósito; acrescentar uma variante é uma linha, mais o teste.

Prova feita com o material disponível: nos dois documentos de `examples/`, a
estrutura extraída é carácter a carácter a mesma antes e depois da alteração
(576 e 139 nós, texto final idêntico).
