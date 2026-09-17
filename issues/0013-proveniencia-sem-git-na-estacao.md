# ISSUE-0013: a proveniência perde o commit quando não há git na estação

- **Estado:** Aberta
- **Data:** 2026-09-17
- **GitHub:** #63 (sub-issue de #58)
- **Onde dói:** `cct/proveniencia.py` (`estado_git`, L41-51)

## O que acontece

O `manifest.json` da corrida feita na estação do CRL em 2026-09-17 traz:

```json
"environment": {
  "python": "3.13.5",
  "platform": "Windows-11-10.0.26200-SP0",
  "git": { "commit": null, "dirty": null }
}
```

A corrida está registada, com hashes de todas as entradas e saídas, mas **sem identificação
da versão do código que a produziu**. Não há aviso nenhum: nem na saída da corrida, nem no
manifesto, nem no relatório.

## Porque é que isto importa

O ADR-0014 estabelece que cada corrida produz um manifesto com comando, *commit*, ambiente
e hashes. O propósito é poder responder, meses depois, à pergunta *que código produziu este
resultado?*. Com `commit: null` essa pergunta fica sem resposta, e o manifesto passa a
provar apenas integridade local dos ficheiros.

Numa estação institucional, que é onde o trabalho a sério acontece, o git não está
instalado. Ou seja: o caso em que a proveniência mais importa é precisamente aquele em que
ela se degrada, e em silêncio.

## Causa

```python
def estado_git(raiz: Path) -> dict:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=raiz, text=True,
            stderr=subprocess.DEVNULL).strip()
        ...
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
```

Sem git no PATH, o `subprocess` levanta `FileNotFoundError`, subclasse de `OSError`, que é
apanhado. A função devolve `None` sem distinguir três situações muito diferentes: git não
instalado; pasta que não é um repositório; e git a falhar por outra razão. O `stderr` do
git é descartado em todos os casos.

## O que devia acontecer

Duas coisas, e a segunda é a que resolve o problema de fundo:

1. **Distinguir e registar o motivo.** Em vez de `null` mudo, guardar por que razão não há
   *commit* (`git_ausente`, `fora_de_repositorio`, `erro`) e avisar uma vez na saída da
   corrida. Um `null` explicado vale muito mais do que um `null` silencioso.
2. **Não depender do git para saber a versão.** Se o produto passa a ser distribuído sem
   git, a identificação da versão tem de viajar com o código — por exemplo um ficheiro de
   versão escrito na preparação do pacote offline, que o manifesto lê quando o git não
   responde. Isto liga-se ao pacote offline e merece ser desenhado em conjunto.

## Notas

Prioridade baixa face aos restantes achados do gate: não impede ninguém de trabalhar. Mas
é uma perda silenciosa, e essas são as que só se descobrem quando já é tarde, com uma
corrida antiga cuja origem ninguém consegue reconstituir.
