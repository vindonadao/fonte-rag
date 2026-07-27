"""Configuração central do Fonte — settings carregadas do ambiente / .env.

Os parâmetros do RAG (collection, k, chunk_size...) vivem aqui como PARÂMETROS,
não constantes espalhadas. No v1.0 multi-tenant, `default_collection` vira uma
collection por cliente — mesma mudança de uma linha (ver CLAUDE.md).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Chaves / conexão
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    database_url: str = ""

    # Observabilidade (Langfuse)
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Parâmetros do RAG (defensáveis em entrevista — ver README "Decisões técnicas")
    default_collection: str = "donadao_docs"      # v1.0: uma por cliente
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "claude-sonnet-4-6"          # confira o id atual na doc Anthropic
    retriever_k: int = 4
    chunk_size: int = 1000
    chunk_overlap: int = 200


settings = Settings()
