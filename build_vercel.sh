#!/bin/bash
# Build script para Vercel

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Executar migrations (cria as tabelas automaticamente)
echo "🗄️  Executando migrations no banco de dados..."
python manage.py migrate --noinput

# Configurar banco de dados inicial (se necessário)
echo "⚙️  Configurando banco de dados..."
python manage.py setup_database

echo "✅ Build concluído!"
