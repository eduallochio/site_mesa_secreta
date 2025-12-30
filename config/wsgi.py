"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Executar migrations automaticamente no primeiro deploy
try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    execute_from_command_line(['manage.py', 'create_default_superuser'])
except Exception as e:
    print(f"Migration error (pode ser ignorado se já executado): {e}")

application = get_wsgi_application()

# Vercel compatibility
app = application
