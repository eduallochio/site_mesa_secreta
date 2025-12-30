# 🔥 CORREÇÃO DO ERRO 500 NO VERCEL

## ❌ Problema Atual
Server Error (500) no deploy do Vercel

## 🔍 Causa Provável
As variáveis de ambiente não estão configuradas no Vercel, fazendo o Django crashar ao tentar conectar no banco.

---

## ✅ SOLUÇÃO PASSO A PASSO

### 1️⃣ PRIMEIRO: Execute os Scripts no Supabase

Se ainda não fez isso, execute na ordem:

#### A) Dados Iniciais
1. Acesse: https://supabase.com/dashboard/project/szlilldcemfhimfikqig/sql/new
2. Copie todo conteúdo de: `banco/002_dados_iniciais.sql`
3. Cole no SQL Editor e clique em **RUN**

**Aguarde ver:**
```
✅ Usuário admin criado/atualizado!
✅ Configuração do site criada/atualizada!
✅ BANCO DE DADOS CONFIGURADO COM SUCESSO!
```

#### B) Segurança (RLS)
1. No SQL Editor, clique em **New Query**
2. Copie todo conteúdo de: `banco/003_seguranca_rls.sql`
3. Cole no SQL Editor e clique em **RUN**

**Aguarde ver:**
```
✅ RLS habilitado em todas as tabelas
🔒 SEGURANÇA MÁXIMA CONFIGURADA!
```

---

### 2️⃣ SEGUNDO: Configure as Variáveis no Vercel (CRÍTICO!)

Acesse: https://vercel.com/dashboard

1. Selecione o projeto: **site_mesa_secreta**
2. Vá em: **Settings** → **Environment Variables**
3. Adicione estas 3 variáveis:

#### Variável 1: DATABASE_URL
```
postgresql://postgres:C%23Sh%25s0%7CF%3A8mAQ%23X@db.szlilldcemfhimfikqig.supabase.co:5432/postgres
```
- Marque: ✅ Production, ✅ Preview, ✅ Development

#### Variável 2: DEBUG
```
False
```
- Marque: ✅ Production, ✅ Preview, ✅ Development

#### Variável 3: DJANGO_SECRET_KEY
```
django-insecure-vo3fh^w&!txlj=y+xf#d19xgu6+5n^k@_16la8l6uf)d6*atf#
```
- Marque: ✅ Production, ✅ Preview, ✅ Development

---

### 3️⃣ TERCEIRO: Redeploy no Vercel

Após adicionar as variáveis:

1. Vá em: **Deployments**
2. Clique nos 3 pontos (...) do último deployment
3. Selecione: **Redeploy**
4. Aguarde o build terminar (2-3 minutos)

---

## 🎯 Como Verificar se Funcionou

### ✅ Teste 1: Homepage
- URL: https://site-mesa-secreta.vercel.app/
- Deve carregar normalmente (não 500)

### ✅ Teste 2: Admin
- URL: https://site-mesa-secreta.vercel.app/admin/
- Deve mostrar tela de login
- Login: `admin` / `admin123`
- Deve entrar no painel

---

## 🔧 Se Continuar com Erro 500

### Ver Logs do Vercel

1. No projeto, vá em: **Deployments**
2. Clique no deployment mais recente
3. Clique em: **View Function Logs**
4. Procure por erros em vermelho

### Erros Comuns

**Erro: "DATABASE_URL não configurado"**
- Solução: Volte ao passo 2 e adicione DATABASE_URL

**Erro: "could not connect to server"**
- Solução: Verifique se DATABASE_URL está correto (com a senha!)

**Erro: "relation 'auth_user' does not exist"**
- Solução: Execute o script 002_dados_iniciais.sql no Supabase

**Erro: "no such table: django_session"**
- Solução: Execute o script 001_criar_tabelas.sql no Supabase

---

## 📋 Checklist Completo

- [ ] Script 001_criar_tabelas.sql executado no Supabase
- [ ] Script 002_dados_iniciais.sql executado no Supabase
- [ ] DATABASE_URL adicionado no Vercel
- [ ] DEBUG=False adicionado no Vercel  
- [ ] DJANGO_SECRET_KEY adicionado no Vercel
- [ ] Redeploy realizado no Vercel
- [ ] Homepage abre sem erro 500
- [ ] Admin /admin/ abre
- [ ] Login funciona (admin/admin123)

---

## 🚨 IMPORTANTE

**NÃO adicione USE_LOCAL_DB no Vercel!**
- Essa variável é APENAS para desenvolvimento local
- No Vercel, sem USE_LOCAL_DB, ele usa automaticamente o PostgreSQL

**Prioridade das variáveis:**
1. **DATABASE_URL** → OBRIGATÓRIO para Vercel funcionar
2. **DEBUG=False** → Necessário para modo produção
3. **DJANGO_SECRET_KEY** → Necessário para sessões

---

## 💡 Alternativa Rápida: Importar .env

Se preferir, você pode importar todas de uma vez:

1. No Vercel: **Settings** → **Environment Variables**
2. Clique em: **Import .env**
3. Selecione o arquivo: `.env_vercel`
4. Marque todos os ambientes
5. Clique em: **Import**

---

## 📞 Próximo Passo

Depois de configurar, me avise se o erro 500 foi resolvido ou se precisa ver os logs!
