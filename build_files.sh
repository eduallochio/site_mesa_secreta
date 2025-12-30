#!/bin/bash

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos (não precisa de banco de dados)
python manage.py collectstatic --noinput --clear

# Migrar banco de dados (somente se DATABASE_URL estiver configurado)
if [ -n "$DATABASE_URL" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
else
    echo "Skipping migrations (no DATABASE_URL found)"
fi
