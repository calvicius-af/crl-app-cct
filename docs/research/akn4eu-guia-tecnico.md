# Guia técnico sobre AKN4EU (Akoma Ntoso for European Union)

## 1. Enquadramento geral do AKN4EU

Akoma Ntoso for European Union (AKN4EU) é a especificação técnica comum, baseada em XML, adoptada pelas instituições da União Europeia para representar e trocar documentos legislativos de forma estruturada e legível por máquina.[^1][^2][^3] AKN4EU é definido e mantido pelo Interinstitutional Metadata and Formats Committee (IMFC), que desde 2018 tem o mandato de desenvolver normas interinstitucionais para conteúdos e metadados estruturados e para a sua troca automatizada e segura.[^1][^2][^4]

A especificação AKN4EU é uma "localização" do standard internacional Akoma Ntoso (OASIS LegalDocumentML) ao contexto da legislação da UE, reutilizando o vocabulário XML de base mas restringindo elementos, atributos e padrões de modelação para se alinhar com o Common Vocabulary (CoV) interinstitucional.[^5][^4][^6] Na prática, AKN4EU define como os conceitos jurídicos e estruturais acordados entre juristas, tradutores e outros profissionais (CoV) são codificados em elementos Akoma Ntoso em ficheiros XML usados em todo o ciclo decisório da UE.[^5][^4]

## 2. Relação entre CoV, Akoma Ntoso e AKN4EU

O IMFC Common Vocabulary (CoV) é um conjunto de conceitos estruturais (por exemplo, artigo, considerando, anexo, título, preâmbulo) que reflectem a forma como as pessoas que trabalham com textos legais da UE se referem às suas partes.[^4] Cada conceito no CoV possui uma definição, rótulo e, muitas vezes, relações hierárquicas com outros conceitos (por exemplo, artigos contidos em capítulos).[^4]

Num segundo nível, Akoma Ntoso fornece o vocabulário XML genérico (elementos como `<act>`, `<bill>`, `<article>`, `<preamble>`, `<body>`, `<attachment>`) e o respectivo esquema XSD que podem representar grande variedade de documentos legislativos, parlamentares e judiciais.[^7][^6] AKN4EU é a concretização técnica que mapeia explicitamente cada conceito CoV para elementos e atributos Akoma Ntoso, definindo também restrições de uso e regras adicionais de validação.[^5][^8][^4]

Deste modo, AKN4EU funciona como camada de integração: por um lado preserva a semântica interinstitucional expressa no CoV e, por outro, garante compatibilidade com o standard Akoma Ntoso e com infra‑estruturas que o suportam (por exemplo, editores XML, pipelines de publicação, ferramentas de análise semântica).[^9][^5][^6]

## 3. Escopo e versões de AKN4EU

As versões iniciais de AKN4EU foram focadas em actos jurídicos adoptados através do procedimento legislativo ordinário (regulamentos, directivas, decisões) e nas correspondentes propostas legislativas.[^1][^3] A versão 3.0, adoptada pelo IMFC em 17 de Abril de 2020, consolidou esta cobertura e veio acompanhada de documentação estruturada em volumes e de uma biblioteca de exemplos XML de regulamentos, directivas, decisões e propostas.[^9][^8]

A documentação mais recente (por exemplo, série 4.1 em partes 1–4 disponível em apresentações técnicas) mostra a extensão gradual do escopo a outros tipos de documentos, incluindo resoluções do Parlamento Europeu, anexos complexos com tabelas e imagens e, em versões mais recentes, actos autónomos da Comissão e documentos do Comité Económico e Social Europeu.[^9][^5][^10] Comunicações recentes do Gabinete das Publicações indicam a adopção de AKN4EU 5.0, que incorpora Akoma Ntoso 3.1 e alarga ainda mais o perímetro interinstitucional.[^11]

Embora AKN4EU esteja operacional em vários fluxos de trabalho, a própria página de vocabulários da UE sublinha que a especificação continua a ser "work in progress" e que ainda não cobre todos os tipos de documentos.[^1][^2] Isto implica coexistência com formatos legados (por exemplo, bases SGML/XML anteriores ou formatos internos) e a necessidade de estratégias de migração e conversão incremental.

## 4. Arquitectura conceptual de um documento AKN4EU

### 4.1 Estrutura de alto nível

Um documento legislativo em AKN4EU é, em essência, um documento Akoma Ntoso com uma raiz `<akomaNtoso>` que contém um elemento de tipo de documento (por exemplo, `<act>` para um acto adoptado ou `<bill>` para uma proposta).[^6][^5] No caso de um regulamento, por exemplo, a estrutura típica é:

```xml
<akomaNtoso>
  <act name="REG">
    <meta>…</meta>
    verPage>…</coverPage>
    <preface>…</preface>
    <preamble>…</preamble>
    <body>…</body>
    clusions>…</conclusions>
    <attachments>…</attachments>
  </act>
</akomaNtoso>
```

As componentes principais são:

- `<meta>`: metadados normativos, técnicos e de gestão (identificadores, citações, relações com outros actos, informações de publicação, etc.).[^5][^8]
- `verPage>`: elementos de apresentação como título completo, número do acto, dados de adopção, entidade emissora (Parlamento, Conselho, etc.).[^5][^10]
- `<preface>`: partes introdutórias não normativas (por exemplo, fórmulas, referências protocolares).[^5]
- `<preamble>`: considerandos (`<recital>` em termos CoV), geralmente estruturados em parágrafos enumerados.[^5][^10]
- `<body>`/`<mainBody>`: enunciado normativo (artigos, capítulos, secções, anexos remissivos, etc.).[^5]
- `clusions>`: fórmulas finais e assinaturas.[^10]
- `<attachments>`: anexos, frequentemente estruturados como documentos separados `<doc name="ANNEX">` com a sua própria capa e corpo.[^10]

### 4.2 Modelação do corpo normativo

O corpo de um acto utiliza um modelo de conteúdo relativamente uniforme em AKN4EU, aplicável tanto a actos legislativos como a outros documentos e plenamente alinhado com a sintaxe ELI para identificar subdivisões.[^5] Elementos como `<article>`, `hapter>`, `<section>`, `<subsection>` e `<paragraph>` formam a hierarquia, sendo cada um identificado por atributos de número e, por vezes, por identificadores únicos (`eId`).[^5][^8]

No contexto AKN4EU, a modelação é conduzida pelo CoV, que estabelece, por exemplo, que os artigos são contidos no corpo principal, que os considerandos precedem o articulado e que os anexos são referenciados como documentos distintos, mas ligados.[^4][^5] A especificação define ainda regras de ocorrência (por exemplo, certos tipos de documentos têm sempre preâmbulo e conclusões) e convenções de marcação para estruturas recorrentes como tabelas, listas de pontos e fórmulas.[^5][^10]

## 5. Metadados e ligação ao ELI

### 5.1 Metadados normativos e técnicos

O elemento `<meta>` em AKN4EU agrega metadados essenciais para gestão do ciclo de vida do acto, interoperabilidade com outros sistemas e exploração avançada (pesquisa, navegação por relações, etc.).[^5][^8] Entre os metadados mais relevantes encontram‑se:

- Identificadores FRBR (work, expression, manifestation) para distinguir a obra jurídica, a expressão linguística e a manifestação concreta (ficheiro, publicação).[^6][^8]
- Identificadores ELI (European Legislation Identifier) expressos como URIs, eventualmente com fragmentos que direccionam para subdivisões específicas do acto.[^9][^5]
- Relações com outros actos (por exemplo, acto que altera, revoga, codifica ou complementa outro), frequentemente codificadas com elementos de referência (`<relation>`, `<modification>`, `<passiveModifications>`).[^9][^12]
- Metadados de publicação (JOUE, datas de adopção e entrada em vigor, número CELEX).[^9][^8]

A documentação AKN4EU inclui uma secção de correspondência entre termos do CoV e elementos de metadados Akoma Ntoso, o que garante consistência semântica entre a análise de negócio e a codificação XML.[^5][^4]

### 5.2 Integração com o European Legislation Identifier (ELI)

Um dos objectivos explícitos de AKN4EU é assegurar plena compatibilidade com a sintaxe do European Legislation Identifier, permitindo que cada acto e cada subdivisão (artigo, número, alínea, anexo) tenha um identificador URI estável e interoperável.[^9][^13] O modelo de conteúdo do corpo foi desenhado para suportar directamente a sintaxe de fragmentos ELI, garantindo que a navegação por URI coincide com a estrutura textual.[^5][^9]

Trabalhos recentes de interoperabilidade semântica demonstram como as ontologias associadas a ELI e Akoma Ntoso podem ser mapeadas, de forma a ligar representações de textos jurídicos com metadados e grafos de conhecimento.[^13] Isto é particularmente relevante para aplicações de linked open legal data e para projectos de espaço europeu de dados jurídicos (European Legal Data Space), nos quais AKN4EU é referido como componente central.[^11][^3]

## 6. Validação, esquemas e pacotes AKN4EU

### 6.1 Esquemas XML e regras de validação

Do ponto de vista técnico, a validação de documentos AKN4EU depende de um conjunto de artefactos: esquemas XML (XSD), regras Schematron e, nalguns casos, validações adicionais de negócio implementadas em software.[^14][^8] O standard Akoma Ntoso fornece o esquema de base, enquanto AKN4EU restringe o espaço de soluções, definindo subconjuntos de elementos e atributos permitidos e regras de coocorrência.[^5][^8]

A documentação AKN4EU especifica regras como:

- Quais elementos Akoma Ntoso são autorizados em cada tipo de documento (por exemplo, combinação específica de `<preamble>`, `<body>`, `<attachments>` em regulamentos).[^10][^5]
- Quais atributos são obrigatórios ou proibidos (por exemplo, valores permitidos para o atributo `@name` de `<act>`, como "REG", "DIR", "DEC").[^10]
- Restrições sobre aninhamento de elementos (por exemplo, não permitir determinados tipos de secções dentro de outros).[^5]
- Consistência entre metadados e conteúdo (por exemplo, verificar se um acto marcado como "revoga" outro efectivamente contém cláusulas de revogação referenciadas).[^8]

Os esquemas e exemplos podem ser obtidos a partir do portal de vocabulários da UE, na secção de "Schemas" associada a AKN4EU, bem como através de pacotes de documentação disponibilizados pelo Gabinete das Publicações.[^14][^9]

### 6.2 Estrutura do pacote AKN4EU_ZIP

Para trocas interinstitucionais, AKN4EU prevê um pacote ZIP com convenções de estrutura e de nomenclatura de ficheiros, designado AKN4EU_ZIP.[^5] A documentação de directrizes (Part 1 – guideline) descreve:

- Estrutura de directórios e nome dos ficheiros XML principais (por exemplo, separando o acto principal de anexos).[^5]
- Ficheiros auxiliares, como metadados adicionais, folhas de estilo ou artefactos de validação opcionais.[^5]
- Convenções para múltiplas línguas (por exemplo, ficheiros separados por versão linguística ou marcação da língua dentro do mesmo ficheiro, dependendo do caso de uso).[^5]

Estas convenções são essenciais para integração com sistemas institucionais (por exemplo, repositórios JOUE, sistemas de gestão legislativa do Parlamento, Conselho e Comissão) e para pipelines automatizados de tratamento, tradução e publicação.[^9][^11]

## 7. Exemplos concretos de modelação em AKN4EU

### 7.1 Acto legislativo (regulamento)

A documentação "Document types – Part 2" mostra como um regulamento típico da UE é representado em AKN4EU.[^10] O elemento `<act>` tem o atributo `name="REG"` e contém a estrutura padrão de capa, preâmbulo, corpo, conclusões e anexos.[^10]

No preâmbulo, cada considerando é frequentemente modelado como um parágrafo (`<p>`) eventualmente dentro de um elemento estrutural que representa o conjunto de recitais, com numeração explícita.[^5][^10] O corpo contém `<article>` numerados, eventualmente agrupados em capítulos (`hapter>`), com subdivisões internas em parágrafos, números e alíneas, com marcação consistente que permite referir cada unidade por URI ELI.[^5][^9]

Anexos complexos, como tabelas técnicas, são modelados através de elementos de tabela Akoma Ntoso (por exemplo, `<table>`, `<tr>`, `<td>`), com regras AKN4EU adicionais para cabeçalhos, notas de rodapé e referências cruzadas.[^5][^10] Este nível de granularidade é crucial, por exemplo, para aplicar automaticamente alterações posteriores a anexos ou para gerar vistas específicas em sistemas de informação.[^9][^8]

### 7.2 Proposta de directiva (bill)

Para propostas legislativas, AKN4EU utiliza o elemento `<bill>`, com estrutura análoga à de `<act>`, mas com metadados específicos que indicam o estado no processo legislativo (por exemplo, propostas da Comissão, textos do Conselho, textos em primeira leitura do Parlamento).[^9][^5] A modelação permite, por exemplo, comparar automaticamente versões sucessivas de um texto, identificando modificações activas (introduzidas por um documento em outro) e passivas (efeitos sofridos por um texto).[^12][^9]

Esta distinção é importante para análise da evolução legislativa e para ferramentas que visualizam a cadeia de alterações ao longo do tempo, algo particularmente relevante para quem acompanha a transposição em direito nacional, incluindo o contexto português.[^13][^9]

## 8. Conceitos técnicos chave

### 8.1 FRBR e tipos de identificadores

Akoma Ntoso e, por extensão, AKN4EU, adoptam o modelo FRBR (Functional Requirements for Bibliographic Records) para distinguir entre:

- Obra (work): o conteúdo jurídico abstracto (por exemplo, o regulamento enquanto tal).[^6]
- Expressão (expression): uma versão linguística e temporal específica (por exemplo, o texto consolidado em português à data X).[^6][^8]
- Manifestação (manifestation): a concretização física ou digital (ficheiro XML, PDF no JOUE, etc.).[^6][^8]

Os identificadores ELI e outros identificadores institucionais (por exemplo, CELEX) podem ser associados a diferentes níveis, facilitando tarefas como manutenção de versões, consolidação automática e gestão de traduções.[^13][^9]

### 8.2 Modificações activas e passivas

No ecossistema Akoma Ntoso, uma "modificação" é uma mudança que um documento introduz em outro.[^12] Distinguem‑se habitualmente:

- Modificações activas: disposições do documento A que alteram explicitamente o documento B (por exemplo, "O artigo 3.º do Regulamento (UE) 2017/1938 passa a ter a seguinte redacção").[^12]
- Modificações passivas: efeitos sofridos pelo documento B em virtude de actos posteriores, podendo ser inferidas a partir das marcas de modificação registadas.[^12]

Em AKN4EU, estas relações são capturadas em metadados e, muitas vezes, em elementos estruturais ou atributos que anotam o texto alterado, permitindo gerar vistas consolidadas ou linhas de tempo de alterações de forma automatizada.[^9][^8]

### 8.3 Componentes reutilizáveis e anexos

A especificação AKN4EU prevê uma distinção clara entre o documento principal e componentes anexos ou incorporados, quer através de `<attachments>`, quer por meio de referências a outros documentos (`<documentRef>`).[^10][^5] Isto é relevante para:

- Reutilização de anexos comuns a vários actos.
- Manutenção separada de anexos de grande dimensão (por exemplo, listas de códigos, tabelas técnicas).[^9][^8]
- Integração com repositórios externos (por exemplo, bases de dados técnicas, listas TARIC, etc.), embora este aspecto vá para além do núcleo AKN4EU estrito.[^9]

## 9. Integração com outros sistemas e iniciativas europeias

### 9.1 Sistemas institucionais e JOUE

AKN4EU foi concebido para se integrar com o ecossistema do Gabinete das Publicações da UE (OP), incluindo os sistemas de gestão do Jornal Oficial da União Europeia (JOUE) e o Portal de Dados abertos jurídicos.[^9][^3] A utilização de um formato estruturado comum permite pipeline de produção mais automatizado desde a redacção interna até à publicação e reutilização em portais públicos.[^1][^11]

Ao mesmo tempo, AKN4EU articula‑se com programas como o Acquis Management Programme da Comissão, centrado na gestão do acervo legislativo e na sua acessibilidade para humanos e máquinas.[^11] Esta integração é importante para iniciativas como o European Legal Data Space, onde dados jurídicos estruturados são insumo central para aplicações analíticas e de inteligência artificial.[^11][^3]

### 9.2 Interoperabilidade com sistemas de migração, asilo e justiça

Embora AKN4EU se concentre na representação de documentos legislativos, a sua utilização interage com outras infra‑estruturas de interoperabilidade de informação na UE, como os sistemas de fronteiras, vistos, asilo e registos criminais (EES, VIS, Eurodac, ETIAS, SIS, ECRIS‑TCN) que partilham um quadro comum de interoperabilidade técnica.[^15][^16][^17] Estes sistemas utilizam regulamentos que, sendo publicados e mantidos em formato estruturado AKN4EU, podem ser mais facilmente ligados a especificações técnicas, esquemas de dados e documentação de implementação.[^15][^17]

No domínio específico do asilo, a Agência da União Europeia para o Asilo (EUAA) desenvolve bases de dados e plataformas (IDS, Case Law Database, Who is Who in International Protection) que dependem de uma representação clara e interoperável das fontes normativas do Sistema Europeu Comum de Asilo (CEAS).[^18][^19] A disponibilidade de actos relevantes em AKN4EU facilita a integração entre o texto normativo e estas plataformas, embora a modelação das decisões administrativas e jurisprudenciais siga, em muitos casos, modelos complementares.[^19][^20]

### 9.3 Articulação com ontologias e dados ligados

A transformação de documentos AKN4EU em grafos de conhecimento é uma área activa de investigação, em particular quando se mapeiam as ontologias associadas a ELI e Akoma Ntoso para permitir interoperabilidade semântica entre recursos jurídicos.[^13] Estes mapeamentos abrem caminho a representações RDF/OWL do conteúdo e dos metadados legislativos, que podem ser consumidas por aplicações de análise de políticas, motores de inferência jurídica e ferramentas de visualização de redes normativas.[^13][^3]

Neste contexto, AKN4EU fornece a camada documental estruturada que serve de base à extracção de entidades, relações e padrões normativos, potenciando abordagens de dados abertos ligados e interacção com outras ontologias do domínio público europeu (por exemplo, EuroVoc, CPV, ontologias de dados abertos da UE).[^13][^3]

## 10. Implicações práticas para contextos nacionais (incluindo Portugal)

### 10.1 Transposição e notificação de legislação da UE

A própria Comissão refere que os Estados‑Membros podem adoptar ou reutilizar AKN4EU para fins de transposição e notificação da legislação da UE a nível nacional.[^9] Em termos práticos, isto significa que autoridades nacionais que gerem bases de dados legislativas (por exemplo, serviços de justiça, parlamentos, gabinetes de publicações oficiais) podem alinhar a sua modelação XML com AKN4EU, beneficiando de:

- Reutilização de esquemas e exemplos para modelar actos nacionais que transpõem direito da UE.
- Facilidade de ligação entre artigos nacionais e disposições europeias através de identificadores ELI e metadados de relação.
- Possibilidade de integração em fluxos de reporte à Comissão que usem formatos compatíveis.[^13][^9]

Em Portugal, projectos que analisam o funcionamento do sistema de asilo e a integração da legislação europeia, como o estudo sobre reforço do sistema de asilo português, beneficiam de uma representação estruturada dos actos europeus para cruzamento com medidas nacionais.[^21] Mesmo que o ordenamento português utilize outros formatos internos, o conhecimento de AKN4EU é relevante para interoperabilidade com sistemas europeus e para a concepção de taxonomias e ontologias jurídicas alinhadas com o CoV.[^4][^13]

### 10.2 Integração com práticas de análise, visualização e IA

Para profissionais que trabalham em análise de políticas, ciência de dados jurídicos ou aplicações de IA, AKN4EU oferece vantagens claras:

- Permite a extracção sistemática de estruturas (artigos, considerandos, anexos) e relações (modificações, remissões) directamente do XML, sem recorrer exclusivamente a processamento de linguagem natural.
- Facilita a construção de grafos de conhecimento e modelos de representação de normas que podem ser explorados em bases de dados de grafos (por exemplo, Neo4j) ou em infra‑estruturas de dados ligados.[^13][^6]
- Fornece um ponto de partida estável para pipelines de processamento com LLM, em que o texto é segmentado e contextualizado com metadados e identificadores robustos.[^11][^3]

Para um contexto português, isto pode traduzir‑se na criação de camadas de integração entre legislação europeia em AKN4EU e legislação nacional estruturada (por exemplo, em iniciativas futuras inspiradas neste modelo), suportando análises sobre transposição, conformidade e impacto em domínios como as relações laborais, a segurança social ou o asilo.[^21][^20]

## 11. Síntese dos principais conceitos

- **AKN4EU**: especificação XML interinstitucional da UE baseada em Akoma Ntoso, destinada a representar e trocar actos legislativos e outros documentos, alinhada com o IMFC Common Vocabulary.[^1][^9]
- **CoV (Common Vocabulary)**: conjunto de conceitos estruturais e semânticos acordados entre instituições para descrever partes de documentos legislativos; serve de base à modelação em AKN4EU.[^4]
- **Akoma Ntoso (AKN)**: standard internacional OASIS para representação de documentos legislativos, parlamentares e judiciais, oferecendo o vocabulário XML de base e o esquema.[^7][^6]
- **ELI (European Legislation Identifier)**: esquema de identificação URI de actos legislativos e respectivas subdivisões, plenamente integrado em AKN4EU.[^13][^9]
- **IMFC**: comité interinstitucional responsável por metadados e formatos, incluindo o desenvolvimento de AKN4EU e do CoV.[^1][^4]
- **Validação e pacotes**: AKN4EU recorre a XSD, Schematron e convenções de pacotes ZIP (AKN4EU_ZIP) para assegurar a conformidade estrutural e semântica dos documentos trocados.[^5][^14]
- **Integração**: AKN4EU é peça central na digitalização dos processos legislativos da UE, na construção do European Legal Data Space e na interoperabilidade com sistemas e iniciativas como o Acquis Management Programme, ELI, plataformas da EUAA e redes de informação em migração e asilo.[^11][^19][^3]

---

## References

1. [AKN4EU - EU Vocabularies - Publications Office of the EU](https://op.europa.eu/en/web/eu-vocabularies/akn4eu) - AKN4EU is the future machine-readable structured format for the exchange of legal documents in the E...

2. [AKN4EU - EU Vocabularies - Publications Office of the EU](https://op.europa.eu/pt/web/eu-vocabularies/akn4eu) - Built on the IMFC Common Vocabulary, Akoma Ntoso for European Union (AKN4EU) is the future machine-r...

3. [A Common Structured Format for EU Legislative Documents](https://joinup.ec.europa.eu/collection/semic-support-centre/solution/common-structured-format-eu-legislative-documents)

4. [IMFC Common Vocabulary - Publications Office of the EU](https://op.europa.eu/en/web/eu-vocabularies/cov) - IMFC Common Vocabulary (CoV) provides standardized semantic concepts for EU legislative documents, e...

5. [AKN4EU_4-1_PART_1_guideline](https://www.scribd.com/document/735037473/AKN4EU-4-1-PART-1-guideline) - This document provides guidelines and modeling for the AKN4EU file format. It describes the structur...

6. [Akoma Ntoso - Wikipedia, the free encyclopedia](https://en.wikipedia-on-ipfs.org/wiki/Akoma_Ntoso)

7. [an overview - 2 Akoma Ntoso](https://unsceb-hlcm.github.io/part1/index-13.html) - The Akoma Ntoso7 (AKN) standard was developed to describe, in a machine-readable format, parliamenta...

8. [AKN4EU Documentation](http://publications.europa.eu/resource/cellar/7675b2e4-5fbb-11eb-8146-01aa75ed71a1.0001.01/DOC_2)

9. [Akoma Ntoso for EU (AKN4EU) version 3.0 has been published](https://ec.europa.eu/isa2/news/akoma-ntoso-eu-akn4eu-version-30-has-been-published_en/) - Akoma Ntoso for EU (AKN4EU) version 3.0 has been published

10. [AKN4EU 4-1 PART 2 Document-Types | PDF - Scribd](https://www.scribd.com/document/780190161/AKN4EU-4-1-PART-2-Document-types) - Scribd is the world's largest social reading and publishing site.

11. [Publications Office of the European Union's Post - akn4eu](https://www.linkedin.com/posts/publications-office-of-the-european-union_akn4eu-activity-7384260280559755264-PC9s) - Today we hosted the third AKN4EU Technical Workshop! 3️⃣ #AKN4EU (Akoma Ntoso for European Union) pr...

12. [Akoma Ntoso | Legis Info](https://legisinfo.com/tag/akoma-ntoso/) - First of all, we need to introduce some Akoma Ntoso terminology. In Akoma Ntoso, a change is known a...

13. [Semantic Interoperability for Legal Information: Mapping the European Legislation Identifier (ELI) and Akoma Ntoso (AKN) Ontologies](https://dl.acm.org/doi/pdf/10.1145/3614321.3614327) - The legislative landscape, characterized by overwhelming amounts of legal data which, on many occasi...

14. [Schemas - EU Vocabularies - Publications Office of the EU](https://op.europa.eu/en/web/eu-vocabularies/schemas) - A schema (XML Schema / XSD file) is a machine-readable representation/description of either the actu...

15. [CHAPTER I General provisions](https://www.legislation.gov.uk/eur/2019/818/body/adopted/data.xht)

16. [Interoperability between EU information systems in the field of ...](https://www.europarl.europa.eu/legislative-train/theme-area-of-justice-and-fundamental-rights/file-jd-interoperability-between-eu-information-systems-(law-enforcementmigration)?sid=10001) - Regulation for interoperability between EU information systems on police and judicial cooperation, a...

17. [Interoperability between EU border and security information systems](https://www.eerstekamer.nl/eu/documenteu/pe_628267_briefing_van_de)

18. [5.1. Asylum knowledge - EUAA - European Union](https://euaa.europa.eu/asylum-report-2024/51-asylum-knowledge) - The European Union Agency for Asylum - EUAA is an agency of the European Union mandated with support...

19. [Information and Analysis of Developments in Asylum](https://euaa.europa.eu/asylum-knowledge/information-and-analysis-developments-asylum) - The European Union Agency for Asylum - EUAA is an agency of the European Union mandated with support...

20. [The Emerging Architecture of EU Asylum Policy (Chapter 8)](https://www.cambridge.org/core/books/eu-law-in-populist-times/emerging-architecture-of-eu-asylum-policy/0103FD1814DD6E91930DAAA9172DE2E3) - 8 - The Emerging Architecture of EU Asylum Policy. Insights into the Administrative Governance of th...

21. [Making Asylum Systems Work in the EU. (FCGulbenkian) - ISPUP](https://ispup.up.pt/en/projeto/making-asylum-systems-work-in-the-eu-fcgulbenkian-2/) - Summary: The large influx of refugees observed since 2015 has put considerable pressure on asylum sy...

