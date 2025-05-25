# avisos/urls.py - URLs completas actualizadas
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/eliminar-foto/', views.eliminar_foto_perfil, name='eliminar_foto_perfil'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Avisos CRUD
    path('avisos/', views.AvisoListView.as_view(), name='lista_avisos'),
    path('aviso/<int:pk>/', views.AvisoDetailView.as_view(), name='aviso_detalle'),
    path('aviso/crear/', views.AvisoCreateView.as_view(), name='crear_aviso'),
    path('aviso/<int:pk>/editar/', views.AvisoUpdateView.as_view(), name='editar_aviso'),
    path('mis-avisos/', views.mis_avisos, name='mis_avisos'),
    path('aviso/<int:aviso_id>/eliminar/', views.eliminar_aviso, name='eliminar_aviso'),
    path('aviso/<int:aviso_id>/cambiar-estado/', views.cambiar_estado_aviso, name='cambiar_estado_aviso'),
    path('aviso/<int:aviso_id>/restaurar/', views.restaurar_aviso, name='restaurar_aviso'),
    
    # Comentarios
    path('aviso/<int:aviso_id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    
    # API endpoints
    path('api/tipos-aviso/', views.api_tipos_aviso, name='api_tipos_aviso'),
    path('api/mis-avisos-estadisticas/', views.mis_avisos_estadisticas, name='mis_avisos_estadisticas'),
]