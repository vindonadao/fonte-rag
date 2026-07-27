"""Fase 5 — Observabilidade. Langfuse v4: tracing, custo e latência.

Cada pergunta vira um trace com latência, tokens, custo e o prompt exato.
Olhar no dashboard: p95 (a média mente), custo/pergunta (insumo do pricing v1.0),
e qual etapa domina o tempo — retrieval ou geração.

⚠️ Ajustado para langfuse 4.x: o handler mudou de `langfuse.callback` para
`langfuse.langchain`, e o `session_id` deixou de ir no construtor — agora vai
como metadata reservada (`langfuse_session_id`) no config do LangChain.
Confira o quickstart oficial se a versão mudar de novo.
"""
import os

from langfuse.langchain import CallbackHandler


def langfuse_enabled() -> bool:
    """Só instrumenta se as chaves do Langfuse estiverem no ambiente."""
    return bool(os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"))


def get_handler() -> CallbackHandler:
    """Callback do Langfuse. As chaves vêm do ambiente (LANGFUSE_*)."""
    return CallbackHandler()


def run_config(session_id: str | None = None) -> dict:
    """Config do LangChain: anexa o handler do Langfuse só se houver chaves.

    Sem Langfuse configurado, retorna config vazio — o RAG funciona igual, só não
    gera trace. Basta preencher LANGFUSE_* no .env para a Fase 5 ligar sozinha.
    """
    if not langfuse_enabled():
        return {}
    config: dict = {"callbacks": [get_handler()]}
    if session_id:
        config["metadata"] = {"langfuse_session_id": session_id}
    return config
