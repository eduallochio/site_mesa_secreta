from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Postagem, Video


@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    """Admin personalizado para Postagens com melhorias de UX"""
    
    list_display = ('titulo_com_status', 'categoria_badge', 'preview_imagem', 'data_publicacao', 'acoes_rapidas')
    list_display_links = ('titulo_com_status',)
    list_filter = ('categoria', 'status', 'data_publicacao', 'data_criacao')
    search_fields = ('titulo', 'subtitulo', 'conteudo')
    date_hierarchy = 'data_publicacao'
    list_per_page = 20
    
    # Ações em massa personalizadas
    actions = ['publicar_postagens', 'marcar_como_rascunho', 'duplicar_postagem']
    
    fieldsets = (
        ('📝 Informações Principais', {
            'fields': ('titulo', 'subtitulo', 'categoria', 'status'),
            'description': 'Preencha as informações básicas da postagem'
        }),
        ('📄 Conteúdo', {
            'fields': ('conteudo',),
            'description': 'Escreva o conteúdo completo usando o editor'
        }),
        ('🖼️ Mídia', {
            'fields': ('imagem_capa', 'preview_imagem_atual'),
            'description': 'Adicione uma imagem de capa atraente'
        }),
        ('📅 Publicação', {
            'fields': ('data_publicacao',),
            'classes': ('collapse',),
        }),
        ('ℹ️ Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao', 'preview_imagem_atual')
    
    # Configurações de salvamento
    save_on_top = True
    
    def titulo_com_status(self, obj):
        """Exibe o título com ícone de status"""
        if obj.status == 'publicado':
            icon = '✅'
            color = '#00ff88'
        else:
            icon = '📝'
            color = '#ff9800'
        return format_html(
            '<span style="color: {};">{}</span> <strong>{}</strong>',
            color, icon, obj.titulo[:50]
        )
    titulo_com_status.short_description = 'Título'
    
    def categoria_badge(self, obj):
        """Exibe a categoria com badge colorido"""
        colors = {
            'novidades': '#2196F3',
            'dicas': '#4CAF50',
            'reviews': '#FF5722'
        }
        color = colors.get(obj.categoria, '#9E9E9E')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_categoria_display().upper()
        )
    categoria_badge.short_description = 'Categoria'
    
    def preview_imagem(self, obj):
        """Exibe preview da imagem de capa"""
        if obj.imagem_capa:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; '
                'border-radius: 8px; border: 2px solid #8b5cf6;" />',
                obj.imagem_capa.url
            )
        return format_html('<span style="color: #999;">Sem imagem</span>')
    preview_imagem.short_description = 'Preview'
    
    def preview_imagem_atual(self, obj):
        """Exibe preview maior da imagem atual"""
        if obj.imagem_capa:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="max-width: 400px; border-radius: 8px; '
                'box-shadow: 0 4px 8px rgba(0,0,0,0.2);" />'
                '<p style="color: #666; margin-top: 10px;">📏 Tamanho recomendado: 1200x630px</p>'
                '</div>',
                obj.imagem_capa.url
            )
        return format_html('<p style="color: #999;">Nenhuma imagem enviada ainda</p>')
    preview_imagem_atual.short_description = 'Preview Atual'
    
    def acoes_rapidas(self, obj):
        """Botões de ação rápida"""
        return format_html(
            '<a class="button" href="/postagens/{}" target="_blank" '
            'style="background: #8b5cf6; color: white; padding: 6px 12px; '
            'text-decoration: none; border-radius: 4px; font-size: 12px;">👁️ Ver</a>',
            obj.pk
        )
    acoes_rapidas.short_description = 'Ações'
    
    # Ações em massa
    def publicar_postagens(self, request, queryset):
        """Publica postagens selecionadas"""
        count = queryset.update(status='publicado')
        self.message_user(request, f'{count} postagem(ns) publicada(s) com sucesso! ✅')
    publicar_postagens.short_description = '✅ Publicar postagens selecionadas'
    
    def marcar_como_rascunho(self, request, queryset):
        """Marca postagens como rascunho"""
        count = queryset.update(status='rascunho')
        self.message_user(request, f'{count} postagem(ns) marcada(s) como rascunho 📝')
    marcar_como_rascunho.short_description = '📝 Marcar como rascunho'
    
    def duplicar_postagem(self, request, queryset):
        """Duplica postagens selecionadas"""
        count = 0
        for obj in queryset:
            obj.pk = None
            obj.titulo = f'{obj.titulo} (Cópia)'
            obj.status = 'rascunho'
            obj.save()
            count += 1
        self.message_user(request, f'{count} postagem(ns) duplicada(s) 📋')
    duplicar_postagem.short_description = '📋 Duplicar postagens'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin personalizado para Vídeos"""
    
    list_display = ('titulo_com_preview', 'youtube_id', 'preview_thumbnail', 'data_publicacao', 'acoes')
    list_display_links = ('titulo_com_preview',)
    list_filter = ('data_publicacao',)
    search_fields = ('titulo', 'descricao', 'youtube_id')
    date_hierarchy = 'data_publicacao'
    list_per_page = 20
    
    fieldsets = (
        ('🎬 Informações do Vídeo', {
            'fields': ('titulo', 'youtube_id', 'preview_video'),
            'description': 'Configure o vídeo do YouTube'
        }),
        ('📝 Descrição', {
            'fields': ('descricao',),
        }),
        ('📅 Publicação', {
            'fields': ('data_publicacao',),
            'classes': ('collapse',),
        }),
        ('ℹ️ Informações do Sistema', {
            'fields': ('data_criacao',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('data_criacao', 'preview_video')
    save_on_top = True
    
    def titulo_com_preview(self, obj):
        """Título com ícone"""
        return format_html('🎬 <strong>{}</strong>', obj.titulo[:50])
    titulo_com_preview.short_description = 'Título'
    
    def preview_thumbnail(self, obj):
        """Preview da thumbnail do YouTube"""
        return format_html(
            '<img src="https://img.youtube.com/vi/{}/mqdefault.jpg" '
            'width="120" height="90" style="border-radius: 8px; '
            'border: 2px solid #8b5cf6;" />',
            obj.youtube_id
        )
    preview_thumbnail.short_description = 'Thumbnail'
    
    def preview_video(self, obj):
        """Preview do vídeo embutido"""
        if obj.youtube_id:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<iframe width="560" height="315" '
                'src="https://www.youtube.com/embed/{}" '
                'frameborder="0" allowfullscreen '
                'style="border-radius: 8px;"></iframe>'
                '<p style="margin-top: 10px;"><a href="{}" target="_blank" '
                'style="color: #8b5cf6;">🔗 Abrir no YouTube</a></p>'
                '</div>',
                obj.youtube_id, obj.get_youtube_url()
            )
        return 'Adicione um ID de vídeo para ver o preview'
    preview_video.short_description = 'Preview do Vídeo'
    
    def acoes(self, obj):
        """Ações rápidas"""
        return format_html(
            '<a href="{}" target="_blank" '
            'style="background: #FF0000; color: white; padding: 6px 12px; '
            'text-decoration: none; border-radius: 4px; font-size: 12px;">▶️ YouTube</a>',
            obj.get_youtube_url()
        )
    acoes.short_description = 'Ações'


# Personalização completa do Admin
admin.site.site_header = '🎲 Mesa Secreta - Painel de Administração'
admin.site.site_title = 'Mesa Secreta Admin'
admin.site.index_title = 'Bem-vindo ao Quartel General! 🎮'
admin.site.site_url = '/'  # Link para o site
admin.site.enable_nav_sidebar = True  # Sidebar moderna
