from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Postagem, Video, ConfiguracaoSite


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

    def get_queryset(self):
        return Video.objects.order_by('-data_publicacao')
