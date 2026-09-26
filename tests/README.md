# Testes

A suite mistura testes unitários rápidos, integrações de formatos e provas que
dependem do corpus local. Todos correm pelo mesmo comando:

```bash
python -m pytest -q
```

Os testes que precisam de ficheiros não distribuídos podem ser ignorados num
clone limpo. A execução local da suite, por si só, não prova o corpus real,
a instalação offline nem a importação no MaxQDA. O CI tem um job de corpus
estrito e um workflow SMB separado; ver
[plano da primeira release](../docs/validacao/plano-primeira-release.md).

## Mapa atual

| Grupo | Ficheiros principais |
|---|---|
| Extração e estrutura | `test_extractor*.py`, `test_adapter_v2.py` |
| Docling opcional | `test_extractor_docling.py`, `test_docling_integracao.py` |
| Codificação e triagem | `test_lexical.py`, `test_semantico.py`, `test_triagem.py`, `test_fase3*.py` |
| Diacronia | `test_diacronia.py`, `test_escolher_par.py`, `test_fase5b.py` |
| QDPX e offsets | `test_qdpx*.py`, `test_qdc.py` |
| Dados e contratos | `test_schemas.py`, `test_variaveis.py`, `test_referencia_harness.py` |
| Operação | `test_sanidade.py`, `test_proveniencia.py`, `test_inventario_workspace.py` |
| Aquisição e nomes | `test_recolha.py`, `test_nomeacao.py`, `test_aquisicao.py` |
| Instalação e limites | `test_pacote_offline.py`, `test_doctor.py`, `test_limites_docling.py`, `test_subprocesso_utf8.py` |
| Regressão e desempenho | `test_corpus.py`, `test_desempenho.py`, `test_completude.py` |

Os nomes `fase3`, `fase3b`, `fase3c` e `fase5b` são históricos. Não devem ser
copiados para funcionalidades novas; os testes novos recebem o nome do domínio.

## Estrutura de destino

```text
tests/
├── unit/
├── integration/
├── e2e/
├── corpus/
├── fixtures/
│   ├── synthetic/
│   ├── public/
│   └── golden/
└── conftest.py
```

A migração será gradual, juntamente com alterações reais, para evitar um commit
grande que só mova ficheiros. Quando os grupos forem separados, usar marcadores
`unit`, `integration`, `e2e`, `requires_docling`, `requires_corpus` e `slow`.

## Resultados dos testes

Os testes de unidade devem usar diretórios temporários; comandos de corpus,
desempenho e ensaios manuais podem produzir ficheiros em `results/`, que
ficam fora do Git. Baselines aprovadas e artefactos dourados pequenos pertencem a
`tests/fixtures/golden/` ou `examples/`, com proveniência documentada.
