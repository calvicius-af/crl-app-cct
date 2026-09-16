# ADR-0019: a lista do INE é um sinal de âmbito, nunca uma decisão

- **Estado:** Aceite
- **Data:** 2026-09-16
- **Decidido por:** coordenação do RNC

## Contexto

A classificação de âmbito (PRI/SPE/APU) dependia de uma lista de empregadores
escrita à mão, com dez entradas, e de uma regra sobre formas jurídicas. Sem mais
nada, uma empresa pública entra como PRI por omissão e contamina qualquer
leitura por âmbito — é a tarefa 4 do §10 do README do RNC.

Foi proposta como fonte a lista que o INE publica anualmente: **Entidades do
Setor Institucional das Administrações Públicas**, 4 241 entidades para 2025, em
doze subsectores do S.13 nos termos do SEC 2010.

A lista é boa, é oficial, é datada e é exaustiva. **Mas responde a outra
pergunta.**

O INE classifica por **contas nacionais**: uma entidade está em S.13 se for
produtor não mercantil, o que se decide pelo teste dos 50% de cobertura dos
custos por receitas de mercado. O RNC classifica por **regime laboral**: APU são
as entidades cujos trabalhadores estão sob a LTFP e cujos IRCT são depositados na
DGAEP, e por isso não saem no BTE.

Os dois critérios divergem, e divergem nos dois sentidos. Verificado sobre a
lista de 2025:

| Entidade | Em S.13? | Âmbito no RNC | O que aconteceria se a lista decidisse |
|---|---|---|---|
| Metropolitano de Lisboa, E.P.E. | **sim** (S.13112) | SPE, processável | saía do pipeline como APU |
| Rádio e Televisão de Portugal, S.A. | **sim** (S.13112) | SPE, processável | saía do pipeline como APU |
| Infraestruturas de Portugal, S.A. | **sim** (S.13112) | SPE, processável | saía do pipeline como APU |
| TUB — Transportes Urbanos de Braga, E.M. | **sim** (S.131324) | SPE, processável | saía do pipeline como APU |
| CP — Comboios de Portugal | **não** | SPE | nenhum sinal |
| Carris | **não** | SPE | nenhum sinal |
| EPAL | **não** | SPE | nenhum sinal |
| Empresa Metropolitana de Estacionamento da Maia, E.M. | **não** | SPE (processada do BTE 31/2026) | nenhum sinal |

São 174 entidades com forma jurídica empresarial dentro de S.13 — empresas
públicas reclassificadas em contas nacionais. Usar a lista como autoridade
retirava-as todas do pipeline, e é exatamente o modo de falha que o §5.2 do
README do RNC identifica: *um falso APU retira um documento do pipeline sem
ninguém dar por isso*.

## Decisão

**Importamos a lista, e ela dá um sinal com duas camadas — nunca uma decisão.**

O construtor (`scripts/construir_entidades_publicas.py`) separa cada entidade
pela forma jurídica do nome:

| Camada | Quem | Âmbito proposto |
|---|---|---|
| `APU` | 4 067 entidades sem forma jurídica empresarial: municípios, freguesias, órgãos regionais, serviços e fundos autónomos, fundos de segurança social | APU |
| `SPE_PROVAVEL` | 174 entidades com forma jurídica empresarial (`, E.P.E.`, `, E.M.`, `, S.A.`, `Unipessoal`, `Lda`) | **SPE**, nunca APU |

E na classificação, a lista entra em **segundo** lugar, entre o vocabulário da
equipa e a regra:

1. vocabulário da equipa — decide, sem aviso;
2. **lista do INE — propõe, sempre com aviso**;
3. regra das formas jurídicas;
4. omissão: PRI.

Três propriedades que a tornam segura:

- **uma entrada com forma empresarial propõe SPE, nunca APU.** É a camada que
  evita o erro caro;
- **toda a proposta vinda da lista sai com aviso**, mesmo quando acerta, porque
  o critério dela não é o do RNC. O catálogo regista `ambito_origem=ine`;
- **a ausência da lista não significa nada.** A CP e a Carris não estão lá e são
  SPE. Cair fora da lista devolve a decisão à regra, não a «privado confirmado».

Só entram entradas com dez ou mais caracteres: com 4 241 nomes, uma chave curta
(«Maia») encaixa por acaso dentro de outro nome e classifica mal em silêncio.

## Alternativas consideradas

| Alternativa | Porque não |
|---|---|
| Usar a lista como autoridade para APU | Retirava do pipeline o Metropolitano de Lisboa, a RTP, as Infraestruturas de Portugal e mais 171 entidades. É o erro que a lista parecia resolver e na verdade causava |
| Importar só os municípios e freguesias, e ignorar o resto | Perde os 174 casos ambíguos, que são precisamente a população que a equipa precisa de classificar à mão. Ficariam invisíveis |
| Não importar, e esperar pela lista da DGAEP | A lista da DGAEP responderia à pergunta certa, mas não a temos. E esta, usada como sinal, cobre 4 067 entidades de administração pública que a regex de hoje apanha por acaso ou não apanha |
| Tratar a coincidência com a lista como decisão silenciosa quando o sinal é APU | Um município é quase sempre APU, mas «quase sempre» não é a norma desta base: nenhuma proposta automática de APU passa sem revisão, porque o custo de errar é assimétrico |

## Consequências

**Torna fácil:** classificar as 4 067 entidades de administração pública sem as
escrever à mão; e ver, numa lista de 174 nomes, exatamente quais são os casos
que precisam de decisão humana — que é o material de trabalho da tarefa 4.

**Torna difícil:** confundir sector institucional com regime laboral. O ficheiro
declara a distinção em cada linha, e o script recusa-se a ser lido de outra
maneira.

**Passa a ser obrigatório manter:** a separação das duas camadas ao construir o
ficheiro, e os testes que fixam os casos-armadilha pelo nome — Metropolitano de
Lisboa, RTP, TUB de um lado; CP, Carris, EPAL do outro.

**Custo assumido:** um vocabulário de 4 241 linhas versionado, que tem de ser
reconstruído todos os anos quando o INE publica a lista nova; e o facto de a
lista, por desenhos, nunca resolver sozinha um caso — só o propõe.

## Revisitar quando

Quando existir uma lista do lado da DGAEP com as entidades cujos trabalhadores
estão sob a LTFP. Essa responde à pergunta certa e passaria a ser a fonte de
primeira linha, com a do INE a ficar como confirmação.

Também se o INE passar a publicar, na mesma lista, a distinção entre entidades
reclassificadas e administração pública em sentido estrito — hoje ela só se
infere da forma jurídica no nome, que é uma heurística.
