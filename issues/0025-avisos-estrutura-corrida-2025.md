# ISSUE-0025: avisos de estrutura que ficaram na corrida de 2025

- **Estado:** Resolvida no código (2026-09-25) — falta confirmar numa corrida da estação
- **Data:** 2026-09-25
- **GitHub:** #91
- **Onde dói:** `cct/extractor.py` (estrutura), `cct/sanidade.py`, `cct/auditoria.py`, `cct/recorte.py`

## O que acontece

Na terceira corrida de 2025 (277 PDF, commit `e44c0c0`), os 277 documentos chegam ao QDPX,
mas ficam 144 problemas no relatório. Por tipo:

| # | Aviso | Ocorrências |
|---|---|---|
| 1 | Anexo de remuneração sem nenhuma tabela (INCM ×3, Portway, SUPERBOOK, EMPORDEF) | 6 |
| 2 | Anexo com a tabela fora do corpo do nó | 24 |
| 3 | Corpo sem frase terminada em ponto («Mapas de horário», «Parentalidade») | 147 em 71 documentos |
| 4 | Cláusula ou artigo sem conteúdo | 21 |
| 5 | Nenhuma cláusula ou artigo reconhecido (EMPORDEF, EPAL, DHL) | 3 |
| 6 | Tabela provavelmente rodada, com palavras invertidas (AGEAS, p27) | 1 |
| 7 | Sem pasta de versões correspondente | 39 |

O TINITA está no #42 e as tabelas colapsadas no #84 (ISSUE-0024).

## O que devia acontecer

Cada aviso aponta um defeito real. Os que vêm de padrões de redação (corpos que remetem
para a lei, documentos só com tabelas) distinguem-se de uma perda de texto.

## Como reproduzir

```bash
python -m cct.pipeline_tema --pdfs data/raw/bte/bte_2025 \
    --codebook codebooks/4_08_protecao_dados.yaml --out results/runs/2025/2025_4_08
```

## Notas

Hipóteses e plano no #91. O aviso 4 pode ter diminuído com o commit `781b2f0`, que ainda
não passou por uma corrida. Registo das corridas:
[corrida-2025-macos-2026-09-24.md](../docs/validacao/corrida-2025-macos-2026-09-24.md).

## Resolução (2026-09-25)

Causa registada para os sete tipos, cada uma com o documento e a página, e corrigida por
uma regra geral com um teste que falha antes e passa depois. O registo completo, com a
medida dos 277 PDF antes e depois, está em
[avisos-2025-2026-09-25.md](../docs/validacao/avisos-2025-2026-09-25.md).

| # | Causa | Regra |
|---|---|---|
| 1 | Tabelas publicadas como imagem (INCM p3, Portway p2, SUPERBOOK p28, LAGOS p18); EMPORDEF tinha grelha torta | o aviso diz a página da imagem; os traços quase direitos passam a direitos |
| 2 | Regulamentos em anexo com os capítulos soltos; subanexos «I-(A)» como irmãos; «ANEXO A» perdia a palavra ANEXO; enquadramentos sem grelha | hierarquia dos anexos articulados e das partes; numeração com letra; níveis lidos como tabela |
| 3 | Redação: remissão acabada em ordinal («34.ª»), dois pontos antes do cabeçalho seguinte; e defeitos: «secção» minúscula como cabeçalho | ordinal fecha a frase; dois pontos + cabeçalho sem perda medida é redação; marcadores estruturais só com maiúscula |
| 4 | «[Revogado.]» e «(...)» lidos como título; «Pelo presente instrumento, […]:» lido como assinatura | são corpo; a assinatura nomeia uma entidade |
| 5 | EPAL numera «Cláusula VII-8»; EMPORDEF «Cláusula de revisão»; DHL não tem articulado | numeração romana por capítulo; designador «de revisão»; mensagem própria da alteração salarial só com tabelas |
| 6 | AGEAS: uma palavra vertical («Gestão») abaixo do mínimo de 10 letras rodadas | basta uma palavra |
| 7 | Nome da subpasta de versões | uma linha com o total, a regra e os nomes |
