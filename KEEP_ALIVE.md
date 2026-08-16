# Keep-alive do Supabase

O banco do Fonte roda no plano free do Supabase, que **pausa o projeto após ~7 dias
sem atividade que chegue no Postgres**. Visita ao dashboard ou resposta cacheada da API
não contam. Este projeto é o caso extremo: como não tem deploy (a prova pública é o
`demo.mp4`), não existe tráfego orgânico nenhum para segurar o banco.

Foi o que aconteceu em **05/08/2026**: o banco caiu no meio de uma rodada de avaliação.

## Estado atual

**Ativo e validado desde 16/08/2026.** Primeira execução verde do workflow, confirmada
por dois caminhos independentes: a linha `resposta: [{"id":1,"pinged_at":"2026-08-16T10:04:38+00:00"}]`
no log do Actions, e a mesma marca de tempo lida direto no Postgres via `DATABASE_URL`.

Entre 06/08 e 16/08 o workflow rodou 11 vezes e **falhou nas 11**, gerando e-mail de falha
todo dia. Não era defeito do keep-alive: era o setup abaixo pela metade. Duas causas
somadas, cada uma suficiente para derrubar sozinha:

| Passo pulado | Sintoma no log |
|---|---|
| Passo 1, projeto nunca restaurado após a queda de 05/08 | `curl: (6) Could not resolve host` |
| Passo 3, secret `SUPABASE_KEY` nunca cadastrado (só o `URL` estava lá) | `SUPABASE_KEY:` vazio no bloco `env` |

O passo 2 também não tinha sido feito: a tabela `public.keep_alive` não existia no banco
restaurado. Foi aplicada em 16/08 pelo `keep_alive.sql`.

A lição é que o e-mail de falha diário **era o sistema funcionando**, não ruído. Job
vermelho aqui significa banco em risco, e a contagem de 7 dias corre em silêncio por trás.

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
   a linha `resposta: [{"id":1,"pinged_at":...}]`. Para não depender só do que o próprio
   job diz de si mesmo, confira a marca de tempo direto no banco:

   ```bash
   .venv/bin/python -c "
   url=[l.split('=',1)[1].strip() for l in open('.env') if l.startswith('DATABASE_URL=')][0].strip('\"').replace('postgresql+psycopg://','postgresql://')
   import psycopg
   with psycopg.connect(url) as c, c.cursor() as cur:
       cur.execute('select id, pinged_at, now()-pinged_at as idade from public.keep_alive')
       print(cur.fetchall())
   "
   ```

   A `DATABASE_URL` do `.env` está no formato SQLAlchemy (`postgresql+psycopg://`); o
   `psycopg` puro recusa esse prefixo, daí o `replace`. Ela também carrega a senha do
   banco, então cuidado ao imprimir a URL ou deixá-la vazar em mensagem de erro.

> ⚠️ **Chave anon, nunca `service_role`.** Este repositório é público. A anon só alcança
> a tabela `keep_alive`, que não guarda dado nenhum, e por isso o `keep_alive.sql` cria as
> três policies (select, insert, update) em vez de depender do bypass de RLS.

## Limites que o keep-alive não resolve

### Teto de projetos ativos na org free

A organização free tem **teto de projetos ativos**. Se o teto estourar, o excedente pausa
por política e nenhum keep-alive segura. A saída nesse caso é distribuir os projetos entre
organizações ou migrar para o Pro.

O Fonte é produto próprio e vive numa conta dedicada, então nesse ponto o keep-alive aqui
é solução definitiva, não mitigação temporária.

### ⏳ O GitHub desliga o cron após 60 dias sem commit

> "In a public repository, scheduled workflows are automatically disabled when no
> repository activity has occurred in 60 days."
> ([docs do GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows))

Este é o modo de falha mais provável daqui em diante, e o mais traiçoeiro: o keep-alive
não fica vermelho, ele simplesmente **para de existir**. Sem job não há e-mail de falha,
e o banco pausa 7 dias depois sem ninguém ser avisado.

O Fonte é exatamente o perfil de risco: repositório **público** (a regra só vale para
públicos) e sem desenvolvimento contínuo, porque a prova pública é o `demo.mp4`. Contando
do último commit, o prazo vence perto de **04/10/2026**.

Duas saídas, e vale escolher uma antes da data:

- **Reativar na mão.** Aba Actions → o workflow aparece desabilitado → "Enable workflow".
  Depende de alguém lembrar, o que é justamente o que falhou antes.
- **Qualquer commit no repositório zera os 60 dias.** É o que acontece de graça enquanto
  o projeto estiver vivo, e é a razão de este documento existir: cada correção registrada
  aqui já serve de atividade.

Nada disso é hipótese sobre o Supabase; é política do GitHub, e independe do banco.
