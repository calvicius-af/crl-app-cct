# ISSUE-0022: os nomes dos ficheiros não seguem o esquema definido em docs/rnc/README.md

- **Estado:** Aberta
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
