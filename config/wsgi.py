"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializar Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Executar migrations de forma thread-safe
import threading
migration_lock = threading.Lock()
migrations_executed = False

def run_migrations():
    global migrations_executed
    if migrations_executed:
        return
    
    with migration_lock:
        if migrations_executed:
            return
            
        print("🔧 Verificando estado do banco de dados...")
        
        from django.core.management import call_command
        from django.db import connection
        from django.db.utils import OperationalError
        
        try:
            # Forçar conexão e verificar tabelas
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_configuracaosite'")
                if not cursor.fetchone():
                    print("⚠️  Tabela core_configuracaosite não encontrada, executando migrations...")
                    call_command('migrate', '--noinput', verbosity=2)
                    call_command('create_default_superuser', verbosity=1)
                    print("✅ Migrations executadas com sucesso!")
                else:
                    print("✅ Banco de dados já configurado")
        except OperationalError as e:
            print(f"⚠️  Erro no banco, executando migrations: {e}")
            try:
                call_command('migrate', '--noinput', verbosity=2)
                call_command('create_default_superuser', verbosity=1)
                print("✅ Migrations executadas após erro!")
            except Exception as migrate_error:
                print(f"❌ Erro ao executar migrations: {migrate_error}")
                raise
        except Exception as e:
            print(f"❌ Erro no setup: {e}")
            raise
        
        migrations_executed = True

# Executar migrations na importação
run_migrations()

# Vercel compatibility
app = application
