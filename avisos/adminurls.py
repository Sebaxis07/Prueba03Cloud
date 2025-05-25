# avisos/admin_urls.py
from django.urls import path
from . import views  # Usamos las vistas que ya tienes en views.py

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Listas
    path('avisos/', views.admin_avisos_list, name='admin_avisos_list'),
    path('usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('comentarios/', views.admin_comentarios_list, name='admin_comentarios_list'),
    path('estadisticas/', views.admin_estadisticas, name='admin_estadisticas'),
    
    # Acciones AJAX
    path('avisos/<int:aviso_id>/toggle/', views.admin_toggle_aviso, name='admin_toggle_aviso'),
    path('usuarios/<int:user_id>/toggle/', views.admin_toggle_usuario, name='admin_toggle_usuario'),
    path('comentarios/<int:comentario_id>/toggle/', views.admin_toggle_comentario, name='admin_toggle_comentario'),
    path('usuarios/<int:user_id>/verificar/', views.admin_verificar_usuario, name='admin_verificar_usuario'),
    path('avisos/<int:aviso_id>/estado/', views.admin_cambiar_estado_aviso, name='admin_cambiar_estado_aviso'),
]