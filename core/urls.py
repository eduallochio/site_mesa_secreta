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
]
