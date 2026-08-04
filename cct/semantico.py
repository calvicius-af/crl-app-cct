"""Codificação semântica via LLM (Fase 4).

Aplica-se APENAS às cláusulas sem anotação lexical — a cascata do plano:
lexical (barato) → contexto → LLM (só no resto). O backend é injetável:
qualquer callable prompt→resposta (mock nos testes; CLI do Claude na
execução real). Respostas em JSON são validadas contra o codebook e
cacheadas em disco por hash do prompt.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

MAX_CHARS_LOTE = 12000
CONFIANCA_MINIMA = 0.5

PROMPT_BASE = """És um assistente de análise qualitativa de convenções coletivas de trabalho portuguesas do CRL.

Livro de códigos do tema {tema}:
{codebook}

Analisa as cláusulas abaixo. Para cada cláusula que trate substantivamente de um dos códigos acima, devolve um objeto JSON. Ignora cláusulas que não tratem destes temas. A variabilidade terminológica é esperada (ex.: "cadastro individual" = registo de pessoal); interpreta pelo sentido jurídico, não pelas palavras exatas.

Responde APENAS com um array JSON (pode ser vazio []), sem mais texto:
[{{"id": <número da cláusula entre parênteses retos>, "codigo": "<id do código>", "confianca": <0.0-1.0>, "justificacao": "<uma frase>"}}]

CLÁUSULAS (cada uma começa com o seu número [n]):
{clausulas}"""


def _resumo_codebook(codebook: dict) -> str:
    linhas = []
    for c in codebook.get("codigos", []):
        termos = ", ".join(c.get("termos", [])[:6])
        linhas.append(f"- {c['id']} {c.get('nome', '')}: exemplos de termos: {termos}")
    return "\n".join(linhas)


def _montar_lotes(candidatas: list[dict], texto: str,
                  max_chars: int = MAX_CHARS_LOTE) -> list[list[dict]]:
    lotes, atual, tamanho = [], [], 0
    for no in candidatas:
        n_chars = no["char_end"] - no["char_start"]
        if atual and tamanho + n_chars > max_chars:
            lotes.append(atual)
            atual, tamanho = [], 0
        atual.append(no)
        tamanho += n_chars
    if atual:
        lotes.append(atual)
    return lotes


def _extrair_json(resposta: str):
    m = re.search(r"\[.*\]", resposta, re.DOTALL)
    if not m:
        return []
    try:
        dados = json.loads(m.group(0))
        return dados if isinstance(dados, list) else []
    except json.JSONDecodeError:
        return []


def codificar_semantico(doc: dict, texto: str, codebook: dict, backend,
                        nos_ja_anotados: set[str],
                        cache_dir: Path,
                        max_lotes: int | None = None,
                        max_chars: int = MAX_CHARS_LOTE) -> dict:
    """Codifica semanticamente as cláusulas não anotadas pelo lexical.

    Erros do backend num lote não interrompem os restantes — ficam
    registados em `falhas` no resultado."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    ids_validos = {c["id"] for c in codebook.get("codigos", [])}
    resumo = _resumo_codebook(codebook)

    candidatas = [n for n in doc["nos"]
                  if n["tipo"] in ("clausula", "artigo")
                  and n.get("folha")
                  and n.get("origem", "novo") == "novo"
                  and n["id"] not in nos_ja_anotados]
    por_rotulo = {n["rotulo"]: n for n in candidatas}

    anotacoes = []
    falhas = []
    lotes = _montar_lotes(candidatas, texto, max_chars=max_chars)
    if max_lotes is not None:
        lotes = lotes[:max_lotes]
    for n_lote, lote in enumerate(lotes, 1):
        corpo = "\n\n".join(
            f"[{i}] {texto[n['char_start']:n['char_end']]}"
            for i, n in enumerate(lote, 1))
        prompt = PROMPT_BASE.format(tema=codebook.get("tema", ""),
                                    codebook=resumo, clausulas=corpo)
        chave = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        ficheiro = cache_dir / f"{chave}.json"
        if ficheiro.exists():
            resposta = ficheiro.read_text(encoding="utf-8")
        else:
            try:
                resposta = backend(prompt)
            except Exception as e:
                falhas.append(f"lote {n_lote}: {e}")
                continue
            ficheiro.write_text(resposta, encoding="utf-8")
        for item in _extrair_json(resposta):
            if not isinstance(item, dict):
                continue  # modelos pequenos às vezes devolvem strings soltas
            # emparelhamento primário por índice numérico (robusto com
            # modelos pequenos); rótulo exato como recurso
            no = None
            try:
                idx = int(item.get("id"))
                if 1 <= idx <= len(lote):
                    no = lote[idx - 1]
            except (TypeError, ValueError):
                pass
            if no is None:
                no = por_rotulo.get(str(item.get("rotulo", "")).strip())
            codigo = str(item.get("codigo", "")).strip()
            try:
                confianca = float(item.get("confianca", 0))
            except (TypeError, ValueError):
                continue
            if no is None or codigo not in ids_validos:
                continue
            if not (CONFIANCA_MINIMA <= confianca <= 1.0):
                continue
            anotacoes.append({
                "no_id": no["id"],
                "char_start": no["char_start"],
                "char_end": no["char_end"],
                "codigo": codigo,
                "confianca": confianca,
                "metodo": "llm",
                "nivel": "clausula",
                "evidencia": str(item.get("justificacao", ""))[:300],
            })
            for eixo in codebook.get("eixos", []):
                if codigo.startswith(eixo + "."):
                    anotacoes.append({**anotacoes[-1], "codigo": eixo})
    return {
        "versao_schema": "0.1",
        "doc_id": doc["doc_id"],
        "anotacoes": anotacoes,
        "falhas": falhas,
    }


def backend_lmstudio(prompt: str, modelo: str,
                     base_url: str = "http://127.0.0.1:1234",
                     temperatura: float = 0.0,
                     max_tokens: int = 6000,
                     timeout: int = 600) -> str:
    """Backend local: servidor OpenAI-compatível do LM Studio."""
    import urllib.request

    corpo = json.dumps({
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperatura,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    pedido = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=corpo, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"LM Studio HTTP {e.code}: {detalhe}") from e
    return dados["choices"][0]["message"]["content"]


def backend_claude_cli(prompt: str, modelo: str = "haiku") -> str:
    """Backend real: CLI do Claude Code em modo não-interativo.

    Requer sessão autenticada (`claude` já usado nesse terminal). Se o
    modelo pedido não estiver disponível no plano, tenta sem --model.
    """
    import os
    # variáveis ANTHROPIC_* herdadas (ex.: API key antiga no .zshrc) têm
    # prioridade sobre a sessão iniciada e causam 401 — usar só o login da CLI
    ambiente = {k: v for k, v in os.environ.items()
                if not k.startswith("ANTHROPIC_")}

    def correr(args):
        return subprocess.run(["claude", "-p", prompt, "--output-format", "text",
                               *args], capture_output=True, text=True,
                              timeout=300, env=ambiente)

    r = correr(["--model", modelo] if modelo else [])
    if r.returncode != 0 and modelo:
        r = correr([])  # fallback: modelo por omissão da sessão
    if r.returncode != 0:
        detalhe = (r.stderr or "").strip() or (r.stdout or "").strip()
        raise RuntimeError(
            f"claude CLI falhou (rc={r.returncode}): {detalhe[:400] or 'sem output'}. "
            "Confirma que 'claude' funciona nesse terminal (corre: claude -p 'ok').")
    return r.stdout
