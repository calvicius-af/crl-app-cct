# Mission: Docling na extração de convenções coletivas

## Why

O `cct/extractor.py` reconstrói a hierarquia das convenções (capítulo → secção →
cláusula → número → alínea) com cerca de uma dúzia de expressões regulares sobre o texto
plano que o `pdfplumber` devolve. Cada PDF do BTE com layout fora do comum obriga a mais
uma regra. O Docling devolve documentos já segmentados por um modelo de layout — títulos,
parágrafos, listas e **tabelas** vêm identificados, com a página de origem. A missão é
saber usar isso para reduzir a heurística que hoje sustenta a Fase 1 do pipeline, sem
perder a propriedade de zero-perda nem a rastreabilidade por offsets.

## Success looks like

- Converter um PDF do BTE com o Docling e explicar, sem consultar documentação, o que
  cada opção do pipeline fez ao documento.
- Percorrer um `DoclingDocument` em Python e listar as cláusulas de uma convenção
  **sem escrever uma única expressão regular**.
- Extrair uma tabela salarial de um anexo para `pandas`/CSV com a estrutura de linhas e
  colunas preservada — hoje o extractor trata tabelas como texto entre sentinelas.
- Instalar e correr o Docling numa máquina do CRL **sem acesso à internet**, com os
  modelos pré-descarregados.
- Escrever a decisão técnica: onde é que o Docling entra no pipeline do AppCCT, onde é
  que não entra, e com que custo.

## Constraints

- **As máquinas do CRL não têm internet.** O Docling descarrega modelos de ML na primeira
  utilização; qualquer receita que dependa disso é inútil em produção. O pré-fetch de
  modelos e o `artifacts_path` são matéria obrigatória, não avançada.
- Instalação pesada: o `pip install docling` puxa o PyTorch. Medido nesta sessão,
  um ambiente virtual limpo com `docling` ocupa **5,5 GB**, contra os ~30 MB das quatro
  dependências actuais do AppCCT. Isto é um argumento de decisão, não um detalhe.
- Só CPU. Nada de pipeline VLM com GPU.
- O AppCCT tem uma suite automática e um corpus revisto por peritas. Aprende-se ao lado do
  pipeline, não por cima dele.

## Out of scope

- RAG, *embeddings* e *chunking* para pesquisa semântica — o AppCCT já tem o seu próprio
  `cct/semantico.py`. O Docling entra aqui como extrator, não como motor de pesquisa.
- Pipeline VLM (GraniteDocling e afins) e ASR/vídeo.
- Substituir o `cct/extractor.py`. A missão é *avaliar e absorver estrutura*, e a decisão
  de substituir (ou não) é o produto do fim, não a premissa do início.
