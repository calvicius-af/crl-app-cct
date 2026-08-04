# Solução técnica para tornar os IRCT portugueses compatíveis com ELI, ELI-DL e AKN4EU

Documento de trabalho para o Centro de Relações Laborais (CRL), Ministério do Trabalho, Solidariedade e Segurança Social. Português europeu, Acordo Ortográfico, linguagem neutra em género. Ao longo do texto distinguem-se três estatutos epistémicos: **Facto** (verificável em fonte primária ou oficial), **Interpretação** (leitura fundamentada do autor) e **Hipótese de trabalho** (proposta de desenho a validar). Sempre que existe incerteza normativa, indica-se onde verificar a base legal.

Nota terminológica inicial. IRCT significa Instrumentos de Regulamentação Coletiva de Trabalho. ELI significa European Legislation Identifier (Identificador Europeu da Legislação). ELI-DL é a extensão do ELI para legislação em preparação (Draft Legislation). AKN4EU é a localização europeia do Akoma Ntoso, o formato XML da OASIS (norma LegalDocML) para documentos jurídicos. FRBR é o modelo Functional Requirements for Bibliographic Records, que separa obra (work), expressão (expression) e manifestação (manifestation). SKOS é o Simple Knowledge Organization System, modelo do W3C para vocabulários controlados. BTE é o Boletim do Trabalho e Emprego. DRE é o Diário da República Eletrónico.

---

## TL;DR

1. **É viável mas não trivial, e depende de uma decisão de governação que ainda não existe.** Tecnicamente, os IRCT podem ser tornados compatíveis com ELI, ELI-DL e AKN4EU criando um espaço de nomes ELI próprio (por exemplo `data.bte.gov.pt/eli/irct/...`), um perfil de metadados que estenda a ontologia ELI ao ciclo de vida laboral (depósito, vigência, sobrevigência, caducidade), taxonomias SKOS e um perfil Akoma Ntoso para a estrutura textual. A camada assenta sobre o PostgreSQL existente como fonte de verdade, com exportação RDF materializada e XML gerado a partir das unidades textuais.

2. **O ponto de dor central é institucional e de formato, não conceptual.** Facto: o ELI está implementado apenas na 1.ª série do DRE; a 2.ª série do DRE e o BTE estão fora do ELI, e o BTE é publicado em PDF sem identificadores estruturados nem RDFa. O código de convenção da DGERT existe mas não é exposto como URI persistente. Sem um mandato interinstitucional (DGERT, GEP, INCM, AMA, DGAEP), a solução do CRL fica correta mas não oficial.

3. **Portugal deve ir além do precedente francês.** Facto: a França (DILA/Légifrance) atribui ELI aos atos do Journal officiel, incluindo os arrêtés d'extension (equivalentes às portarias de extensão), mas NÃO atribui ELI ao texto da convenção coletiva em si, que fica na base KALI com identificadores próprios (KALICONT/KALIARTI). A recomendação é identificar com ELI tanto os instrumentos não negociais (portarias) como as próprias convenções, colmatando a lacuna que o modelo francês deixa em aberto.

---

## Key Findings

1. **Base legal da tipologia (Facto).** O artigo 2.º do Código do Trabalho (Lei n.º 7/2009) estabelece que os IRCT podem ser negociais ou não negociais. Os negociais são a convenção coletiva, o acordo de adesão e a decisão arbitral em processo de arbitragem voluntária. As convenções coletivas podem ser contrato coletivo (CCT, entre associação sindical e associação de empregadores), acordo coletivo (ACT, entre associação sindical e uma pluralidade de empregadores) e acordo de empresa (AE, entre associação sindical e um empregador). Os não negociais são a portaria de extensão (PE), a portaria de condições de trabalho (PCT) e a decisão arbitral em processo de arbitragem obrigatória ou necessária. Verificar a versão consolidada em `diariodarepublica.pt` (Lei n.º 7/2009 consolidada) porque a Lei n.º 13/2023, de 3 de abril (Agenda do Trabalho Digno), alterou os artigos 500.º a 502.º e 510.º a 513.º, com entradas em vigor faseadas (alguns a 4 de abril de 2023, outros a 1 de maio de 2023). [Portal ACT](https://portal.act.gov.pt/AnexosPDF/Legisla%C3%A7%C3%A3o%20nacional/C%C3%B3digo%20do%20trabalho.pdf)

2. **Setor público tem regime próprio (Facto).** A Lei Geral do Trabalho em Funções Públicas (LTFP, Lei n.º 35/2014) regula a negociação coletiva nos artigos 347.º e seguintes. Prevê acordos coletivos de trabalho (ACT) e acordos coletivos de empregador público (ACEP; artigo 364.º), e como instrumento não convencional a decisão de arbitragem necessária. Facto relevante para a modelação: desde 1 de janeiro de 2023, por força do Decreto-Lei n.º 84-F/2022, de 16 de dezembro, as publicações do direito coletivo da função pública passaram do Diário da República para o BTE; o depósito faz-se na DGAEP (não na DGERT), ao abrigo do artigo 368.º da LTFP.

3. **O ELI em Portugal (Facto).** A entidade responsável é a Imprensa Nacional-Casa da Moeda (INCM). Portugal implementou o Pilar 1 do ELI em 19 de dezembro de 2016 e o Pilar 2 em 27 de julho de 2017, em conformidade com a ontologia ELI de metadados versão 1.1; o ELI aplica-se a todos os atos publicados na 1.ª série do DRE a partir de 2 de janeiro de 1991 (data em que o Decreto-Lei n.º 1/91 determinou a identificação de cada ato por número e data). [EUR-Lex](https://eur-lex.europa.eu/content/eli-register/portugal.html) A página oficial do registo ELI (EUR-Lex, Portugal) declara textualmente: «O ELI não está implementado para os atos jurídicos publicados na 2.ª série do Diário da República.» Não existe qualquer implementação ELI para o BTE.

4. **Arquitetura técnica do DRE (Facto, com implicação de projeto).** O `data.dre.pt` expõe três templates de URI (diário, ato jurídico, legislação consolidada), [EUR-Lex](https://eur-lex.europa.eu/content/eli-register/portugal.html) vocabulários SKOS (lista de regiões, lista de tipos de atos, lista de emissores) em ficheiros RDF, e metadados ELI embutidos em HTML+RDFa. Interpretação: o utilizador descreve o site como Single-Page Application com RDFa embutido, sem content negotiation nem endpoint JSON/RDF separado. Isto significa que replicar o modelo do DRE dá conformidade de Pilar 2 e 3 mas herda uma limitação de acesso a dados (ausência de endpoint separado) que a solução IRCT deve evitar, prevendo desde o início a exportação RDF materializada e, idealmente, um endpoint.

5. **O quadro ELI e as suas extensões (Facto).** O quadro ELI decorre das Conclusões do Conselho da UE de 26 de outubro de 2012 (2012/C 325/02) e de 6 de novembro de 2017 (2017/C 441/05); [Eli](https://eli.gov.pl/) a primeira versão da ELI Ontology foi lançada em 2014. [Wikipedia](https://en.wikipedia.org/wiki/European_Legislation_Identifier) As URIs ELI são descritas por templates legíveis por máquina (IETF RFC 6570), com componentes semânticos opcionais e sem ordem predefinida; [Wikipedia](https://en.wikipedia.org/wiki/European_Legislation_Identifier) o template genérico é `/eli/{jurisdiction}/{agent}/{sub-agent}/{year}/{month}/{day}/{type}/{natural identifier}/{level 1…}/{point in time}/{version}/{language}`. [Wikipedia](https://en.wikipedia.org/wiki/European_Legislation_Identifier) O ELI-DL (Draft Legislation) foi publicado em 2020, estendendo o quadro aos processos de elaboração; [Wikipedia](https://en.wikipedia.org/wiki/European_Legislation_Identifier) a versão 3.0 da ontologia ELI-DL (release publicada em 10 de novembro de 2023, [Interoperable Europe](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/releases) comummente citada como de 2024) assenta na ELI Ontology 1.5. Existe também a ELI Impact Ontology (ELI-I) versão 1.0, de 2024, [Wikipedia](https://en.wikipedia.org/wiki/European_Legislation_Identifier) para modelar o impacto de alterações.

6. **AKN4EU e Akoma Ntoso (Facto).** Akoma Ntoso versão 1.0 é norma OASIS aprovada em 29 de agosto de 2018 (Part 2: Specifications editada por Fabio Vitali, Monica Palmirani, Roger Sperberg e Véronique Parisse); [OASIS Open](https://www.oasis-open.org/standard/akn-v1-0/) segundo `akomantoso.info`, está agendada uma nova revisão para aprovação até final de julho de 2026. [Akomantoso](http://akomantoso.info/) O AKN4EU é a localização europeia mantida pelo Interinstitutional Metadata and Formats Committee (IMFC) sob coordenação do Publications Office; a versão em vigor é a 4.1.1 (errata datada de 30 de abril de 2024), que torna o atributo `@xml:id` obrigatório para elementos fora de `<meta>` e alinha o conteúdo com o uso de URIs ELI para subdivisões. O AKN4EU cobre sobretudo o processo legislativo ordinário da UE; aplicá-lo a convenções coletivas é uma customização (extensão/restrição do esquema geral do Akoma Ntoso), o que o próprio Akoma Ntoso prevê.

7. **Precedente comparativo francês (Facto, via investigação dirigida).** A DILA atribui a cada ato do JORF duas URIs ELI (uma canónica baseada no NOR, outra alias baseada no número de série), com o template `/eli/{type}/{année}/{mois}/{jour}/{identifiant naturel}/{version}/{level}`. [Wikipedia](https://fr.wikipedia.org/wiki/Identifiant_europ%C3%A9en_de_la_l%C3%A9gislation) Os arrêtés d'extension de convenções coletivas, sendo publicados no JORF, recebem ELI do tipo `/eli/arrete/...`. Contudo, o texto negociado da convenção coletiva não recebe ELI: fica na base KALI com identificadores KALICONT (contrato) e KALIARTI (artigo), acedido por URLs do tipo `legifrance.gouv.fr/conv_coll/id/KALICONT...`. Exemplo real: a convenção IDCC 3248 está em `https://www.legifrance.gouv.fr/conv_coll/id/KALICONT000046993250`. [GitHub](https://github.com/SocialGouv/cdtn-admin/discussions/1199) Interpretação: o modelo francês identifica o ato administrativo estatal mas deixa a fonte coletiva autónoma sem identificador ELI; é precisamente essa lacuna que a solução portuguesa deve preencher.

8. **Precedente luxemburguês (Facto, relevante para arquitetura de dados).** O Luxemburgo (Legilux) aplica ELI a duas séries do Mémorial (A e B, sendo B administrativo) e disponibiliza um endpoint SPARQL público (`data.legilux.public.lu/sparql`) com dois modelos coexistentes: JOLux (metadados finos, incluindo projetos) e ELI (só textos legislativos). Interpretação: demonstra que aplicar ELI a uma série administrativa e servir os dados por SPARQL é praticável, e é um modelo de referência superior ao do DRE português quanto ao acesso a dados.

---

## Details

Os entregáveis são apresentados em ficheiros separados, conforme pedido, para gerir limites de dimensão.

### Ficheiro A — Arquitetura da solução

**A.1 Visão (Hipótese de trabalho).** Uma camada de identificação e metadados ELI/ELI-DL/AKN4EU sobreposta ao grafo de conhecimento existente. O ELI é tratado como camada de identificação e de metadados sobre o PostgreSQL; a exportação RDF é materializada; o XML Akoma Ntoso é gerado a partir das unidades textuais. Esta abordagem é coerente com a arquitetura schema-first do utilizador e com a tabela canónica polimórfica `unidade_textual` com embeddings, versionamento bitemporal e proveniência.

**A.2 Camadas.**
a) Fonte de verdade: PostgreSQL com pgvector; tabela `unidade_textual` polimórfica; versionamento bitemporal (tempo de transação e tempo de validade) e proveniência. Interpretação: o versionamento bitemporal é um ativo decisivo, porque o ELI/FRBR exige distinguir versões no tempo (expressões) e a caducidade/sobrevigência dos IRCT é, por natureza, um problema temporal.
b) Camada de identificação ELI: uma tabela `eli_identifier` que gera URIs determinísticos a partir do código de convenção da DGERT, do tipo de IRCT e da referência do BTE, garantindo persistência e reprodutibilidade.
c) Camada de metadados: tabelas para propriedades ELI nucleares, propriedades ELI-DL (fase de negociação/depósito) e extensões IRCT (outorgantes, CAE, âmbito geográfico e pessoal, datas de vigência).
d) Camada de exportação: materialização em RDF (Turtle e JSON-LD) e geração de XML Akoma Ntoso a partir das unidades textuais; publicação de RDFa embutido em HTML à imagem do `data.dre.pt`, mas complementada por um endpoint de dados (ficheiros RDF descarregáveis e, em fase madura, SPARQL como no Legilux).
e) Alinhamento com o pipeline existente: PyMuPDF e Docling para extração estrutural do PDF do BTE; LangExtract e Ollama (Qwen 2.5 14B local) para extração de entidades e mapeamento de cláusulas; MAXQDA para análise qualitativa; deteção de contraordenações por regex determinístico como camada de anotação semântica sobre o Akoma Ntoso. Interpretação: o par PyMuPDF/Docling é adequado à conversão PDF para estrutura, mas a qualidade tipográfica variável do BTE (tabelas salariais complexas, colunas) obrigará a revisão humana no laço; não se deve assumir extração totalmente automática.

**A.3 Faseamento com decision gates (Hipótese de trabalho).**
Fase 0, fundação: modelação, vocabulários SKOS, template de URI, perfil de aplicação. Gate: validação jurídica pela DGERT e pela DGAEP (para o setor público) da tipologia e do ciclo de vida.
Fase 1, piloto: 50 a 100 convenções recentes do BTE com ELI e metadados. Gate: taxa de validação superior a um limiar acordado (proposta: 95 por cento) no Validador ELI da Sparna (`labs.sparna.fr/eli-validator`).
Fase 2, Akoma Ntoso: geração de AKN4EU para o corpus piloto. Gate: validação de esquema sem erros e revisão humana de 100 por cento das tabelas salariais.
Fase 3, escala e ELI-DL: retroação ao corpus histórico do BTE e modelação da fase de negociação, depósito e mediação/conciliação/arbitragem com ELI-DL. Gate: cobertura do histórico definido como prioritário e concordância inter-anotadores.
Fase 4, federação: sincronização por Pilar 4 (sitemap e feed Atom/RSS), alinhamento com `data.dre.pt` (INCM) e com o Publications Office. Gate: mandato interinstitucional formalizado.

### Ficheiro B — Especificação de URIs ELI para IRCT

**B.1 Ponto de partida (Facto).** Portugal (data.dre.pt) usa três templates: para o diário `/eli/diario/{série}/{número no ano}/{ano}/{suplemento}/{língua}/{formato}`; [EUR-Lex](https://eur-lex.europa.eu/content/eli-register/portugal.html) para o ato jurídico `/eli/{tipo}/{número}/{ano}/{mês}/{dia}/{região}/dre/{língua}/{formato}`; para a legislação consolidada `/eli/{tipo}/{número}/{ano}/{região}/cons/{data}/{língua}/{formato}`. Os acrónimos de tipo (por exemplo `dec-lei`, `lei`, `port`, `declegreg`) constam de uma lista SKOS de tipos de atos.

**B.2 Problema específico dos IRCT (Interpretação).** Ao contrário dos diplomas do DRE, as convenções não têm numeração sequencial própria oficial; têm um código de convenção interno da DGERT e são referenciadas pelo número e data do BTE em que são publicadas. A denominação muda a cada revisão (a DGERT avisa que o título corresponde à alteração mais recente). Logo, o identificador natural do ELI não pode ser um simples número de ato; tem de ser um identificador estável que sobreviva às mudanças de denominação.

**B.3 Template proposto (Hipótese de trabalho).**

```
/eli/irct/{tipo}/{ano}/{id-natural}/{ponto-no-tempo}/{versao}/{lingua}/{formato}
```

em que:
a) `{tipo}` usa acrónimos controlados: `cct`, `act`, `ae`, `adesao`, `da-vol` (decisão arbitral voluntária), `pe`, `pct`, `da-obr` (decisão arbitral obrigatória/necessária), e para a função pública `act-fp` e `acep`.
b) `{id-natural}` é o código de convenção da DGERT (ou o número de depósito na DGAEP para o setor público), garantindo estabilidade face a mudanças de denominação.
c) `{ponto-no-tempo}` e `{versao}` implementam a distinção FRBR expressão/versão (por exemplo, `cons/AAAAMMDD` para texto consolidado, à imagem do DRE).

Exemplos ilustrativos (Hipótese de trabalho, a validar quando o espaço de nomes estiver decidido):
- Convenção (obra): `/eli/irct/cct/2024/{codigo-dgert}`
- Revisão publicada no BTE n.º 8 de 2024: expressão ligada à obra por `eli:changes`.
- Texto consolidado: `/eli/irct/cct/2024/{codigo-dgert}/cons/20240229/pt/html`.
- Portaria de extensão publicada em BTE e em DRE: duas manifestações da mesma obra, ligadas por `eli:is_another_publication_of`, remetendo para a convenção por uma propriedade de extensão.

**B.4 Revisões, consolidação e relações (Hipótese de trabalho).** Revisões parciais e globais modelam-se como novas expressões/obras ligadas por `eli:changes`/`eli:changed_by`; o texto consolidado usa `eli:consolidates`/`eli:consolidated_by` (a ontologia ELI distingue explicitamente mudança de consolidação). Acordos de adesão ligam-se à convenção-base; portarias de extensão ligam-se por uma propriedade `estende` (extensão do perfil, ver Ficheiro E); avisos de cessação de vigência preenchem `eli:date_no_longer_in_force`.

**B.5 Relação BTE/DRE (Facto e Interpretação).** As portarias de extensão e de condições de trabalho são publicadas simultaneamente no BTE e no DRE (embora a extensão para as Regiões Autónomas competa aos Governos Regionais). [Mtsss](https://bte.gep.mtsss.gov.pt/completos/2024/bte37_2024.pdf) Cada publicação deve ser uma manifestação distinta ligada por `eli:is_another_publication_of`, tal como a especificação espanhola trata os atos publicados em dois jornais oficiais. Onde houver incerteza sobre qual publicação é a autêntica, verificar o artigo 519.º do Código do Trabalho e a Portaria n.º 1172/2009.

### Ficheiro C — Perfil de metadados ELI/ELI-DL para IRCT

**C.1 Propriedades ELI nucleares aplicáveis (Facto).** `eli:changes`/`eli:changed_by`, `eli:consolidates`/`eli:consolidated_by`, `eli:repeals`, `eli:in_force`, `eli:first_date_entry_in_force`, `eli:date_no_longer_in_force`, `eli:is_about`, `eli:passed_by`, `eli:responsibility_of`, `eli:is_realized_by`/`eli:realizes`/`eli:embodies` (níveis FRBR), `eli:cited_by_case_law` (útil para ligar a jurisprudência do STJ e das Relações sobre caducidade). As propriedades `first_date_entry_in_force` e `date_no_longer_in_force` têm domínio LegalResource ou LegalExpression.

**C.2 Extensões necessárias para IRCT (Hipótese de trabalho).** A ontologia ELI não cobre conceitos laborais; propõem-se propriedades de extensão:
a) Outorgantes/subscritores (associações sindicais e de empregadores, ou empregador em AE), com ligação a autoridades registáveis.
b) Âmbito setorial via CAE (Classificação Portuguesa de Atividades Económicas; nota: CAE-Rev.4 a partir de 1 de janeiro de 2025, CAE-Rev.3 até 31 de dezembro de 2024, o que obriga a versionar o vocabulário CAE).
c) Âmbito geográfico (distrito/concelho, alinhável com autoridades NUTS/NAL do Publications Office).
d) Âmbito pessoal (categorias e profissões abrangidas).
e) Data de depósito e número de depósito na DGERT (ou DGAEP), publicação em BTE (número e data), cobertura potencial (número de trabalhadores/empresas, dado que a DGERT publica).

**C.3 Ciclo de vida temporal (Facto, base legal a citar no perfil).** O artigo 501.º do Código do Trabalho (na redação da Lei n.º 13/2023) rege sobrevigência e caducidade: havendo denúncia, a convenção mantém-se em sobrevigência durante a negociação ou no mínimo 12 meses; o período de negociação com suspensões não pode exceder 18 meses; decorrido o prazo, a convenção mantém-se em vigor 45 dias após comunicação ao ministério, após o que caduca. O artigo 500.º rege a denúncia; os artigos 510.º a 513.º regem a arbitragem obrigatória e necessária. Estes estados (vigência, sobrevigência, denúncia, caducidade, cessação) devem ser conceitos SKOS (Ficheiro D) preenchendo propriedades temporais. Verificar sempre a versão consolidada em `diariodarepublica.pt` porque houve suspensões excecionais de prazos (por exemplo a Lei n.º 55/2014 e medidas de suspensão de sobrevigência).

**C.4 Mapeamento para ELI-DL (Facto).** Para a fase de negociação/depósito, usar as classes ELI-DL: `DraftLegislationWork` (o projeto de convenção) e `AmendmentToDraftLegislationWork` (proposta de revisão); [Interoperable Europe](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/release/final1) `LegislativeProcess` (o processo negocial, com super-classe genérica `Process`); [Interoperable Europe](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/release/v2) `LegislativeProcessWork` (documentação do processo); `LegislativeActivity` (as fases: proposta, resposta, negociação direta, conciliação, mediação, arbitragem, com super-classe genérica `Activity` [Interoperable Europe](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/release/v2) e a propriedade `activity_order` para ordenar); e a classe `Decision` (nova na versão 3.0, super-classe de `Vote`, [Interoperable Europe](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/releases) com propriedades `decision_outcome` e `decision_method`) [europa](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/release/3) para deliberações de comissões paritárias. Requisito normativo (Facto): todas as URIs de entidades ELI-DL devem começar por `/eli/dl/`. [europa](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology-draft-legislation-eli-dl/release/final1) Interpretação: a fase de depósito na DGERT e o aviso de projeto de portaria publicado na Separata do BTE (para apreciação pública) mapeiam-se naturalmente para atividades ELI-DL, sendo este um dos usos mais promissores e originais da solução.

### Ficheiro D — Taxonomia SKOS (excerto em Turtle)

Interpretação: apresenta-se um excerto ilustrativo; os URIs finais dependem do espaço de nomes decidido. Alinhar com EuroVoc, onde o conceito «collective agreement» existe, e com os vocabulários SKOS do `data.dre.pt`.

```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix irct: <https://data.bte.gov.pt/def/irct#> .
@prefix eurovoc: <http://eurovoc.europa.eu/> .

irct:TipoIRCT a skos:ConceptScheme ;
    skos:prefLabel "Tipos de instrumento de regulamentação coletiva de trabalho"@pt .

irct:convencao-coletiva a skos:Concept ;
    skos:inScheme irct:TipoIRCT ;
    skos:prefLabel "Convenção coletiva"@pt ;
    skos:exactMatch eurovoc:2loc_a_verificar .   # verificar URI EuroVoc de "collective agreement"

irct:cct a skos:Concept ; skos:broader irct:convencao-coletiva ;
    skos:prefLabel "Contrato coletivo"@pt ; skos:notation "cct" .
irct:act a skos:Concept ; skos:broader irct:convencao-coletiva ;
    skos:prefLabel "Acordo coletivo"@pt ; skos:notation "act" .
irct:ae a skos:Concept ; skos:broader irct:convencao-coletiva ;
    skos:prefLabel "Acordo de empresa"@pt ; skos:notation "ae" .
irct:acordo-adesao a skos:Concept ; skos:prefLabel "Acordo de adesão"@pt .
irct:da-voluntaria a skos:Concept ; skos:prefLabel "Decisão arbitral (arbitragem voluntária)"@pt .
irct:portaria-extensao a skos:Concept ; skos:prefLabel "Portaria de extensão"@pt ; skos:notation "pe" .
irct:portaria-condicoes a skos:Concept ; skos:prefLabel "Portaria de condições de trabalho"@pt ; skos:notation "pct" .
irct:da-obrigatoria a skos:Concept ; skos:prefLabel "Decisão arbitral (arbitragem obrigatória ou necessária)"@pt .
irct:acep a skos:Concept ; skos:prefLabel "Acordo coletivo de empregador público"@pt ; skos:notation "acep" .

irct:EventoCicloVida a skos:ConceptScheme ;
    skos:prefLabel "Eventos do ciclo de vida do IRCT"@pt .
irct:deposito     a skos:Concept ; skos:inScheme irct:EventoCicloVida ; skos:prefLabel "Depósito"@pt .
irct:publicacao   a skos:Concept ; skos:inScheme irct:EventoCicloVida ; skos:prefLabel "Publicação em BTE"@pt .
irct:vigencia     a skos:Concept ; skos:inScheme irct:EventoCicloVida ; skos:prefLabel "Vigência"@pt .
irct:sobrevigencia a skos:Concept ; skos:inScheme irct:EventoCicloVida ; skos:prefLabel "Sobrevigência"@pt ;
    skos:scopeNote "Artigo 501.º do Código do Trabalho."@pt .
irct:denuncia     a skos:Concept ; skos:inScheme irct:EventoCicloVida ; skos:prefLabel "Denúncia"@pt .
irct:caducidade   a skos:Concept ; skos:inScheme irct:EventoCicloVida ; skos:prefLabel "Caducidade"@pt .
irct:revisao-parcial a skos:Concept ; skos:prefLabel "Revisão parcial"@pt .
irct:revisao-global  a skos:Concept ; skos:prefLabel "Revisão global"@pt .
irct:consolidacao a skos:Concept ; skos:prefLabel "Texto consolidado"@pt .
irct:cessacao     a skos:Concept ; skos:prefLabel "Cessação de vigência"@pt .
```

Ponto de dor a assinalar: a correspondência com o EuroVoc é grosseira (o EuroVoc tem «collective agreement» e «collective bargaining», mas não distingue CCT/ACT/AE nem os instrumentos não negociais portugueses). O `skos:exactMatch` só deve ser usado onde a equivalência for real; nos restantes casos usar `skos:closeMatch` ou `skos:broadMatch`. Verificar os URIs EuroVoc exatos em `op.europa.eu/en/web/eu-vocabularies`.

### Ficheiro E — Ontologia OWL/RDF (perfil de aplicação, excerto)

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix eli: <http://data.europa.eu/eli/ontology#> .
@prefix irct: <https://data.bte.gov.pt/def/irct#> .

irct:InstrumentoRCT a owl:Class ; rdfs:subClassOf eli:LegalResource ;
    rdfs:label "Instrumento de regulamentação coletiva de trabalho"@pt .
irct:ConvencaoColetiva a owl:Class ; rdfs:subClassOf irct:InstrumentoRCT .
irct:ContratoColetivo  a owl:Class ; rdfs:subClassOf irct:ConvencaoColetiva .
irct:PortariaExtensao  a owl:Class ; rdfs:subClassOf irct:InstrumentoRCT .

irct:estende a owl:ObjectProperty ;
    rdfs:domain irct:PortariaExtensao ; rdfs:range irct:ConvencaoColetiva ;
    rdfs:label "estende"@pt ;
    rdfs:comment "Liga uma portaria de extensão à convenção cujo regime é estendido."@pt .

irct:adereA a owl:ObjectProperty ;
    rdfs:domain irct:InstrumentoRCT ; rdfs:range irct:ConvencaoColetiva ;
    rdfs:label "adere a"@pt .

irct:temOutorgante a owl:ObjectProperty ; rdfs:domain irct:InstrumentoRCT .
irct:ambitoCAE a owl:DatatypeProperty ; rdfs:domain irct:InstrumentoRCT .
irct:dataDeposito a owl:DatatypeProperty ; rdfs:domain irct:InstrumentoRCT .
irct:caducaEm a owl:DatatypeProperty ; rdfs:subPropertyOf eli:date_no_longer_in_force .
```

Interpretação: manter o perfil como subclasse de `eli:LegalResource` garante que qualquer consumidor ELI (validador, EUR-Lex, Cellar) processa os IRCT sem conhecer a extensão laboral, e a extensão acrescenta a semântica específica. As relações de revisão/consolidação reutilizam `eli:changes`/`eli:consolidates` em vez de propriedades novas, para maximizar a interoperabilidade.

### Ficheiro F — Perfil AKN4EU/Akoma Ntoso

**F.1 Estrutura (Facto).** Um documento Akoma Ntoso organiza-se em `<meta>`, `<coverPage>`, `<preface>`, `<preamble>`, corpo (`<body>`/`<mainBody>`), `<conclusions>` e `<attachments>`. Os contentores hierárquicos incluem `chapter`, `section`, `article`, `paragraph`, `clause`, `part`, `list`, entre outros. No AKN4EU, um `<article>` deve ter `<num>` e pode ter `<heading>`, e o conteúdo dos anexos vai em `<attachments>` com `<doc name="ANNEX">`; tabelas usam o modelo de tabela HTML.

**F.2 Mapeamento IRCT (Hipótese de trabalho).**
a) Cláusulas da convenção para `<article>` (numeradas) ou `<clause>`.
b) Capítulos para `<chapter>`; secções para `<section>`.
c) Anexos (tabelas salariais, definição de categorias) para `<attachments>`/`<doc name="ANNEX">`.
d) Tabelas salariais para o modelo de tabela HTML dentro do anexo; casos tipograficamente complexos convertidos em imagem apenas como último recurso, com nota de perda de legibilidade por máquina.
e) Outorgantes e âmbito nas referências de metadados (`<references>` com `TLCOrganization`, `TLCConcept`), ligando às autoridades SKOS do Ficheiro D.
f) Estados de vigência/caducidade nos metadados de ciclo de vida (`<lifecycle>`) e nas propriedades ELI dos metadados FRBR.

**F.3 Exemplo AKN (excerto realista, Hipótese de trabalho).**

```xml
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <act name="cct">
    <meta>
      <identification source="#dgert">
        <FRBRWork>
          <FRBRthis value="/akn/pt/act/cct/2024/{codigo-dgert}/!main"/>
          <FRBRuri value="/akn/pt/act/cct/2024/{codigo-dgert}"/>
          <FRBRdate date="2024-02-29" name="publicationBTE"/>
          <FRBRauthor href="#outorgantes"/>
          <FRBRcountry value="pt"/>
        </FRBRWork>
        <FRBRExpression>
          <FRBRthis value="/akn/pt/act/cct/2024/{codigo-dgert}/pt@/!main"/>
          <FRBRlanguage language="por"/>
        </FRBRExpression>
        <FRBRManifestation>
          <FRBRthis value="/akn/pt/act/cct/2024/{codigo-dgert}/pt@/!main.xml"/>
          <FRBRformat value="xml"/>
        </FRBRManifestation>
      </identification>
      <lifecycle source="#dgert">
        <eventRef date="2024-02-15" type="generation" refersTo="#deposito"/>
        <eventRef date="2024-02-29" type="generation" refersTo="#publicacao"/>
      </lifecycle>
      <references source="#crl">
        <TLCConcept eId="deposito" href="/def/irct#deposito" showAs="Depósito"/>
        <TLCOrganization eId="outorgantes" href="/org/exemplo" showAs="Associação outorgante"/>
      </references>
    </meta>
    <preface><longTitle><p>Contrato coletivo entre ... — Revisão global</p></longTitle></preface>
    <body>
      <chapter eId="chp_1"><num>Capítulo I</num><heading>Âmbito e vigência</heading>
        <article eId="art_1"><num>Cláusula 1.ª</num><heading>Âmbito</heading>
          <paragraph eId="art_1__para_1"><num>1</num>
            <content><p>O presente contrato coletivo aplica-se em todo o território nacional ...</p></content>
          </paragraph>
        </article>
      </chapter>
    </body>
    <attachments>
      <attachment><doc name="ANNEX"><mainBody><!-- tabela salarial em modelo HTML --></mainBody></doc></attachment>
    </attachments>
  </act>
</akomaNtoso>
```

Interpretação: usar `name="cct"` no `<act>` e a Naming Convention do Akoma Ntoso (`/akn/pt/act/...`) em paralelo com o ELI (`/eli/irct/...`); as duas convivem, tal como no AKN4EU a URI ELI é usada para referenciar subdivisões. Verificar a compatibilidade exata dos atributos com o esquema AKN4EU 4.1.1 antes de fixar o perfil.

### Ficheiro G — Análise de lacunas e riscos

**G.1 O que falta na 2.ª série do DRE (Facto).** O ELI não está implementado na 2.ª série do DRE. Como parte dos IRCT não negociais (portarias) também é publicada no DRE, uma solução completa exige coordenação com a INCM ou, em alternativa, tratar a publicação BTE como a manifestação primária e a publicação DRE como secundária.

**G.2 Limitações do BTE (Facto e Interpretação, ponto de dor sem suavização).** O BTE é publicado em PDF, sem identificadores estruturados, sem RDFa, sem content negotiation e sem qualquer camada semântica. As denominações das convenções mudam a cada revisão. O código de convenção da DGERT existe mas não é exposto como URI persistente e resolúvel. A ferramenta de pesquisa da DGERT (SIMPLEX+) liga ao PDF do BTE mas não expõe dados abertos estruturados. Consequência: toda a extração terá de partir de PDF, com custo e erro não desprezáveis, sobretudo em tabelas salariais. Esta é a maior fonte de esforço e risco do projeto.

**G.3 Esforço estimado (Interpretação, a calibrar).** Fase 0 e Fase 1 (fundação e piloto de 50–100 convenções) são exequíveis com a infraestrutura local descrita, num horizonte de meses, sendo o gargalo a validação jurídica e a revisão humana das tabelas. A Fase 3 (retroação ao histórico completo do BTE) é a mais pesada e deve ser priorizada por relevância (convenções em vigor com maior cobertura de trabalhadores primeiro). Não confiar em automação total; prever revisão no laço.

**G.4 Dependências institucionais (Facto).** DGERT (depósito, registo e publicação das convenções do setor privado, e preparação das portarias); DGAEP (depósito dos ACT/ACEP do setor público, desde 2023 publicados no BTE); GEP (edição do BTE); INCM (ELI do DRE e potencial anfitrião do espaço de nomes); AMA (interoperabilidade, European Interoperability Framework, Estratégia Nacional de Dados). O Instituto de Informática da Segurança Social é dependência de infraestrutura do utilizador.

**G.5 Risco de governação (Interpretação).** Sem um mandato interinstitucional que decida quem detém e mantém o espaço de nomes ELI dos IRCT, a solução do CRL será tecnicamente correta mas sem estatuto oficial, replicando o risco de fragmentação. A decisão sobre o domínio (`data.bte.gov.pt` versus extensão de `data.dre.pt`) é bloqueadora e deve ser tomada na Fase 0.

**G.6 Risco de desvio face ao precedente (Interpretação).** Copiar o modelo francês levaria a identificar apenas as portarias (atos estatais) e a deixar as convenções sem ELI. Recomenda-se explicitamente não seguir essa opção; o valor acrescentado da solução portuguesa está em identificar a própria fonte coletiva.

---

## Recommendations

1. **Fase 0 imediata — decidir governação e fundação (bloqueador).** Obter da DGERT, GEP, INCM e AMA uma decisão sobre o espaço de nomes ELI dos IRCT e sobre a entidade mantenedora. Em paralelo, congelar a tipologia SKOS (Ficheiro D) e o template de URI (Ficheiro B) com validação jurídica da DGERT (setor privado) e DGAEP (setor público). Critério que altera a decisão: se a INCM aceitar estender `data.dre.pt` aos IRCT, adotar esse domínio; caso contrário, criar `data.bte.gov.pt`.

2. **Fase 1 — piloto de 50 a 100 convenções recentes.** Gerar ELI e metadados ELI (Ficheiro C) sobre o PostgreSQL e exportar RDF materializado. Critério de passagem: taxa de validação igual ou superior a 95 por cento no Validador ELI da Sparna e revisão jurídica de uma amostra. Se a taxa ficar abaixo, corrigir o perfil antes de escalar.

3. **Fase 2 — Akoma Ntoso/AKN4EU para o piloto.** Gerar XML conforme o perfil do Ficheiro F, validando contra o esquema AKN4EU 4.1.1. Critério: zero erros de esquema e revisão humana de 100 por cento das tabelas salariais. Ponto de decisão: se a conversão de tabelas complexas exceder um custo aceitável, admitir imagem com nota de limitação, mas medir a percentagem de tabelas não legíveis por máquina como indicador de dívida técnica.

4. **Fase 3 — ELI-DL para o ciclo negocial e retroação histórica.** Modelar depósito, aviso de projeto na Separata, conciliação, mediação e arbitragem com as classes ELI-DL (URIs sob `/eli/dl/`). Priorizar o histórico por cobertura de trabalhadores. Critério: começar apenas depois de a Fase 1 estar estável, para não propagar erros de modelação.

5. **Fase 4 — federação e dados abertos.** Implementar o Pilar 4 (sitemap e feed) e, seguindo o exemplo do Legilux, disponibilizar um endpoint de dados (ficheiros RDF e, se possível, SPARQL), evitando a limitação de acesso do `data.dre.pt`. Critério: mandato interinstitucional formalizado e alinhamento com o Publications Office (EuroVoc, NAL).

6. **Transversal — não replicar a lacuna francesa.** Atribuir ELI tanto às portarias como às convenções. Verificar sempre a base legal em versão consolidada em `diariodarepublica.pt` (Código do Trabalho e LTFP) antes de fixar estados de ciclo de vida, dada a instabilidade legislativa recente (Lei n.º 13/2023 e suspensões de prazos).

---

## Caveats

1. **Repositórios do utilizador inacessíveis (Facto).** O repositório GitHub `calvicius-af/portal-cct-crl2030` devolveu erro 404 (privado ou inexistente à data da consulta) e o espelho GitLab `antonio.fula/portal-das-relacoes-de-trabalho` tem apenas 1 commit (criado em 29 de maio de 2026) com README que não renderiza conteúdo por ser servido como aplicação dinâmica. Não foi possível ler README, código ou esquemas. Consequência: o alinhamento com o trabalho existente do utilizador baseia-se apenas na descrição fornecida no enunciado (pipeline PyMuPDF/Docling/LangExtract/Ollama, PostgreSQL+pgvector, Kùzu, LlamaIndex, tabela `unidade_textual`). Recomenda-se partilhar os repositórios ou torná-los acessíveis para afinar o perfil de aplicação ao esquema real.

2. **Exemplos de URI são hipóteses (Hipótese de trabalho).** Os templates e exemplos de URI ELI e Akoma Ntoso são propostas; os valores concretos dependem da decisão de governação (Fase 0). Não devem ser tratados como identificadores oficiais.

3. **Correspondências EuroVoc por confirmar (Interpretação).** O EuroVoc tem conceitos de convenção coletiva e negociação coletiva mas não a granularidade portuguesa (CCT/ACT/AE, PE/PCT); os `skos:exactMatch` do Ficheiro D devem ser verificados um a um em `op.europa.eu` antes de publicação.

4. **Precedente francês parcialmente inferido (Facto com ressalva).** A conclusão de que o texto da convenção coletiva francesa não recebe ELI assenta na documentação de âmbito da DILA/EUR-Lex (que enumera apenas atos do JORF e administrativos) e no uso do espaço de nomes KALICONT/KALIARTI; não foi possível inspecionar diretamente o HTML de uma página KALI viva por bloqueio anti-robô do Légifrance. A atribuição de ELI aos arrêtés d'extension é confirmada por exemplo real de arrêté com ELI, mas não foi possível carregar a página específica de um arrêté de extensão para exibir a sua cadeia ELF exata.

5. **Versões das normas em evolução (Facto).** A ELI Ontology está na versão 1.5 (2024), o ELI-DL na 3.0 e o AKN4EU na 4.1.1 (errata de 30 de abril de 2024); o Akoma Ntoso tem nova revisão agendada para aprovação até final de julho de 2026. O perfil deve fixar a versão de cada norma usada e prever revisão quando saírem novas versões.

6. **Orçamento e infraestrutura (Interpretação).** A solução foi desenhada para infraestrutura local com orçamento limitado e dependência do Instituto de Informática da Segurança Social; a Fase 4 (endpoint SPARQL, federação Pilar 4) pode exigir recursos adicionais e deve ser avaliada em função da capacidade real na altura.

### Resumo de pontos-chave

O maior obstáculo não é conceptual (o mapeamento IRCT para ELI/ELI-DL/AKN4EU é viável e está especificado nos Ficheiros B a F) mas sim institucional e de formato: a ausência de ELI na 2.ª série do DRE, a natureza PDF-only do BTE, e a falta de um mandato que decida o espaço de nomes. A recomendação operacional é começar pela governação e por um piloto validado, reutilizar ao máximo a ontologia ELI (subclassificando `eli:LegalResource`), estender apenas o que é laboral-específico, e ir além do precedente francês identificando também as convenções, não só as portarias.