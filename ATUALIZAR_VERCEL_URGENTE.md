# ⚠️ ATUALIZAÇÃO URGENTE NO VERCEL

## Problema
O site está com erro **MaxClientsInSessionMode** porque está usando porta 5432 (Session Mode) do Supabase.

Para Vercel serverless, precisamos usar **porta 6543 (Transaction Mode)**.

## Solução - Atualizar Environment Variable no Vercel

### Passo 1: Acessar Vercel
1. Acesse: https://vercel.com/dashboard
2. Selecione: **site_mesa_secreta**
3. Clique em: **Settings**
4. Vá em: **Environment Variables**

### Passo 2: Atualizar DATABASE_URL
1. Encontre a variável: `DATABASE_URL`
2. Clique em **Edit** (ícone de lápis)
3. **Substitua o valor** por:
```
postgresql://postgres.szlilldcemfhimfikqig:C%23Sh%25s0%7CF%3A8mAQ%23X@aws-1-sa-east-1.pooler.supabase.com:6543/postgres
```
4. Certifique-se que está marcado para: **Production, Preview e Development**
5. Clique em **Save**

### Passo 3: Forçar Redeploy
1. Vá em: **Deployments**
2. Clique nos 3 pontinhos do último deploy
3. Clique em: **Redeploy**

### O que mudou?
- **Antes:** `:5432` (Session Mode - limite baixo de conexões)
- **Depois:** `:6543` (Transaction Mode - limite alto, ideal para serverless)

## Problema adicional: django_admin_log

Também falta a tabela `django_admin_log`. Após atualizar a porta, execute:

```bash
# Localmente com USE_LOCAL_DB=False
python manage.py migrate
```

Ou execute no Supabase SQL Editor:
```sql
-- Será criada automaticamente pelo Django Admin quando rodar migrations
```
