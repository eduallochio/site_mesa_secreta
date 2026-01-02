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
    desenvolvedor_nome = models.CharField('Desenvolvedor', max_length=100, default='OmegaSistem', blank=True)
    desenvolvedor_url = models.URLField('URL do Desenvolvedor', default='https://omegasistem.com.br', blank=True)
    
    # Políticas e Termos
    politica_privacidade = models.TextField('Política de Privacidade', blank=True, help_text='Conteúdo da política de privacidade (aceita HTML)')
    politica_privacidade_atualizada = models.DateField('Data de Atualização da Privacidade', null=True, blank=True, help_text='Última atualização da política')
    termos_uso = models.TextField('Termos de Uso', blank=True, help_text='Conteúdo dos termos de uso (aceita HTML)')
    termos_uso_atualizado = models.DateField('Data de Atualização dos Termos', null=True, blank=True, help_text='Última atualização dos termos')
    
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
    
    def get_total_visualizacoes(self):
        """Retorna o total de visualizações únicas desta postagem"""
        return EstatisticaVisualizacao.objects.filter(
            tipo_conteudo='postagem',
            conteudo_id=self.id
        ).values('session_key').distinct().count()
    
    def get_tempo_medio_visualizacao(self):
        """Retorna o tempo médio de visualização em segundos"""
        from django.db.models import Avg
        resultado = EstatisticaVisualizacao.objects.filter(
            tipo_conteudo='postagem',
            conteudo_id=self.id,
            tempo_visualizacao__gt=0
        ).aggregate(Avg('tempo_visualizacao'))
        
        tempo_medio = resultado['tempo_visualizacao__avg']
        return round(tempo_medio) if tempo_medio else 0
    
    def get_scroll_medio(self):
        """Retorna a profundidade média de scroll"""
        from django.db.models import Avg
        resultado = EstatisticaVisualizacao.objects.filter(
            tipo_conteudo='postagem',
            conteudo_id=self.id
        ).aggregate(Avg('scroll_profundidade'))
        
        scroll_medio = resultado['scroll_profundidade__avg']
        return round(scroll_medio) if scroll_medio else 0
    
    def get_visualizacoes_ultimos_30_dias(self):
        """Visualizações dos últimos 30 dias"""
        from datetime import timedelta
        data_limite = timezone.now() - timedelta(days=30)
        
        return EstatisticaVisualizacao.objects.filter(
            tipo_conteudo='postagem',
            conteudo_id=self.id,
            data_visualizacao__gte=data_limite
        ).values('session_key').distinct().count()
    
    def get_taxa_engajamento(self):
        """Taxa de engajamento baseada no tempo e scroll"""
        tempo_medio = self.get_tempo_medio_visualizacao()
        scroll_medio = self.get_scroll_medio()
        
        # Considera engajado se passou mais de 30s E rolou mais de 50%
        if tempo_medio >= 30 and scroll_medio >= 50:
            return 'Alto'
        elif tempo_medio >= 15 and scroll_medio >= 25:
            return 'Médio'
        else:
            return 'Baixo'


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


class EstatisticaVisualizacao(models.Model):
    """Modelo para rastrear visualizações de conteúdo"""
    
    TIPO_CONTEUDO_CHOICES = [
        ('postagem', 'Postagem'),
        ('video', 'Vídeo'),
        ('home', 'Página Inicial'),
    ]
    
    tipo_conteudo = models.CharField('Tipo de Conteúdo', max_length=20, choices=TIPO_CONTEUDO_CHOICES)
    conteudo_id = models.IntegerField('ID do Conteúdo', null=True, blank=True, help_text='ID da postagem ou vídeo (null para home)')
    conteudo_titulo = models.CharField('Título do Conteúdo', max_length=255, blank=True)
    
    # Informações da sessão
    session_key = models.CharField('Session Key', max_length=40, db_index=True)
    
    # Dados técnicos
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    
    # Métricas de tempo
    tempo_visualizacao = models.IntegerField('Tempo de Visualização (segundos)', default=0, help_text='Tempo que o usuário passou na página')
    scroll_profundidade = models.IntegerField('Profundidade de Scroll (%)', default=0, help_text='Porcentagem da página que foi rolada')
    
    # Data e hora
    data_visualizacao = models.DateTimeField('Data de Visualização', auto_now_add=True, db_index=True)
    data_saida = models.DateTimeField('Data de Saída', null=True, blank=True, help_text='Quando o usuário saiu da página')
    
    class Meta:
        verbose_name = 'Estatística de Visualização'
        verbose_name_plural = 'Estatísticas de Visualizações'
        ordering = ['-data_visualizacao']
        indexes = [
            models.Index(fields=['tipo_conteudo', 'conteudo_id']),
            models.Index(fields=['data_visualizacao']),
        ]
    
    def __str__(self):
        if self.conteudo_titulo:
            return f'{self.tipo_conteudo}: {self.conteudo_titulo} - {self.data_visualizacao.strftime("%d/%m/%Y %H:%M")}'
        return f'{self.tipo_conteudo} - {self.data_visualizacao.strftime("%d/%m/%Y %H:%M")}'
