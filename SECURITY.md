# Segurança

## Superfície de exposição

A aplicação corre inteiramente na máquina local e **não faz pedidos de rede**. Não abre
portas, não escuta ligações, não envia telemetria.

A única exceção é opcional e local: se a camada semântica for ativada (`--semantica`), a
aplicação fala com um servidor de modelo de linguagem em `http://127.0.0.1:1234`
(por exemplo, LM Studio), na própria máquina. Está desligada por omissão. O backend aceita
somente `localhost`, `127.0.0.1` ou `::1`; uma URL remota falha antes de qualquer pedido de
rede. Não existe backend para serviços externos — ver
[ADR-0012](docs/adr/0012-modelos-locais-obrigatorios.md).

Não há credenciais, chaves nem segredos: não há nada a que autenticar-se.

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

Quatro bibliotecas, todas com licença permissiva: `pdfplumber`, `openpyxl`, `pyyaml`,
`jsonschema` (mais `pytest` em desenvolvimento). A interface gráfica usa `tkinter`, da
biblioteca padrão do Python.

Se o repositório for alojado no GitHub, recomenda-se ativar os alertas do Dependabot e o
*secret scanning*, que são gratuitos em repositórios públicos e privados.
