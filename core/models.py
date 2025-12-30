from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
import requests
import logging

logger = logging.getLogger(__name__)


class ConfiguracaoSite(models.Model):
    """Model singleton para configurações editáveis do site"""
    
    # Estatísticas da Home
    jogos_analisados = models.IntegerField('Jogos Analisados', default=150, help_text='Número exibido na home')
    videos_por_mes = models.IntegerField('Vídeos por Mês', default=15, help_text='Número exibido na home')
    inscritos_canal = models.IntegerField('Inscritos no Canal (Manual)', default=2000, help_text='Número manual ou obtido da API')
    usar_inscritos_automatico = models.BooleanField('Usar Inscritos Automático do YouTube', default=False, help_text='Buscar automaticamente da API do YouTube')
    
    # YouTube API
    youtube_api_key = models.CharField('YouTube API Key', max_length=100, blank=True, help_text='Chave de API do Google Cloud Console')
    youtube_channel_id = models.CharField('YouTube Channel ID', max_length=100, blank=True, help_text='ID do canal do YouTube')
    
    # Textos da Home
    hero_titulo = models.CharField('Título Principal', max_length=200, default='Bem-vindo à Mesa Secreta')
    hero_descricao = models.TextField('Descrição Principal', default='Reviews completos, análises profundas e as melhores estratégias para dominar o mundo dos jogos de tabuleiro modernos e RPGs')
    
    # Redes Sociais
    youtube_url = models.URLField('URL do YouTube', blank=True, default='https://youtube.com/@mesasecreta')
    instagram_url = models.URLField('URL do Instagram', blank=True, default='https://instagram.com/mesasecreta')
    tiktok_url = models.URLField('URL do TikTok', blank=True, default='https://tiktok.com/@mesasecreta')
    twitter_url = models.URLField('URL do Twitter/X', blank=True)
    facebook_url = models.URLField('URL do Facebook', blank=True)
    
    # Informações do Footer
    sobre_texto = models.TextField('Texto Sobre', default='O Quartel General dos jogos de tabuleiro e RPG! Conteúdo de qualidade sobre reviews, notícias e dicas para todos os níveis de jogadores.')
    email_contato = models.EmailField('Email de Contato', blank=True)
    desenvolvedor_nome = models.CharField('Nome do Desenvolvedor', max_length=100, default='OmegaSistem', blank=True)
    desenvolvedor_url = models.URLField('URL do Desenvolvedor', default='https://omegasistem.com.br', blank=True)
    
    # Políticas e Termos
    politica_privacidade = models.TextField('Política de Privacidade', blank=True, help_text='Conteúdo da política de privacidade (aceita HTML)')
    termos_uso = models.TextField('Termos de Uso', blank=True, help_text='Conteúdo dos termos de uso (aceita HTML)')
    
    # SEO
    meta_description = models.CharField('Meta Description', max_length=160, blank=True)
    meta_keywords = models.CharField('Meta Keywords', max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'
    
    def __str__(self):
        return 'Configurações do Site'
    
    def get_inscritos_youtube(self):
        """Busca o número de inscritos diretamente da API do YouTube"""
        if not self.youtube_api_key or not self.youtube_channel_id:
            return None
        
        try:
            url = f'https://www.googleapis.com/youtube/v3/channels'
            params = {
                'part': 'statistics',
                'id': self.youtube_channel_id,
                'key': self.youtube_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                subscriber_count = int(data['items'][0]['statistics']['subscriberCount'])
                return subscriber_count
            
        except requests.RequestException as e:
            logger.error(f'Erro ao buscar inscritos do YouTube: {e}')
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f'Erro ao processar resposta da API do YouTube: {e}')
        
        return None
    
    def get_inscritos_display(self):
        """Retorna o número de inscritos a ser exibido (automático ou manual)"""
        if self.usar_inscritos_automatico:
            inscritos_auto = self.get_inscritos_youtube()
            if inscritos_auto is not None:
                return inscritos_auto
        
        return self.inscritos_canal
    
    def save(self, *args, **kwargs):
        # Garantir que existe apenas uma instância
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Retorna a instância única de configuração"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Postagem(models.Model):
    """Model para artigos, dicas e reviews de jogos"""
    
    CATEGORIA_CHOICES = [
        ('novidades', 'Novidades'),
        ('dicas', 'Dicas e Tutoriais'),
        ('reviews', 'Review de Jogos'),
    ]
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('publicado', 'Publicado'),
    ]
    
    titulo = models.CharField('Título', max_length=200)
    subtitulo = models.CharField('Subtítulo/Resumo', max_length=300, blank=True)
    conteudo = RichTextField('Conteúdo', config_name='default')
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='novidades')
    imagem_capa = models.ImageField('Imagem de Capa', upload_to='postagens/', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='rascunho')
    data_publicacao = models.DateTimeField('Data de Publicação', default=timezone.now)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Postagem'
        verbose_name_plural = 'Postagens'
        ordering = ['-data_publicacao']
    
    def __str__(self):
        return self.titulo


class Video(models.Model):
    """Model para vídeos do YouTube"""
    
    titulo = models.CharField('Título do Vídeo', max_length=200)
    youtube_id = models.CharField('ID do YouTube', max_length=50, help_text='ID do vídeo do YouTube (ex: dQw4w9WgXcQ)')
    descricao = models.TextField('Descrição', blank=True)
    data_publicacao = models.DateTimeField('Data de Publicação', default=timezone.now)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vídeo'
        verbose_name_plural = 'Vídeos'
        ordering = ['-data_publicacao']
    
    def __str__(self):
        return self.titulo
    
    def get_youtube_url(self):
        """Retorna a URL completa do vídeo no YouTube"""
        return f'https://www.youtube.com/watch?v={self.youtube_id}'
    
    def get_embed_url(self):
        """Retorna a URL para incorporar o vídeo"""
        return f'https://www.youtube.com/embed/{self.youtube_id}'
