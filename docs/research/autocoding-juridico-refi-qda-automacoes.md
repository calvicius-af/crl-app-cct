# Auto‑coding de texto jurídico e integração com ficheiros REFI‑QDA (.qdpx) usando automações

## Visão geral

O formato REFI‑QDA (.qdpx) é um padrão aberto baseado em XML, concebido para troca de projetos entre diferentes softwares de análise qualitativa (CAQDAS), como NVivo, ATLAS.ti, MAXQDA, QualCoder, QDA Miner, f4analyse e outros. Este formato permite exportar documentos, códigos, codificações e metadados para um ficheiro único comprimido (.qdpx), que pode depois ser importado em várias aplicações.[^1][^2][^3][^4]

Não existe, até à data, um “autocoder jurídico para .qdpx” pronto a usar, focado especificamente em legislação ou direito do trabalho, mas é tecnicamente possível construir pipelines que pegam em texto legal, o processam em ferramentas como n8n ou KNIME, produzem anotações/códigos e depois geram ficheiros XML compatíveis com o padrão REFI‑QDA que podem ser convertidos ou empacotados como .qdpx. Surgiram também bibliotecas open‑source em Python, como a `pyqdpx`, que permitem ler e escrever ficheiros .qdpx programaticamente, o que facilita a integração com fluxos de automação e modelos de linguagem.[^5][^6][^7][^8]

## O padrão REFI‑QDA e o formato .qdpx

O REFI‑QDA Project definiu um formato de intercâmbio de projetos de análise qualitativa baseado em XML, em que o ficheiro de projeto é guardado com a extensão .qdpx. Este ficheiro funciona como um arquivo (zip) que inclui um documento XML principal (estrutura de projeto, códigos, codificações, casos, memos) e os ficheiros de dados (textos, PDFs, imagens, áudio, vídeo).[^3][^4][^9][^1]

Instituições como a DANS (Países Baixos) recomendam o .qdpx como formato preferencial para preservação a longo prazo de projetos qualitativos, dado o seu carácter aberto e amplamente implementado em múltiplos CAQDAS. Documentação de fornecedores como MAXQDA, ATLAS.ti, QualCoder e f4analyse confirma que o REFI‑QDA é hoje o formato típico para exportar e importar projetos entre softwares.[^10][^2][^11][^1][^3]

## Software CAQDAS com autocoding e suporte .qdpx

### MAXQDA

O MAXQDA suporta exportação de projetos para o formato REFI‑QDA (.qdpx) a partir do menu "Save Project As" selecionando "REFI‑QDA Project". Nesta exportação são incluídos textos, PDFs, imagens, áudio e vídeo, bem como códigos, segmentos codificados e variáveis de casos, com algumas limitações para tipos específicos de dados (por exemplo, certas codificações em PDFs ou focos de grupos).[^12][^9][^3]

No que respeita a auto‑coding, o MAXQDA oferece:

- Autocoding baseado em pesquisa de palavras, que permite procurar termos em documentos de texto, PDFs e tabelas e codificar automaticamente os resultados.[^13][^14]
- Autocoding baseado em dicionários (categorias e famílias de palavras) para marcar automaticamente trechos onde ocorram termos de um léxico definido.[^13]
- AI Assist Coding, em que um código com definição pode ser usado para que o programa marque automaticamente todos os locais relevantes para esse código, recorrendo a assistência de IA.[^13]

Embora estas funcionalidades sejam internas ao MAXQDA, os resultados podem ser exportados em .qdpx e, em versões recentes, todos os tipos de exportação de códigos (Word, Excel, website, TXT, .qdpx, .mtr) estão disponíveis de forma mais integrada nos menus.[^14][^12]

### NVivo

O NVivo permite auto‑coding de várias formas, incluindo:

- Auto‑coding baseado em palavras e frases através de queries, útil para atribuir códigos automaticamente a ficheiros em função do vocabulário que contêm.[^15][^16]
- Auto‑coding de dados estruturados com base em estilos de parágrafo ou estrutura do documento (por exemplo, entrevistas em que cada pergunta está num determinado estilo), usando o Auto Code Wizard.[^17][^18]
- Auto‑coding por temas, em que o NVivo identifica substantivos e grupos de palavras para sugerir códigos temáticos.[^18][^15]

As versões recentes do NVivo implementam o REFI‑QDA, permitindo exportar projetos como .qdpx e importá‑los noutras ferramentas compatíveis. A documentação e guias de formação sobre NVivo sublinham o uso de auto‑coding como forma de acelerar a codificação manual e de servir de ponto de partida para revisão humana.[^19][^4][^15][^18]

### ATLAS.ti

O ATLAS.ti também implementa o REFI‑QDA, permitindo exportar bundles de projetos em formato .qdpx, que podem ser abertos em outros CAQDAS como QualCoder ou MAXQDA. A documentação de preservação digital indica que, a partir da versão 8, o REFI‑QDA está plenamente implementado e que os curadores podem receber ficheiros .atlproj ou .qdpx para preservação ou migração.[^2][^20]

Em termos de auto‑coding, o ATLAS.ti oferece ferramentas de importação de dados de inquéritos, bem como funcionalidades de codificação automática e, em versões recentes, módulos com IA para resumo e codificação.[^20]

### QualCoder e outras ferramentas

O QualCoder é um CAQDAS open‑source que implementa o padrão REFI‑QDA para exportar e importar codebooks e, com algumas limitações, projetos completos. A documentação refere que o export/import de projetos é funcional, embora não se possa garantir o cumprimento total do padrão em todos os aspectos (por exemplo, alguns detalhes de áudio/vídeo e pequenas diferenças de offset em codificações de texto).[^21][^22][^11]

Ferramentas como QDA Miner, f4analyse e outros produtos comerciais também suportam o REFI‑QDA, permitindo exportar códigos e projetos para .qdpx e importar ficheiros deste tipo gerados por outros programas.[^23][^10]

## Bibliotecas e ferramentas para manipular .qdpx em código

Uma evolução recente relevante é a biblioteca `pyqdpx`, open‑source, disponibilizada via PyPI e GitHub, que permite processar ficheiros .qdpx de acordo com o padrão REFI‑QDA. Esta biblioteca não só lê ficheiros .qdpx e extrai spans de texto anotados/codificados, como também permite editar os ficheiros e inserir novas anotações que podem depois ser visualizadas em software como o NVivo.[^6]

O autor da biblioteca refere a utilização da `pyqdpx` num projeto em que comentários de YouTube foram anotados manualmente em NVivo e automaticamente por um modelo generativo (Gemma 2) via script em Python, tendo o output dos dois anotadores sido posteriormente fundido num único ficheiro usando `pyqdpx`. Este tipo de workflow ilustra como anotações automáticas produzidas por modelos de linguagem podem ser integradas com codificação manual num ficheiro .qdpx, pronto a ser aberto num CAQDAS.[^6]

Além de `pyqdpx`, a especificação REFI‑QDA está publicada publicamente e descreve com detalhe a estrutura XML dos ficheiros, tornando possível gerar ou transformar .qdpx a partir de outros formatos XML ou JSON usando linguagens como Python, R ou Java.[^4][^1]

## Automação com n8n: de texto jurídico a XML/qdpx

O n8n é uma plataforma de automação low‑code/open‑source que permite encadear nodes para extração de ficheiros, processamento de texto, chamadas a modelos de linguagem e conversão de formatos, incluindo JSON e XML. Existem nodes para extração de texto de PDFs e para conversão de JSON em XML, bem como integrações com serviços de LLM ou APIs HTTP genéricas.[^24][^7][^25]

Discussões na comunidade n8n mostram que uma abordagem típica para ir de texto (por exemplo, extraído de PDF) a XML é:

- Extrair o texto usando um node de "PDF to Text" ou semelhante.
- Usar expressões, regex ou um LLM para identificar padrões ou segmentos específicos e produzir um objeto JSON estruturado.
- Converter o JSON em XML com um node de conversão apropriado.
[^7][^25][^24]

Aplicado ao contexto jurídico/laboral, este tipo de fluxo pode:

- Ler textos de legislação, contratos coletivos ou acórdãos em PDFs oficiais.
- Passar o texto por um LLM ou regras heurísticas para produzir uma lista de segmentos com atributos como `document_id`, `start_char`, `end_char`, `code_name` ou `article_reference`.
- Gerar XML que respeite (ou seja facilmente transformável em) a estrutura de segmentos de codificação do REFI‑QDA.
[^25][^24][^4]

Depois, esse XML pode ser:

- Incorporado num documento REFI‑QDA completo (manualmente ou via script), comprimido como .qdpx.
- Ou transformado em .qdpx via uma ferramenta de linha de comando baseada em `pyqdpx` que leia o XML intermédio e crie o projeto.
[^4][^6]

## Automação com KNIME: text mining e preparação de códigos

O KNIME é uma plataforma de análise de dados low‑code amplamente utilizada em text mining, incluindo extração de texto de PDFs, tokenização, stemming, POS tagging, dictionary tagging e classificação supervisionada. A sua extensão de Text Processing fornece nodes para converter PDFs em "Document objects", aplicar listas de stopwords, converter caixa, fazer stemming e criar bag‑of‑words ou vetores de documentos.[^8][^5]

Tutoriais sobre KNIME mostram workflows em que textos são classificados automaticamente (por exemplo, reviews de restaurantes) com base em termos presentes nos documentos, usando algoritmos como decision trees, e em que o resultado da classificação é um conjunto de etiquetas por documento. Embora esses exemplos sejam de reviews, os mesmos princípios aplicam‑se a textos jurídicos: artigos, cláusulas ou parágrafos podem ser tratados como documentos e classificados em categorias (por exemplo, "tempo de trabalho", "retribuição", "saúde e segurança").[^5][^8]

Em termos de integração com .qdpx, o KNIME não tem, de origem, um node específico para gerar ficheiros REFI‑QDA, mas:

- Pode produzir tabelas estruturadas com colunas de IDs de documentos, offsets de texto e códigos atribuídos.
- Tem nodes para conversão de dados em XML ou para exportação em CSV/JSON que depois podem ser usados em scripts externos para gerar o XML REFI‑QDA.
[^26][^5]

Assim, um fluxo plausible seria:

- Usar KNIME para processar e classificar segmentos de texto jurídico.
- Exportar o resultado como CSV/JSON.
- Usar um script em Python com `pyqdpx` para converter esses resultados em segmentos codificados dentro de um projeto REFI‑QDA.
[^5][^6]

## Outros caminhos de auto‑coding e integração

### Auto‑coding interno seguido de exportação .qdpx

Uma via relativamente simples é usar o auto‑coding interno dos CAQDAS (por exemplo, queries de palavras, dicionários, AI Assist) para aplicar códigos a textos jurídicos importados, e depois exportar o projeto em .qdpx.[^16][^15][^13]

Este método tem as seguintes características:

- Não exige construir um pipeline externo; o trabalho de auto‑coding corre dentro do software (MAXQDA, NVivo, ATLAS.ti, etc.).[^16][^13]
- O ficheiro .qdpx resultante pode ser importado noutros CAQDAS ou arquivado em repositórios que preferem o formato REFI‑QDA.[^1][^3]

Limitações importantes incluem a falta de controlo fino sobre o esquema XML subjacente e a dificuldade em integrar diretamente automações externas (n8n, KNIME) no processo de codificação.

### QualCoder como ponte aberta

Porque o QualCoder é open‑source e já suporta importação e exportação de projetos em REFI‑QDA, pode funcionar como ponte entre pipelines automáticos e software proprietário. Por exemplo:[^11][^21]

- Gerar um ficheiro REFI‑QDA (XML) com códigos e segmentos em script.
- Abrir esse projeto no QualCoder para verificação e eventual ajuste.
- Exportar novamente em .qdpx para importar em NVivo, MAXQDA ou ATLAS.ti.
[^27][^21][^11]

A documentação do QualCoder assinala, no entanto, que podem existir pequenas incompatibilidades (por exemplo, deslocações de um carácter em codificações ao importar em ATLAS.ti ou necessidade de opções específicas para importação em MAXQDA), pelo que é essencial testar e validar.[^11]

## Exemplo de arquitetura de pipeline (alto nível)

Combinando os elementos anteriores, pode descrever‑se um pipeline genérico para auto‑coding de texto jurídico com saída em .qdpx:

1. **Ingestão de texto**  
   - Fonte: PDFs de legislação, convenções coletivas, decisões jurisprudenciais.  
   - Ferramenta: n8n ou KNIME para extrair texto (`PDF to Text`, `PDF Parser`, etc.).[^25][^5]

2. **Pré‑processamento e segmentação**  
   - Normalização de texto (caixa, remoção de stopwords, tratamento de acentos).  
   - Segmentação por unidades jurídicas relevantes (artigos, números, alíneas, cláusulas).  
   - Em KNIME, usar nodes de Text Processing; em n8n, regex ou funções JavaScript.[^24][^8][^5]

3. **Auto‑coding / classificação**  
   - Opção A: Classificadores treinados (em KNIME) para atribuir categorias (por exemplo, temas de direito do trabalho).  
   - Opção B: Modelos de linguagem (por API) chamados a partir de n8n para sugerir códigos e produzir JSON com spans e rótulos.  
   - Opção C: Regras heurísticas/dicionários de termos jurídicos (por exemplo, listas de palavras‑chave para temas específicos).  
[^8][^24][^5]

4. **Produção de estrutura REFI‑QDA intermédia (XML/JSON)**  
   - Transformar o output do auto‑coding num esquema próximo do REFI‑QDA (lista de segmentos com identificador de documento, posição inicial/final e código associado).  
   - Em n8n, converter JSON em XML; em KNIME, usar nodes de escrita XML ou exportar CSV para script externo.[^7][^25]

5. **Geração de .qdpx com `pyqdpx` ou ferramenta equivalente**  
   - Num ambiente Python, usar `pyqdpx` para criar um novo projeto REFI‑QDA, importar documentos fonte (ou referências para esses documentos) e inserir as codificações automáticas como anotações.[^6]
   - Comprimir a estrutura em ficheiro .qdpx conforme o padrão REFI‑QDA.[^4][^6]

6. **Revisão e enriquecimento em CAQDAS**  
   - Abrir o .qdpx resultante em NVivo, MAXQDA, ATLAS.ti ou QualCoder.  
   - Rever manualmente os códigos sugeridos, ajustar a árvore de códigos, adicionar memos e análises adicionais.  
[^2][^21][^3]

## Considerações específicas para texto jurídico e relações laborais

Textos jurídicos (leis, códigos, IRCT, acórdãos) têm características que exigem cuidado no auto‑coding:

- Forte dependência de remissões (artigos que fazem referência a outros, diplomas que alteram ou revogam anteriores), o que torna útil pensar em ontologias ou grafos além de mera codificação temática.[^28]
- Linguagem técnica e fórmulas recorrentes, que podem favorecer abordagens baseadas em dicionários e padrões, mas também desafiar modelos treinados em linguagem geral.
- Necessidade de rastreabilidade e auditabilidade das decisões de codificação, especialmente em contextos de investigação aplicada ou consultoria técnico‑jurídica.

Os CAQDAS com funcionalidades de auto‑coding servem bem como ponto de partida, mas, para fluxos verdadeiramente automáticos do tipo n8n/KNIME → .qdpx, a combinação de bibliotecas como `pyqdpx` com pipelines de text mining ou LLM parece ser, atualmente, a via mais flexível.

## Limitações e pontos de atenção

- **Inexistência de produto turnkey**: não foi identificado um produto que faça, de forma integrada, "auto‑coding de legislação → ficheiro .qdpx" com foco em direito do trabalho ou em ordenamentos jurídicos específicos.[^1][^4]
- **Compatibilidades REFI‑QDA**: mesmo entre softwares que implementam o padrão, há relatos de pequenas incompatibilidades (offsets, tipos de dados não suportados), pelo que qualquer pipeline automático deve ser testado cuidadosamente com o software de destino.[^9][^11]
- **Questões de proteção de dados**: ao usar LLMs em fluxos n8n/KNIME, deve considerar‑se a localização dos servidores, termos de tratamento de dados e, no caso português/europeu, o RGPD, sobretudo se os textos contiverem dados pessoais sensíveis.

## Referências em estilo APA 7.ª edição

DANS. (2019, August 20). *New open standard for qualitative data launched*. https://dans.knaw.nl/en/news/new-open-standard-for-qualitative-data-launched/[^1]

Ihrmark, D., & Tyrkkö, J. (2023). Learning text analytics without coding? An introduction to KNIME. *Education for Information, 39*(3), 321–342. https://doi.org/10.3233/EFI-230027[^8]

MAXQDA. (2020, October 28). *Version 20.2.2 (Release Notes)*. https://updates.maxqda.de/2020/ReleaseNotes20.2.2.html[^12]

MAXQDA. (2021, November 21). *Export und Import von Projektdaten im REFI-QDA Format*. https://www.maxqda.com/de/hilfe-mx22/reports/export-und-import-von-projektdaten-im-refi-qda-format[^9]

MAXQDA. (2022). *Feature overview MAXQDA 2022* [PDF]. https://www.maxqda.com/wp/wp-content/uploads/sites/2/MAXQDA-features.pdf[^14]

MAXQDA. (n.d.). *How can I autocode my text?* https://help.maxqda.com/en/support/solutions/articles/80001149816-how-can-i-autocode-my-text-[^13]

Nvivo by Lumivero. (2026, May 27). *NVivo | Qualitative data analysis (QDA) software*. https://lumivero.com/products/nvivo/[^29]

Pethő, G. (2025, June 27). *pyqdpx, an open-source and free Python library for processing data exchange files that conform to the REFI-QDA XML standard* [LinkedIn post]. LinkedIn. https://www.linkedin.com/posts/gergely-peth%C5%91-458a04236_a-week-ago-i-released-pyqdpx-an-open-source-activity-734476082840066[^6]

QualCoder. (2021). *Import und Export (REFI-QDA)*. https://qualcoder.org/doc/de/6.1.-Imports-and-Exports/[^11]

QualCoder. (n.d.). *Index – QualCoder documentation*. https://qualcoder.org/doc/en/[^21]

QDAsoftware.org. (2024, May 16). *REFI-QDA Project*. https://www.qdasoftware.org/project[^4]

University of Illinois Library. (2020, January 23). *Qualitative Data Analysis: Atlas.ti*. https://guides.library.illinois.edu/c.php?g=997192&p=10050819[^20]

WordStat / Provalis Research. (2018, July 25). *Automatically code segments in a QDA Miner Project* [Video]. YouTube. https://www.youtube.com/watch?v=JwLdd8u7xnk[^23]

Zenodo. (2025, July 30). *¿Cómo transferir un proyecto de ATLAS.ti a QualCoder?* https://zenodo.org/records/15781919[^27]

---

## References

1. [New open standard for qualitative data launched - DANS - KNAW](https://dans.knaw.nl/en/news/new-open-standard-for-qualitative-data-launched/)

2. [https://conservancy.umn.edu/server/api/core/bitstr...](https://conservancy.umn.edu/server/api/core/bitstreams/9ed5db72-2c39-4023-be1a-7ac4c7bf5ff2/content)

3. [Export and Import REFI-QDA Projects - maxqda](https://www.maxqda.com/help/report-and-export/export-and-import-refi-qda-projects) - The QDPX file that is created during the export contains all documents of the project including exte...

4. [REFI-QDA Project](https://www.qdasoftware.org/project) - The QDA software packages that have implemented the REFI-QDA Project, enable some or all of these co...

5. [Text Processing with KNIME](https://medium.com/low-code-for-advanced-data-science/in-this-topic-i-will-show-some-examples-of-text-processing-with-knime-894379ed0852) - A walkthrough of some of the key functionality and applications

6. [Gergely Pethő's Post](https://www.linkedin.com/posts/gergely-peth%C5%91-458a04236_a-week-ago-i-released-pyqdpx-an-open-source-activity-7344760828400664576-capo) - A week ago I released pyqdpx, an open-source and free Python library for processing data exchange fi...

7. [GitHub - jezweb/n8n-nodes-data-converter: Comprehensive data ...](https://github.com/jezweb/n8n-nodes-data-converter) - Comprehensive data conversion node for n8n - Handle Base64, Binary, Format conversions (JSON/XML/YAM...

8. [Learning text analytics without coding? An introduction to KNIME - Daniel Ihrmark, Jukka Tyrkkö, 2023](https://journals.sagepub.com/doi/10.3233/EFI-230027?icid=int.sj-abstract.similar-articles.3) - The combination of the quantitative turn in linguistics and the emergence of text analytics has crea...

9. [Export und Import von Projektdaten im REFI-QDA Format - MAXQDA](https://www.maxqda.com/de/hilfe-mx22/reports/export-und-import-von-projektdaten-im-refi-qda-format) - Die „Rotterdam Exchange Format Initiative (REFI)“, ein Konsortium von interessierten Wissenschaftler...

10. [Exchange projects between software programs: REFI-QDA](https://www.audiotranskription.de/en/exchange-projects-between-software-programs-refi-qda/) - The REFI-QDA standard, which audiotranskription has helped to develop in recent years, enables the e...

11. [Import und Export](https://qualcoder.org/doc/de/6.1.-Imports-and-Exports/) - QualCoder Website

12. [Version 20.2.2 (2020-10-28)](https://updates.maxqda.de/2020/ReleaseNotes20.2.2.html)

13. [How can I autocode my text? : MAXQDA Support](https://help.maxqda.com/en/support/solutions/articles/80001149816-how-can-i-autocode-my-text-) - MAXQDA offers several options for automatically encoding texts: Autocodes based on found words: The ...

14. [[PDF] Feature Overview MAXQDA 2022](https://www.maxqda.com/wp/wp-content/uploads/sites/2/MAXQDA-features.pdf)

15. [[PDF] Introduction to Nvivo – a tool for qualitative data analysis](https://snd.se/sites/default/files/2024-04/Introduction%20to%20NVivo%20-%20a%20tool%20for%20qualitative%20data%20analysis.pdf)

16. [Coding](https://help-nv.qsrinternational.com/12/mac/v12.1.115-d3ea61/Content/coding/coding.htm)

17. ["Autocoding" through Styled or Structured Textual Data](https://scalar.usc.edu/works/using-nvivo-an-unofficial-and-unauthorized-primer/autocoding-through-data-ingestion.8) - To achieve automatic coding (writing information to a node) using structure data, upload or create t...

18. [Understanding Auto-Coding in Nvivo - Project Guru](https://www.projectguru.in/processing-auto-coding-nvivo/) - Nvivo allows the documents to get automatically coded in respective nodes. This saves time from goin...

19. [Switching Qualitative Software? Export & Import Projects the RIGHT Way](https://www.youtube.com/watch?v=8yFWlkNdhx8) - Are you switching between qualitative analysis software and worried about losing your work? In this ...

20. [Qualitative Data Analysis: Atlas.ti - University of Illinois LibGuides](https://guides.library.illinois.edu/c.php?g=997192&p=10050819) - Resources on conducting qualitative data analysis

21. [Index - QualCoder](https://qualcoder.org/doc/en/) - QualCoder Website

22. [Draft:QualCoder - Wikipedia](https://en.wikipedia.org/wiki/Draft:QualCoder)

23. [Automatically Code Segments in a QDA Miner Project - YouTube](https://www.youtube.com/watch?v=JwLdd8u7xnk) - Automatically code text segments in a QDA Miner Project using the results of WordStat content analys...

24. [Target text from a PDF and store in xml - Questions](https://community.n8n.io/t/target-text-from-a-pdf-and-store-in-xml/59320) - I have tested the PDF to Text extraction and I can see a dump of the text. I would like to know how ...

25. [Extract from File integrations | Workflow automation with ...](https://n8n.io/integrations/extract-from-file/) - Integrate Extract from File with hundreds of other apps. Create sophisticated automations between Ex...

26. [Exploring qualitative annotations with KNIME](https://www.youtube.com/watch?v=-x9_28MtYtw) - This tutorial describes how to use KNIME to explore annotations generated in Fiji using the Qualitat...

27. [¿Cómo transferir un proyecto de ATLAS.ti a QualCoder? - Zenodo](https://zenodo.org/records/15781919) - Presentación (guía multilingüe) en la que se detalla el proceso para transferir un proyecto de análi...

28. [Bridging the Legal Divide: Contractual Enforceability and Acceptability in the AI-Driven Automated Conversion of Smart Legal Contracts](https://ieeexplore.ieee.org/document/10835661/) - Many people find the legal system to be convoluted and resource-intensive with all of the complicati...

29. [NVivo by Lumivero | Qualitative data analysis (QDA) software](https://lumivero.com/products/nvivo/) - NVivo, the leading QDA software for qualitative research. Organize, code, and analyze unstructured d...

