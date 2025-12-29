"""
Serviço para integração com YouTube
Busca vídeos do canal Mesa Secreta automaticamente
"""
import feedparser
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from core.models import Video


class YouTubeService:
    """Serviço para buscar vídeos do YouTube via RSS Feed"""
    
    def __init__(self, channel_id=None):
        # Usa o ID do settings.py ou o fornecido
        self.channel_id = channel_id or getattr(settings, 'YOUTUBE_CHANNEL_ID', None)
    
    def get_channel_feed_url(self):
        """Retorna a URL do RSS feed do canal"""
        return f'https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}'
    
    def fetch_latest_videos(self, max_results=15):
        """
        Busca os últimos vídeos do canal
        
        Args:
            max_results: Número máximo de vídeos a buscar
        
        Returns:
            Lista de dicionários com informações dos vídeos
        """
        feed_url = self.get_channel_feed_url()
        
        try:
            feed = feedparser.parse(feed_url)
            videos = []
            
            for entry in feed.entries[:max_results]:
                # Extrair o ID do vídeo da URL
                video_id = entry.yt_videoid if hasattr(entry, 'yt_videoid') else entry.id.split(':')[-1]
                
                # Converter data de publicação com timezone
                if hasattr(entry, 'published_parsed'):
                    published = datetime(*entry.published_parsed[:6])
                    published = timezone.make_aware(published)
                else:
                    published = timezone.now()
                
                video_data = {
                    'youtube_id': video_id,
                    'titulo': entry.title,
                    'descricao': entry.summary if hasattr(entry, 'summary') else '',
                    'data_publicacao': published,
                    'url': entry.link
                }
                
                videos.append(video_data)
            
            return videos
        
        except Exception as e:
            print(f"Erro ao buscar vídeos do YouTube: {e}")
            return []
    
    def sync_videos_to_database(self, max_results=15):
        """
        Sincroniza vídeos do YouTube com o banco de dados
        
        Args:
            max_results: Número máximo de vídeos a sincronizar
        
        Returns:
            Tupla (novos, atualizados)
        """
        videos = self.fetch_latest_videos(max_results)
        novos = 0
        atualizados = 0
        
        for video_data in videos:
            video, created = Video.objects.update_or_create(
                youtube_id=video_data['youtube_id'],
                defaults={
                    'titulo': video_data['titulo'],
                    'descricao': video_data['descricao'],
                    'data_publicacao': video_data['data_publicacao']
                }
            )
            
            if created:
                novos += 1
            else:
                atualizados += 1
        
        return (novos, atualizados)
