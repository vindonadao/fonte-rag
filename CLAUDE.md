# CLAUDE.md — Fonte (`fonte-rag`)

Contexto canônico do projeto para o Claude Code. Leia antes de mexer.

## O que é

**Fonte** — RAG documental que responde perguntas sobre um acervo de documentos
**citando arquivo e página**, com guardrails, observabilidade e avaliação medida.
Segundo projeto de IA do portfólio (o primeiro é o Agente Diagnóstico, em produção).

Produto da Donadão Labs · slug `fonte-rag` · alvo `fonte.donadaolabs.com`.

**Duas vidas, um código:**
1. **v0.1 — Portfólio (atual).** Corpus = documentos da própria Donadão Labs
   (propostas, contratos, escopos). Fecha as palavras-chave do CV com lastro real:
   Python, RAG, Vector DB, LangChain, embeddings, observabilidade, guardrails, Docker.
2. **v1.0 — Produto de venda (DEPOIS da entrevista).** Mesmo motor, multi-tenant,
   *"pergunte aos seus contratos"* para contabilidades, administradoras de condomínio,
   imobiliárias e advogados. **Não construir nada do v1.0 agora.**

## Stack

Python 3.11+ · FastAPI + uvicorn · LangChain · pgvector (Supabase, Postgres que já existe) ·
OpenAI `text-embedding-3-small` (embeddings) · Anthropic (geração) · Langfuse (tracing) ·
RAGAS (avaliação) · Docker.

## Mapa do código

| Arquivo | Fase | Papel |
|---|---|---|
| `app/config.py` | 0 | Settings/env (pydantic-settings). Parâmetros do RAG centralizados. |
| `app/ingest.py` | 1 | Carregar PDFs → chunk → embed → gravar no pgvector. `python -m app.ingest` |
| `app/retriever.py` | 2 | Busca por similaridade (`k=4`). Se o retrieval é ruim, o RAG é ruim. |
| `app/chain.py` | 3 | RAG chain com citação. temperature 0 + "Não encontrei". É a identidade. |
| `app/guardrails.py` | 4 | `validate_input` (injection) + `validate_output` (grounding). |
| `app/observability.py` | 5 | Handler do Langfuse. |
| `app/main.py` | 0/3/4 | FastAPI: `/health` e `POST /ask` — junta as fases num fluxo. |
| `eval/golden_set.json` | 6 | Perguntas + respostas esperadas (15, todas com resposta no acervo). |
| `eval/abstention_set.json` | 6 | 6 perguntas SEM resposta no acervo. Mede a recusa, não o acerto. |
| `eval/run.py` | 6 | Roda golden set (4 métricas via LLM-juiz) + taxa de abstenção. |

## Decisão de arquitetura que importa

`collection_name` e o caminho do corpus são **parâmetros**, não constantes espalhadas.
No v1.0, cada cliente vira uma collection própria — mesma mudança de uma linha (mesmo
raciocínio multi-tenant do Donadão OPS). Custa zero agora, economiza refactor depois.

## Regras do projeto

- **`.env` NUNCA commitado** (já no `.gitignore`). Chave vazada em repo é o erro nº 1 —
  e ironicamente é AI Security, o que a vaga cobra. No v1.0 vira incidente LGPD.
- **`docs/` versionado vazio** (`docs/*` ignorado, só `docs/.gitkeep` entra). PDFs de
  corpus/cliente ficam fora do git.
- **Só adiciona skill no LinkedIn depois da fase funcionando.** Skill sem lastro explode
  na primeira pergunta técnica.
- **Não perseguir score perfeito:** 0.85 com limitação documentada > 0.99 inexplicável.

## Definition of Done (v0.1)

- [ ] `/ask` responde citando arquivo e página
- [ ] Diz "Não encontrei" quando não sabe (pergunta fora do corpus)
- [ ] Guardrail rejeita injection óbvia
- [ ] Traces no Langfuse com latência e custo
- [ ] 4 métricas RAGAS rodadas e **anotadas no README**
- [ ] `docker build` + `docker run` funcionando
- [ ] Repositório `fonte-rag`, **sem `.env`**, README completo
- [ ] Demo no ar ou vídeo gravado

## Estado atual

**rev-0.5 — Fases 1–4 e 6 concluídas.** Supabase dedicado (`fonte-rag`, conta própria,
PG 17.6, eu-north-1), `vector` ativa, `DATABASE_URL` Session pooler + `+psycopg`. Corpus
= 3 PDFs de exemplo (contrato, proposta, termo) em `sample_docs/`.
`/ask` responde com citação (arquivo + página 1-based), diz "Não encontrei" fora do
corpus, guardrail rejeita injection — validado via API. Modelo `claude-sonnet-4-6`.

**Avaliação (Fase 6):** golden set de 13 perguntas reais + LLM-juiz em `eval/run.py`
(RAGAS 0.4.3 não importa com LangChain 1.x). Scores: faithfulness 0.969, answer_relevancy
0.946, context_precision 0.954, context_recall 0.923 — no README. Achado: "objeto do
contrato" com context_recall baixo = gap de retrieval (chunk longo, k=4).

**Fixes:** `load_dotenv()` em `app/__init__.py`; observability tolerante a Langfuse
ausente; citação com nome do arquivo + página 1-based.

**Fase 5 OK (rev-0.6):** Langfuse ligado, `auth_check()` OK, traces com latência+custo.
Medido: custo/pergunta ~US$ 0,005–0,009; latência ~3,3–7,5 s (geração domina).

**Fase 7 OK (rev-0.8):** Docker via **colima** (não precisa Docker Desktop). Imagem
`fonte-rag:latest` (1.33GB); container respondeu `/ask` com `.env` injetado em runtime.
Demo gravável em `make demo` + `roteiro-video.md` (rev-0.7).

**Falta (só ações do Vinicius):** Fase 8 — gravar o vídeo (`make demo`) e/ou deploy
(Render/Railway/Fly → `fonte.donadaolabs.com`, DEPOIS de rotacionar as chaves do chat).
Melhorias: trocar `PyPDFDirectoryLoader` (sunset); k maior/re-ranking; enxugar imagem
(tirar ragas/datasets do runtime).

Ligar o Docker: `colima start` (motor já instalado).

Ativar o ambiente: `source .venv/bin/activate` (ou usar `./.venv/bin/python`).

**rev-1.1 (05/08/2026) — precisão do README + medição de abstenção.** Conjunto de
abstenção criado (6 perguntas fora do corpus) e integrado ao `make eval`; README corrigido
(chunk é caractere e não token; escala de 9 chunks com k=4 declarada; limitações ampliadas).
**Pendência RESOLVIDA em 16/08/2026** (ver rev-1.4): abstenção medida em **6/6 = 1.000** e
publicada no README com a escala declarada.

**rev-1.3 (16/08/2026) — keep-alive ligado e validado.** O banco voltou e a tabela-sentinela
`public.keep_alive` foi criada. O workflow `keep-supabase-alive` teve a **primeira execução
verde**, confirmada no log do Actions e conferida direto no Postgres. As 11 falhas seguidas
de 06/08 a 16/08 eram setup pela metade (projeto pausado + secret `SUPABASE_KEY` ausente),
não defeito de código. **Risco em aberto:** o GitHub desabilita workflows agendados após 60
dias sem commit em repositório público, e este é público. Prazo perto de **04/10/2026**;
qualquer commit zera. Detalhes e comandos de diagnóstico em `KEEP_ALIVE.md`.

**rev-1.4 (16/08/2026) — abstenção medida.** `make eval` rodado com o banco de volta (corpus
intacto: 9 chunks em `donadao_docs`). **Abstenção 6/6 = 1.000.** Golden set de 15 perguntas:
0.977 / 0.977 / 0.967 / 0.943. **Achado importante para entrevista:** os scores variam entre
rodadas (a anterior deu 0.983 / 0.967 / 0.957 / 0.940 com o mesmo código e o mesmo corpus),
porque o juiz é um LLM mesmo com temperature 0. O README passou a pedir leitura em **faixa
(0.94 a 0.98)**, não no terceiro decimal. A perda é estável e concentrada nas mesmas duas
perguntas (objeto do contrato e prazo de go-live), o que confirma gap de retrieval e não
ruído.

⚠️ A `DATABASE_URL` do `.env` está em formato SQLAlchemy (`postgresql+psycopg://`) e leva a
senha do banco embutida. O `psycopg` puro recusa esse prefixo, então troque por
`postgresql://` antes de conectar, e evite imprimir a URL: ela vaza a senha em mensagem de
erro.

## Fatos técnicos verificados (para defender em entrevista)

Medidos no banco e no código em 05/08/2026, não estimados:

- **Embedding:** `text-embedding-3-small`, **1536 dimensões** (confirmado via `vector_dims`).
- **Corpus indexado:** **9 chunks** na collection `donadao_docs`. Chunk médio 731 caracteres,
  maior 988, menor 74. Com `k=4`, cada pergunta recebe ~44% do acervo.
- **Similaridade:** cosseno (`DistanceStrategy.COSINE` é o default do `langchain-postgres`).
- **Índices existentes:** btree nas PKs e GIN em `cmetadata`. **Nenhum índice vetorial**, e
  não é possível criar: a coluna é `vector` sem dimensão e o pgvector responde
  `column does not have dimensions` (reproduzido). Exige `ALTER TABLE ... TYPE vector(1536)`.
- **Metadados por chunk (JSONB):** `source`, `page` (0-based, convertido para 1-based em
  `chain.py`), `page_label`, `total_pages`, `creator`, `producer`, `creationdate`.
- **Guardrail de saída é inócuo:** `validate_output` só reprova com `docs` vazio, e com `k`
  fixo isso nunca ocorre.
- **Geração é Anthropic; OpenAI só embeda** (a Anthropic não tem modelo de embedding).

## ⚠️ Aviso de versão

As APIs de LangChain, Langfuse e RAGAS mudam rápido; o conhecimento base vai até
jan/2026. Os módulos são o **esqueleto correto do raciocínio** — confira a doc oficial
de cada lib ao instalar. Se um import não bater, é versão, não é o código.
