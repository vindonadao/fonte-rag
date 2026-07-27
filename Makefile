# Fonte — atalhos de desenvolvimento. Tudo roda dentro da .venv local.
PY := ./.venv/bin/python

.DEFAULT_GOAL := help
.PHONY: help install lock ingest dev eval health docker-build docker-run

help:  ## lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## cria a .venv e instala as dependências
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

lock:  ## congela o ambiente atual em requirements.lock.txt
	$(PY) -m pip freeze > requirements.lock.txt

ingest:  ## Fase 1 — ingere os PDFs de docs/ no pgvector
	$(PY) -m app.ingest

dev:  ## sobe a API (uvicorn com reload) em :8000
	$(PY) -m uvicorn app.main:app --reload

eval:  ## Fase 6 — roda o golden set e mede com RAGAS
	$(PY) -m eval.run

demo:  ## roda a demo narrável (para gravar o vídeo)
	$(PY) demo.py

health:  ## bate no /health (a API precisa estar de pé)
	curl -s http://127.0.0.1:8000/health

docker-build:  ## Fase 7 — constrói a imagem fonte-rag
	docker build -t fonte-rag .

docker-run:  ## Fase 7 — roda o container (injeta .env em runtime)
	docker run --env-file .env -p 8000:8000 fonte-rag
