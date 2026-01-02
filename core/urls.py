from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('postagens/', views.PostagemListView.as_view(), name='postagem_list'),
    path('postagens/<int:pk>/', views.PostagemDetailView.as_view(), name='postagem_detail'),
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # API de rastreamento
    path('api/track-view/', views.track_view, name='track_view'),
    path('api/postagem/<int:pk>/stats/', views.get_postagem_stats, name='postagem_stats'),
]
