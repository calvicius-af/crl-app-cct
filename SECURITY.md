# Segurança

## Superfície de exposição

A aplicação corre na máquina local, não abre portas, não escuta ligações e não envia
telemetria. A instalação base não faz pedidos de rede durante o processamento.

A única exceção é opcional e local: se a camada semântica for ativada (`--semantica`), a
aplicação fala com um servidor de modelo de linguagem em `http://127.0.0.1:1234`
(por exemplo, LM Studio), na própria máquina. Está desligada por omissão. O backend aceita
somente `localhost`, `127.0.0.1` ou `::1`; uma URL remota falha antes de qualquer pedido de
rede. Não existe backend para serviços externos — ver
[ADR-0012](docs/adr/0012-modelos-locais-obrigatorios.md).

O extrator Docling opcional pode descarregar modelos na primeira execução. Em ambientes
fechados, os modelos devem ser pré-instalados a partir de uma origem aprovada; a execução
normal usa apenas os ficheiros locais.

O produto não requer credenciais, chaves ou segredos. Ficheiros `.env` não devem ser
guardados no repositório nem dentro das cópias locais em `vendor/`.

## Dados tratados

- **Convenções coletivas** publicadas no Boletim do Trabalho e Emprego — documentos
  públicos. Contêm nomes de signatários, que constam da publicação oficial.
- **Exports do MaxQDA** — trabalho interno do CRL, não público. Ficam em `data/raw/`,
  fora do controlo de versões, e não devem ser publicados sem decisão da instituição.

Nada disto é enviado para fora da máquina.

## Reportar uma vulnerabilidade

Se encontrar um problema de segurança, **não abra um issue público**. Contacte
diretamente a equipa do projeto no Centro de Relações Laborais, descrevendo o problema, o
impacto e como reproduzi-lo. A resposta é dada com a maior brevidade possível e a
correção é publicada com o devido crédito, se assim for desejado.

Em contexto institucional, aplica-se cumulativamente a política de segurança da informação
da entidade responsável pelos sistemas.

## Dependências

Quatro bibliotecas diretas na instalação base, todas com licença permissiva:
`pdfplumber`, `openpyxl`, `pyyaml`, `jsonschema` (mais `pytest` em desenvolvimento). A
interface gráfica usa `tkinter`, da biblioteca padrão do Python. O Docling é opcional e
tem uma cadeia de dependências distinta, que deve ser inventariada e fixada antes de uma
instalação institucional.

Se o repositório for alojado no GitHub, recomenda-se ativar os alertas do Dependabot e o
*secret scanning*, que são gratuitos em repositórios públicos e privados.
