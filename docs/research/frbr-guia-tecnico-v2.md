# Guia técnico sobre o modelo FRBR (Functional Requirements for Bibliographic Records)

## 1. Enquadramento geral do FRBR

Functional Requirements for Bibliographic Records (FRBR) é um modelo conceptual desenvolvido sob a égide da IFLA para descrever, de forma estruturada, o universo bibliográfico e as funções que os registos devem cumprir para responder às necessidades dos utilizadores.[^1][^2][^3] O relatório final foi publicado em 1998, na sequência de um estudo iniciado em 1991 por um grupo de trabalho da IFLA, e passou a ser uma referência para a reavaliação de códigos de catalogação e de sistemas de gestão de catálogos.[^1][^2][^3]

FRBR adopta explicitamente a abordagem de modelação entidade‑relação: identifica entidades de interesse para os utilizadores de registos bibliográficos, define os seus atributos e explicita os tipos de relações que podem existir entre essas entidades.[^1][^4][^5] Não é um código de catalogação nem um formato de registo, mas um modelo de alto nível, neutro quanto a regras e tecnologias, destinado a servir de base à concepção de códigos (como o RDA) e de sistemas.[^4][^3]

## 2. Objectivos funcionais e tarefas do utilizador

O modelo FRBR foi concebido para responder à pergunta: “que funções deve um registo bibliográfico desempenhar para apoiar as tarefas dos utilizadores?”.[^5][^4] Para isso, identifica quatro tarefas fundamentais associadas à interacção com informação bibliográfica:

- **Encontrar (find)**: localizar entidades que correspondam a critérios de pesquisa do utilizador (por exemplo, todos os recursos sobre um tema, de um autor, numa língua).[^4][^5]
- **Identificar (identify)**: confirmar que a entidade descrita é efectivamente aquela que o utilizador procura, ou distinguir entre entidades semelhantes.[^4]
- **Seleccionar (select)**: escolher uma entidade adequada às necessidades do utilizador (por exemplo, seleccionar a edição com certas características físicas ou linguísticas).[^5]
- **Obter (obtain)**: adquirir acesso à entidade, seja por empréstimo, compra, acesso digital ou outro meio.[^4][^5]

Estes quatro verbos funcionais são a base para a definição de que atributos e relações são prioritários num registo bibliográfico e em que nível de granularidade devem ser representados.[^4][^5] Por exemplo, aspectos como forma de conteúdo, meio de suporte, idioma ou data de publicação são directamente relacionados com as tarefas de seleccionar e obter.

## 3. Estrutura conceptual: grupos de entidades

### 3.1 Visão geral dos três grupos

FRBR organiza a sua ontologia em três grupos de entidades, concebidos para separar produtos intelectuais, agentes responsáveis por esses produtos e assuntos sobre os quais tratam.[^1][^2][^4]

- **Grupo 1**: produtos de esforço intelectual ou artístico – os próprios recursos bibliográficos.
- **Grupo 2**: entidades responsáveis pela criação, produção, disseminação ou custódia dos recursos.[^2][^4]
- **Grupo 3**: entidades que podem servir como assunto dos recursos (incluindo entidades dos grupos 1 e 2).[^4][^5]

Esta separação clarifica o papel de cada entidade em relação às tarefas do utilizador e à estrutura dos registos, permitindo modelar de forma mais precisa as dependências e responsabilidades.[^2][^3]

### 3.2 Entidades do Grupo 1: obra, expressão, manifestação, exemplar

O Grupo 1 contém as entidades mais discutidas e distintivas do modelo FRBR.[^1][^2]

- **Obra (work)**: criação intelectual ou artística distinta, entendida de forma abstracta (por exemplo, o conceito de "Os Maias" enquanto obra literária).[^1][^2]
- **Expressão (expression)**: realização intelectual ou artística concreta de uma obra (por exemplo, o texto de "Os Maias" na língua original, uma tradução para outra língua, uma partitura com arranjo específico).[^1][^4]
- **Manifestação (manifestation)**: incorporação física de uma expressão (por exemplo, uma edição específica publicada por uma editora em determinada data e formato).[^2][^4]
- **Exemplar (item)**: cópia individual de uma manifestação, com características de exemplar (assinatura, localização, estado de conservação).[^1][^2]

A relação entre estas entidades é muitas vezes ilustrada pela cadeia: uma obra **é realizada através** de uma ou mais expressões; cada expressão **é incorporada** em uma ou mais manifestações; cada manifestação **é exemplificada** por um ou mais exemplares.[^1][^2] As duas primeiras entidades (obra e expressão) são abstractas, enquanto manifestação e exemplar se aproximam do nível físico ou instanciado.[^4]

### 3.3 Entidades do Grupo 2: agentes responsáveis

O Grupo 2 agrega entidades responsáveis pelo conteúdo intelectual ou artístico, pela produção e disseminação física e pela custódia das entidades de Grupo 1.[^2][^4]

- **Pessoa (person)**: indivíduo identificado (autor, editor, tradutor, compositor, etc.).[^4]
- **Corpo colectivo (corporate body)**: organização ou grupo de indivíduos que actua como unidade (instituição, editora, biblioteca, associação).[^2][^4]

Modelos posteriores (FRAD e RDA) vêm a explicitar também a entidade **família**, mas no modelo FRBR original esta não é referida explicitamente.[^6][^3] As relações típicas incluem, por exemplo, "obra é criada por pessoa", "manifestação é produzida por corpo colectivo" ou "exemplar é detido por biblioteca X".[^6][^2]

### 3.4 Entidades do Grupo 3: assuntos

O Grupo 3 identifica categorias de entidades que podem servir como assunto de uma obra, juntamente com os próprios grupos 1 e 2 (uma obra pode ter como assunto outra obra ou uma pessoa).[^4][^5]

- **Conceito (concept)**: ideia ou noção abstrata (por exemplo, "democracia", "teoria da vinculação").[^4]
- **Objecto (object)**: coisa material ou objecto físico concreto.[^4]
- **Evento (event)**: ocorrência histórica ou acto concreto (por exemplo, "Revolução dos Cravos").[^4]
- **Lugar (place)**: localização geográfica (por exemplo, "Lisboa", "União Europeia").[^4]

O facto de FRBR permitir que entidades de todos os grupos sejam assuntos facilita a modelação de universos documentais complexos, como colecções de legislação, actas parlamentares ou registos de património cultural.[^4][^7]

## 4. Atributos e relações no modelo entidade‑relação

### 4.1 Atributos das entidades

Cada entidade em FRBR é caracterizada por atributos que capturam informações relevantes para as tarefas dos utilizadores.[^5][^1] Exemplos típicos incluem:

- **Obra**: título preferido, forma de obra, data de criação, público‑alvo.[^5]
- **Expressão**: idioma, forma de expressão (texto, som, imagem em movimento), arranjo, versão.[^5]
- **Manifestação**: título tal como aparece, declaração de responsabilidade, dados de publicação, forma de suporte, extensão, dimensões.[^5]
- **Exemplar**: localização, assinatura, estado físico, número de inventário.[^5]
- **Pessoa**: nome, datas associadas, profissão ou ocupação, título.[^6]
- **Conceito, objecto, evento, lugar**: designação preferida, variantes, data ou período, coordenadas (para lugar), etc.[^5]

Estes atributos não são prescrições de elementos de dados concretos, mas orientações sobre que propriedades são relevantes para suportar as tarefas find/identify/select/obtain.[^5][^3]

### 4.2 Relações entre entidades de Grupo 1

As relações entre entidades são centrais no modelo FRBR, dado que permitem construir vistas estruturadas (por exemplo, agrupar todas as manifestações de uma mesma obra).[^1][^2] No Grupo 1, as principais relações são:

- **Obra – expressão**: uma obra é realizada através de uma ou mais expressões; uma expressão realiza uma obra.[^1][^2]
- **Expressão – manifestação**: uma expressão é incorporada numa ou mais manifestações; uma manifestação incorpora uma expressão.[^1][^2]
- **Manifestação – exemplar**: uma manifestação é exemplificada por um ou mais exemplares; um exemplar exemplifica uma manifestação.[^1][^2]

Para além disso, existem relações entre obras (por exemplo, adaptação, tradução, revisão, continuação), entre expressões (por exemplo, revisão de uma expressão anterior), entre manifestações (reimpressões, reedições, versões fac-similadas).[^1][^5] Estas relações são importantes para construir árvores ou grafos de variantes e derivados.

### 4.3 Relações com agentes e assuntos

Relações entre entidades de Grupo 1 e Grupo 2 especificam responsabilidades, como "obra é criada por pessoa", "manifestação é produzida por corpo colectivo" ou "exemplar é possuído por biblioteca".[^6][^2] Estas relações suportam tarefas de pesquisa por autor, editor, instituição responsável, etc.

Relações entre Grupo 1 e Grupo 3, por seu lado, modelam o sujeito (subject) da obra: "obra tem como assunto conceito X", "obra tem como assunto lugar Y".[^4][^5] Isto permite, por exemplo, agrupar todas as obras sobre um determinado evento histórico ou sobre um determinado lugar.

## 5. FRBR, FRAD, FRSAD, FRBRoo e IFLA LRM

### 5.1 A família de modelos "FRBR"

FRBR foi o primeiro de uma família de modelos conceptuais bibliográficos desenvolvidos pela IFLA, focado nos registos bibliográficos em sentido estrito.[^3] Posteriormente, foram desenvolvidos:

- **FRAD (Functional Requirements for Authority Data)**, centrado em dados de autoridade (nomes, títulos autorizados, pontos de acesso).[^3]
- **FRSAD (Functional Requirements for Subject Authority Data)**, focado em dados de autoridade de assunto.[^3]

Estes três modelos são frequentemente referidos como a “família FRBR”.[^3] Para facilitar implementações em contexto de objectos orientados e de web semântica, foi desenvolvida também uma versão objecto‑orientada, **FRBRoo**, alinhada com o modelo de referência museológico **CIDOC CRM**.[^7][^8]

### 5.2 FRBRoo e harmonização com CIDOC CRM

FRBRoo é uma re‑expressão dos modelos FRBR, FRAD e FRSAD em termos de uma ontologia objecto‑orientada compatível com CIDOC CRM, destinada a facilitar a interoperabilidade semântica entre dados bibliográficos e museológicos.[^7][^9] A harmonização começou em 2003 com a criação de um grupo internacional de trabalho FRBR/CIDOC CRM, com o objectivo de alinhar conceitos e permitir que informação equivalente em bibliotecas e museus seja recuperada sob os mesmos conceitos.[^9][^7]

FRBRoo introduz classes e propriedades mais detalhadas, explicitando conceitos que em FRBR estavam implícitos, e é particularmente adequado para representações em RDF/OWL e para construção de grafos de conhecimento inter‑domínios.[^7][^8]

### 5.3 IFLA LRM e LRMoo

O **IFLA Library Reference Model (IFLA LRM)**, aprovado em 2017, consolida e sucede aos modelos FRBR, FRAD e FRSAD, propondo um modelo conceptual unificado para dados bibliográficos.[^3][^9] LRM clarifica e generaliza vários conceitos, incluindo o das entidades e das relações, e tem vindo a servir de base para a evolução de normas como o RDA.

Em paralelo, o modelo **LRMoo** foi desenvolvido como sucessor de FRBRoo, alinhando a ontologia bibliográfica com o LRM e mantendo a integração com CIDOC CRM.[^9][^7][^10] Este desenvolvimento reforça a trajectória de FRBR como ponto de partida histórico que evolui para modelos mais expressivos e interoperáveis.

## 6. Exemplos concretos de aplicação do modelo FRBR

### 6.1 Exemplo simples: monografia textual

Considere um romance publicado em várias edições e traduções. Num cenário FRBR:[^4][^5]

- **Obra**: o conteúdo intelectual abstracto do romance (a história, personagens, enredo).
- **Expressão A**: texto original na língua em que foi escrito.
- **Expressão B**: tradução para português europeu; **Expressão C**: adaptação simplificada para jovens.
- **Manifestação A1**: primeira edição impressa da expressão A por uma editora específica, com certo ISBN.
- **Manifestação B1**: edição em brochura da tradução portuguesa (Expressão B) por uma editora portuguesa.
- **Exemplar B1‑a**: cópia concreta da Manifestação B1 detida pela Biblioteca X em Lisboa.

Um catálogo "FRBRizado" apresentaria estas entidades agrupadas, permitindo ao utilizador ver claramente que todas as traduções, edições e formatos se referem à mesma obra, e navegar entre elas segundo as suas necessidades.[^2][^5]

### 6.2 Exemplos em catálogos e serviços reais

Projectos conduzidos por OCLC e outras instituições testaram a "FRBRização" de grandes bases de registos MARC, agrupando registos que representam manifestações distintas da mesma obra.[^2] Estes testes mostraram a viabilidade de reorganizar catálogos segundo a estrutura de obra‑expressão‑manifestação‑exemplar, ainda que com desafios significativos na inferência das relações a partir de dados herdados.[^2][^11]

Paralelamente, materiais de formação para o RDA usam exemplos concretos para ilustrar como entidades FRBR são mapeadas para instruções de catalogação e para a estrutura de registos, consolidando a adopção do modelo em práticas correntes.[^6][^12]

## 7. Implicações técnicas para modelação, sistemas e dados ligados

### 7.1 Impacto na concepção de esquemas e bases de dados

Como modelo entidade‑relação, FRBR incentivou o abandono de uma visão de registo plano único em favor de arquitecturas com múltiplas tabelas ou objectos interligados (obra, expressão, manifestação, exemplar, agentes, assuntos).[^2][^5] Em contextos de bases de dados relacionais, isto traduz‑se em esquemas normalizados com chaves e relações explícitas; em contextos orientados a grafos ou RDF, traduz‑se em nós e arestas que correspondem directamente às entidades e relações FRBR.[^7][^13]

Esta estrutura mais granular permite melhor reutilização de dados (por exemplo, registar apenas uma vez os dados de uma obra e ligar‑lhe múltiplas manifestações) e oferece maior flexibilidade para visualizações centradas no utilizador (por exemplo, agrupamento por obra ou por expressão).[^2][^5]

### 7.2 Relação com RDA e códigos de catalogação

O código **Resource Description and Access (RDA)** foi fortemente influenciado por FRBR e pelos modelos associados (FRAD, FRSAD), incorporando a distinção conceptual entre obra, expressão, manifestação e exemplar na sua estrutura de instruções.[^4][^3] Materiais de formação RDA referem explicitamente os três grupos de entidades FRBR e explicam como os elementos de dados se repartem por estes níveis.[^6][^12]

Este alinhamento significa que, embora FRBR não seja uma norma de codificação em si, as suas ideias permeiam as práticas de catalogação modernas, e sistemas que implementam RDA beneficiam de uma base conceptual FRBR.[^4][^3]

### 7.3 FRBR, FRBRoo, LRM e web semântica

A re‑expressão de FRBR em FRBRoo e, depois, em LRMoo, abriu caminho a modelações em ontologias formais, alinhadas com CIDOC CRM e pensadas para web semântica.[^7][^9][^10] Nestes contextos, as entidades FRBR tornam‑se classes de ontologia, as relações tornam‑se propriedades, e os atributos são tratados como propriedades de dados ou de objecto.

Este movimento é particularmente relevante para projectos de dados ligados em bibliotecas, arquivos e museus, onde se pretende integrar dados de múltiplas instituições e domínios num grafo comum e interoperável.[^7][^13] A ligação a CIDOC CRM, em particular, facilita a integração de informação bibliográfica com informação sobre património cultural material e imaterial.[^9][^7]

## 8. Relação com contextos europeus e jurídicos

### 8.1 FRBR no contexto da União Europeia

Embora FRBR não tenha sido concebido especificamente para o domínio jurídico, os seus conceitos inspiraram a modelação de entidades em iniciativas como o European Legislation Identifier (ELI) e a estrutura obra‑expressão‑manifestação adoptada em formatos como Akoma Ntoso e AKN4EU.[^14][^2][^3] Nestes contextos, a ideia de distinguir a obra jurídica (conteúdo normativo abstracto), a expressão (versões linguísticas e temporais) e a manifestação (ficheiro concreto, publicação oficial) é crucial para gerir versões, consolidações e traduções.[^14][^15]

Do ponto de vista técnico, isto aproxima a representação de textos jurídicos da lógica FRBR, facilitando a integração entre catálogos bibliográficos, bases de dados jurídicas e grafos de conhecimento que cruzam legislação, doutrina e jurisprudência.[^14][^13]

### 8.2 Relevância para contextos nacionais e aplicações em ciências sociais

Para instituições e projectos em contextos nacionais (incluindo Portugal), compreender FRBR e a sua evolução para LRM e LRMoo é relevante para:

- Conceber bases de dados e esquemas XML/JSON para colecções bibliográficas, legislativas ou documentais que queiram suportar agregação por obra e por expressão.
- Integrar catálogos tradicionais com sistemas orientados a grafos (por exemplo, Neo4j) ou infra‑estruturas de dados ligados.
- Dialogar com padrões internacionais em iniciativas de interoperabilidade (por exemplo, participação em catálogos colectivos europeus ou em projectos de dados abertos culturais).[^3][^10]

Em áreas como estudos de políticas, direito, sociologia ou psicologia, este tipo de modelação permite construir mapas mais rigorosos de relações entre obras (por exemplo, cadeias de citações, famílias de edições, traduções e adaptações), bem como ligar recursos bibliográficos a contextos institucionais e espaciais.[^13][^10]

## 9. Síntese dos principais conceitos de FRBR

- **Modelo conceptual entidade‑relação** desenvolvido pela IFLA (1998) para descrever o universo bibliográfico e as funções dos registos bibliográficos.[^1][^2]
- **Quatro tarefas do utilizador**: encontrar, identificar, seleccionar e obter, que orientam a escolha de atributos e relações a representar.[^4][^5]
- **Três grupos de entidades**: produtos intelectuais (Grupo 1), agentes responsáveis (Grupo 2) e assuntos (Grupo 3), com destaque para a quadripartição obra–expressão–manifestação–exemplar.[^1][^2][^4]
- **Família FRBR**: extensão do modelo a dados de autoridade (FRAD) e de assunto (FRSAD), e re‑expressão objecto‑orientada (FRBRoo) alinhada com CIDOC CRM.[^7][^3]
- **IFLA LRM e LRMoo**: modelos que sucedem e consolidam FRBR, FRAD, FRSAD e FRBRoo, oferecendo uma base conceptual unificada para dados bibliográficos e sua integração com dados museológicos.[^9][^3][^10]
- **Impacto prático**: influência nos códigos de catalogação (como RDA), reestruturação de catálogos para níveis múltiplos, e papel central em iniciativas de dados ligados e integração entre bibliotecas, arquivos e museus.[^2][^4][^13]

---

## References

1. [Functional Requirements of Bibliographic Records (FRBR)](https://www.loc.gov/aba/pcc/conser/summit/FRBR-summit.html)

2. [FRBR - OCLC](https://www.oclc.org/research/activities/frbr.html)

3. [IFLA’s Bibliographic Conceptual Models](https://www.ifla.org/g/cataloguing/ifla-s-bibliographic-conceptual-models/) - Since the 1990s, IFLA has led the development of conceptual models for bibliographic data. FRBR, Fun...

4. [FRBR and cataloging – ANSSWeb](https://acrl.ala.org/anss/index.php/publications/cataloging-qa/frbr-and-cataloging2012-aug/)

5. [Functional Requirements for Bibliographic Records (FRBR)](https://ebooks.inflibnet.ac.in/lisp3/chapter/knowledge-organization-and-processing-cataloguing/)

6. [australian_train_the_trainer_text_-_rda_train_the_trainer_module_2.docx](https://www.nla.gov.au/sites/default/files/australian_train_the_trainer_text_-_rda_train_the_trainer_module_2.docx)

7. [Short Intro](https://www.cidoc-crm.org/frbroo/short-intro-frbroo)

8. [From FRBR to FRBR OO through CIDOC CRM… - SlideServe](https://www.slideserve.com/cbrandy/from-frbr-to-frbr-oo-through-cidoc-crm-powerpoint-ppt-presentation) - Gain insights into the key features and structures of FRBR and CIDOC CRM, as well as how to utilize ...

9. [LRMoo Short Intro - CIDOC CRM](https://cidoc-crm.org/lrmoo/short-intro-frbroo) - The FRBR model was originally designed as an entity-relationship model by a study group appointed by...

10. [O LRMoo e a integração de dados de bibliotecas e museus - FEBAB](https://portal.febab.org.br/cbbd2024/article/view/3160) - O artigo aborda a integração de dados de bibliotecas e museus proposta pelo LRMoo, uma evolução do F...

11. [Functional requirements for bibliographic records: Critical issues and challenges facing FRBR research and practice](https://asistdl.onlinelibrary.wiley.com/doi/10.1002/bult.2007.1720330609)

12. [FRBR_Module 1_Overview [Read-Only] - Library of Congress](https://www.loc.gov/catworkshop/RDA%20training%20materials/FRBR_Module%201_Overview/FRBR_Module%201_Overview.pdf)

13. [Moving from ISAD(G) to a CIDOC CRM-based Linked Data Model in ...](https://dl.acm.org/doi/10.1145/3605910) - CIDOC CRM and the FRBRoo were also used in the EthnoMuse digital library to represent processes and ...

14. [Semantic Interoperability for Legal Information: Mapping the European Legislation Identifier (ELI) and Akoma Ntoso (AKN) Ontologies](https://dl.acm.org/doi/pdf/10.1145/3614321.3614327) - The legislative landscape, characterized by overwhelming amounts of legal data which, on many occasi...

15. [Akoma Ntoso for EU (AKN4EU) version 3.0 has been published](https://ec.europa.eu/isa2/news/akoma-ntoso-eu-akn4eu-version-30-has-been-published_en/) - Akoma Ntoso for EU (AKN4EU) version 3.0 has been published

