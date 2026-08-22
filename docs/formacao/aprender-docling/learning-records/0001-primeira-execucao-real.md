# Primeira conversão real, executada pelo formando

Em 2026-08-21 o formando correu a lição 1 num PDF real do BTE
(`3_BTE_2_ACIP_FESAHT.pdf`), com um comando multi-linha e flags, e obteve uma conversão
bem-sucedida em 78,4 s. É evidência de nível **Operador** do
[referencial de competências](../../referencial-competencias-python.md): executa um comando
existente, interpreta o output do terminal, e reconhece quando algo (a descarga de
`modelscope.cn`) não bate certo com a expectativa de trabalho offline — trouxe o log em vez
de assumir que estava tudo bem ou desistir.

## Evidência

- Comando corrido com continuação de linha (`\` + Enter) e flags depois do caminho do PDF.
- Log completo trazido para análise, incluindo timestamps — permitiu reconstruir a sequência
  exacta de downloads (RapidOCR via `modelscope.cn`, depois layout via Hugging Face).

## Implicações

- O formando já não precisa de exemplos de "como formatar um comando de terminal" — dúvidas
  futuras podem assumir esse nível.
- A oficina ganhou o seu primeiro facto confirmado por execução real (ver `NOTES.md`,
  "Verificação do material"): o segundo host de rede (`modelscope.cn`) para o motor de OCR
  por omissão. As lições 03 e o cartão de referência foram corrigidos com esta informação.
- Próximo passo natural: repetir a conversão com `--no-ocr` e comparar o tempo e o número de
  hosts contactados — é o primeiro passo real da lição 4, ainda por escrever.
