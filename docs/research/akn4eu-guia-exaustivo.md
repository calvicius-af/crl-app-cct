<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Cria um guia exaustivo sobre o que é o AKN4EU. Deve focar-se mais nos aspectos técnicos do que nos aspectos introdutórios. Preciso de exemplos concretos, explicação de termos e ligações com outros temas relevantes para o entendimento dos principais conceitos. Usa linguagem clara sem perder o rigor técnico.

O AKN4EU é a especificação XML interinstitucional usada pelas instituições da União Europeia para representar e trocar actos legislativos e documentos relacionados de forma estruturada, baseada no standard Akoma Ntoso e alinhada com o Common Vocabulary (CoV) do IMFC.[^1_1][^1_2][^1_3] É, em termos práticos, a “localização para a UE” do Akoma Ntoso: define exactamente que elementos e atributos usar, que estruturas são permitidas e como ligar tudo isso a identificadores como o ELI, assegurando interoperabilidade entre sistemas de redacção, tradução, publicação e reutilização de legislação.[^1_4][^1_5][^1_6]

Preparei um relatório em Markdown com um guia técnico detalhado (estrutura XML, ligação ao CoV e ao ELI, exemplos de regulamentos e propostas, validação XSD/Schematron, integração com outros sistemas europeus e implicações para contextos nacionais como o português). Pode utilizá‑lo como referência de trabalho ou base para formação técnica.
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://op.europa.eu/en/web/eu-vocabularies/akn4eu

[^1_2]: https://op.europa.eu/pt/web/eu-vocabularies/akn4eu

[^1_3]: https://joinup.ec.europa.eu/collection/semic-support-centre/solution/common-structured-format-eu-legislative-documents

[^1_4]: https://op.europa.eu/en/web/eu-vocabularies/cov

[^1_5]: https://www.scribd.com/document/735037473/AKN4EU-4-1-PART-1-guideline

[^1_6]: https://en.wikipedia-on-ipfs.org/wiki/Akoma_Ntoso

[^1_7]: https://unsceb-hlcm.github.io/part1/index-13.html

[^1_8]: http://publications.europa.eu/resource/cellar/7675b2e4-5fbb-11eb-8146-01aa75ed71a1.0001.01/DOC_2

[^1_9]: https://ec.europa.eu/isa2/news/akoma-ntoso-eu-akn4eu-version-30-has-been-published_en/

[^1_10]: https://www.scribd.com/document/780190161/AKN4EU-4-1-PART-2-Document-types

[^1_11]: https://www.linkedin.com/posts/publications-office-of-the-european-union_akn4eu-activity-7384260280559755264-PC9s

[^1_12]: https://legisinfo.com/tag/akoma-ntoso/

[^1_13]: https://dl.acm.org/doi/pdf/10.1145/3614321.3614327

[^1_14]: https://op.europa.eu/en/web/eu-vocabularies/schemas

[^1_15]: https://www.legislation.gov.uk/eur/2019/818/body/adopted/data.xht

[^1_16]: https://www.europarl.europa.eu/legislative-train/theme-area-of-justice-and-fundamental-rights/file-jd-interoperability-between-eu-information-systems-(law-enforcementmigration)?sid=10001

[^1_17]: https://www.eerstekamer.nl/eu/documenteu/pe_628267_briefing_van_de

[^1_18]: https://euaa.europa.eu/asylum-report-2024/51-asylum-knowledge

[^1_19]: https://euaa.europa.eu/asylum-knowledge/information-and-analysis-developments-asylum

[^1_20]: https://www.cambridge.org/core/books/eu-law-in-populist-times/emerging-architecture-of-eu-asylum-policy/0103FD1814DD6E91930DAAA9172DE2E3

[^1_21]: https://ispup.up.pt/en/projeto/making-asylum-systems-work-in-the-eu-fcgulbenkian-2/

[^1_22]: https://onlinelibrary.wiley.com/doi/10.1111/imig.13303

[^1_23]: https://www.tandfonline.com/doi/full/10.1080/14675986.2024.2349475

[^1_24]: https://bristoluniversitypressdigital.com/view/journals/frs/14/1/article-p145.xml

[^1_25]: https://www.mdpi.com/2227-7102/15/4/437

[^1_26]: https://academic.oup.com/eurpub/article/doi/10.1093/eurpub/ckaf161.068/8301811

[^1_27]: https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-023-15931-1

[^1_28]: http://link.springer.com/10.1007/978-3-030-29171-6_7

[^1_29]: https://onlinelibrary.wiley.com/doi/10.1111/cch.12538

[^1_30]: https://home-affairs.ec.europa.eu/networks/european-migration-network-emn_en

[^1_31]: https://www.euaa.europa.eu/asylum-report-2024/51-asylum-knowledge

[^1_32]: https://www.share-network.eu/erasmusplushercon

[^1_33]: https://home-affairs.ec.europa.eu/networks/european-migration-network-emn/about-emn_en

[^1_34]: https://www.euaa.europa.eu/es/node/23963

[^1_35]: https://www.euaa.europa.eu/asylum-knowledge/asylum-processes

[^1_36]: https://www.europarl.europa.eu/doceo/document/A-8-2018-0348_EN.html

[^1_37]: http://projeto.lexml.gov.br/documentacao/Parte-3-XML-Schema.pdf

[^1_38]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10060946/

[^1_39]: https://www.scribd.com/document/780190157/AKN4EU-4-1-PART-4-Reference

[^1_40]: https://fragdenstaat.de/anfrage/dokumentation-des-common-exchange-model-cem-und-des-common-vocabulary-cov-des-interinstitutional-metadata-and-formats-committee-imfc/


---

# Preciso que faças uma investigação em tudo semelhante para o modelo FRBR (Functional Requirements for Bibliographic Records)

O modelo FRBR (Functional Requirements for Bibliographic Records) é um modelo conceptual entidade‑relação, desenvolvido pela IFLA, que estrutura o “universo bibliográfico” em torno de quatro tarefas de utilizador (find, identify, select, obtain) e de três grupos de entidades (WEMI, agentes e assuntos), servindo de base a códigos como o RDA e a programas de transição bibliográfica alinhados com a Web Semântica.[^2_1][^2_2][^2_3][^2_4] Em domínios como o jurídico, os conceitos FRBR são usados para distinguir entre a obra normativa, as suas expressões linguísticas, as manifestações em diferentes formatos (por exemplo, AKN4EU, PDF) e os exemplares concretos, facilitando a gestão de versões, a identificação estável (por exemplo, via ELI) e a integração em grafos de conhecimento.[^2_5][^2_6][^2_7][^2_8]

Preparei um relatório em Markdown com um guia técnico detalhado sobre FRBR (entidades, atributos, relações, tarefas de utilizador, exemplos concretos, ligação a RDA, IFLA LRM, FRBRoo, CIDOC CRM e AKN4EU), com foco conceptual e implicações para modelação de dados e grafos de conhecimento. Pode reutilizá‑lo como base para documentação técnica, formação ou desenho de modelos de dados.
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_20][^2_21][^2_22][^2_23][^2_24][^2_25][^2_26][^2_27][^2_28][^2_29][^2_30][^2_31][^2_32][^2_33][^2_34][^2_35][^2_36][^2_37][^2_38][^2_39][^2_40][^2_41][^2_42][^2_43][^2_44][^2_45][^2_46][^2_47][^2_48][^2_49][^2_50][^2_51][^2_52][^2_53][^2_54][^2_55][^2_56][^2_57][^2_58][^2_59][^2_60][^2_61][^2_62][^2_63][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://www.loc.gov/item/2001433363/

[^2_2]: https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/frbr/frbr.pdf

[^2_3]: https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/frbr/frbr_2008.pdf

[^2_4]: https://en.wikipedia.org/wiki/Functional_Requirements_for_Bibliographic_Records

[^2_5]: https://ebooks.inflibnet.ac.in/lisp3/chapter/knowledge-organization-and-processing-cataloguing/

[^2_6]: https://www.loc.gov/catworkshop/RDA training materials/FRBR_Module%201_Overview/FRBR_Module%201_Overview.pdf

[^2_7]: https://www.nla.gov.au/sites/default/files/australian_train_the_trainer_text_-_rda_train_the_trainer_module_2.docx

[^2_8]: https://www.imrpress.com/journal/ko/45/4/10.5771/0943-7444-2018-4-310

[^2_9]: https://www.semanticscholar.org/paper/6b6c7973d3dbd7a2970fa0b6bd38f1454e98f005

[^2_10]: https://abes.fr/en/normalisation-modeles-et-formats/transition-bibliographique/

[^2_11]: https://dl.acm.org/doi/pdf/10.1145/3614321.3614327

[^2_12]: https://joinup.ec.europa.eu/collection/semic-support-centre/solution/common-structured-format-eu-legislative-documents

[^2_13]: https://www.loc.gov/catworkshop/RDA training materials/LC RDA Training/FRBR_Module%201_Overview/FRBRFundamentals_20120809_student.pdf

[^2_14]: https://dialnet.unirioja.es/descarga/articulo/6119078.pdf

[^2_15]: https://dcpapers.dublincore.org/files/articles/952137861/dcmi-952137861.pdf

[^2_16]: https://dcevents.dublincore.org/IntConf/dc-2017/paper/download/499/606

[^2_17]: https://en.wikipedia-on-ipfs.org/wiki/Akoma_Ntoso

[^2_18]: https://www.semanticscholar.org/paper/4942b93da72e937a99ae2f779db28c055aef2480

[^2_19]: https://www.semanticscholar.org/paper/d8e1e1e49a3472209a45d56e01251544bec76c4e

[^2_20]: http://periodicos.sbu.unicamp.br/ojs/index.php/rdbci/article/view/2052

[^2_21]: https://www.degruyterbrill.com/document/doi/10.1515/9783598440366.0.43/html

[^2_22]: https://www.semanticscholar.org/paper/a4c5d568bcb8ac0f9c691347a15fa288c6274885

[^2_23]: https://www.tandfonline.com/doi/full/10.1080/14649055.2000.10765660

[^2_24]: https://www.taylorfrancis.com/books/9781000031805/chapters/10.1081/E-ELIS3-120043744

[^2_25]: https://fr.slideshare.net/slideshow/fundamental-relationship-of-bibliography-resource/273492167

[^2_26]: https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/icp/icp_2009-en.pdf

[^2_27]: https://onlinelibrary.wiley.com/doi/10.1111/imig.13303

[^2_28]: https://www.tandfonline.com/doi/full/10.1080/14675986.2024.2349475

[^2_29]: https://bristoluniversitypressdigital.com/view/journals/frs/14/1/article-p145.xml

[^2_30]: https://www.mdpi.com/2227-7102/15/4/437

[^2_31]: https://academic.oup.com/eurpub/article/doi/10.1093/eurpub/ckaf161.068/8301811

[^2_32]: https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-023-15931-1

[^2_33]: http://link.springer.com/10.1007/978-3-030-29171-6_7

[^2_34]: https://onlinelibrary.wiley.com/doi/10.1111/cch.12538

[^2_35]: https://home-affairs.ec.europa.eu/networks/european-migration-network-emn_en

[^2_36]: https://www.euaa.europa.eu/asylum-report-2024/51-asylum-knowledge

[^2_37]: https://op.europa.eu/en/web/eu-vocabularies/akn4eu

[^2_38]: https://euaa.europa.eu/asylum-report-2024/51-asylum-knowledge

[^2_39]: https://www.share-network.eu/erasmusplushercon

[^2_40]: https://www.legislation.gov.uk/eur/2019/818/body/adopted/data.xht

[^2_41]: https://home-affairs.ec.europa.eu/networks/european-migration-network-emn/about-emn_en

[^2_42]: https://ispup.up.pt/en/projeto/making-asylum-systems-work-in-the-eu-fcgulbenkian-2/

[^2_43]: https://www.europarl.europa.eu/legislative-train/theme-area-of-justice-and-fundamental-rights/file-jd-interoperability-between-eu-information-systems-(law-enforcementmigration)?sid=10001

[^2_44]: https://www.euaa.europa.eu/es/node/23963

[^2_45]: https://www.euaa.europa.eu/asylum-knowledge/asylum-processes

[^2_46]: https://www.europarl.europa.eu/doceo/document/A-8-2018-0348_EN.html

[^2_47]: https://euaa.europa.eu/asylum-knowledge/information-and-analysis-developments-asylum

[^2_48]: https://www.cambridge.org/core/books/eu-law-in-populist-times/emerging-architecture-of-eu-asylum-policy/0103FD1814DD6E91930DAAA9172DE2E3

[^2_49]: https://www.eerstekamer.nl/eu/documenteu/pe_628267_briefing_van_de

[^2_50]: http://projeto.lexml.gov.br/documentacao/Parte-3-XML-Schema.pdf

[^2_51]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10060946/

[^2_52]: https://www.scribd.com/document/780190157/AKN4EU-4-1-PART-4-Reference

[^2_53]: https://unsceb-hlcm.github.io/part1/index-13.html

[^2_54]: https://ec.europa.eu/isa2/news/akoma-ntoso-eu-akn4eu-version-30-has-been-published_en/

[^2_55]: https://www.scribd.com/document/735037473/AKN4EU-4-1-PART-1-guideline

[^2_56]: https://op.europa.eu/en/web/eu-vocabularies/cov

[^2_57]: https://op.europa.eu/en/web/eu-vocabularies/schemas

[^2_58]: https://legisinfo.com/tag/akoma-ntoso/

[^2_59]: https://www.linkedin.com/posts/publications-office-of-the-european-union_akn4eu-activity-7384260280559755264-PC9s

[^2_60]: http://publications.europa.eu/resource/cellar/7675b2e4-5fbb-11eb-8146-01aa75ed71a1.0001.01/DOC_2

[^2_61]: https://op.europa.eu/pt/web/eu-vocabularies/akn4eu

[^2_62]: https://www.scribd.com/document/780190161/AKN4EU-4-1-PART-2-Document-types

[^2_63]: https://fragdenstaat.de/anfrage/dokumentation-des-common-exchange-model-cem-und-des-common-vocabulary-cov-des-interinstitutional-metadata-and-formats-committee-imfc/


---

# Preciso que faças uma investigação em tudo semelhante para o modelo FRBR (Functional Requirements for Bibliographic Records)

O modelo FRBR é um modelo conceptual entidade‑relação da IFLA que estrutura o “universo bibliográfico” em conjuntos de entidades, atributos e relações, pensado para alinhar os registos com as tarefas dos utilizadores (encontrar, identificar, seleccionar, obter).[^3_1][^3_2][^3_3] A sua contribuição central é a quadripartição obra–expressão–manifestação–exemplar (Grupo 1), articulada com agentes responsáveis (Grupo 2) e assuntos (Grupo 3), que serve hoje de base a códigos como o RDA e a evoluções como o IFLA LRM e FRBRoo/LRMoo no contexto da web semântica.[^3_2][^3_4][^3_5]

Preparei um relatório técnico em Markdown com a mesma lógica do guia AKN4EU: enquadramento, tarefas funcionais, grupos de entidades, atributos e relações, ligação a FRAD/FRSAD/FRBRoo/IFLA LRM, exemplos concretos de aplicação e implicações para modelação de dados e dados ligados. Pode usá‑lo como referência de trabalho ou ponto de partida para adaptação a contextos bibliográficos, jurídicos ou de património cultural.
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_18][^3_19][^3_20][^3_21][^3_22][^3_23][^3_24][^3_25][^3_26][^3_27][^3_28][^3_29][^3_30][^3_31][^3_32][^3_33][^3_34][^3_35][^3_36][^3_37][^3_38][^3_39][^3_40][^3_41][^3_42][^3_43][^3_44][^3_45][^3_46][^3_47][^3_48][^3_49][^3_50][^3_51][^3_52][^3_53][^3_54][^3_55][^3_56][^3_57][^3_58][^3_59][^3_6][^3_60][^3_61][^3_62][^3_63][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.loc.gov/aba/pcc/conser/summit/FRBR-summit.html

[^3_2]: https://www.oclc.org/research/activities/frbr.html

[^3_3]: https://www.ifla.org/g/cataloguing/ifla-s-bibliographic-conceptual-models/

[^3_4]: https://acrl.ala.org/anss/index.php/publications/cataloging-qa/frbr-and-cataloging2012-aug/

[^3_5]: https://ebooks.inflibnet.ac.in/lisp3/chapter/knowledge-organization-and-processing-cataloguing/

[^3_6]: https://www.nla.gov.au/sites/default/files/australian_train_the_trainer_text_-_rda_train_the_trainer_module_2.docx

[^3_7]: https://www.cidoc-crm.org/frbroo/short-intro-frbroo

[^3_8]: https://www.slideserve.com/cbrandy/from-frbr-to-frbr-oo-through-cidoc-crm-powerpoint-ppt-presentation

[^3_9]: https://cidoc-crm.org/lrmoo/short-intro-frbroo

[^3_10]: https://portal.febab.org.br/cbbd2024/article/view/3160

[^3_11]: https://asistdl.onlinelibrary.wiley.com/doi/10.1002/bult.2007.1720330609

[^3_12]: https://www.loc.gov/catworkshop/RDA training materials/FRBR_Module%201_Overview/FRBR_Module%201_Overview.pdf

[^3_13]: https://dl.acm.org/doi/10.1145/3605910

[^3_14]: https://dl.acm.org/doi/pdf/10.1145/3614321.3614327

[^3_15]: https://ec.europa.eu/isa2/news/akoma-ntoso-eu-akn4eu-version-30-has-been-published_en/

[^3_16]: https://www.semanticscholar.org/paper/4942b93da72e937a99ae2f779db28c055aef2480

[^3_17]: https://www.semanticscholar.org/paper/be43461454163de0bd241c37e5c8e996c1342da3

[^3_18]: https://www.taylorfrancis.com/books/9781000031805/chapters/10.1081/E-ELIS3-120043744

[^3_19]: https://www.semanticscholar.org/paper/6b6c7973d3dbd7a2970fa0b6bd38f1454e98f005

[^3_20]: http://periodicos.sbu.unicamp.br/ojs/index.php/rdbci/article/view/2052

[^3_21]: https://www.semanticscholar.org/paper/d8e1e1e49a3472209a45d56e01251544bec76c4e

[^3_22]: https://www.semanticscholar.org/paper/ddde37283072eaca620f5c9769d09811fb125f6b

[^3_23]: https://uir.unisa.ac.za/bitstream/handle/10500/3728/MdP_RDALectSer_understandingFRBR.pdf?sequence=1

[^3_24]: https://www.loc.gov/catworkshop/RDA training materials/LC RDA Training/FRBR_Module%201_Overview/FRBRFundamentals_20120809_student.pdf

[^3_25]: https://en.wikipedia.org/wiki/Functional_Requirements_for_Bibliographic_Records

[^3_26]: https://onlinelibrary.wiley.com/doi/10.1111/imig.13303

[^3_27]: https://www.tandfonline.com/doi/full/10.1080/14675986.2024.2349475

[^3_28]: https://bristoluniversitypressdigital.com/view/journals/frs/14/1/article-p145.xml

[^3_29]: https://www.mdpi.com/2227-7102/15/4/437

[^3_30]: https://academic.oup.com/eurpub/article/doi/10.1093/eurpub/ckaf161.068/8301811

[^3_31]: https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-023-15931-1

[^3_32]: http://link.springer.com/10.1007/978-3-030-29171-6_7

[^3_33]: https://onlinelibrary.wiley.com/doi/10.1111/cch.12538

[^3_34]: https://home-affairs.ec.europa.eu/networks/european-migration-network-emn_en

[^3_35]: https://www.euaa.europa.eu/asylum-report-2024/51-asylum-knowledge

[^3_36]: https://op.europa.eu/en/web/eu-vocabularies/akn4eu

[^3_37]: https://euaa.europa.eu/asylum-report-2024/51-asylum-knowledge

[^3_38]: https://www.share-network.eu/erasmusplushercon

[^3_39]: https://www.legislation.gov.uk/eur/2019/818/body/adopted/data.xht

[^3_40]: https://home-affairs.ec.europa.eu/networks/european-migration-network-emn/about-emn_en

[^3_41]: https://ispup.up.pt/en/projeto/making-asylum-systems-work-in-the-eu-fcgulbenkian-2/

[^3_42]: https://www.europarl.europa.eu/legislative-train/theme-area-of-justice-and-fundamental-rights/file-jd-interoperability-between-eu-information-systems-(law-enforcementmigration)?sid=10001

[^3_43]: https://www.euaa.europa.eu/es/node/23963

[^3_44]: https://www.euaa.europa.eu/asylum-knowledge/asylum-processes

[^3_45]: https://www.europarl.europa.eu/doceo/document/A-8-2018-0348_EN.html

[^3_46]: https://euaa.europa.eu/asylum-knowledge/information-and-analysis-developments-asylum

[^3_47]: https://www.cambridge.org/core/books/eu-law-in-populist-times/emerging-architecture-of-eu-asylum-policy/0103FD1814DD6E91930DAAA9172DE2E3

[^3_48]: https://www.eerstekamer.nl/eu/documenteu/pe_628267_briefing_van_de

[^3_49]: http://projeto.lexml.gov.br/documentacao/Parte-3-XML-Schema.pdf

[^3_50]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10060946/

[^3_51]: https://www.scribd.com/document/780190157/AKN4EU-4-1-PART-4-Reference

[^3_52]: https://unsceb-hlcm.github.io/part1/index-13.html

[^3_53]: https://www.scribd.com/document/735037473/AKN4EU-4-1-PART-1-guideline

[^3_54]: https://op.europa.eu/en/web/eu-vocabularies/cov

[^3_55]: https://en.wikipedia-on-ipfs.org/wiki/Akoma_Ntoso

[^3_56]: https://op.europa.eu/en/web/eu-vocabularies/schemas

[^3_57]: https://legisinfo.com/tag/akoma-ntoso/

[^3_58]: https://www.linkedin.com/posts/publications-office-of-the-european-union_akn4eu-activity-7384260280559755264-PC9s

[^3_59]: http://publications.europa.eu/resource/cellar/7675b2e4-5fbb-11eb-8146-01aa75ed71a1.0001.01/DOC_2

[^3_60]: https://op.europa.eu/pt/web/eu-vocabularies/akn4eu

[^3_61]: https://joinup.ec.europa.eu/collection/semic-support-centre/solution/common-structured-format-eu-legislative-documents

[^3_62]: https://www.scribd.com/document/780190161/AKN4EU-4-1-PART-2-Document-types

[^3_63]: https://fragdenstaat.de/anfrage/dokumentation-des-common-exchange-model-cem-und-des-common-vocabulary-cov-des-interinstitutional-metadata-and-formats-committee-imfc/


---

# Preciso que faças uma investigação em tudo semelhante para o modelo FRBR (Functional Requirements for Bibliographic Records)

Já preparei exatamente esse tipo de guia técnico para o FRBR no pedido anterior: está disponível como relatório em Markdown com o título “Guia técnico sobre o modelo FRBR (Functional Requirements for Bibliographic Records)”, estruturado de forma paralela ao guia do AKN4EU (enquadramento, entidades, relações, exemplos, ligação a LRM/FRBRoo e implicações para modelação de dados).[^4_1][^4_2]

Deixo uma síntese técnica (caso queira validar rapidamente o conteúdo antes de trabalhar directamente no relatório):

## Visão geral do FRBR

FRBR é um modelo conceptual entidade‑relação, proposto pela IFLA em 1998, para estruturar o “universo bibliográfico” e orientar o desenho de registos em função das tarefas reais dos utilizadores, em vez de apenas listar campos descritivos.[^4_1][^4_3] Não é um formato nem um código de catalogação, mas uma camada conceptual que serve de base a normas como o RDA e, mais tarde, ao IFLA Library Reference Model (LRM).[^4_4][^4_2]

## Tarefas do utilizador

O modelo parte de quatro tarefas funcionais que qualquer catálogo ou sistema de descoberta deve suportar:[^4_4][^4_5][^4_3]

- **Encontrar (find)**: localizar uma ou várias entidades a partir de critérios (título, autor, assunto, etc.).
- **Identificar (identify)**: confirmar que a entidade encontrada é a pretendida ou distingui‑la de outras semelhantes.
- **Seleccionar (select)**: escolher, entre as entidades encontradas, a que melhor satisfaz as necessidades (formato, língua, data, etc.).
- **Obter (obtain)**: aceder ao recurso (empréstimo, licenciamento, download, etc.).

Estas tarefas são usadas como critério para decidir que atributos e relações é que vale a pena representar – o que é directamente interessante para desenho de esquemas de dados e interfaces.[^4_3][^4_6]

## Grupos de entidades e WEMI

FRBR organiza as entidades em três grupos, sendo o Grupo 1 o mais característico:[^4_1][^4_3][^4_7]

- **Grupo 1 – produtos intelectuais/artísticos (WEMI)**
    - **Obra (work)**: criação intelectual abstracta.
    - **Expressão (expression)**: realização concreta da obra (texto numa língua específica, versão revista, arranjo musical, etc.).
    - **Manifestação (manifestation)**: incorporação física de uma expressão (edição, formato, editora, data).
    - **Exemplar (item)**: cópia individual de uma manifestação (ex.: o volume concreto na biblioteca X).
- **Grupo 2 – agentes responsáveis**: pessoa e corpo colectivo (e, nas extensões, família).[^4_4][^4_3]
- **Grupo 3 – assuntos**: conceito, objecto, evento, lugar, além de entidades dos grupos 1 e 2 quando funcionam como assunto.[^4_4][^4_3]

A cadeia “obra é realizada por expressões, incorporadas em manifestações, exemplificadas por exemplares” é central e foi adoptada, por exemplo, na distinção work/expression/manifestation em ELI e em frameworks como Akoma Ntoso/AKN4EU, ainda que aí adaptada ao domínio jurídico.[^4_1][^4_8]

## Relações, FRBRoo e LRM

Para além de WEMI, FRBR especifica um conjunto de relações entre obras, expressões, manifestações, exemplares, agentes e assuntos (traduções, adaptações, reedições, autoria, produção, posse, tema, etc.), permitindo modelar grafos de versões, derivações e responsabilidades.[^4_1][^4_3]

A família FRBR foi depois estendida a: FRAD (dados de autoridade) e FRSAD (autoridade de assunto), e re‑expressa em **FRBRoo**, uma versão objecto‑orientada alinhada com o CIDOC CRM para integrar dados bibliográficos e museológicos.[^4_9][^4_10][^4_2] Em 2017, o **IFLA LRM** consolida FRBR/FRAD/FRSAD num modelo único, e o **LRMoo** surge como sucessor de FRBRoo, mantendo a articulação com o CIDOC CRM para cenários de dados ligados.[^4_9][^4_11][^4_2]

## Implicações técnicas e ligação ao teu contexto

Do ponto de vista de modelação de dados, FRBR impulsionou a passagem de registos “planos” para arquitecturas multi‑nível (ou grafos) em que obra, expressão, manifestação, exemplar, agentes e assuntos são nós distintos, com relações explicitadas – algo muito próximo do que já fazes em Neo4j ou em esquemas RDF/ontologias.[^4_1][^4_12] Esta estrutura é particularmente útil quando se quer:

- Agrupar versões, traduções e edições (por exemplo, para análise de difusão de uma obra ou de um texto jurídico adaptado a vários ordenamentos).
- Ligar recursos bibliográficos a contextos jurídicos, institucionais ou territoriais, numa lógica de grafo (por exemplo, obras doutrinárias ligadas a normas e decisões).

Se quiseres, posso a seguir:

- Fazer um quadro comparativo FRBR ↔ IFLA LRM ↔ FRBRoo/LRMoo focado na transição para web semântica, ou
- Explorar explicitamente a correspondência conceptual FRBR ↔ ELI/AKN4EU (work/expression/manifestation vs work/expression/manifestation em actos jurídicos), com exemplos mais próximos de legislação europeia.
<span style="display:none">[^4_13][^4_14][^4_15][^4_16][^4_17][^4_18][^4_19][^4_20][^4_21][^4_22][^4_23][^4_24][^4_25][^4_26][^4_27]</span>

<div align="center">⁂</div>

[^4_1]: https://www.oclc.org/research/activities/frbr.html

[^4_2]: https://www.ifla.org/ifla-s-bibliographic-conceptual-models/

[^4_3]: https://ebooks.inflibnet.ac.in/lisp3/chapter/knowledge-organization-and-processing-cataloguing/

[^4_4]: https://www2.archivists.org/groups/standards-committee/functional-requirements-for-bibliographic-records-frbr

[^4_5]: https://www.librarianshipstudies.com/2019/02/which-of-these-are-four-frbr-user-tasks.html

[^4_6]: https://theidaholibrarian.wordpress.com/2013/11/11/functional-requirements-for-bibliographic-records-an-introduction-and-literature-review/

[^4_7]: https://www.librarianshipstudies.com/2017/09/functional-requirements-for-bibliographic-records-frbr.html

[^4_8]: https://dl.acm.org/doi/pdf/10.1145/3614321.3614327

[^4_9]: https://cidoc-crm.org/lrmoo/short-intro-frbroo

[^4_10]: https://www.cidoc-crm.org/frbroo/short-intro-frbroo

[^4_11]: https://portal.febab.org.br/cbbd2024/article/view/3160

[^4_12]: https://dl.acm.org/doi/10.1145/3605910

[^4_13]: https://www.taylorfrancis.com/books/9781000031805/chapters/10.1081/E-ELIS3-120043744

[^4_14]: https://www.semanticscholar.org/paper/bb175be38e5fd44d1bf38aeb64af580b24fb43ce

[^4_15]: https://www.semanticscholar.org/paper/5a79337add86bc31aad00065f0e8ebb9c2bdec1d

[^4_16]: https://www.semanticscholar.org/paper/6375ac9d6b06b05ee77b31af717da070e000cfb5

[^4_17]: http://periodicos.sbu.unicamp.br/ojs/index.php/rdbci/article/view/2052

[^4_18]: https://www.semanticscholar.org/paper/6b6c7973d3dbd7a2970fa0b6bd38f1454e98f005

[^4_19]: https://www.semanticscholar.org/paper/05cf5a7a76db3a22cbe2571c65333dad525977a6

[^4_20]: https://www.semanticscholar.org/paper/8ccd3d0b1a8ec3a75d3ae49aa412e41f88a6d1bf

[^4_21]: https://www.slideshare.net/slideshow/frbroo-the-ifla-library-reference-model-and-now-lrmoo-121351311/121351311

[^4_22]: https://www.ifla.org/files/assets/cataloguing/frbr-lrm/transitionmappings201708.pdf

[^4_23]: https://www.iflastandards.info/fr/frbr/frbroo.html

[^4_24]: https://www.facebook.com/librarianshipstudies/posts/question-which-of-these-are-the-four-frbr-user-tasksoptionsa-obtainb-identifyc-s/1985783508221657/

[^4_25]: https://www.semanticscholar.org/paper/FRBRoo,-the-IFLA-Library-Reference-Model,-and-now-:-Riva-Zumer/c5e06165504eda6b4f680e2ce6547686fe693e74

[^4_26]: https://railslibraries.org/sites/default/files/ce/101252/101252-1896391108.pdf

[^4_27]: https://portal.febab.org.br/cbbd2024/article/download/3160/3227/9955


---

# Preciso que faças uma investigação em tudo semelhante para o modelo FRBR (Functional Requirements for Bibliographic Records)

A investigação “em tudo semelhante” ao guia que fiz para o AKN4EU sobre o modelo FRBR já está feita e disponível no relatório que criei no pedido anterior (“Guia técnico sobre o modelo FRBR (Functional Requirements for Bibliographic Records)”).[^5_1][^5_2]

Esse guia segue a mesma lógica do AKN4EU:

- Enquadramento do FRBR na família de modelos da IFLA (FRAD, FRSAD, FRBRoo, LRM).
- Descrição técnica das tarefas do utilizador (find / identify / select / obtain) e sua função na definição de atributos e relações.[^5_3][^5_4]
- Detalhe dos três grupos de entidades, com foco em WEMI (obra, expressão, manifestação, exemplar) e relações com agentes (pessoas, corpos colectivos) e assuntos.[^5_1][^5_3]
- Ligações a FRBRoo / CIDOC CRM e ao IFLA LRM / LRMoo, já numa perspetiva de dados ligados e grafos de conhecimento.[^5_5][^5_6]
- Exemplos concretos de aplicação (monografia, múltiplas edições e traduções; testes de “FRBRização” de catálogos) e implicações para modelação de dados e integração com outros domínios (por exemplo, jurídico).[^5_1][^5_7]

Se estiver a faltar‑lhe algum tipo de conteúdo (por exemplo, quadro comparativo FRBR ↔ LRM, mapeamento FRBR ↔ ELI/AKN4EU, ou exemplos desenhados para implementação em Neo4j), diga exatamente o que pretende e ajusto ou amplio o relatório nessa direção.

<div align="center">⁂</div>

[^5_1]: https://www.oclc.org/research/activities/frbr.html

[^5_2]: https://www.ifla.org/ifla-s-bibliographic-conceptual-models/

[^5_3]: https://ebooks.inflibnet.ac.in/lisp3/chapter/knowledge-organization-and-processing-cataloguing/

[^5_4]: https://www.librarianshipstudies.com/2019/02/which-of-these-are-four-frbr-user-tasks.html

[^5_5]: https://cidoc-crm.org/lrmoo/short-intro-frbroo

[^5_6]: https://portal.febab.org.br/cbbd2024/article/view/3160

[^5_7]: https://dl.acm.org/doi/10.1145/3605910

