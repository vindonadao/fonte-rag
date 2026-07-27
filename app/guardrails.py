"""Fase 4 — Guardrails. AI Security: prompt injection + context control.

A blocklist é a camada MAIS FRACA (burla-se com paráfrase). Está aqui como
primeira barreira barata. A defesa real são as três da chain: contexto isolado
do prompt, temperature=0, e a saída "Não encontrei". Ver OWASP Top 10 for LLM.
"""
MAX_LEN = 500
BLOCK = ["ignore as instruções", "ignore previous", "system prompt",
         "esqueça as regras", "you are now", "disregard"]


def validate_input(q: str) -> tuple[bool, str]:
    if not q or not q.strip():
        return False, "Pergunta vazia."
    if len(q) > MAX_LEN:
        return False, "Pergunta longa demais."
    if any(p in q.lower() for p in BLOCK):
        return False, "Pergunta rejeitada."
    return True, ""


def validate_output(answer: str, docs: list) -> tuple[bool, str]:
    """Grounding check: a resposta veio mesmo do contexto?"""
    if not docs and "não encontrei" not in answer.lower():
        return False, "Resposta sem contexto de apoio."
    return True, ""
