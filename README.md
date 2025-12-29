# 🎲 Mesa Secreta - Guia Rápido

## ✅ Sistema Implementado

### Funcionalidades Principais

1. **🎨 Admin Melhorado** - Interface intuitiva com editor de texto rico
2. **Painel Administrativo** - Gerenciar postagens e vídeos
3. **Sistema de Postagens** - Artigos com categorias (Novidades, Dicas, Reviews)
4. **Galeria de Vídeos** - Integração com YouTube
5. **🆕 Sincronização Automática** - Busca vídeos do YouTube automaticamente
6. **Design Responsivo** - Tema Dark/Neon do Mesa Secreta

### 🆕 Melhorias no Admin

- ✅ **Editor de texto rico (CKEditor)** - Formatação visual completa
- ✅ **Preview de imagens** ao fazer upload
- ✅ **Ações em massa** - Publicar, despublicar, duplicar
- ✅ **Badges coloridos** por categoria
- ✅ **Preview de vídeos** do YouTube embutido
- ✅ **Interface temática** Mesa Secreta
- ✅ **Organização visual** com emojis e seções

Veja o guia completo em [docs/GUIA_ADMIN.md](docs/GUIA_ADMIN.md)

## 🚀 Como Começar

### 1. Acessar o Admin
```
URL: http://127.0.0.1:8000/admin
Usuário: admin
Senha: (a que você definiu)
```

### 2. Configurar ID do Canal YouTube

Edite [config/settings.py](config/settings.py) linha 134:
```python
YOUTUBE_CHANNEL_ID = 'UCseuIDaqui'  # Substituir pelo ID real
```

**Como encontrar o ID do canal:**
1. Acesse YouTube Studio
2. Configurações → Canal → Configurações avançadas
3. Copie o ID do canal (começa com UC...)

### 3. Sincronizar Vídeos do YouTube

Execute o comando:
```bash
python manage.py sync_youtube
```

Isso vai buscar automaticamente os últimos 15 vídeos do canal e adicionar ao site!

### 4. Criar Postagens

1. Acesse o admin: http://127.0.0.1:8000/admin
2. Clique em **Postagens** → **Adicionar Postagem**
3. Preencha:
   - Título
   - Subtítulo (resumo)
   - Conteúdo
   - Categoria
   - Status: Publicado
   - Imagem de capa (opcional)
4. Salvar

## 📁 Estrutura do Projeto

```
site_mesa_secreta/
├── config/              # Configurações Django
│   ├── settings.py      # YOUTUBE_CHANNEL_ID aqui
│   └── urls.py
├── core/                # App principal
│   ├── models.py        # Postagem e Video
│   ├── views.py         # Lógica das páginas
│   ├── admin.py         # Painel admin
│   ├── youtube_service.py  # 🆕 Integração YouTube
│   ├── templates/       # HTML
│   ├── static/          # CSS
│   └── management/
│       └── commands/
│           └── sync_youtube.py  # 🆕 Comando de sincronização
├── docs/                # Documentação
│   ├── INTEGRACAO_YOUTUBE.md  # 🆕 Guia YouTube
│   └── PROJETO_MESA_SECRETA.md
└── media/               # Uploads de imagens
```

## 🎨 URLs Disponíveis

- `/` - Página inicial
- `/postagens/` - Lista de postagens
- `/postagens/<id>/` - Detalhes da postagem
- `/videos/` - Galeria de vídeos
- `/admin/` - Painel administrativo

## 🔧 Comandos Úteis

```bash
# Iniciar servidor
python manage.py runserver

# Sincronizar vídeos do YouTube (🆕)
python manage.py sync_youtube

# Criar superusuário
python manage.py createsuperuser

# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Coletar arquivos estáticos (produção)
python manage.py collectstatic
```

## 🎬 Sincronização Automática de Vídeos

### Opções do Comando

```bash
# Padrão (15 vídeos)
python manage.py sync_youtube

# Buscar mais vídeos
python manage.py sync_youtube --max-results=30

# Canal diferente
python manage.py sync_youtube --channel-id=UCoutroID123
```

### Agendar Sincronização Automática

**Windows:**
1. Abra o Agendador de Tarefas
2. Criar Tarefa Básica
3. Gatilho: Diário às 8:00
4. Ação: `python.exe manage.py sync_youtube`

Veja mais detalhes em [docs/INTEGRACAO_YOUTUBE.md](docs/INTEGRACAO_YOUTUBE.md)

## 🎨 Personalização

### Cores do Tema

Edite [core/static/core/css/style.css](core/static/core/css/style.css) linhas 8-20:

```css
:root {
    --primary-color: #8b5cf6;  /* Roxo */
    --accent-color: #00ff88;   /* Neon Verde */
    --bg-color: #0a0a0a;       /* Fundo escuro */
}
```

### Links Sociais

Edite [core/templates/core/base.html](core/templates/core/base.html) linhas 31-42

## 📚 Documentação Completa

- [PROJETO_MESA_SECRETA.md](docs/PROJETO_MESA_SECRETA.md) - Visão geral do projeto
- [INTEGRACAO_YOUTUBE.md](docs/INTEGRACAO_YOUTUBE.md) - 🆕 Guia de integração YouTube
- [Portal_Mesa_Secreta.md](docs/Portal_Mesa_Secreta.md) - Briefing original

## 🆘 Problemas Comuns

### Vídeos não aparecem
1. Verifique se configurou o `YOUTUBE_CHANNEL_ID` correto
2. Execute `python manage.py sync_youtube`
3. Veja o terminal para mensagens de erro

### CSS não carrega
```bash
# Force reload do navegador: Ctrl + Shift + R
# Ou limpe o cache do navegador
```

### Erro ao fazer upload de imagens
- Certifique-se que o Pillow está instalado: `pip install Pillow`

## 🚀 Próximos Passos Sugeridos

1. ✅ Configurar ID do canal YouTube
2. ✅ Sincronizar primeiros vídeos
3. ✅ Criar algumas postagens de teste
4. ⏳ Agendar sincronização automática
5. ⏳ Personalizar cores/logo (opcional)
6. ⏳ Deploy para produção

## 💡 Dicas

- Execute `sync_youtube` **após publicar novos vídeos** no canal
- Use **Rascunho** para postagens que ainda não quer publicar
- Imagens de capa melhoram muito o visual das postagens
- A sincronização YouTube **não remove** vídeos, apenas adiciona novos
