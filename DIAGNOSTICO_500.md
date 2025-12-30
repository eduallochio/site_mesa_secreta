# 🔍 Diagnóstico do Erro 500 - Passo a Passo

## 1️⃣ VERIFICAR LOGS DO VERCEL (CRÍTICO!)

### Como acessar os logs:

1. Acesse: https://vercel.com/dashboard
2. Clique no projeto: **site_mesa_secreta**
3. Vá em: **Deployments** (menu lateral)
4. Clique no deployment mais recente (o primeiro da lista)
5. Clique na aba: **Functions**
6. Role até encontrar erros em vermelho

### O que procurar nos logs:

❌ **"DATABASE_URL not found"** → Variável não foi configurada
❌ **"could not connect to server"** → Senha errada ou URL incorreta
❌ **"relation 'auth_user' does not exist"** → Tabelas não foram criadas
❌ **"no such table"** → Banco vazio, sem dados iniciais
❌ **"ALLOWED_HOSTS"** → Problema de configuração do Django
❌ **"ImportError"** → Falta alguma dependência no requirements.txt

---

## 2️⃣ CHECKLIST DE CONFIGURAÇÃO

### ✅ A) Variáveis de Ambiente no Vercel

Vá em: **Settings** → **Environment Variables**

Verifique se TODAS essas 3 variáveis existem e estão corretas:

**1. DATABASE_URL**
```
postgresql://postgres:C%23Sh%25s0%7CF%3A8mAQ%23X@db.szlilldcemfhimfikqig.supabase.co:5432/postgres
```
- ⚠️ **ATENÇÃO**: Senha DEVE estar URL-encoded (com %23, %25, %7C)
- Marcar: Production, Preview, Development

**2. DEBUG**
```
False
```
- Marcar: Production, Preview, Development

**3. DJANGO_SECRET_KEY**
```
django-insecure-vo3fh^w&!txlj=y+xf#d19xgu6+5n^k@_16la8l6uf)d6*atf#
```
- Marcar: Production, Preview, Development

### ✅ B) Dados no Supabase

Execute esta query no SQL Editor para verificar:

```sql
-- Verificar se usuário admin existe
SELECT COUNT(*) as usuarios FROM auth_user WHERE username = 'admin';

-- Verificar se configuração existe
SELECT COUNT(*) as configs FROM core_configuracaosite;

-- Verificar se migrations foram registradas
SELECT COUNT(*) as migrations FROM django_migrations;
```

**Resultado esperado:**
- usuarios: 1
- configs: 1
- migrations: 20+

Se algum for 0, você precisa executar:
- `banco/002_dados_iniciais.sql` no Supabase

### ✅ C) RLS (Row Level Security)

Execute no SQL Editor:

```sql
-- Verificar políticas RLS
SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public';
```

Se retornar 0, execute:
- `banco/003_seguranca_rls.sql` no Supabase

---

## 3️⃣ COMANDOS PARA TESTE RÁPIDO

### Testar conexão ao banco (no Supabase SQL Editor):

```sql
-- Teste 1: Ver se usuário postgres consegue acessar
SELECT current_user, current_database();

-- Teste 2: Listar todas as tabelas
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Teste 3: Contar registros essenciais
SELECT 
    (SELECT COUNT(*) FROM auth_user) as usuarios,
    (SELECT COUNT(*) FROM core_configuracaosite) as configs,
    (SELECT COUNT(*) FROM django_migrations) as migrations;
```

---

## 4️⃣ PROBLEMAS COMUNS E SOLUÇÕES

### ❌ Erro: "could not connect to server"

**Causa:** Senha incorreta ou URL malformada

**Solução:**
1. Verifique se a senha no Vercel está URL-encoded
2. Teste a conexão no Supabase primeiro
3. Copie exatamente do arquivo `.env_vercel`

### ❌ Erro: "relation does not exist"

**Causa:** Tabelas não foram criadas

**Solução:**
1. Execute `banco/001_criar_tabelas.sql` no Supabase
2. Execute `banco/002_dados_iniciais.sql` no Supabase
3. Faça redeploy no Vercel

### ❌ Erro: "no module named 'psycopg2'"

**Causa:** Dependência faltando

**Solução:**
1. Verifique se `psycopg2-binary==2.9.10` está no requirements.txt
2. Commit e push
3. Vercel fará redeploy automático

### ❌ Erro: "ALLOWED_HOSTS"

**Causa:** Django rejeitando domínio do Vercel

**Solução:**
1. Já está configurado como `ALLOWED_HOSTS = ['*']` no settings.py
2. Se mudar, precisa incluir: `.vercel.app` e domínio personalizado

### ❌ Erro: "DisallowedHost"

**Causa:** DEBUG=True em produção

**Solução:**
1. Certifique-se que `DEBUG=False` está no Vercel
2. Não adicione `USE_LOCAL_DB` no Vercel

---

## 5️⃣ PASSO A PASSO PARA RESOLVER

Execute na ordem:

### 1. Deletar e recriar variáveis (às vezes Vercel não atualiza)

No Vercel:
1. **Delete** a variável DATABASE_URL
2. **Adicione novamente** com a senha correta URL-encoded
3. Aguarde 10 segundos
4. Faça **Redeploy**

### 2. Limpar cache do Vercel

1. Vá em **Deployments**
2. Clique nos 3 pontos do último deploy
3. Selecione: **Redeploy**
4. Marque: **Use existing Build Cache** → **DESMARCADO**
5. Clique em **Redeploy**

### 3. Verificar build logs

Após o redeploy:
1. Clique no deployment
2. Vá em **Building**
3. Procure por erros durante a instalação de dependências
4. Vá em **Functions** → procure erros de runtime

---

## 6️⃣ TESTE LOCAL PARA VALIDAR

Como você tem SQLite local funcionando, teste se o código Django está OK:

```bash
# No terminal local
python manage.py check
python manage.py check --deploy
```

Se retornar erros, são problemas de código que também afetarão produção.

---

## 🆘 SE NADA FUNCIONAR

### Me envie:

1. **Screenshot dos logs do Vercel** (aba Functions)
2. **Screenshot das variáveis de ambiente** (Settings → Environment Variables)
3. **Resultado da query SQL**:
```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

Com essas informações consigo identificar o problema exato!

---

## 📝 IMPORTANTE

- ⚠️ **NÃO** adicione `USE_LOCAL_DB` no Vercel
- ⚠️ Senha DEVE estar URL-encoded no DATABASE_URL
- ⚠️ Todas as variáveis devem estar marcadas para Production
- ⚠️ RLS está ativo, mas Django (postgres) não é afetado

**Formato correto da senha:**
- Original: `C#Sh%s0|F:8mAQ#X`
- URL-encoded: `C%23Sh%25s0%7CF%3A8mAQ%23X`
- ✅ Use a versão URL-encoded no Vercel!
