"""Fonte — API FastAPI. Junta as fases num fluxo único.

Rotas:
- GET  /health  → checkpoint da Fase 0 ({"status": "ok"}).
- POST /ask     → pergunta → guardrail entrada → retriever → RAG com citação →
                  guardrail saída (grounding) → resposta com fonte.
"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.chain import build_chain
from app.retriever import get_retriever
from app.guardrails import validate_input, validate_output
from app.observability import run_config

app = FastAPI(title="Fonte", description="RAG documental com citação de fonte")

_chain = None


def get_chain():
    """Constrói a chain uma vez (lazy) e reaproveita entre requisições."""
    global _chain
    if _chain is None:
        _chain = build_chain()
    return _chain


class AskRequest(BaseModel):
    question: str
    session_id: str | None = None


class AskResponse(BaseModel):
    answer: str
    ok: bool
    reason: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # Fase 4 — guardrail de entrada (rejeita injection óbvia)
    ok, reason = validate_input(req.question)
    if not ok:
        return AskResponse(answer="", ok=False, reason=reason)

    # Fase 2 — trechos que embasam a resposta (usados no grounding check)
    docs = get_retriever().invoke(req.question)

    # Fase 3 + 5 — geração com citação, instrumentada no Langfuse
    answer = get_chain().invoke(req.question, config=run_config(req.session_id))

    # Fase 4 — guardrail de saída (a resposta veio mesmo do contexto?)
    ok, reason = validate_output(answer, docs)
    if not ok:
        return AskResponse(answer="", ok=False, reason=reason)

    return AskResponse(answer=answer, ok=True)
