"""Fase 1 — Ingestão. Carregar → chunk → embed → gravar no pgvector.

O coração do RAG. Roda uma vez por corpus:  python -m app.ingest
"""
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
import os

DEFAULT_COLLECTION = "donadao_docs"   # v1.0: uma collection por cliente


def ingest(path: str = "sample_docs/", collection: str | None = None):
    collection = collection or os.environ.get("COLLECTION", DEFAULT_COLLECTION)
    # 1. carregar
    docs = PyPDFDirectoryLoader(path).load()

    # 2. quebrar em chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,      # overlap evita cortar a frase no meio
    )
    chunks = splitter.split_documents(docs)

    # 3. embeddings + 4. gravar
    store = PGVector(
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        collection_name=collection,
        connection=os.environ["DATABASE_URL"],
        use_jsonb=True,
    )
    store.add_documents(chunks)
    print(f"{len(chunks)} chunks gravados em '{collection}'.")


if __name__ == "__main__":
    ingest()
