# Changelog — Fonte · RAG documental com citação de fonte

Produto de IA da Donadão Labs. Versionamento por revisões (`rev-X.Y`).

## [rev-1.0] — 2026-07-27

### Release público — histórico consolidado
- **Repositório aberto ao público.** O histórico anterior (rev-0.1 a rev-0.11) foi
  reescrito num único commit inicial, porque commits antigos guardavam a mídia e o corpus
  de um cliente real usado no desenvolvimento. O working tree é 100% fictício; a narrativa
  de cada versão está preservada abaixo neste CHANGELOG.
- **v0.1 entregue:** RAG documental com citação de fonte, guardrails, observabilidade
  (Langfuse) e avaliação medida (métricas RAGAS via LLM-juiz). Ver README para arquitetura,
  scores e decisões técnicas.

## [rev-0.11] — 2026-07-27

### Faxina: projeto 100% com dados fictícios (pronto para repo público)
- **Corpus real removido de tudo:** apagados os PDFs do cliente de `docs/` (originais
  seguem no projeto de origem) e **zeradas as collections do Supabase** — re-ingerido
  apenas o corpus de exemplo em `donadao_docs` (0 chunks com dado real; confirmado por SQL).
- **Corpus de exemplo agora é o canônico:** `ingest` default aponta para `sample_docs/`;
  terceiro documento fictício adicionado (`TERMO-EXEMPLO-003.pdf`) — corpus de 3 docs,
  9 chunks.
- **`golden_set.json` reconstruído** com 15 perguntas sobre o corpus fictício.
- **Reavaliação (métricas RAGAS via LLM-juiz):** faithfulness **0.983**, answer_relevancy
  **0.967**, context_precision **0.957**, context_recall **0.940** — atualizados no README
  e no rodapé da demo.
- **`demo.gif`/`demo.mp4` regravados** sobre o corpus fictício, com os scores novos.
- **Menções ao cliente removidas** do CHANGELOG e do CLAUDE.md.
- ⚠️ Resta, se for tornar público: o **histórico git** ainda guarda a mídia/dados antigos
  (rev-0.4 a rev-0.10). Rewrite/squash do histórico antes de abrir (ver conversa).

## [rev-0.10] — 2026-07-27

### Demo pública com corpus de exemplo (sem dados de cliente)
- **Motivo:** o `demo.gif`/`demo.mp4` da rev-0.9 mostravam um contrato real (nome do
  cliente + valores + cláusula de confidencialidade). Trocado por corpus fictício.
- **`scripts/gen_sample_corpus.py`** (fpdf2) gera `sample_docs/`: um contrato e uma
  proposta de empresa fictícia (Aurora Comércio), valores redondos, mesma estrutura de
  cláusulas — a demo roda igual sem expor ninguém.
- Corpus de exemplo ingerido na collection separada **`demo_docs`** (o corpus real segue
  intocado em `donadao_docs`).
- **Collection parametrizada por env `COLLECTION`** em `retriever.py`/`ingest.py` (default
  `donadao_docs`) — é o mesmo gancho multi-tenant do v1.0, agora exercitado de verdade.
- `demo.tape` roda a demo sobre `demo_docs`; `demo.gif`/`demo.mp4` **regravados** com os
  dados fictícios e re-embutidos no README.
- ⚠️ Nota para tornar o repo público: `golden_set.json`, este CHANGELOG e o CLAUDE.md
  ainda citam o cliente real; e o histórico git da rev-0.9 guarda a mídia antiga. Fazer
  uma passada de sanitização antes de abrir.

## [rev-0.9] — 2026-07-26

### Fase 8 — Vídeo da demo gerado (fecha o DoD v0.1)
- **`demo.gif` + `demo.mp4`** renderizados com **vhs** (`demo.tape`) — o `make demo`
  rodando de verdade: resposta com citação, "Não encontrei", guardrail e o sumário de
  scores/Langfuse. GIF 271 KB, MP4 225 KB (1100×820, ~27 s).
- GIF **embutido no topo do README** (seção Demo) — quem abre o repo vê o produto tocando.
- `demo.py`: `warnings.filterwarnings("ignore")` para a tela sair limpa na gravação.
- **DoD v0.1 completo:** as 8 fases construídas, validadas e medidas.

## [rev-0.8] — 2026-07-26

### Fase 7 — Docker validado
- Motor via **colima** (já instalado; dispensa Docker Desktop). `docker build` → imagem
  `fonte-rag:latest` (1.33GB, base `python:3.11-slim`).
- Container rodou com `.env` injetado em runtime (`--env-file`, nunca na imagem): `/health`
  OK e `/ask` respondeu com citação **de dentro do container**, falando com Supabase +
  Anthropic + OpenAI pela rede. Parado e removido ao fim.
- Confirmado: `.dockerignore` + `COPY app/` mantêm `.env` e `docs/` fora da imagem.
- Melhoria futura: imagem carrega `ragas`/`datasets` (só usados na avaliação) — dá pra
  separar deps de runtime e enxugar o tamanho.

## [rev-0.7] — 2026-07-26

### Demo gravável
- `demo.py` + `make demo`: roda o fluxo (resposta com citação, "Não encontrei", guardrail)
  num output limpo, com sumário de scores e status do Langfuse.
- `roteiro-video.md`: narração de ~90 s + checklist para gravar o vídeo do portfólio.

## [rev-0.6] — 2026-07-26

### Fase 5 — Observabilidade ligada (Langfuse)
- Chaves `LANGFUSE_*` no `.env`; `auth_check()` OK. Handler já tolerante desde rev-0.4.
- Traces confirmados no dashboard (via API) com latência e custo por pergunta.
- **Números medidos:** custo/pergunta ~US$ 0,005–0,009; latência ~3,3–7,5 s. A **geração**
  (LLM) domina — o retrieval no pgvector é sub-segundo. Registrado no README (seção
  Observabilidade), conectando com o pricing por pergunta do v1.0.

## [rev-0.5] — 2026-07-26

### Fase 6 — Avaliação medida (RAGAS metrics)
- **`golden_set.json` reconstruído a partir do corpus real** — 13 perguntas com respostas
  que rastreiam ao conteúdo dos 3 PDFs (lidos, não inventados). As respostas genéricas
  antigas (faixas de tier etc.) não batiam com este corpus específico.
- **`eval/run.py` reescrito:** a lib RAGAS 0.4.3 não importa com o LangChain 1.x instalado
  (`langchain_community.chat_models.vertexai` foi removido). Em vez de rebaixar o stack,
  as 4 métricas do RAGAS são computadas com um **LLM-juiz** (`claude-sonnet-4-6`, temp 0),
  robusto a item malformado (guarda por pergunta) e ao formato de resposta em blocos.
- **Scores (golden set de 13):** faithfulness **0.969**, answer_relevancy **0.946**,
  context_precision **0.954**, context_recall **0.923** — anotados no README.
- **Diagnóstico:** única pergunta fraca foi "objeto do contrato" (context_recall ~0.30);
  cláusula longa vs `chunk 1000`/`k=4` → problema de **retrieval**, não de geração
  (faithfulness seguiu alto). Documentado em Limitações.
- README: limitação nova — juiz e gerador são o mesmo modelo (pode inflar levemente).

## [rev-0.4] — 2026-07-26

### RAG rodando de ponta a ponta (Fases 1–4) com corpus real
- **Supabase novo** (`fonte-rag`, conta dedicada, Postgres 17.6, região eu-north-1),
  extensão `vector` ativa, `DATABASE_URL` via Session pooler + `+psycopg`.
- **Fase 1 — ingestão:** corpus de 3 PDFs (contrato, proposta e termo de entrega;
  **fora do git**, `docs/` é ignorado). Texto extraível confirmado. **39 chunks** no
  pgvector. _(O corpus foi trocado por documentos de exemplo fictícios na rev-0.11.)_
- **Fase 2 — retrieval validado:** trechos corretos por pergunta, com arquivo e página.
- **Fase 3 — geração com citação:** `/ask` responde ancorado no corpus, citando arquivo
  e página; diz **"Não encontrei"** para pergunta fora do corpus (anti-alucinação).
  Modelo `claude-sonnet-4-6` confirmado como válido na conta.
- **Fase 4 — guardrails:** injection rejeitada pela API real. Testado via `uvicorn` +
  `curl` (`/health`, `/ask` real, `/ask` injection).

### Fixes de wiring
- `app/__init__.py`: `load_dotenv()` no import — ingest/chain/langfuse/psycopg enxergam
  as chaves (o roadmap não carregava o `.env`).
- `app/observability.py`: tolerante a Langfuse ausente — sem chaves, `run_config` retorna
  `{}` e o RAG roda igual (Fase 5 liga sozinha quando as chaves entrarem).
- `app/chain.py`: citação agora usa **nome do arquivo** (não o caminho todo) e **página
  1-based** (o PyPDF indexa em 0).

### Pendente
- **Fase 5 (Langfuse):** faltam as chaves `LANGFUSE_*` no `.env`.
- **Fase 6 (RAGAS):** rebuild do `golden_set.json` a partir do corpus real (as respostas
  pré-preenchidas eram de padrões genéricos; a proposta ingerida é de Google Ads) +
  rodar as 4 métricas e anotar no README.
- Trocar `PyPDFDirectoryLoader` (langchain-community em sunset) por integração standalone.

## [rev-0.3] — 2026-07-15

### Utilitários (sem depender de chave/corpus)
- **`Makefile`** com atalhos: `install`, `lock`, `ingest`, `dev`, `eval`, `health`,
  `docker-build`, `docker-run` (`make help` lista tudo). Tudo roda na `.venv` local.
- **`golden_set.json` expandido** para **12 perguntas** (era 2). **6 com `ground_truth`
  preenchido** — só as que rastreiam a padrões documentados (modelo 30/60/10 + taxa de
  adjudicação não reembolsável, faixas dos tiers Sistema/Produto e Presença Digital, SEO
  como obrigação de meio, foro pelo Código Civil). Cada uma leva `nota` pedindo confirmação
  no PDF real. **6 marcadas TODO** (`ground_truth` vazio) — PI, garantia, SLA,
  confidencialidade, rescisão, prazo de entrega — para preencher com o documento real
  (regra de zero invenção: não chuto resposta de documento que não vi).
- **`eval/run.py`**: pula com aviso as perguntas sem `ground_truth` e reporta quantas
  ficaram de fora (nada de golden set parcial se passando por completo).

### `.env`
- Criado `.env` local (cópia do `.env.example`, vazio) — **fora do git**, pronto para colar
  as chaves.

## [rev-0.2] — 2026-07-15

### Fase 0 concluída (ambiente rodando)
- **`.venv` criada** (Python 3.14.6 — única disponível; wheels `cp314` existem para
  todas as 116 deps) e **`pip install -r requirements.txt`** com sucesso.
- **`requirements.lock.txt`** commitado (`pip freeze`, 116 pacotes pinados) — trava o
  ambiente que funciona: `langchain==1.3.13`, `langfuse==4.14.0`, `ragas==0.4.3`,
  `fastapi==0.139.0`, `anthropic==0.116.0`.
- **Checkpoint validado:** `uvicorn app.main:app` sobe sem erro; `GET /health` →
  `{"status":"ok"}`; `POST /ask` com injection é rejeitado pelo guardrail sem chamar o LLM.

### Fix — Langfuse v4 (o "as APIs mudam rápido" do roadmap, na prática)
- Instalou **Langfuse 4.x**, que quebra o import do roadmap (`langfuse.callback`).
  Corrigido em `app/observability.py`: handler agora vem de `langfuse.langchain` e o
  `session_id` vai como metadata reservada (`langfuse_session_id`) no config do LangChain,
  não mais no construtor. `app/main.py` passou a usar `run_config(session_id)`.
- Demais módulos (`ingest`/`retriever`/`chain`) importam sem ajuste no **LangChain 1.x**.

### Pendente (precisa de chaves / corpus — ver CLAUDE.md)
- Preencher `.env` (OpenAI, Anthropic, DATABASE_URL do Supabase, Langfuse).
- `create extension if not exists vector;` no Supabase, ingerir corpus e rodar `/ask` real.

## [rev-0.1] — 2026-07-15

### Fundação (scaffold)
- **Projeto criado** a partir do `Fonte_Roadmap.md`. Estrutura `fonte-rag/` com
  `app/` (módulos por fase), `eval/` (avaliação) e `docs/` (corpus, versionado vazio).
- **Stack fixada:** Python 3.11+ · FastAPI · LangChain · pgvector (Supabase) ·
  OpenAI (embeddings) · Anthropic (geração) · Langfuse · RAGAS · Docker.
- **`requirements.txt`**, **`Dockerfile`** (`python:3.11-slim`, `--no-cache-dir`,
  `.env` fora da imagem), **`.dockerignore`**.
- **`.env.example`** com o modelo de chaves; **`.env` no `.gitignore` antes do 1º commit**
  (regra de ouro — chave vazada é o erro nº 1 / futuro incidente LGPD no v1.0).
- **`README.md`** completo: arquitetura, decisões técnicas, tabela de resultados RAGAS
  (a preencher), limitações conhecidas e roadmap v0.1 → v1.0.
- **`CLAUDE.md`** canônico: mapa do código por fase, decisão multi-tenant e DoD.

### Esqueleto das fases (esqueleto correto, ainda não executado)
- **Fase 0** — `app/config.py`: settings via `pydantic-settings`, parâmetros do RAG
  centralizados. `app/main.py`: FastAPI com `/health` e `POST /ask` unindo o fluxo.
- **Fase 1** — `app/ingest.py`: PDFs → chunk (1000/200) → embeddings → pgvector.
- **Fase 2** — `app/retriever.py`: busca por similaridade (`k=4`).
- **Fase 3** — `app/chain.py`: RAG chain com citação, `temperature=0` e saída
  "Não encontrei" (a identidade: Fonte responde com fonte).
- **Fase 4** — `app/guardrails.py`: `validate_input` (injection) + `validate_output`
  (grounding check).
- **Fase 5** — `app/observability.py`: handler do Langfuse (tracing, custo, latência).
- **Fase 6** — `eval/golden_set.json` (seed com 2 perguntas, expandir p/ 10–15) e
  `eval/run.py` (monta dataset + mede RAGAS: faithfulness, answer_relevancy,
  context_precision, context_recall).

### Decisão de arquitetura (custa zero agora)
- `collection_name` e caminho do corpus são **parâmetros**, não constantes — no v1.0
  cada cliente vira uma collection própria (mesmo padrão multi-tenant do Donadão OPS).

### Pendente (roadmap — ver CLAUDE.md e Fonte_Roadmap.md)
- Fase 0: `python -m venv .venv` + `pip install -r requirements.txt` + preencher `.env`.
- Habilitar `create extension if not exists vector;` no Supabase.
- Ingerir corpus (10–20 PDFs da Donadão Labs), validar retrieval, rodar `/ask`.
- Rodar RAGAS e **anotar os 4 scores no README**.
- `docker build`/`run`; deploy (Render/Railway/Fly) mirando `fonte.donadaolabs.com`
  ou vídeo de demo se o tempo apertar.

### Aviso de versão
- APIs de LangChain/Langfuse/RAGAS mudam rápido (conhecimento base até jan/2026).
  Os módulos são o esqueleto do raciocínio — conferir a doc oficial de cada lib ao instalar.
