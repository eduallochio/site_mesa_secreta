#!/bin/bash

# Executar migrations
python manage.py migrate --noinput

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário automaticamente se não existir
python manage.py create_default_superuser
