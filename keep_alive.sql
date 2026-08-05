-- ============================================================
-- Donadão Labs · keep-alive (Supabase free tier) — Fonte
-- ------------------------------------------------------------
-- PROBLEMA: o Supabase pausa projetos do plano free após 7 dias
-- SEM ATIVIDADE NO BANCO. "Atividade" = uma query que de fato
-- chega no Postgres. Visita ao dashboard ou resposta cacheada da
-- API NÃO contam. Foi exatamente o que derrubou este projeto em
-- 05/08/2026 (sintoma: FATAL "tenant/user not found" no pooler).
--
-- SOLUÇÃO: esta tabela-sentinela guarda UMA única linha (id = 1)
-- que um job externo (GitHub Actions) atualiza todo dia. Esse
-- UPSERT é atividade real e reseta o timer de inatividade.
-- A tabela não cresce: é sempre a mesma linha sendo sobrescrita.
--
-- VARIANTE ANON (obrigatória aqui): o repositório fonte-rag é
-- PÚBLICO, então o workflow usa a chave anon, nunca a service_role.
-- Por isso a tabela precisa das 3 policies abaixo (select, insert e
-- update): sem a de SELECT o upsert não enxerga a linha para
-- resolver o conflito e grava zero, com o job ficando verde.
--
-- Rode este SQL uma vez, no SQL Editor do projeto Supabase.
-- É idempotente: pode rodar de novo sem quebrar nada.
-- ============================================================

create table if not exists public.keep_alive (
  id         integer primary key,
  pinged_at  timestamptz not null default now()
);

grant select, insert, update on public.keep_alive to anon;
grant select, insert, update on public.keep_alive to authenticated;
grant all on public.keep_alive to service_role;

alter table public.keep_alive enable row level security;

drop policy if exists keep_alive_anon_select on public.keep_alive;
drop policy if exists keep_alive_anon_insert on public.keep_alive;
drop policy if exists keep_alive_anon_update on public.keep_alive;

create policy keep_alive_anon_select on public.keep_alive
  for select to anon using (true);
create policy keep_alive_anon_insert on public.keep_alive
  for insert to anon with check (true);
create policy keep_alive_anon_update on public.keep_alive
  for update to anon using (true) with check (true);

-- Garante que a linha exista já na criação
insert into public.keep_alive (id, pinged_at) values (1, now())
  on conflict (id) do update set pinged_at = excluded.pinged_at;
