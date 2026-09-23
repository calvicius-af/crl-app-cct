"""Controlos de sanidade da extração — canários de defeitos estruturais.

Não substituem a revisão humana: apanham as falhas que se detetam sem
conhecer o conteúdo, e que na prática denunciam problemas de ordem de
leitura ou de perda de texto. Os avisos vão para o relatório da corrida.

Os dois controlos nasceram da revisão MaxQDA de 2026-08-25, onde ambos
os sintomas apareceram: uma cláusula ficou sem conteúdo (o texto tinha
sido colocado antes do próprio cabeçalho) e dois documentos tinham
matéria depois da nota de depósito legal.
"""
import re

# nota de depósito do art. 494.º CT: fecha SEMPRE uma convenção publicada
# ("Depositado em 23 de janeiro…", "Depositado a 17 de julho…"). Pode vir
# colada à assinatura na mesma linha ("…Rosa Depositado a 7 de agosto…"),
# porque o extrator une a assinatura e a nota que o PDF traz seguidas.
RE_DEPOSITO = re.compile(r"^Depositad[oa]\s+(?:em|a)\s+\d", re.IGNORECASE)
RE_DEPOSITO_MID = re.compile(
    r"^.*\bDepositad[oa]\s+(?:em|a)\s+\d", re.IGNORECASE)
# retificações: publicam a correção de outra convenção e referem-se ao
# depósito desta — não têm nota de depósito própria (AE-ALT-RECT no
# registo; confirmação do utilizador na importação MaxQDA de 2026-09-17)
RE_RETIFICACAO = re.compile(
    r"\bRECT\b|[-–]RECT$|retifica", re.IGNORECASE)
# "( Revogado. )" fecha a frase tanto como "Revogado." — o fecho pode
# vir separado por espaços
RE_FRASE_FECHADA = re.compile(r"[.!?][\s)\]»”\"']*$")
_TIPOS_COM_CORPO = ("clausula", "artigo")


def clausulas_sem_corpo(doc: dict, texto: str) -> list[str]:
    """Cláusulas e artigos cujo corpo não tem uma única frase terminada.

    Um cabeçalho seguido logo de outro cabeçalho é o sintoma clássico de
    conteúdo deslocado; um corpo sem qualquer ponto final é quase sempre
    texto truncado.
    """
    falhas = []
    for no in doc.get("nos", []):
        if no.get("tipo") not in _TIPOS_COM_CORPO or not no.get("folha", True):
            continue
        bruto = texto[no["char_start"]:no["char_end"]]
        # a primeira linha é o próprio rótulo
        corpo = "\n".join(bruto.split("\n")[1:]).strip()
        if not corpo:
            falhas.append(f"{no['rotulo']}: sem conteúdo")
        elif not any(RE_FRASE_FECHADA.search(l) for l in corpo.split("\n") if l.strip()):
            falhas.append(f"{no['rotulo']}: corpo sem frase terminada em ponto")
    return falhas


def deposito_no_fim(texto: str, e_retificacao: bool = False) -> str | None:
    """Verifica que a nota de depósito legal fecha o documento.

    Retificações (confirmação de 2026-09-17): não têm nota de depósito
    própria — referem-se ao depósito da convenção que retificam. O
    subtipo AE-ALT-RECT (ou equivalente) desliga o controlo.
    """
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    if not linhas:
        return "documento vazio"
    if e_retificacao:
        return None
    # a nota pode vir colada à assinatura ("Rosa Depositado a 7…")
    posicao = next((i for i, l in enumerate(linhas)
                     if RE_DEPOSITO.match(l) or RE_DEPOSITO_MID.match(l)), None)
    if posicao is None:
        return "sem nota de depósito (art. 494.º CT) — documento truncado?"
    restantes = len(linhas) - posicao - 1
    if restantes:
        return (f"{restantes} linha(s) depois da nota de depósito "
                f"— ordem de leitura suspeita")
    return None


AVISO_RETIFICACAO_SEM_ARTICULADO = (
    "retificação sem articulado próprio: zero cláusulas é o esperado")
AVISO_SEM_ESTRUTURA = (
    "nenhuma cláusula ou artigo reconhecido: estrutura não reconhecida pelo "
    "extrator, ou documento sem articulado — verificar o PDF")


def e_retificacao(doc: dict) -> bool:
    """Pelo subtipo do schema ou pelo tipo IRCT (AE-ALT-RECT etc.), que o
    pipeline põe no doc como 'tipo_registo'."""
    return bool(RE_RETIFICACAO.search(doc.get("subtipo", ""))
                or RE_RETIFICACAO.search(doc.get("tipo_registo", "")))


def sem_articulado(doc: dict) -> str | None:
    """Zero cláusulas nunca fica ambíguo (ISSUE-0014, issue #64).

    Numa retificação é o resultado certo: a retificação corrige outra
    convenção e não tem articulado próprio. Noutro documento pode ser um
    defeito do extrator ou um documento sem articulado, e diz-se isso, sem
    sugerir truncagem.
    """
    if any(no.get("tipo") in _TIPOS_COM_CORPO for no in doc.get("nos", [])):
        return None
    return AVISO_RETIFICACAO_SEM_ARTICULADO if e_retificacao(doc) else AVISO_SEM_ESTRUTURA


def verificar(doc: dict, texto: str) -> list[str]:
    """Todos os controlos; devolve a lista de avisos (vazia = tudo bem)."""
    from .auditoria import tabelas_esperadas

    avisos = []
    aviso = sem_articulado(doc)
    if aviso:
        avisos.append(aviso)
    aviso = deposito_no_fim(texto, e_retificacao=e_retificacao(doc))
    if aviso:
        avisos.append(aviso)
    vazias = clausulas_sem_corpo(doc, texto)
    if vazias:
        avisos.append(f"{len(vazias)} cláusula(s)/artigo(s) sem corpo válido: "
                      + "; ".join(vazias[:5])
                      + (" …" if len(vazias) > 5 else ""))
    sem_tabela = tabelas_esperadas(doc, texto)
    if sem_tabela:
        avisos.extend(sem_tabela[:5]
                      + (["…"] if len(sem_tabela) > 5 else []))
    return avisos
