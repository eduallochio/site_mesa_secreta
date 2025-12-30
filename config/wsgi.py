"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Executar migrations ANTES de inicializar o Django
import django
django.setup()

from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError

try:
    # Verificar se o banco precisa de migrations
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        if not cursor.fetchone():
            print("Banco de dados vazio, executando migrations...")
            call_command('migrate', '--noinput', verbosity=0)
            call_command('create_default_superuser', verbosity=0)
        else:
            # Verificar se há migrations pendentes
            try:
                call_command('migrate', '--noinput', '--check', verbosity=0)
            except SystemExit:
                print("Migrations pendentes encontradas, executando...")
                call_command('migrate', '--noinput', verbosity=0)
except OperationalError as e:
    print(f"Executando migrations iniciais: {e}")
    try:
        call_command('migrate', '--noinput', verbosity=0)
        call_command('create_default_superuser', verbosity=0)
    except Exception as migrate_error:
        print(f"Erro ao executar migrations: {migrate_error}")
except Exception as e:
    print(f"Erro no setup do banco: {e}")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel compatibility
app = application
