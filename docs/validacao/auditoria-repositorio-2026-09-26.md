# Auditoria do repositório para a primeira release, 26-09-2026

Base examinada: `main` em `9faa8fe` (após PR #101). Esta auditoria atualiza
as instruções de uso corrente; ADRs, specs, issues e registos de gates
anteriores conservam o seu contexto e a sua data. Uma menção histórica a
comportamento antigo nesses ficheiros não é instrução para a instalação atual.

## Método e cobertura

- Inventário do repositório, README, CONTRIBUTING, documentação de operação,
  arquitetura, dados, validação, instalação, RNC, specs e issues; confronto
  das instruções com `cct/`, `scripts/`, `tests/`, constraints e os workflows
  `.github/workflows/testes.yml` e `instalacao-rede.yml`.
- Pesquisa de afirmações temporais e comandos de uso (Python, caminhos,
  aquisição, esquema RNC, Docling, OCR, métricas, numeração, fases e CI).
  As páginas de investigação, ADRs aceites/substituídos e os gates datados
  foram tratados como arquivo, sem reescrever a evidência original.
- Verificações automáticas de referências locais, segurança do conteúdo e
  espaços em branco do diff; a execução de pytest e a validação nas estações
  constam do [plano da primeira release](plano-primeira-release.md).

## Divergências corrigidas

| Área | Situação observada | Instrução atual |
|---|---|---|
| Aquisição | O guia omitira a confirmação individual de siglas na GUI | `app.py` oferece «Confirmar siglas…», guarda `siglas.csv` local e só processa os documentos marcados; CLI `nomeacao --confirmar CHAVE` existe. |
| PDFs | O erro antigo de `convencoes/convencoes` ainda aparecia como contexto | `pipeline_tema._pdfs_da_pasta` aceita pasta anual, `convencoes` e âmbito; a primeira e a segunda abrangem os âmbitos processáveis. Conferir contagem real. |
| Esquema RNC | Guia afirmava que SPEC-0004 ainda não estava implementada | ADR-0022 e `nomeacao --migrar --correspondencia` já implementados; a migração controlada de nomes escritos não autoriza mudanças posteriores de siglas sem decisão. |
| Numeração | README e guia listavam cláusulas por extenso como pendência | `cct/numeracao.py`, `cct/diacronia.py` e `tests/test_numeracao.py` dão chave canónica. |
| Qualidade | Valores 0,88/0,57 e AUTO apresentados como prova atual | Valores rotulados históricos; revisão do gabarito e validação humana da faixa AUTO pendentes (GitHub #10). |
| Instalação | Guia institucional pressupunha cópia local e, ao mesmo tempo, instalação em rede; tinha estimativas fixas | Disco local, unidade mapeada e UNC distinguidos; CI SMB não substitui estação CRL; medir tamanho do pacote gerado. |
| Rede | «Totalmente offline» e «só duas exceções» ignoravam a aquisição | Operação base offline; recolha do BTE opcional com autorização; modelos Docling pré-provisionáveis; semântica apenas loopback. |
| Testes | Windows 3.13 e CI SMB não constavam de requisitos; leitura de skips excessivamente otimista | Matriz CI atual e gates manuais separados; plano de release com evidência por ambiente. |
| Workspace | Esquema de destino descrito como se fosse criado pelos comandos | Caminhos reais de aquisição e `--out` distinguidos da proposta de arrumação futura. |

## Pontos que continuam a exigir decisão ou prova

1. **Estação CRL real**: o runner SMB simula partilha local, mas não a conta,
   proxy, permissões, região e instalação da equipa. Repetir instalação em
   `L:\`/UNC e botão «Verificar instalação» na GUI; ver ISSUE-0009/#59.
2. **Dados do BTE e MaxQDA**: índices, `siglas.csv`, PDFs, exports e resultados
   não são distribuídos no repositório. Rever cada nome por confirmar e os
   outorgantes de retificações; não converter `nomeado` em aprovação humana.
3. **Extração**: comparar as tabelas do BTE 31/2026 com o PDF célula a
   célula, em especial 380/384/385/386. A completude e os avisos automáticos
   não demonstram correção semântica de um valor.
4. **Docling e QDPX**: testar modelos offline na plataforma alvo, recursos e
   importação visual do QDPX final no MaxQDA (ISSUE-0003). OCR e semântica
   têm gate próprio se forem incluídos no âmbito da entrega.
5. **Gabarito e AUTO**: corrigir a referência humana (#10), remedir e obter
   aprovação das peritas; definir a política de revisão antes de publicar
   métricas ou afirmar que a faixa AUTO dispensa leitura.
6. **Proposta de BD operacional**: o modelo de dados ligado ao PR #101 é
   rascunho para reação (#14), sem implementação operacional nesta release.

## Critério de manutenção da documentação

Alterações futuras a comandos, caminhos, estados de aquisição, formatos,
instalação ou resultados devem atualizar na mesma mudança README, guia de
operação, página técnica relevante e ensaio de release. Uma solução manual
na estação deve registar sintoma, causa verificada, comando, ambiente,
evidência e resultado; só após revisão entra como regra reutilizável no
guia (§5.1). Manter a documentação histórica datada e apontar para a
instrução corrente em vez de alterar o registo da experiência.
