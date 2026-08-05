# Keep-alive do Supabase

O banco do Fonte roda no plano free do Supabase, que **pausa o projeto após ~7 dias
sem atividade que chegue no Postgres**. Visita ao dashboard ou resposta cacheada da API
não contam. Este projeto é o caso extremo: como não tem deploy (a prova pública é o
`demo.mp4`), não existe tráfego orgânico nenhum para segurar o banco.

Foi o que aconteceu em **05/08/2026**: o banco caiu no meio de uma rodada de avaliação.

## Como diagnosticar

| Sintoma | Significado |
|---|---|
| `curl` no `https://<ref>.supabase.co` não resolve (exit 6, NXDOMAIN) | **Pausado.** Emergência real |
| `FATAL: (ENOTFOUND) tenant/user ... not found` no pooler | **Pausado.** Mesmo caso, visto pelo Postgres |
| REST responde 401 ou 200 e o keep-alive está verde | Vivo. E-mail "going to be paused" aqui é ruído |

## Como funciona

`.github/workflows/keep-alive.yml` faz um **UPSERT diário** (06:00 UTC) na tabela
`public.keep_alive`, que guarda uma linha só. Escrita real reseta o timer de inatividade,
e a tabela nunca cresce.

Três detalhes que existem por causa de falha real em outros projetos da frota:

- **UPSERT, não PATCH.** `PATCH ?id=eq.1` precisa enxergar a linha para filtrar; sem policy
  de SELECT ele casa zero linhas, devolve 204 e o job fica verde sem ter gravado nada.
- **Verificação do retorno.** O workflow faz `grep pinged_at` na resposta e falha se não
  achar. Job verde sem gravação é o pior modo de falha, porque ninguém é avisado.
- **Diário, não a cada 3 dias.** O intervalo de 3 dias se provou insuficiente na frota.

## Setup (uma vez)

1. **Restaurar o projeto** no dashboard do Supabase, se estiver pausado.
   A conta é a `fonte@donadaolabs.com`, não a org principal da Donadão Labs.
2. **Rodar `keep_alive.sql`** no SQL Editor do projeto.
3. **Secrets** em Settings → Secrets and variables → Actions:
   - `SUPABASE_URL` → `https://<ref>.supabase.co`
   - `SUPABASE_KEY` → **anon / publishable key** (Settings → API)
4. **Validar**: aba Actions → `keep-supabase-alive` → Run workflow, e conferir no log
   a linha `resposta: [{"id":1,"pinged_at":...}]`.

> ⚠️ **Chave anon, nunca `service_role`.** Este repositório é público. A anon só alcança
> a tabela `keep_alive`, que não guarda dado nenhum, e por isso o `keep_alive.sql` cria as
> três policies (select, insert, update) em vez de depender do bypass de RLS.

## Limite que o keep-alive não resolve

A organização free tem **teto de projetos ativos**. Se o teto estourar, o excedente pausa
por política e nenhum keep-alive segura. A saída nesse caso é distribuir os projetos entre
organizações ou migrar para o Pro.

O Fonte é produto próprio e vive numa conta dedicada, então o keep-alive aqui é solução
definitiva, não mitigação temporária.
