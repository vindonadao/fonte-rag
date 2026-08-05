"""Fase 6 — Avaliação. Mede o RAG num golden set com as 4 métricas do RAGAS.

    python -m eval.run

Nota de engenharia: a lib RAGAS 0.4.3 tem conflito de import com o LangChain 1.x
instalado (importa `langchain_community.chat_models.vertexai`, caminho removido nas
versões novas do langchain-community). Em vez de travar o stack que já funciona, as
quatro métricas — as MESMAS do RAGAS — são computadas aqui com um LLM-juiz
(claude-sonnet-4-6, temperature 0):

- faithfulness       → a resposta é fiel ao contexto? (mede ALUCINAÇÃO)
- answer_relevancy   → a resposta responde à pergunta?
- context_precision  → o contexto recuperado é relevante? (retrieval trouxe lixo?)
- context_recall     → o contexto contém o necessário para a resposta esperada?

Diagnóstico que vale ouro: faithfulness baixo = problema de GERAÇÃO/prompt;
context_precision/recall baixo = problema de RETRIEVAL (chunk, k, embedding).

Além do golden set, roda o ABSTENTION SET (`abstention_set.json`): perguntas
plausíveis que NÃO têm resposta no acervo. Golden set mede o acerto quando a
resposta existe; abstenção mede a recusa quando ela não existe. Sem o segundo,
o "Não encontrei" é uma promessa não medida — e ele é a identidade do produto.
"""
import json
import re
from pathlib import Path

from langchain_anthropic import ChatAnthropic

from app.chain import build_chain
from app.retriever import get_retriever

GOLDEN = Path(__file__).parent / "golden_set.json"
ABSTENTION = Path(__file__).parent / "abstention_set.json"
KEYS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]

# Mesmo critério do guardrail de saída (app/guardrails.py): a recusa é o texto
# que o system prompt manda o modelo devolver quando o contexto não sustenta.
REFUSAL = "não encontrei"

JUDGE = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

RUBRIC = """Você é um avaliador rigoroso de sistemas RAG. Dada uma PERGUNTA, o CONTEXTO
recuperado, a RESPOSTA gerada e a RESPOSTA ESPERADA (ground truth), atribua quatro notas
de 0.0 a 1.0:

- faithfulness: proporção das afirmações da RESPOSTA sustentadas pelo CONTEXTO
  (1.0 = tudo ancorado; 0.0 = inventado).
- answer_relevancy: o quanto a RESPOSTA responde diretamente à PERGUNTA, sem enrolação.
- context_precision: o quanto o CONTEXTO recuperado é relevante para responder à PERGUNTA.
- context_recall: o quanto o CONTEXTO contém a informação da RESPOSTA ESPERADA.

Responda SOMENTE um JSON válido, sem texto ao redor:
{"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0, "context_recall": 0.0}"""


def judge(question: str, contexts: list[str], answer: str, ground_truth: str) -> dict:
    ctx = "\n---\n".join(contexts) or "(vazio)"
    prompt = (
        f"{RUBRIC}\n\nPERGUNTA:\n{question}\n\nCONTEXTO:\n{ctx}\n\n"
        f"RESPOSTA:\n{answer}\n\nRESPOSTA ESPERADA:\n{ground_truth}"
    )
    raw = JUDGE.invoke(prompt).content
    if isinstance(raw, list):  # alguns provedores retornam blocos
        raw = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in raw)
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise ValueError(f"juiz não devolveu JSON: {raw[:120]}")
    data = json.loads(match.group(0))
    return {k: max(0.0, min(1.0, float(data.get(k, 0.0)))) for k in KEYS}


def run_abstention(chain) -> tuple[int, int]:
    """Mede a taxa de abstenção: o sistema recusa quando não tem a resposta?

    Não usa LLM-juiz. O critério é binário e verificável: a resposta contém a
    frase de recusa? Falso negativo aqui (o modelo responde algo) é o pior erro
    possível num RAG documental, porque a alucinação sai com cara de citação.
    """
    perguntas = json.loads(ABSTENTION.read_text(encoding="utf-8"))
    print(f"\n\nAbstenção — {len(perguntas)} perguntas SEM resposta no acervo...\n")
    acertos = 0
    for i, item in enumerate(perguntas, 1):
        q = item["question"]
        try:
            answer = chain.invoke(q)
        except Exception as e:
            print(f"  [{i}/{len(perguntas)}] ERRO: {type(e).__name__} — {q[:50]}")
            continue
        recusou = REFUSAL in answer.lower()
        acertos += recusou
        print(f"  [{i}/{len(perguntas)}] {'RECUSOU ' if recusou else 'RESPONDEU'} | {q[:52]}")
        if not recusou:
            print(f"       ↳ vazou: {answer[:110].strip()}")
    return acertos, len(perguntas)


def main():
    golden = [g for g in json.loads(GOLDEN.read_text(encoding="utf-8"))
              if g.get("ground_truth", "").strip()]
    chain = build_chain()
    retriever = get_retriever()

    totals = {k: 0.0 for k in KEYS}
    ok = 0
    print(f"Avaliando {len(golden)} perguntas com LLM-juiz (claude-sonnet-4-6)...\n")
    for i, item in enumerate(golden, 1):
        q = item["question"]
        try:
            contexts = [d.page_content for d in retriever.invoke(q)]
            answer = chain.invoke(q)
            s = judge(q, contexts, answer, item["ground_truth"])
        except Exception as e:  # não deixa um item derrubar a rodada inteira
            print(f"  [{i:>2}/{len(golden)}] ERRO: {type(e).__name__} — {q[:50]}")
            continue
        ok += 1
        for k in KEYS:
            totals[k] += s[k]
        print(f"  [{i:>2}/{len(golden)}] " +
              "  ".join(f"{k[:4]}={s[k]:.2f}" for k in KEYS) + f"  | {q[:48]}")

    if not ok:
        raise SystemExit("Nenhuma pergunta avaliada.")
    print(f"\n==== MÉDIAS (golden set de {ok} perguntas) ====")
    for k in KEYS:
        print(f"  {k:18} {totals[k]/ok:.3f}")

    acertos, total = run_abstention(chain)
    print(f"\n==== ABSTENÇÃO ({total} perguntas fora do corpus) ====")
    print(f"  taxa de recusa     {acertos}/{total} = {acertos/total:.3f}")


if __name__ == "__main__":
    main()
