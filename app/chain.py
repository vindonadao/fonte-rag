"""Fase 3 — Geração com citação. A identidade do produto: Fonte responde com fonte.

Três decisões deliberadas (defensáveis em entrevista):
- temperature=0        → para RAG factual, criatividade é bug, não feature.
- "Não encontrei"      → dar ao modelo uma saída honesta é a defesa nº 1 contra alucinação.
- citação arquivo+página → resposta sem fonte é resposta que ninguém audita (é o produto).
"""
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.retriever import get_retriever

SYSTEM = """Você é o Fonte, assistente que responde perguntas sobre um acervo de documentos.

Regras:
- Responda SOMENTE com base no contexto abaixo.
- Se o contexto não tiver a resposta, diga exatamente: "Não encontrei essa informação nos documentos."
- Nunca invente número, prazo ou valor.
- Cite a fonte (arquivo e página) ao final de cada afirmação.

Contexto:
{context}"""


def _cite(meta: dict) -> str:
    """Fonte legível: nome do arquivo + página 1-based (o PyPDF indexa em 0)."""
    src = os.path.basename(str(meta.get("source", "?")))
    page = meta.get("page")
    page_str = str(page + 1) if isinstance(page, int) else str(meta.get("page_label", "?"))
    return f"{src} p.{page_str}"


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[{_cite(d.metadata)}]\n{d.page_content}" for d in docs
    )


def build_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM),
        ("human", "{question}"),
    ])
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    return (
        {"context": get_retriever() | format_docs,
         "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
