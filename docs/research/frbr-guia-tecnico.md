# Guia técnico sobre o modelo FRBR (Functional Requirements for Bibliographic Records)

## 1. Enquadramento geral do FRBR

Functional Requirements for Bibliographic Records (FRBR) é um modelo conceptual entidade‑relação desenvolvido sob os auspícios da International Federation of Library Associations and Institutions (IFLA) nos anos 1990, publicado em relatório final em 1998.[^1][^2][^3] O objectivo principal do FRBR é explicitar os requisitos funcionais que um registo bibliográfico deve cumprir para apoiar tarefas típicas de utilizadores de catálogos e bases de dados bibliográficos, de forma independente de códigos de catalogação específicos.[^4][^5]

O modelo FRBR promove uma visão centrada no utilizador, articulando entidades, atributos e relações em torno de quatro tarefas de alto nível (find, identify, select, obtain) que descrevem como as pessoas procuram, reconhecem, escolhem e acedem a recursos bibliográficos.[^4][^5] Desta forma, FRBR serve como base conceptual para o desenho de esquemas de metadados, formatos de registo e interfaces de sistemas, em vez de ser um formato ou código de catalogação em si mesmo.[^4][^6]

## 2. Estrutura conceptual: entidades, atributos e relações

FRBR assenta em três componentes principais: grupos de entidades, atributos de cada entidade e relações entre entidades.[^2][^5]

### 2.1 Grupos de entidades

O modelo organiza as entidades em três grupos:[^4][^5]

- **Grupo 1**: produtos do esforço intelectual ou artístico que são alvo de interesse dos utilizadores: *obra* (work), *expressão* (expression), *manifestação* (manifestation) e *exemplar* (item) – frequentemente referidos pela sigla WEMI.[^4][^2]
- **Grupo 2**: entidades responsáveis pela criação, produção, distribuição ou custódia dos recursos do grupo 1: *pessoa* (person), *família* (family, introduzida posteriormente em FRAD) e *entidade colectiva* (corporate body).[^7][^5]
- **Grupo 3**: entidades que podem servir de assunto de obras: *conceito* (concept), *objecto* (object), *evento* (event) e *lugar* (place), além das próprias entidades dos grupos 1 e 2 que também podem ser assunto.[^4][^5]

O Grupo 1 é a base do modelo, estruturando a visão do "universo bibliográfico" em torno da distinção entre a criação intelectual abstracta (obra), a sua realização intelectual concreta (expressão), a materialização física dessa expressão (manifestação) e o exemplar individual (item).[^4][^2]

### 2.2 Atributos

Para cada entidade, FRBR enumera atributos que capturam características relevantes para as tarefas de utilizador.[^2][^5] Por exemplo:

- Obra: título da obra, forma da obra, data da obra, público‑alvo, etc.[^5]
- Expressão: forma da expressão (texto, notação musical, som), idioma, contexto de realização, etc.[^5]
- Manifestação: título tal como aparece na fonte de informação, edição, designação de edição, forma de suporte, dimensões, etc.[^5][^3]
- Item: assinatura, identificador de exemplar, estado de conservação, restrições de acesso, etc.[^5]

A associação de atributos a entidades visa tanto satisfazer tarefas de identificação (reconhecer um recurso como o pretendido) como apoiar a selecção entre alternativas (por exemplo, escolher entre diferentes edições).[^2][^5]

### 2.3 Relações

Relações em FRBR ligam entidades entre si e são fundamentais para permitir a navegação no universo bibliográfico.[^4][^2] Alguns exemplos incluem:

- Relações entre entidades do grupo 1: uma obra tem expressões, uma expressão é realizada numa manifestação, uma manifestação é exemplificada por items.[^4]
- Relações entre grupos 1 e 2: uma obra é criada por uma pessoa ou entidade colectiva, uma manifestação é produzida por um editor.[^4][^7]
- Relações entre obras: uma obra adapta outra, continua outra, comenta outra, etc.[^4]
- Relações de assunto entre grupos 1/2 e 3: uma obra tem como assunto um conceito, objecto, evento, lugar ou outra entidade.[^4][^5]

O relatório FRBR sublinha que as relações são o "veículo" para que o utilizador navegue entre entidades relacionadas, descobrindo versões, traduções, adaptações, comentários e críticas a partir de um ponto de entrada inicial.[^4]

## 3. As quatro tarefas de utilizador

FRBR identifica quatro tarefas de utilizador que os registos bibliográficos devem suportar:[^4][^5]

1. **Find (Encontrar)**: permitir ao utilizador localizar entidades que correspondam a critérios de pesquisa (por exemplo, por autor, assunto, título).[^5][^6]
2. **Identify (Identificar)**: confirmar que a entidade encontrada corresponde àquilo que o utilizador procura (por exemplo, distinguir entre obras com títulos semelhantes).[^4][^5]
3. **Select (Seleccionar)**: escolher a entidade que melhor satisfaz as necessidades do utilizador (por exemplo, seleccionar uma tradução, edição específica ou formato).[^4][^5]
4. **Obtain (Obter)**: fornecer os meios para aceder ao exemplar ou manifestação desejada (por exemplo, localização física, disponibilidade electrónica, condições de acesso).[^4][^5]

Estas tarefas são utilizadas como referência para determinar quais atributos e relações são necessários em registos bibliográficos de forma a que os catálogos possam cumprir eficazmente as funções para os diferentes tipos de utilizadores.[^2][^6]

## 4. Detalhe do Grupo 1: WEMI

### 4.1 Obra (Work)

Obra é definida como uma "criação intelectual ou artística distinta", entendida como entidade abstracta.[^4][^2] É independente de qualquer materialização específica: por exemplo, "Os Lusíadas" enquanto criação literária, ou a "Nona Sinfonia" de Beethoven enquanto composição musical.[^4]

A obra não é um texto físico nem uma língua particular, mas o conteúdo conceptual subjacente às várias expressões possíveis.[^4][^5] Atributos típicos incluem o título preferido da obra, forma da obra (romance, sinfonia, relatório técnico), data, finalidade e público‑alvo.[^5]

### 4.2 Expressão (Expression)

Expressão é "a forma intelectual ou artística específica que uma obra assume cada vez que é concretizada".[^4][^2] Inclui, por exemplo, uma tradução específica de um romance, um arranjo musical de uma sinfonia, ou a versão revista de um relatório.[^4]

Cada expressão partilha com a obra o conteúdo conceptual, mas difere de outras expressões pela forma de realização – idioma, notação, forma de apresentação do texto, revisão, anotação.[^4][^5] Atributos incluem a língua da expressão, forma da expressão (texto, áudio, vídeo), extensão, características linguísticas e apresentação.[^5]

### 4.3 Manifestação (Manifestation)

Manifestação é a "materialização física" de uma expressão, correspondendo ao conjunto de exemplares produzidos como resultado de um processo de publicação, produção ou distribuição.[^4][^2] Uma edição específica de um livro, com um determinado editor, ano e formato, constitui uma manifestação.[^4]

Atributos de manifestação incluem título tal como figura na fonte, declaração de responsabilidade, edição, data de publicação, editor, série, formato físico, dimensões, identificadores como ISBN.[^5][^3] São estes atributos que correspondem de perto aos dados tradicionalmente registados em listas e catálogos bibliográficos.[^2]

### 4.4 Item (Item)

Item é um exemplar individual de uma manifestação, entidade concreta.[^4][^2] Cada cópia física de uma determinada edição presente numa biblioteca é um item distinto, com a sua própria cota, estado de conservação, marcas de posse, anotações, etc.[^4][^7]

Em ambiente digital, um item pode ser uma instância específica de um ficheiro (por exemplo, um ficheiro alojado num servidor com um identificador persistente), embora a modelação de items digitais levante nuances que foram discutidas em extensões e aplicações posteriores do modelo.[^3][^8]

## 5. Grupos 2 e 3: agentes e assuntos

### 5.1 Grupo 2: agentes

O Grupo 2 inclui entidades que assumem responsabilidade pela criação, produção, disseminação ou custódia das entidades do Grupo 1.[^4][^7] FRBR define originalmente *pessoa* (indivíduo) e *entidade colectiva* (organização, instituição, grupo), enquanto modelos relacionados como FRAD introduzem a entidade *família*.[^7][^5]

Atributos de pessoa podem incluir nome, datas de nascimento e morte, títulos, afiliação; para entidades colectivas incluem nome, tipo de organização, local, data de fundação.[^7][^5] As relações entre agentes e obras ou expressões são essenciais para tarefas de pesquisa por autor, compositor, realizador, etc.[^4]

### 5.2 Grupo 3: assuntos

O Grupo 3 abrange entidades que podem ser assunto de uma obra: conceitos (ideias ou noções abstractas), objectos (entidades materiais), eventos (ocorrências com extensão temporal) e lugares (localizações geográficas ou espaciais).[^4][^5] Além disso, as entidades dos grupos 1 e 2 também podem ocorrer como assuntos.

Este grupo foi posteriormente aprofundado em FRSAD (Functional Requirements for Subject Authority Data), que desenvolve modelo específico para dados de autoridade de assunto, incluindo a entidade *nomen* para lidar com formas de nomeação.[^9][^10] FRBR, contudo, estabelece já a importância das relações de assunto para a navegação temática nos catálogos.[^4]

## 6. Relações detalhadas e navegação no universo bibliográfico

FRBR enumera diversos tipos de relações entre entidades, que podem ser agrupadas em:[^4][^2]

- Relações de equivalência: entre manifestações que representam a mesma expressão (por exemplo, reimpressões).[^4]
- Relações derivativas: entre obras ou expressões em que uma é derivada de outra (traduções, adaptações, resumos, revisões).[^4][^5]
- Relações descritivas: entre uma obra e uma obra que a descreve, comenta, critica ou analisa (por exemplo, uma crítica literária).[^4]
- Relações de parte‑todo: entre obras ou manifestações que se compõem mutuamente (capítulos, volumes, séries).[^4][^5]
- Relações de acompanhamento: obras concebidas para serem usadas conjuntamente (manual + caderno de exercícios).[^4]

Estas relações são fundamentais para funcionalidades avançadas de catálogos, como agrupamento de registros por obra, apresentação de todas as traduções disponíveis, ligação a comentários e críticas, ou navegação entre volumes de uma mesma série.[^4][^6]

## 7. Exemplos concretos de aplicação do modelo FRBR

### 7.1 Exemplo simples: romance traduzido

Considere um romance originalmente publicado em inglês e traduzido para português.

- **Obra**: a criação literária abstracta, independente de língua (por exemplo, o enredo e personagens).[^4]
- **Expressões**: a expressão original em inglês e a expressão traduzida em português; cada tradução (de tradutor diferente, com revisões) é uma expressão distinta.[^4][^5]
- **Manifestações**: diferentes edições da tradução portuguesa (por exemplo, primeira edição em capa mole, edição revista em capa dura), cada uma com atributos específicos de publicação.[^5]
- **Items**: os exemplares individuais dessas edições nas diversas bibliotecas portuguesas.[^7]

Num catálogo orientado por FRBR, o utilizador pode ver todas as expressões e manifestações agrupadas sob a mesma obra, facilitando a escolha da tradução e da edição desejadas, e depois localizar um item disponível para empréstimo.[^4][^6]

### 7.2 Exemplo técnico: uma norma ou relatório em múltiplos formatos

Considere um relatório técnico da Comissão Europeia disponibilizado em PDF, HTML e como ficheiro XML estruturado.

- **Obra**: o relatório enquanto conteúdo intelectual (por exemplo, uma directriz de política).[^4]
- **Expressão**: o texto do relatório numa determinada língua (por exemplo, versão portuguesa), independentemente de formato digital.[^5]
- **Manifestações**: a edição PDF publicada em 2024, a edição HTML no portal institucional e a edição XML conformante com um esquema específico (por exemplo, AKN4EU no contexto jurídico).[^2][^5]
- **Items**: instâncias concretas destes ficheiros, armazenadas em servidores ou repositórios distintos.[^3]

Este tipo de modelação é útil quando se articulam modelos como FRBR com formatos técnicos específicos (por exemplo, AKN4EU), permitindo separar a camada conceptual (FRBR) da camada de representação material (XML, PDF).[^11][^12]

## 8. Implementações, impacto e ligação a outros modelos

### 8.1 Influência em códigos de catalogação e formatos

FRBR teve impacto significativo na revisão de códigos de catalogação e modelos de metadados a partir dos anos 2000.[^10][^6] O código Resource Description and Access (RDA), por exemplo, foi desenhado explicitamente para se alinhar com os modelos FRBR e FRAD, adoptando as entidades WEMI e muitas das relações definidas.[^10][^13]

Projectos nacionais como o programa francês de Transição Bibliográfica (Abes e BnF) assumem FRBR, FRAD e, mais recentemente, IFLA LRM como base para remodelar dados bibliográficos e catálogos em direcção a uma abordagem por entidades.[^10] Em vários países europeus, incluindo contextos universitários, têm sido desenvolvidos catálogos experimentais FRBRizados, que agrupam registos por obra e expressão em vez de apresentarem apenas listas planas de manifestações.[^8][^10]

### 8.2 FRBRoo e integração com CIDOC CRM

Uma evolução importante foi o desenvolvimento de FRBRoo, uma versão orientada a objectos do modelo FRBR, concebida em articulação com o modelo CIDOC CRM usado em dados de museus.[^10][^8] FRBRoo permite representar o universo bibliográfico em termos de classes e propriedades compatíveis com ontologias de património cultural, facilitando integração de dados de bibliotecas, arquivos e museus.[^8][^14]

Esta abordagem é relevante em contextos de dados ligados e Web Semântica, nos quais se pretende interligar descrições de recursos bibliográficos com descrições de objectos museológicos, eventos históricos e outros recursos culturais, em grafos unificados.[^8][^15]

### 8.3 IFLA LRM como sucessor de FRBR

Em 2017, a IFLA publicou o IFLA Library Reference Model (IFLA LRM), que consolida FRBR, FRAD e FRSAD num único modelo conceptual harmonizado.[^16][^8] IFLA LRM mantém as entidades centrais de FRBR, mas introduz uma estrutura hierárquica mais geral (por exemplo, a entidade *res* como superclasse genérica), redefine algumas entidades e relações, e acrescenta a tarefa de utilizador *explore*.[^16][^10]

IFLA LRM foi concebido explicitamente como modelo compatível com a Web Semântica, pensado como ontologia para dados ligados, e serve hoje de referência para programas de transição bibliográfica e para revisões de formatos em todo o mundo.[^10][^8] FRBR, embora ainda importante para compreender a génese do modelo, deve ser hoje lido em articulação com LRM quando se projectam novos sistemas e infra‑estruturas.[^8][^14]

## 9. Ligações com outros temas relevantes

### 9.1 Relação com modelos de representação jurídica (exemplo: AKN4EU)

No domínio jurídico, modelos como FRBR são usados para conceptualmente distinguir entre a obra jurídica (por exemplo, um regulamento europeu enquanto criação normativa), as suas expressões (diferentes versões linguísticas ou redacções consolidadas), as manifestações (edições em JOUE, ficheiros XML em AKN4EU, PDFs) e os exemplares (ficheiros concretos em repositórios).[^11][^17]

A especificação AKN4EU, baseada em Akoma Ntoso, adopta conceitos FRBR para organizar metadados de obras jurídicas (work, expression, manifestation), suportando identificação robusta de versões e consolidações.[^11][^12] Esta articulação permite associar identificadores URIs (por exemplo, ELI) a diferentes níveis FRBR, facilitando a gestão do ciclo de vida legislativo e a integração com grafos de conhecimento jurídicos.[^11][^12]

### 9.2 FRBR, dados ligados e ontologias

O modelo FRBR foi uma das primeiras tentativas no domínio das bibliotecas de formalizar o "universo bibliográfico" de forma explícita em termos de entidades e relações, abrindo caminho à sua expressão em ontologias RDF/OWL.[^8][^15] Trabalhos recentes, especialmente no âmbito do IFLA LRM e FRBRoo, visam precisamente tornar estes modelos adequados para publicação e integração de metadados bibliográficos como dados ligados na Web.[^10][^8]

Para projectos de grafos de conhecimento (por exemplo, em Neo4j) que integrem legislação, doutrina, jurisprudência e outros recursos, FRBR (e LRM) fornecem um quadro conceptual robusto para distinguir níveis de abstração (obra vs expressão vs manifestação) e gerir relações de adaptação, comentário, crítica, tradução, etc.[^8][^14] Em combinação com outros vocabulários (como Dublin Core, ontologias de domínios específicos ou modelos como CIDOC CRM), FRBR permite estabelecer pontes entre mundos bibliográficos, jurídicos e de património cultural.[^15][^10]

## 10. Síntese dos principais conceitos

- **FRBR** é um modelo conceptual entidade‑relação desenvolvido pela IFLA para explicitar requisitos funcionais de registos bibliográficos, centrado em tarefas de utilizador (find, identify, select, obtain).[^1][^4][^5]
- **Entidades** organizam‑se em três grupos: WEMI (obra, expressão, manifestação, item), agentes (pessoa, entidade colectiva, família) e assuntos (conceito, objecto, evento, lugar).[^4][^7][^5]
- **Atributos** descrevem características de cada entidade relevantes para identificação e selecção; **relações** ligam entidades, permitindo navegação entre versões, traduções, adaptações, comentários e assuntos.[^2][^5]
- **Implementações** de FRBR influenciaram códigos como RDA, programas de transição bibliográfica europeus e catálogos orientados a entidades.[^10][^6]
- **Evoluções** como FRBRoo e IFLA LRM integram FRBR em modelos mais amplos, compatíveis com Web Semântica e dados ligados, consolidando a família de modelos FRBR/FRAD/FRSAD.[^16][^8][^14]
- **Integrações** com domínios como o jurídico (por exemplo, AKN4EU) mostram como FRBR pode enquadrar a distinção entre níveis conceptuais e materiais de recursos normativos, apoiando desde a gestão de versões até à construção de grafos de conhecimento.[^11][^12]

---

## References

1. [Functional requirements for bibliographic records : final report](https://www.loc.gov/item/2001433363/) - Includes index. Issued also electronically in HTML and PDF formats.

2. [FRBR](https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/frbr/frbr.pdf)

3. [Functional Requirements for Bibliographic Records](https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/frbr/frbr_2008.pdf)

4. [Functional Requirements for Bibliographic Records - Wikipedia](https://en.wikipedia.org/wiki/Functional_Requirements_for_Bibliographic_Records)

5. [Functional Requirements for Bibliographic Records (FRBR)](https://ebooks.inflibnet.ac.in/lisp3/chapter/knowledge-organization-and-processing-cataloguing/)

6. [FRBR_Module 1_Overview [Read-Only] - Library of Congress](https://www.loc.gov/catworkshop/RDA%20training%20materials/FRBR_Module%201_Overview/FRBR_Module%201_Overview.pdf)

7. [australian_train_the_trainer_text_-_rda_train_the_trainer_module_2.docx](https://www.nla.gov.au/sites/default/files/australian_train_the_trainer_text_-_rda_train_the_trainer_module_2.docx)

8. [IFLA Library Reference Model (IFLA LRM)](https://www.imrpress.com/journal/ko/45/4/10.5771/0943-7444-2018-4-310) - In 1998, the FRBR model (Functional Requirements for Bibliographic Records) was developed under the ...

9. [Functional Requirements for Bibliographic Records and Co-chair and Secretary of the Ifla Working Group on the Functional Requirements for Subject Authority Records (frsar). from a Conceptual Model to Application and System Development](https://www.semanticscholar.org/paper/6b6c7973d3dbd7a2970fa0b6bd38f1454e98f005)

10. [Bibliographic transition - abes.fr](https://abes.fr/en/normalisation-modeles-et-formats/transition-bibliographique/) - The challenge of the bibliographicalAbes transition

11. [Semantic Interoperability for Legal Information: Mapping the European Legislation Identifier (ELI) and Akoma Ntoso (AKN) Ontologies](https://dl.acm.org/doi/pdf/10.1145/3614321.3614327) - The legislative landscape, characterized by overwhelming amounts of legal data which, on many occasi...

12. [A Common Structured Format for EU Legislative Documents](https://joinup.ec.europa.eu/collection/semic-support-centre/solution/common-structured-format-eu-legislative-documents)

13. [FRBR: Fundamental Concepts](https://www.loc.gov/catworkshop/RDA%20training%20materials/LC%20RDA%20Training/FRBR_Module%201_Overview/FRBRFundamentals_20120809_student.pdf)

14. [Osservazioni sul modello IFLA Library Reference Model](https://dialnet.unirioja.es/descarga/articulo/6119078.pdf)

15. [IFLA LRM - Finally Here](https://dcpapers.dublincore.org/files/articles/952137861/dcmi-952137861.pdf)

16. [IFLA LRM- finally here](https://dcevents.dublincore.org/IntConf/dc-2017/paper/download/499/606)

17. [Akoma Ntoso - Wikipedia, the free encyclopedia](https://en.wikipedia-on-ipfs.org/wiki/Akoma_Ntoso)

