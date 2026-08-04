## O que muda

<!-- Em duas linhas: o efeito, não o mecanismo. -->

## Porquê

<!-- Liga a um issue, spec ou ADR, se existir. -->

## Verificação

- [ ] `python -m pytest -q` — todos os testes passam
- [ ] Acrescentei teste(s) para o comportamento novo ou para o problema corrigido
- [ ] `git ls-files | grep -iE '\.(pdf|qdpx|mqda|xlsx|qdc)$'` — nada fora de `examples/` e `tests/`
- [ ] As três regras críticas continuam válidas (UTF-8 sem BOM/LF · zero perda de texto · pipeline agnóstico de temas)
- [ ] Se houve decisão estruturante, escrevi o ADR correspondente
