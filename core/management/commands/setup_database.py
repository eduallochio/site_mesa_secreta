"""
Comando para configurar o banco de dados em produção.
Executa migrations e cria superusuário padrão.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection
from core.models import ConfiguracaoSite

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura o banco de dados: executa migrations e cria dados iniciais'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Iniciando configuração do banco de dados...')
        
        # 1. Executar migrations
        self.stdout.write('📦 Executando migrations...')
        try:
            call_command('migrate', '--noinput', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Migrations executadas com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao executar migrations: {e}'))
            return
        
        # 2. Criar superusuário padrão se não existir
        self.stdout.write('👤 Verificando superusuário...')
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@mesasecreta.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS('✅ Superusuário criado!'))
                self.stdout.write(self.style.WARNING('⚠️  Username: admin | Password: admin123'))
                self.stdout.write(self.style.WARNING('⚠️  ALTERE A SENHA IMEDIATAMENTE!'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Superusuário já existe'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar superusuário: {e}'))
        
        # 3. Criar configuração padrão do site
        self.stdout.write('⚙️  Verificando configuração do site...')
        try:
            config, created = ConfiguracaoSite.objects.get_or_create(
                pk=1,
                defaults={
                    'hero_titulo': 'Bem-vindo ao Mesa Secreta',
                    'hero_descricao': 'Análises completas de jogos de tabuleiro',
                    'sobre_texto': 'Somos apaixonados por jogos de tabuleiro!',
                    'jogos_analisados': 150,
                    'videos_por_mes': 12,
                    'inscritos_canal': 10000,
                    'youtube_url': 'https://youtube.com/@mesasecreta',
                    'desenvolvedor_nome': 'Omega Sistem',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✅ Configuração inicial criada!'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Configuração já existe'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Aviso ao criar configuração: {e}'))
        
        # 4. Mostrar informações do banco
        self.stdout.write('\n📊 Informações do banco de dados:')
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            self.stdout.write(f'   PostgreSQL: {version}')
        
        self.stdout.write('\n' + self.style.SUCCESS('✅ Configuração concluída com sucesso!'))
        self.stdout.write('\n📝 Próximos passos:')
        self.stdout.write('   1. Acesse /admin/')
        self.stdout.write('   2. Faça login com: admin / admin123')
        self.stdout.write('   3. ALTERE A SENHA IMEDIATAMENTE!')
        self.stdout.write('   4. Configure as Configurações do Site')
