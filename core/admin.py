from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum
import csv
from .models import Postagem, Video, ConfiguracaoSite, EstatisticaVisualizacao


class ExportCsvMixin:
    """Mixin para exportar dados em CSV"""
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "📊 Exportar selecionados como CSV"


@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Admin personalizado para Postagens com melhorias de UX e melhores práticas"""
    
    list_display = ('titulo_com_status', 'categoria_badge', 'preview_imagem', 
                   'metricas_visualizacao', 'data_publicacao', 'dias_desde_publicacao', 'acoes_rapidas')
    list_display_links = ('titulo_com_status',)
    list_filter = ('categoria', 'status', 'data_publicacao', 'data_criacao')
    search_fields = ('titulo', 'subtitulo', 'conteudo')
    date_hierarchy = 'data_publicacao'
    list_per_page = 25
    list_select_related = True
    show_full_result_count = True
    
    # Ações em massa personalizadas
    actions = ['publicar_postagens', 'marcar_como_rascunho', 'duplicar_postagem', 
              'agendar_para_hoje', 'export_as_csv']
    
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
            'description': 'Adicione uma imagem de capa atraente (recomendado: 1200x630px)'
        }),
        ('📅 Publicação', {
            'fields': ('data_publicacao',),
            'classes': ('collapse',),
            'description': 'Agende a data de publicação'
        }),
        ('📊 Estatísticas e Métricas', {
            'fields': ('painel_estatisticas',),
            'description': 'Métricas de desempenho desta postagem'
        }),
        ('ℹ️ Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao', 'contador_info'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao', 'preview_imagem_atual', 'contador_info', 'painel_estatisticas')
    
    # Configurações de salvamento
    save_on_top = True
    save_as = True  # Permite "Salvar como novo"
    save_as_continue = True
    
    # Autocomplete para melhor performance
    autocomplete_fields = []
    
    def get_queryset(self, request):
        """Otimiza queries com select_related e prefetch_related"""
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        """Adiciona estatísticas ao topo da lista"""
        extra_context = extra_context or {}
        
        # Estatísticas gerais
        total = Postagem.objects.count()
        publicadas = Postagem.objects.filter(status='publicado').count()
        rascunhos = Postagem.objects.filter(status='rascunho').count()
        esta_semana = Postagem.objects.filter(
            data_publicacao__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        extra_context['stats'] = {
            'total': total,
            'publicadas': publicadas,
            'rascunhos': rascunhos,
            'esta_semana': esta_semana,
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def titulo_com_status(self, obj):
        """Exibe o título com ícone de status"""
        if obj.status == 'publicado':
            icon = '✅'
            color = '#00E5CC'
        else:
            icon = '📝'
            color = '#FF6B35'
        return format_html(
            '<span style="color: {};">{}</span> <strong>{}</strong>',
            color, icon, obj.titulo[:60]
        )
    titulo_com_status.short_description = 'Título'
    titulo_com_status.admin_order_field = 'titulo'
    
    def categoria_badge(self, obj):
        """Exibe a categoria com badge colorido"""
        colors = {
            'novidades': '#00E5CC',
            'dicas': '#4CAF50',
            'reviews': '#FF6B35'
        }
        color = colors.get(obj.categoria, '#9E9E9E')
        return format_html(
            '<span style="background: {}; color: #0a0a0a; padding: 5px 14px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px; '
            'display: inline-block;">{}</span>',
            color, obj.get_categoria_display().upper()
        )
    categoria_badge.short_description = 'Categoria'
    categoria_badge.admin_order_field = 'categoria'
    
    def preview_imagem(self, obj):
        """Exibe preview da imagem de capa"""
        if obj.imagem_capa:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; '
                'border-radius: 8px; border: 2px solid #00E5CC; box-shadow: 0 2px 8px rgba(0,229,204,0.2);" />',
                obj.imagem_capa.url
            )
        return mark_safe('<span style="color: #999;">⚠️ Sem imagem</span>')
    preview_imagem.short_description = '🖼️ Preview'
    
    def preview_imagem_atual(self, obj):
        """Exibe preview maior da imagem atual"""
        if obj.imagem_capa:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="max-width: 100%; max-height: 400px; border-radius: 8px; '
                'box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />'
                '<p style="color: #666; margin-top: 10px; font-size: 13px;">'
                '📏 <strong>Tamanho recomendado:</strong> 1200x630px para melhor SEO</p>'
                '</div>',
                obj.imagem_capa.url
            )
        return mark_safe(
            '<div style="padding: 20px; background: #f5f5f5; border-radius: 8px; text-align: center;">'
            '<p style="color: #999; font-size: 14px;">📸 Nenhuma imagem enviada ainda</p>'
            '</div>'
        )
    preview_imagem_atual.short_description = 'Preview Atual'
    
    def metricas_visualizacao(self, obj):
        """Exibe métricas detalhadas de visualização"""
        total_views = obj.get_total_visualizacoes()
        tempo_medio = obj.get_tempo_medio_visualizacao()
        scroll_medio = obj.get_scroll_medio()
        taxa_engajamento = obj.get_taxa_engajamento()
        
        # Definir cores para taxa de engajamento
        cor_engajamento = {
            'Alto': '#4CAF50',
            'Médio': '#FF9800',
            'Baixo': '#f44336'
        }.get(taxa_engajamento, '#999')
        
        # Converter tempo médio para minutos e segundos
        minutos = tempo_medio // 60
        segundos = tempo_medio % 60
        tempo_texto = f'{minutos}m {segundos}s' if minutos > 0 else f'{segundos}s'
        
        return format_html(
            '<div style="font-size: 11px; line-height: 1.4;">'
            '<div><strong style="color: #00E5CC;">👁️ {}</strong> views</div>'
            '<div>⏱️ {} | 📊 {}%</div>'
            '<div>Engajamento: <span style="color: {}; font-weight: bold;">{}</span></div>'
            '</div>',
            total_views,
            tempo_texto,
            scroll_medio,
            cor_engajamento,
            taxa_engajamento
        )
    metricas_visualizacao.short_description = '📈 Métricas'
    
    def visualizacoes_info(self, obj):
        """Informações sobre visualizações (mantido para compatibilidade)"""
        return mark_safe('<span style="color: #666; font-size: 12px;">🔜 Em breve</span>')
    visualizacoes_info.short_description = '👁️ Views'
    
    def dias_desde_publicacao(self, obj):
        """Mostra há quantos dias foi publicado"""
        if obj.status == 'publicado':
            dias = (timezone.now() - obj.data_publicacao).days
            if dias == 0:
                texto = '🆕 Hoje'
                color = '#00E5CC'
            elif dias == 1:
                texto = 'Ontem'
                color = '#4CAF50'
            elif dias <= 7:
                texto = f'{dias} dias'
                color = '#FF6B35'
            else:
                texto = f'{dias} dias'
                color = '#999'
            return format_html(
                '<span style="color: {}; font-size: 12px;">{}</span>',
                color, texto
            )
        return mark_safe('<span style="color: #999; font-size: 12px;">-</span>')
    dias_desde_publicacao.short_description = '📅 Publicado'
    dias_desde_publicacao.admin_order_field = 'data_publicacao'
    
    def contador_info(self, obj):
        """Exibe contadores úteis"""
        if obj.conteudo:
            palavras = len(obj.conteudo.split())
            caracteres = len(obj.conteudo)
            tempo_leitura = max(1, palavras // 200)  # ~200 palavras por minuto
            
            return format_html(
                '<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">'
                '<p><strong>📊 Estatísticas do Conteúdo:</strong></p>'
                '<ul style="margin: 10px 0; padding-left: 20px;">'
                '<li>📝 <strong>{}</strong> palavras</li>'
                '<li>🔤 <strong>{}</strong> caracteres</li>'
                '<li>⏱️ Tempo de leitura: <strong>~{} min</strong></li>'
                '</ul>'
                '</div>',
                palavras, caracteres, tempo_leitura
            )
        return 'Nenhum conteúdo ainda'
    contador_info.short_description = 'Estatísticas'
    
    def acoes_rapidas(self, obj):
        """Botões de ação rápida"""
        if obj.status == 'publicado':
            return format_html(
                '<a class="button" href="/postagens/{}/" target="_blank" '
                'style="background: #00E5CC; color: #0a0a0a; padding: 6px 12px; '
                'text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600;">'
                '👁️ Visualizar</a>',
                obj.pk
            )
        return mark_safe(
            '<span style="color: #999; font-size: 12px;">Não publicado</span>'
        )
    acoes_rapidas.short_description = '⚡ Ações'
    
    def painel_estatisticas(self, obj):
        """Painel detalhado de estatísticas da postagem"""
        if not obj.pk:
            return mark_safe('<p style="color: #999;">Salve a postagem primeiro para ver estatísticas.</p>')
        
        total_views = obj.get_total_visualizacoes()
        tempo_medio = obj.get_tempo_medio_visualizacao()
        scroll_medio = obj.get_scroll_medio()
        views_30_dias = obj.get_visualizacoes_ultimos_30_dias()
        taxa_engajamento = obj.get_taxa_engajamento()
        
        # Converter tempo médio para formato legível
        minutos = tempo_medio // 60
        segundos = tempo_medio % 60
        tempo_texto = f'{minutos}m {segundos}s' if minutos > 0 else f'{segundos}s'
        
        # Cores para engajamento
        cor_engajamento = {
            'Alto': '#4CAF50',
            'Médio': '#FF9800',
            'Baixo': '#f44336'
        }.get(taxa_engajamento, '#999')
        
        return format_html(
            '<div style="background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); '
            'border: 2px solid #00E5CC; border-radius: 12px; padding: 24px; margin: 10px 0;">'
            
            '<h3 style="color: #00E5CC; margin: 0 0 20px 0; font-size: 18px;">'
            '<i class="fas fa-chart-line"></i> Métricas de Desempenho</h3>'
            
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">'
            
            # Total de Visualizações
            '<div style="background: rgba(0, 229, 204, 0.1); border-left: 4px solid #00E5CC; '
            'padding: 16px; border-radius: 8px;">'
            '<div style="color: #00E5CC; font-size: 12px; text-transform: uppercase; '
            'letter-spacing: 1px; margin-bottom: 8px;">👁️ Total de Visualizações</div>'
            '<div style="color: #fff; font-size: 32px; font-weight: bold;">{}</div>'
            '<div style="color: rgba(255,255,255,0.6); font-size: 11px; margin-top: 4px;">'
            'Visualizações únicas</div>'
            '</div>'
            
            # Últimos 30 dias
            '<div style="background: rgba(255, 107, 53, 0.1); border-left: 4px solid #FF6B35; '
            'padding: 16px; border-radius: 8px;">'
            '<div style="color: #FF6B35; font-size: 12px; text-transform: uppercase; '
            'letter-spacing: 1px; margin-bottom: 8px;">📅 Últimos 30 Dias</div>'
            '<div style="color: #fff; font-size: 32px; font-weight: bold;">{}</div>'
            '<div style="color: rgba(255,255,255,0.6); font-size: 11px; margin-top: 4px;">'
            'Views recentes</div>'
            '</div>'
            
            # Tempo médio
            '<div style="background: rgba(255, 230, 86, 0.1); border-left: 4px solid #FFE656; '
            'padding: 16px; border-radius: 8px;">'
            '<div style="color: #FFE656; font-size: 12px; text-transform: uppercase; '
            'letter-spacing: 1px; margin-bottom: 8px;">⏱️ Tempo Médio</div>'
            '<div style="color: #fff; font-size: 32px; font-weight: bold;">{}</div>'
            '<div style="color: rgba(255,255,255,0.6); font-size: 11px; margin-top: 4px;">'
            'Por visualização</div>'
            '</div>'
            
            # Scroll médio
            '<div style="background: rgba(103, 58, 183, 0.1); border-left: 4px solid #673AB7; '
            'padding: 16px; border-radius: 8px;">'
            '<div style="color: #673AB7; font-size: 12px; text-transform: uppercase; '
            'letter-spacing: 1px; margin-bottom: 8px;">📊 Scroll Médio</div>'
            '<div style="color: #fff; font-size: 32px; font-weight: bold;">{}%</div>'
            '<div style="color: rgba(255,255,255,0.6); font-size: 11px; margin-top: 4px;">'
            'Da página rolada</div>'
            '</div>'
            
            '</div>'
            
            # Taxa de Engajamento
            '<div style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; '
            'padding: 16px; margin-top: 16px; text-align: center;">'
            '<div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 8px;">'
            'Taxa de Engajamento</div>'
            '<div style="color: {}; font-size: 24px; font-weight: bold;">{}</div>'
            '<div style="color: rgba(255,255,255,0.5); font-size: 11px; margin-top: 4px;">'
            'Baseado em tempo e scroll</div>'
            '</div>'
            
            '</div>',
            total_views,
            views_30_dias,
            tempo_texto,
            scroll_medio,
            cor_engajamento,
            taxa_engajamento
        )
    painel_estatisticas.short_description = 'Estatísticas Detalhadas'
    
    # Ações em massa
    def publicar_postagens(self, request, queryset):
        """Publica postagens selecionadas"""
        rascunhos = queryset.filter(status='rascunho')
        count = rascunhos.update(status='publicado', data_publicacao=timezone.now())
        if count:
            self.message_user(
                request, 
                f'✅ {count} postagem(ns) publicada(s) com sucesso!',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                '⚠️ Nenhuma postagem em rascunho foi selecionada.',
                messages.WARNING
            )
    publicar_postagens.short_description = '✅ Publicar postagens selecionadas'
    
    def marcar_como_rascunho(self, request, queryset):
        """Marca postagens como rascunho"""
        count = queryset.update(status='rascunho')
        self.message_user(
            request, 
            f'📝 {count} postagem(ns) marcada(s) como rascunho',
            messages.INFO
        )
    marcar_como_rascunho.short_description = '📝 Marcar como rascunho'
    
    def duplicar_postagem(self, request, queryset):
        """Duplica postagens selecionadas"""
        if queryset.count() > 5:
            self.message_user(
                request,
                '⚠️ Você pode duplicar no máximo 5 postagens por vez.',
                messages.WARNING
            )
            return
        
        count = 0
        for obj in queryset:
            obj.pk = None
            obj.titulo = f'[CÓPIA] {obj.titulo}'
            obj.status = 'rascunho'
            obj.data_publicacao = timezone.now()
            obj.save()
            count += 1
        
        self.message_user(
            request, 
            f'📋 {count} postagem(ns) duplicada(s) com sucesso!',
            messages.SUCCESS
        )
    duplicar_postagem.short_description = '📋 Duplicar postagens'
    
    def agendar_para_hoje(self, request, queryset):
        """Agenda postagens para hoje"""
        count = queryset.update(data_publicacao=timezone.now())
        self.message_user(
            request,
            f'📅 {count} postagem(ns) agendada(s) para hoje!',
            messages.SUCCESS
        )
    agendar_para_hoje.short_description = '📅 Agendar para hoje'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Admin personalizado para Vídeos com melhorias de UX"""
    
    list_display = ('titulo_com_icone', 'youtube_id_display', 'preview_thumbnail', 
                   'duracao_info', 'data_publicacao', 'dias_desde_publicacao', 'acoes')
    list_display_links = ('titulo_com_icone',)
    list_filter = ('data_publicacao', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'youtube_id')
    date_hierarchy = 'data_publicacao'
    list_per_page = 25
    
    actions = ['export_as_csv', 'agendar_para_hoje']
    
    fieldsets = (
        ('🎬 Informações do Vídeo', {
            'fields': ('titulo', 'youtube_id', 'preview_video'),
            'description': 'Configure o vídeo do YouTube. Para encontrar o ID: youtube.com/watch?v=<strong>SEU_ID_AQUI</strong>'
        }),
        ('📝 Descrição', {
            'fields': ('descricao',),
            'description': 'Adicione uma descrição detalhada (suporte a Markdown)'
        }),
        ('📅 Publicação', {
            'fields': ('data_publicacao',),
            'classes': ('collapse',),
            'description': 'Agende a data de publicação'
        }),
        ('ℹ️ Informações do Sistema', {
            'fields': ('data_criacao', 'video_stats'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('data_criacao', 'preview_video', 'video_stats')
    save_on_top = True
    save_as = True
    save_as_continue = True
    
    def get_queryset(self, request):
        """Otimiza queries"""
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        """Adiciona estatísticas"""
        extra_context = extra_context or {}
        
        total = Video.objects.count()
        esta_semana = Video.objects.filter(
            data_publicacao__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        este_mes = Video.objects.filter(
            data_publicacao__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        extra_context['video_stats'] = {
            'total': total,
            'esta_semana': esta_semana,
            'este_mes': este_mes,
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def titulo_com_icone(self, obj):
        """Título com ícone do YouTube"""
        return format_html(
            '<span style="color: #FF0000;">▶️</span> <strong>{}</strong>',
            obj.titulo[:60]
        )
    titulo_com_icone.short_description = 'Título'
    titulo_com_icone.admin_order_field = 'titulo'
    
    def youtube_id_display(self, obj):
        """Exibe o YouTube ID de forma destacada"""
        return format_html(
            '<code style="background: #f5f5f5; padding: 4px 8px; border-radius: 4px; '
            'font-family: monospace; font-size: 11px; color: #FF0000;">{}</code>',
            obj.youtube_id
        )
    youtube_id_display.short_description = '🆔 YouTube ID'
    youtube_id_display.admin_order_field = 'youtube_id'
    
    def preview_thumbnail(self, obj):
        """Preview da thumbnail do YouTube"""
        if obj.youtube_id:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="https://img.youtube.com/vi/{}/mqdefault.jpg" '
                'width="120" height="90" style="border-radius: 8px; '
                'border: 2px solid #FF0000; box-shadow: 0 2px 8px rgba(255,0,0,0.2); '
                'transition: transform 0.3s;" '
                'onmouseover="this.style.transform=\'scale(1.05)\'" '
                'onmouseout="this.style.transform=\'scale(1)\'" />'
                '</a>',
                obj.get_youtube_url(), obj.youtube_id
            )
        return mark_safe('<span style="color: #999;">⚠️ ID inválido</span>')
    preview_thumbnail.short_description = '🖼️ Thumbnail'
    
    def duracao_info(self, obj):
        """Placeholder para duração do vídeo"""
        return mark_safe('<span style="color: #666; font-size: 12px;">🔜 Em breve</span>')
    duracao_info.short_description = '⏱️ Duração'
    
    def dias_desde_publicacao(self, obj):
        """Mostra há quantos dias foi publicado"""
        dias = (timezone.now() - obj.data_publicacao).days
        if dias == 0:
            texto = '🆕 Hoje'
            color = '#FF0000'
        elif dias == 1:
            texto = 'Ontem'
            color = '#FF5722'
        elif dias <= 7:
            texto = f'{dias} dias'
            color = '#FF9800'
        else:
            texto = f'{dias} dias'
            color = '#999'
        return format_html(
            '<span style="color: {}; font-size: 12px;">{}</span>',
            color, texto
        )
    dias_desde_publicacao.short_description = '📅 Publicado'
    dias_desde_publicacao.admin_order_field = 'data_publicacao'
    
    def preview_video(self, obj):
        """Preview do vídeo embutido"""
        if obj.youtube_id:
            return format_html(
                '<div style="margin: 15px 0; background: #f5f5f5; padding: 20px; border-radius: 8px;">'
                '<iframe width="100%" height="400" '
                'src="https://www.youtube.com/embed/{}" '
                'frameborder="0" allowfullscreen '
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                'style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"></iframe>'
                '<div style="margin-top: 15px; display: flex; gap: 10px;">'
                '<a href="{}" target="_blank" '
                'style="background: #FF0000; color: white; padding: 10px 20px; '
                'text-decoration: none; border-radius: 6px; font-weight: 600; flex: 1; text-align: center;">'
                '▶️ Abrir no YouTube</a>'
                '<a href="https://img.youtube.com/vi/{}/maxresdefault.jpg" target="_blank" '
                'style="background: #00E5CC; color: #0a0a0a; padding: 10px 20px; '
                'text-decoration: none; border-radius: 6px; font-weight: 600; flex: 1; text-align: center;">'
                '🖼️ Ver Thumbnail</a>'
                '</div>'
                '</div>',
                obj.youtube_id, obj.get_youtube_url(), obj.youtube_id
            )
        return mark_safe(
            '<div style="padding: 20px; background: #fff3cd; border: 2px dashed #ffc107; '
            'border-radius: 8px; text-align: center;">'
            '<p style="color: #856404; font-size: 14px; margin: 0;">'
            '⚠️ Adicione um ID de vídeo válido para ver o preview</p>'
            '</div>'
        )
    preview_video.short_description = 'Preview do Vídeo'
    
    def video_stats(self, obj):
        """Estatísticas do vídeo"""
        if obj.descricao:
            palavras = len(obj.descricao.split())
            caracteres = len(obj.descricao)
            
            return format_html(
                '<div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">'
                '<p><strong>📊 Estatísticas:</strong></p>'
                '<ul style="margin: 10px 0; padding-left: 20px;">'
                '<li>📝 <strong>{}</strong> palavras na descrição</li>'
                '<li>🔤 <strong>{}</strong> caracteres</li>'
                '<li>🔗 URL: <code style="background: #e0e0e0; padding: 2px 6px; border-radius: 3px;">{}</code></li>'
                '</ul>'
                '</div>',
                palavras, caracteres, obj.get_youtube_url()
            )
        return 'Nenhuma descrição ainda'
    video_stats.short_description = 'Estatísticas'
    
    def acoes(self, obj):
        """Ações rápidas"""
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a href="{}" target="_blank" '
            'style="background: #FF0000; color: white; padding: 6px 12px; '
            'text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600; '
            'display: inline-block;">▶️ YouTube</a>'
            '<a href="/videos/" target="_blank" '
            'style="background: #00E5CC; color: #0a0a0a; padding: 6px 12px; '
            'text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600; '
            'display: inline-block;">👁️ Ver</a>'
            '</div>',
            obj.get_youtube_url()
        )
    acoes.short_description = '⚡ Ações'
    
    def agendar_para_hoje(self, request, queryset):
        """Agenda vídeos para hoje"""
        count = queryset.update(data_publicacao=timezone.now())
        self.message_user(
            request,
            f'📅 {count} vídeo(s) agendado(s) para hoje!',
            messages.SUCCESS
        )
    agendar_para_hoje.short_description = '📅 Agendar para hoje'


# Customizar página inicial do admin
class MesaSecretaAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        """Override para adicionar estatísticas completas na página inicial"""
        extra_context = extra_context or {}
        
        # Estatísticas gerais
        total_postagens = Postagem.objects.count()
        postagens_publicadas = Postagem.objects.filter(status='publicado').count()
        postagens_rascunho = Postagem.objects.filter(status='rascunho').count()
        total_videos = Video.objects.count()
        
        # Postagens por período
        postagens_semana = Postagem.objects.filter(
            data_publicacao__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        postagens_mes = Postagem.objects.filter(
            data_publicacao__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        # Postagens por categoria
        postagens_novidades = Postagem.objects.filter(categoria='novidades').count()
        postagens_dicas = Postagem.objects.filter(categoria='dicas').count()
        postagens_reviews = Postagem.objects.filter(categoria='reviews').count()
        
        # Média de postagens por semana (últimos 30 dias)
        media_postagens_semana = round(postagens_mes / 4.3, 1) if postagens_mes > 0 else 0
        
        # Taxa de publicação
        taxa_publicacao = round((postagens_publicadas / total_postagens * 100), 1) if total_postagens > 0 else 0
        
        # Última atividade
        ultima_postagem = Postagem.objects.order_by('-data_criacao').first()
        ultimo_video = Video.objects.order_by('-data_criacao').first()
        
        extra_context.update({
            'total_postagens': total_postagens,
            'postagens_publicadas': postagens_publicadas,
            'postagens_rascunho': postagens_rascunho,
            'total_videos': total_videos,
            'postagens_semana': postagens_semana,
            'postagens_mes': postagens_mes,
            'postagens_novidades': postagens_novidades,
            'postagens_dicas': postagens_dicas,
            'postagens_reviews': postagens_reviews,
            'media_postagens_semana': media_postagens_semana,
            'taxa_publicacao': taxa_publicacao,
            'ultima_postagem': ultima_postagem,
            'ultimo_video': ultimo_video,
        })
        
        return super().index(request, extra_context)


# Usar o AdminSite customizado
admin_site = MesaSecretaAdminSite(name='admin')

# Registrar os models no site customizado
admin_site.register(Postagem, PostagemAdmin)
admin_site.register(Video, VideoAdmin)


@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    """Admin para configurações editáveis do site"""
    
    fieldsets = (
        ('📊 Estatísticas da Home', {
            'fields': ('jogos_analisados', 'videos_por_mes', 'inscritos_canal_info', 'inscritos_canal', 'usar_inscritos_automatico'),
            'description': 'Números exibidos nas estatísticas da página inicial'
        }),
        ('📺 Integração YouTube', {
            'fields': ('youtube_api_key', 'youtube_channel_id'),
            'description': 'Configure para buscar inscritos automaticamente. <a href="https://console.cloud.google.com/apis/credentials" target="_blank">Obter API Key</a>',
            'classes': ('collapse',)
        }),
        ('🎯 Banner Promocional', {
            'fields': ('banner_preview', 'banner_promocional', 'banner_url', 'banner_ativo'),
            'description': '📐 <strong>Tamanho recomendado:</strong> 1200x250px para melhor visualização'
        }),
        ('✍️ Textos da Home', {
            'fields': ('hero_titulo', 'hero_descricao'),
            'description': 'Textos principais da página inicial'
        }),
        ('🌐 Redes Sociais', {
            'fields': ('youtube_url', 'instagram_url', 'tiktok_url', 'twitter_url', 'facebook_url'),
            'description': 'URLs das redes sociais (deixe em branco para ocultar)'
        }),
        ('ℹ️ Informações do Site', {
            'fields': ('sobre_texto', 'email_contato'),
            'description': 'Informações exibidas no footer do site'
        }),
        ('📜 Políticas e Termos', {
            'fields': ('politica_privacidade', 'politica_privacidade_atualizada', 'termos_uso', 'termos_uso_atualizado'),
            'description': 'Conteúdo das políticas exibidas nos popups. Aceita HTML básico.',
            'classes': ('collapse',)
        }),
        ('�🔍 SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'description': 'Otimização para mecanismos de busca',
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('inscritos_canal_info', 'banner_preview')
    
    def banner_preview(self, obj):
        """Exibe preview do banner atual"""
        if obj.banner_promocional:
            return mark_safe(
                f'<div style="margin: 10px 0;">'
                f'<img src="{obj.banner_promocional.url}" style="max-width: 100%; height: auto; max-height: 250px; border-radius: 12px; '
                f'box-shadow: 0 4px 12px rgba(0, 229, 204, 0.3); border: 2px solid rgba(0, 229, 204, 0.2);" />'
                f'<p style="color: #666; margin-top: 10px; font-size: 13px;">'
                f'✅ <strong>Banner ativo:</strong> {"Sim" if obj.banner_ativo else "Não"}</p>'
                f'</div>'
            )
        return mark_safe(
            '<div style="padding: 20px; background: rgba(255, 152, 0, 0.1); border-radius: 8px; border-left: 4px solid #FF9800;">'
            '<p style="color: #FF9800; font-size: 14px; margin: 0;">📸 Nenhum banner configurado</p>'
            '<small style="color: #999;">Será usado o banner padrão</small>'
            '</div>'
        )
    banner_preview.short_description = 'Preview do Banner'
    
    def inscritos_canal_info(self, obj):
        """Exibe informações sobre os inscritos do YouTube"""
        if obj.usar_inscritos_automatico and obj.youtube_api_key and obj.youtube_channel_id:
            inscritos = obj.get_inscritos_youtube()
            if inscritos is not None:
                return mark_safe(f'<div style="padding: 10px; background: rgba(76, 175, 80, 0.15); border-left: 4px solid #4CAF50; border-radius: 4px;">'
                                f'<strong>✅ Inscritos automáticos:</strong> {inscritos:,} inscritos<br>'
                                f'<small>Atualizado em tempo real da API do YouTube</small></div>')
            else:
                return mark_safe(f'<div style="padding: 10px; background: rgba(244, 67, 54, 0.15); border-left: 4px solid #f44336; border-radius: 4px;">'
                                f'<strong>❌ Erro ao buscar inscritos</strong><br>'
                                f'<small>Verifique a API Key e o Channel ID. Usando valor manual: {obj.inscritos_canal:,}</small></div>')
        elif obj.usar_inscritos_automatico:
            return mark_safe(f'<div style="padding: 10px; background: rgba(255, 152, 0, 0.15); border-left: 4px solid #FF9800; border-radius: 4px;">'
                            f'<strong>⚠️ Configuração incompleta</strong><br>'
                            f'<small>Configure a API Key e Channel ID abaixo para usar inscritos automáticos</small></div>')
        else:
            return mark_safe(f'<div style="padding: 10px; background: rgba(0, 229, 204, 0.15); border-left: 4px solid #00E5CC; border-radius: 4px;">'
                            f'<strong>📝 Modo manual ativo</strong><br>'
                            f'<small>Valor atual: {obj.inscritos_canal:,} inscritos</small></div>')
    
    inscritos_canal_info.short_description = 'Status dos Inscritos'
    
    def has_add_permission(self, request):
        # Permitir apenas uma instância
        return not ConfiguracaoSite.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar a configuração
        return False
    
    def changelist_view(self, request, extra_context=None):
        # Redirecionar para edição da única instância
        config = ConfiguracaoSite.get_config()
        return self.changeform_view(request, str(config.pk), '', extra_context)


@admin.register(EstatisticaVisualizacao)
class EstatisticaVisualizacaoAdmin(admin.ModelAdmin):
    """Admin para visualizar estatísticas de acesso"""
    
    list_display = ('tipo_conteudo', 'conteudo_titulo', 'metricas_badge', 'data_visualizacao', 'ip_address')
    list_filter = ('tipo_conteudo', 'data_visualizacao')
    search_fields = ('conteudo_titulo', 'ip_address', 'session_key')
    date_hierarchy = 'data_visualizacao'
    list_per_page = 50
    readonly_fields = ('tipo_conteudo', 'conteudo_id', 'conteudo_titulo', 
                      'session_key', 'ip_address', 'user_agent', 'data_visualizacao',
                      'tempo_visualizacao', 'scroll_profundidade', 'data_saida')
    
    def has_add_permission(self, request):
        """Desabilitar adição manual"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Apenas visualização"""
        return False
    
    def metricas_badge(self, obj):
        """Exibe métricas em formato badge"""
        minutos = obj.tempo_visualizacao // 60
        segundos = obj.tempo_visualizacao % 60
        tempo_texto = f'{minutos}m {segundos}s' if minutos > 0 else f'{segundos}s'
        
        return format_html(
            '<div style="font-size: 11px;">'
            '<span style="background: #00E5CC; color: #0a0a0a; padding: 3px 8px; '
            'border-radius: 4px; margin-right: 4px;">⏱️ {}</span>'
            '<span style="background: #FF6B35; color: #fff; padding: 3px 8px; '
            'border-radius: 4px;">📊 {}%</span>'
            '</div>',
            tempo_texto,
            obj.scroll_profundidade
        )
    metricas_badge.short_description = '📈 Métricas'
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('tipo_conteudo', 'conteudo_id', 'conteudo_titulo')
        }),
        ('Métricas de Engajamento', {
            'fields': ('tempo_visualizacao', 'scroll_profundidade', 'data_saida')
        }),
        ('Informações da Sessão', {
            'fields': ('session_key', 'ip_address', 'user_agent')
        }),
        ('Data e Hora', {
            'fields': ('data_visualizacao',)
        }),
    )


# Registrar no admin_site customizado também
admin_site.register(ConfiguracaoSite, ConfiguracaoSiteAdmin)

# Personalização completa do Admin
admin.site.site_header = 'Mesa Secreta'
admin.site.site_title = 'Mesa Secreta Admin'
admin.site.index_title = 'Bem-vindo ao Quartel General! 🎮'
admin.site.site_url = '/'  # Link para o site
admin.site.enable_nav_sidebar = True  # Sidebar moderna

admin_site.site_header = 'Mesa Secreta'
admin_site.site_title = 'Mesa Secreta Admin'
admin_site.index_title = 'Dashboard'
admin_site.site_url = '/'
admin_site.enable_nav_sidebar = True
