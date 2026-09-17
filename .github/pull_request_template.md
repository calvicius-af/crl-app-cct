## O que muda

<!-- Em duas linhas: o efeito, não o mecanismo. -->

## Porquê

<!-- Liga a um issue, spec ou ADR, se existir. -->

## Verificação

- [ ] `python -m pytest -q` — todos os testes passam
- [ ] Acrescentei teste(s) para o comportamento novo ou para o problema corrigido
- [ ] `python scripts/verificar_seguranca.py` — sem dados, credenciais, segredos ou ficheiros fora da *allowlist*
- [ ] `python scripts/verificar_referencias.py` — sem links Markdown nem caminhos de documentação locais quebrados ou sensíveis a maiúsculas/minúsculas
- [ ] As três regras críticas continuam válidas (UTF-8 sem BOM/LF · zero perda de texto · pipeline agnóstico de temas)
- [ ] Se houve decisão estruturante, escrevi o ADR correspondente
