# Checklist de importação no MaxQDA — Gate da Fase 0

Ficheiro a importar: `examples/acip_fesaht/saida/projeto.qdpx` (à data: `pipeline/trabalho/fase0_demo.qdpx`)
(2 documentos reais do BTE 2025: AHP/SITESE e ACIP/FESAHT; 7 codificações automáticas de demonstração)

## Passos
1. MaxQDA → **Início → Importar → Projeto REFI-QDA (QDPX)** e escolher `fase0_demo.qdpx`.
2. Confirmar que o projeto abre sem erros ou avisos.

## Verificações (marcar cada uma)
- [x] Os **2 documentos** aparecem no Sistema de Documentos com os nomes `25_PR_001_BTE_01_AHP_SITESE` e `25_PR_003_BTE_02_ACIP_FESAHT`.
- [x] O Sistema de Códigos mostra os códigos `AUTO/Tabela_Salarial`, `AUTO/Subsidio_Refeicao`, `AUTO/Vigencia`.
- [x] No documento AHP/SITESE, o segmento codificado com `AUTO/Subsidio_Refeicao` **começa exatamente em "Artigo 1.º"** e cobre o artigo do valor da alimentação (não desalinhado, não cortado a meio de palavra).
- [x] No documento ACIP/FESAHT, o segmento `AUTO/Vigencia` cobre a **Cláusula 3.ª (Vigência)**.
- [x] Ao clicar num segmento codificado, o comentário/descrição mostra `método=lexical; confiança=…; evidência=…`.
- [x] Caracteres portugueses (ç, ã, º, €) aparecem corretamente em todo o texto.

## Resultado
- Se **todas** as caixas ficarem marcadas → gate da Fase 0 passado; segue-se a Fase 1 (extração robusta).
- Se algum segmento estiver **desalinhado** (offsets errados): anotar o documento, o código e por quantos caracteres está desviado — é a informação necessária para corrigir o exportador.
