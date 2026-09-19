# ISSUE-0022: os nomes dos ficheiros não seguem o esquema definido em docs/rnc/README.md

- **Estado:** Resolvida — 2026-09-18
- **Data:** 2026-09-18
- **GitHub:** (a criar)
- **Onde dói:** `cct/nomeacao.py` (`nome_documento`, `ESQUEMAS`), `docs/rnc/README.md` §4

## O que acontece

Os 14 ficheiros do BTE 31/2026 têm nomes do **esquema de 2025**:

```text
26_PR_001_BTE_31_ACRAL_CESP.pdf
26_PR_006_BTE_31_EmpresaMetropolitana_SINTAP.pdf
```

Mas `docs/rnc/README.md` §4.1 define o esquema RNC com sete campos:

```text
{ANO}_{AMBITO}_{SEQ}_{TIPO}_{CODIRCT}_BTE_{NN}_{SIGLAS}
2026_PRI_377_CCT-ALT_27251_BTE_31_ACRAL-CESP-STRUP+2
```

As diferenças concretas:

| Campo | Esquema de 2025 (atual) | Esquema RNC (docs/rnc/README.md) |
|---|---|---|
| Ano | `26` (2 dígitos) | `2026` (4 dígitos) |
| Âmbito | `PR` | `PRI` |
| Sequencial | `001` (ordinal interno) | `377` (n.º DGCP do `IDDocumento`) |
| Tipo | ausente | `CCT-ALT` |
| Código IRCT | ausente | `27251` |
| BTE | `BTE_31` | `BTE_31` |
| Siglas | `ACRAL_CESP` (underscore) | `ACRAL-CESP-STRUP+2` (hífen, `+N`) |

## O que devia acontecer

Decidir e executar uma das duas:

1. **Migrar os nomes** para o esquema RNC — mas `docs/rnc/README.md` §7 diz
   explicitamente que **os nomes não se alteram**: migrar nomes quebra o trabalho já
   feito no MAXQDA, que referencia os documentos pelo nome. Se for esta via, exige
   decisão de equipa e nova versão do documento.
2. **Corrigir a documentação** — se o esquema RNC ainda não se aplica ao corpus de 2026
   (que foi nomeado com o esquema de 2025), o README deve dizer isso claramente, para
   não parecer que a aplicação está errada quando segue o esquema antigo.

A aplicação já suporta os dois esquemas (`ESQUEMAS = ("pipeline", "rnc")` em
`cct/nomeacao.py`), e `--esquema rnc` gera o formato novo. O que falta é decidir qual é
o vigente para este corpus e alinhar documentação e prática.

## Como reproduzir

```bash
ls data/raw/bte/bte_2026/
python -m cct.nomeacao --esquema rnc --destino /tmp/teste   # simula o esquema novo
```

## Notas

- A confusão é compreensível: `docs/rnc/README.md` §4.1 apresenta o esquema RNC como *a*
  convenção, e §7 diz que os nomes de 2025 se mantêm. Falta uma frase a dizer **a partir
  de quando** o esquema RNC se aplica — o corpus de 2026 foi nomeado com o antigo.
- Verificar o que o `--esquema rnc` produz para estes 14 documentos: se gerar nomes
  válidos (≤63 caracteres, sem colisões), a migração é tecnicamente possível; a decisão
  é de equipa, não técnica.
- Relacionada com a ISSUE-0011 (nomeação e `--siglas`) e com o ADR-0016 (esquema de
  nomes).

## Decisão e o que foi feito

Decisão de equipa: o corte é pelo **ano do corpus**, não pela data em que se corre a
aplicação. Ficheiros de corpos até 2025 mantêm o nome que já têm. A partir do corpus de
2026, inclusive, o esquema RNC é obrigatório, sem período de transição — logo o BTE
31/2026 está abrangido. Fundamentação completa em
[ADR-0021](../docs/adr/0021-corte-por-ano-do-esquema-de-nomes.md).

Executado:

1. `docs/rnc/README.md` §4.1 e §10, `docs/dados/README.md` e
   `docs/operacao/guia-operacao.md` passam a dizer explicitamente a partir de quando o
   esquema RNC se aplica, em vez de só apresentá-lo como a convenção corrente.
2. `python -m cct.nomeacao` **e** `python -m cct.aquisicao` (o encadeamento normal, que
   é o que a app gráfica lança) passam a ter `--esquema rnc` por omissão, alinhados com
   `cct/catalogo.py`, que já assumia `rnc`. A primeira versão desta correção só tinha
   mudado `cct.nomeacao`; `cct.aquisicao` chamava `nomear()` sem indicar esquema e
   continuava a produzir nomes de 2025 — falha apanhada na revisão do PR #69, antes do
   merge. Quem precisar do esquema de 2025 pede-o com `--esquema pipeline`.
3. Os 14 ficheiros do BTE 31/2026 nomeados com o esquema de 2025, os PDF intermédios da
   recolha e as execuções do pipeline geradas a partir deles foram apagados e
   recolhidos de novo com `--esquema rnc`, já nomeados corretamente. Nada disto está
   versionado (`data/` e `results/` são ignorados pelo Git): quem tiver uma cópia do
   corpus de 2026 com o esquema de 2025 tem de repetir esta limpeza e recolha
   localmente — o merge desta correção não a propaga.

Consequência a acompanhar: as ISSUE-0015 a ISSUE-0021 citavam nomes de ficheiro do
esquema antigo (`26_PR_NNN_…`); com o corpus renomeado, passam a referir-se aos nomes
RNC equivalentes (ex.: `26_PR_006_BTE_31_EmpresaMetropolitana_SINTAP` →
`2026_SPE_382_AE_47252_BTE_31_EmpresaMetropolitana-SINTAP`). O defeito de extração que
descrevem não muda.
