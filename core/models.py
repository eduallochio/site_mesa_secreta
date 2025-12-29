from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


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
