"""
Comando de gerenciamento Django para sincronizar vídeos do YouTube
Uso: python manage.py sync_youtube
"""
from django.core.management.base import BaseCommand
from core.youtube_service import YouTubeService


class Command(BaseCommand):
    help = 'Sincroniza vídeos do YouTube com o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--channel-id',
            type=str,
            help='ID do canal do YouTube (opcional)',
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=15,
            help='Número máximo de vídeos a buscar (padrão: 15)',
        )

    def handle(self, *args, **options):
        channel_id = options.get('channel_id')
        max_results = options.get('max_results')
        
        self.stdout.write(self.style.WARNING('Iniciando sincronização de vídeos do YouTube...'))
        
        service = YouTubeService(channel_id=channel_id)
        novos, atualizados = service.sync_videos_to_database(max_results=max_results)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Sincronização concluída!'))
        self.stdout.write(self.style.SUCCESS(f'   Novos vídeos: {novos}'))
        self.stdout.write(self.style.SUCCESS(f'   Vídeos atualizados: {atualizados}'))
        self.stdout.write(self.style.SUCCESS(f'   Total processado: {novos + atualizados}'))
