
Recolher informação
- verificar se existem alterações no site
- verificar publicações em [[BTE]]
- extrair metadados do ficheiro para uma lista, ficheiro ou base de dados
- extrair ficheiros para uma pasta
- renomear os ficheiros se necessário

Retirar informação dos ficheiros
- retirar informação dos PDF para MARKDOWN ou TXT
- fazer lint dos ficheiros retirados
- consoante os metadados (tipo e subtipo. de ficheiros) proceder ao tratamento dos ficheiros, ao nível da estrutura
	- se for primeira convenção, identificar estrutura normal
	- se for revisão global, identificar estrutura normal
	- se for revisão parcial 'e texto consolidado', identificar partes novas e identificar 'texto consolidado'
	- se for revisão parcial '/ texto consolidado', identificar tudo como texto consolidado
	- identificar estrutura normal
		- identificar preambulo
		- identificar capítulos
		- identificar secções
		- identificar cláusulas
		- identificar anexos
			- identificar tabelas
			- identificar regulamentos
			- identificar capítulos
			- identificar secções
			- identificar artigos

Processar temas
- identificar temas
	- procurar primeiro tema
		- procura lexical
		- procura semântica
		- outros tipos de procura
	- codificar primeiro tema
		- atribuir informação do primeiro tema, com grau de confiança
	- procurar segundo tema
	- codificar segundo tema

Com toda a informação recolhida, construir ficheiro para MaxQDA
- construir ficheiro segundo parâmetros QDPX
	- ficheiro de projeto, documento a documento?
