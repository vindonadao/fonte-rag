"""Fase 2 — Retrieval. Busca por similaridade no pgvector.

Se o retrieval está ruim, o RAG inteiro está ruim — nenhum prompt salva
contexto errado. Teste os chunks retornados antes de seguir para a Fase 3.
"""
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
import os


def get_retriever(k: int = 4, collection: str | None = None):
    collection = collection or os.environ.get("COLLECTION", "donadao_docs")
    store = PGVector(
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        collection_name=collection,
        connection=os.environ["DATABASE_URL"],
        use_jsonb=True,
    )
    return store.as_retriever(search_kwargs={"k": k})
