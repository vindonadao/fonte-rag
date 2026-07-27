"""Pacote app do Fonte.

Carrega o .env no import para que qualquer entrada (API, `python -m app.ingest`,
`eval.run`) enxergue as chaves em os.environ — OpenAI, Anthropic, DATABASE_URL e
Langfuse leem direto do ambiente.
"""
from dotenv import load_dotenv

load_dotenv()
