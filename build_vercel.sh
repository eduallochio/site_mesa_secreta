#!/bin/bash
# Build script para Vercel

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Build concluído!"
