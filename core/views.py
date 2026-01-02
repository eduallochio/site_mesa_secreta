from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import Postagem, Video, ConfiguracaoSite, EstatisticaVisualizacao


def home(request):
    """View da página inicial"""
    postagens_destaque = Postagem.objects.filter(status='publicado').order_by('-data_publicacao')[:6]
    videos_recentes = Video.objects.order_by('-data_publicacao')[:3]
    config = ConfiguracaoSite.get_config()
    
    context = {
        'postagens_destaque': postagens_destaque,
        'videos_recentes': videos_recentes,
        'config': config,
    }
    return render(request, 'core/home.html', context)


class PostagemListView(ListView):
    """View para listar todas as postagens publicadas"""
    model = Postagem
    template_name = 'core/postagem_list.html'
    context_object_name = 'postagens'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Postagem.objects.filter(status='publicado').order_by('-data_publicacao')
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        return context


class PostagemDetailView(DetailView):
    """View para exibir uma postagem específica"""
    model = Postagem
    template_name = 'core/postagem_detail.html'
    context_object_name = 'postagem'
    
    def get_queryset(self):
        return Postagem.objects.filter(status='publicado')


class VideoListView(ListView):
    """View para listar todos os vídeos"""
    model = Video
    template_name = 'core/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        return Video.objects.order_by('-data_publicacao')


def login_view(request):
    """View moderna de login"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """View de logout"""
    logout(request)
    return redirect('core:home')


@require_http_methods(["POST"])
def track_view(request):
    """API endpoint para registrar visualizações e métricas"""
    try:
        data = json.loads(request.body)
        
        # Obter ou criar session key
        if not request.session.session_key:
            request.session.create()
        
        # Obter IP do usuário
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Criar ou atualizar estatística
        tipo_conteudo = data.get('tipo_conteudo', 'home')
        conteudo_id = data.get('conteudo_id')
        
        # Buscar estatística existente ou criar nova
        stats, created = EstatisticaVisualizacao.objects.get_or_create(
            session_key=request.session.session_key,
            tipo_conteudo=tipo_conteudo,
            conteudo_id=conteudo_id,
            defaults={
                'conteudo_titulo': data.get('conteudo_titulo', ''),
                'ip_address': ip_address,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        
        # Atualizar métricas
        stats.tempo_visualizacao = data.get('tempo_visualizacao', 0)
        stats.scroll_profundidade = data.get('scroll_profundidade', 0)
        stats.data_saida = timezone.now()
        stats.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Estatística registrada com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


def get_postagem_stats(request, pk):
    """API endpoint para obter estatísticas de uma postagem (somente admin)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    postagem = get_object_or_404(Postagem, pk=pk)
    
    stats = {
        'total_visualizacoes': postagem.get_total_visualizacoes(),
        'tempo_medio': postagem.get_tempo_medio_visualizacao(),
        'scroll_medio': postagem.get_scroll_medio(),
        'visualizacoes_30_dias': postagem.get_visualizacoes_ultimos_30_dias(),
        'taxa_engajamento': postagem.get_taxa_engajamento(),
    }
    
    return JsonResponse(stats)
