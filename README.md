# Fonte — RAG documental com citação de fonte

Pergunte aos seus documentos e receba a resposta com **arquivo e página**.
Produto da Donadão Labs. Guardrails, tracing e avaliação medida.

> A pergunta entra → guardrail → busca vetorial (pgvector) → o modelo responde
> ancorado nos trechos → validação → resposta **com a fonte apontada**.

## Demo

![Demo do Fonte no terminal](demo.gif)

Pergunta respondida **com citação de arquivo e página** → **"Não encontrei"** para
pergunta fora do corpus → **prompt injection barrado** pelo guardrail → métricas e
observabilidade. Reproduza com `make demo`.

## Arquitetura

```
pergunta → guardrail (in) → retriever (pgvector) → LLM (temp 0) → guardrail (out) → resposta com fonte
                                                      ↑                    ↑
                                                 contexto isolado     grounding check
                                     (tudo instrumentado no Langfuse: latência, tokens, custo)
```

## Stack

Python · FastAPI · LangChain · pgvector (Supabase) · OpenAI (embeddings) · Anthropic (geração) · Langfuse · RAGAS · Docker

## Decisões técnicas

- **chunk_size 1000 / overlap 200** — grande demais dilui a busca, pequeno demais perde contexto; overlap não corta a frase no meio.
- **temperature 0** — para RAG factual, criatividade é bug, não feature.
- **"Não encontrei" explícito** — dar ao modelo uma saída honesta é a defesa nº 1 contra alucinação.
- **Citação obrigatória (arquivo + página)** — resposta sem fonte é resposta que ninguém audita. É o produto.
- **`collection` parametrizada** — pronto para multi-tenant (v1.0): uma collection por cliente.

## Resultados (métricas RAGAS, golden set de 15 perguntas)

Corpus de exemplo: 3 documentos **fictícios** (um contrato, uma proposta e um termo de
entrega — em `sample_docs/`, gerados por `scripts/gen_sample_corpus.py`). Sem dados reais
de cliente.

| Métrica | Score | O que mede |
|---|---|---|
| faithfulness | **0.983** | alucinação (resposta fiel ao contexto) |
| answer_relevancy | **0.967** | vai direto ao ponto? |
| context_precision | **0.957** | retrieval trouxe lixo? |
| context_recall | **0.940** | retrieval esqueceu algo? |

**Método:** as quatro métricas são as do RAGAS, computadas com um LLM-juiz
(`claude-sonnet-4-6`, temperature 0) em `eval/run.py`. A lib RAGAS 0.4.3 tem conflito de
import com o LangChain 1.x deste stack (importa um caminho de `langchain-community` já
removido), então em vez de rebaixar o stack, as métricas foram implementadas diretamente —
mesma definição, sem a dependência frágil.

**Leitura dos números:** as duas métricas de retrieval (`context_precision`/`recall`) são
as que primeiro cedem — coerente com o trade-off de `chunk_size` 1000 e `k=4`. Diagnóstico
útil: `faithfulness` alto com `context_recall` menor aponta para o **retrieval**, não para
a geração. Corpus pequeno e limpo puxa os números pra cima; num acervo maior espera-se mais
dispersão. Melhorias no roadmap: `k` maior e re-ranking.

## Observabilidade (Langfuse)

Cada pergunta vira um trace com latência, tokens e custo. Medido num lote de perguntas
sobre o corpus:

- **Custo por pergunta:** ~US$ 0,005 a 0,009 (embeddings + geração).
- **Latência por pergunta:** ~3,3 a 7,5 s.
- **Onde o tempo/custo mora:** na **geração** (LLM). O retrieval é uma única query vetorial
  no pgvector, de sub-segundo — quem pesa é o modelo. É esse o número que vira insumo de
  pricing no v1.0 (preço por pergunta).

## Limitações conhecidas

- Blocklist de guardrail é a camada fraca; burlável por paráfrase (a defesa real é contexto isolado + temp 0 + "Não encontrei").
- Sem re-ranking; `k` fixo em 4 — o `context_recall` é a métrica que primeiro cede.
- Golden set pequeno (15 perguntas) e corpus de exemplo enxuto (3 documentos).
- Avaliação por LLM-juiz (não pela lib RAGAS, por conflito de versão) — juiz e gerador são o mesmo modelo, o que pode inflar levemente as notas.
- Single-tenant nesta versão (multi-tenant no roadmap v1.0).

## Roadmap

- **v0.1 (atual):** single-tenant, corpus Donadão Labs.
- **v1.0:** multi-tenant, upload por cliente, isolamento por collection, painel Next.js, LGPD.

## Rodar local

Atalhos via `make` (rode `make help` para a lista). Tudo roda na `.venv`.

```bash
# 1. ambiente
make install                       # cria .venv + instala deps

# 2. chaves
cp .env.example .env               # e preencha OPENAI/ANTHROPIC/DATABASE_URL/LANGFUSE

# 3. Supabase (SQL Editor): create extension if not exists vector;

# 4. corpus → coloque os PDFs em docs/ e ingira
make ingest                        # Fase 1

# 5. suba a API
make dev                           # uvicorn com reload em :8000
#    GET  /health   → {"status":"ok"}
#    POST /ask      → {"question": "qual o prazo de pagamento?"}

# 6. avaliação
make eval                          # Fase 6 (RAGAS sobre o golden set)
```

### Docker

```bash
docker build -t fonte-rag .
docker run --env-file .env -p 8000:8000 fonte-rag
```

---

Built by Donadão Labs.
