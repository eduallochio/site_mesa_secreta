# 🚀 Configuração Final - Site Mesa Secreta

## ✅ Progresso Atual

- ✅ Código atualizado para PostgreSQL-only
- ✅ Scripts SQL criados
- ✅ Tabelas criadas no Supabase (confirmado por você)
- ⏳ Dados iniciais precisam ser inseridos
- ⏳ Vercel precisa ser configurado

---

## 📋 PRÓXIMOS PASSOS

### 1️⃣ Inserir Dados Iniciais no Supabase (AGORA)

1. Acesse: https://supabase.com/dashboard/project/szlilldcemfhimfikqig/sql/new
2. Abra o arquivo: `banco/002_dados_iniciais.sql`
3. Copie **TODO** o conteúdo
4. Cole no SQL Editor do Supabase
5. Clique em **RUN**

**Resultado esperado:**
```
✅ Usuário admin criado/atualizado!
   Username: admin
   Password: admin123
   ⚠️  ALTERE A SENHA IMEDIATAMENTE APÓS O PRIMEIRO LOGIN!

✅ Configuração do site criada/atualizada!
✅ Migrations registradas no banco!

📊 RESUMO DA CONFIGURAÇÃO:
   Usuários: 1
   Configurações: 1
   Migrations: 26

✅ BANCO DE DADOS CONFIGURADO COM SUCESSO!
```

---

### 2️⃣ Configurar Variáveis de Ambiente no Vercel

#### Opção A: Importar arquivo (Mais Rápido)

1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto: `site_mesa_secreta`
3. Vá em: **Settings** → **Environment Variables**
4. Clique em: **Import .env**
5. Selecione o arquivo: `.env_vercel`
6. Marque: **Production**, **Preview**, **Development**
7. Clique em: **Import**

#### Opção B: Adicionar manualmente

Adicione estas variáveis:

**DATABASE_URL**
```
postgresql://postgres:;EH;z9ZL>v}qk;,X@db.szlilldcemfhimfikqig.supabase.co:5432/postgres
```

**DEBUG**
```
False
```

**DJANGO_SECRET_KEY** (copie do arquivo .env_vercel)

**Importante:** Marque todas as opções (Production, Preview, Development)

---

### 3️⃣ Fazer Deploy no Vercel

Após configurar as variáveis:

1. Vercel fará redeploy automático
2. OU vá em: **Deployments** → **Redeploy**
3. Aguarde o build terminar (2-3 minutos)

---

### 4️⃣ Testar o Site

#### Acessar Admin
1. URL: https://site-mesa-secreta.vercel.app/admin/
2. Login: `admin`
3. Senha: `admin123`
4. ⚠️ **ALTERE A SENHA IMEDIATAMENTE!**

#### Configurar o Site
1. No admin, vá em: **Configurações do Site**
2. Configure:
   - Título e descrição do hero
   - Links das redes sociais
   - YouTube API Key (opcional)
   - Sobre texto
   - Email de contato

#### Testar Homepage
1. URL: https://site-mesa-secreta.vercel.app/
2. Verifique se carrega corretamente
3. Teste os links do footer

---

## 🔧 Problemas Conhecidos

### Problema: DNS não resolve localmente
**Causa:** Firewall ou rede local bloqueando Supabase  
**Solução:** Desenvolvimento apenas no Vercel por enquanto  
**Alternativa:** Tente de outra rede ou use VPN

### Problema: Migrations já aplicadas
**Solução:** O script 002_dados_iniciais.sql já registra todas as migrations

### Problema: Admin não consegue logar
**Verificar:**
1. Dados iniciais foram inseridos? (verifique no SQL Editor)
2. Variáveis de ambiente estão corretas no Vercel?
3. Deploy foi bem-sucedido?

---

## 📊 Verificação de Dados no Supabase

Execute estas queries no SQL Editor para verificar:

```sql
-- Ver usuários
SELECT id, username, email, is_superuser, is_staff 
FROM auth_user;

-- Ver configuração do site
SELECT id, hero_titulo, email_contato 
FROM core_configuracaosite;

-- Ver migrations
SELECT app, name 
FROM django_migrations 
ORDER BY app, name;

-- Contar tabelas
SELECT COUNT(*) as total_tabelas
FROM information_schema.tables
WHERE table_schema = 'public';
```

**Resultado esperado:**
- Usuários: 1 (admin)
- Configurações: 1
- Migrations: 26+
- Tabelas: 19+

---

## 🎯 Checklist Final

- [ ] Script 002_dados_iniciais.sql executado no Supabase
- [ ] Variáveis de ambiente configuradas no Vercel
- [ ] Deploy realizado no Vercel
- [ ] Admin acessível em /admin/
- [ ] Login funcionando (admin/admin123)
- [ ] Senha alterada para uma segura
- [ ] Homepage carregando corretamente
- [ ] Configurações do site editadas
- [ ] Links das redes sociais configurados

---

## 📝 Notas

- Local development está **bloqueado** por problema de DNS
- Toda configuração deve ser feita via **Supabase Dashboard**
- Testes devem ser feitos no **Vercel (produção)**
- Senha padrão **admin123** deve ser alterada IMEDIATAMENTE

---

## ❓ Precisa de Ajuda?

Se algo não funcionar:

1. Verifique os logs no Vercel: Settings → Functions → Logs
2. Execute as queries de verificação no Supabase
3. Confirme que as variáveis de ambiente estão corretas
4. Tente fazer redeploy no Vercel

**Status atual:** Pronto para configuração final! 🚀
