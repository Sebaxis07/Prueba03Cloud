from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.views import LoginView, LogoutView

# Importación de ratelimit para protección contra fuerza bruta
from ratelimit.decorators import RateLimitDecorator

from avisos.authentication import User
from .forms import RegistroForm, LoginForm, AvisoForm, ComentarioForm, BusquedaForm, DetalleAsaltoForm, PerfilUsuarioForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
import logging
import json

from .models import Aviso, Comentario, TipoAviso, PerfilUsuario

logger = logging.getLogger(__name__)
def is_admin(user):
    """Verificar si el usuario es administrador"""
    return user.is_staff or user.is_superuser


def get_client_ip(request):
    """Obtener IP del cliente de forma segura"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):
    """Vista principal del sistema"""
    total_avisos = Aviso.objects.filter(activo=True).count()
    avisos_urgentes = Aviso.objects.filter(
        activo=True,
        prioridad='urgente',
        status='activo'
    ).count()

    hace_24h = timezone.now() - timedelta(hours=24)
    avisos_recientes = Aviso.objects.filter(
        activo=True,
        fecha_creacion__gte=hace_24h
    ).order_by('-fecha_creacion')[:5]

    context = {
        'total_avisos': total_avisos,
        'avisos_urgentes': avisos_urgentes,
        'avisos_recientes': avisos_recientes,
    }

    return render(request, 'Home.html', context)

@RateLimitDecorator(calls=5, period=3600)  # 5 calls per hour
@csrf_protect
def registro(request):
    """Vista de registro de usuarios con validaciones de seguridad"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                login(request, user)

                messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.')

                logger.info(f"Registro exitoso: {user.username} desde IP: {get_client_ip(request)}")

                return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error en registro: {str(e)} - IP: {get_client_ip(request)}")
                messages.error(request, "Error al crear la cuenta. Intente nuevamente.")
                return render(request, 'register.html', {'form': form})
        else:
            logger.warning(f"Errores en formulario de registro: {form.errors}")

            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
    else:
        form = RegistroForm()

    return render(request, 'register.html', {'form': form})

@method_decorator(RateLimitDecorator(calls=10, period=600), name='dispatch')  # 10 calls per 10 minutes
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'Login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        logger.info(f"Login exitoso: {user.username} desde IP: {get_client_ip(self.request)}")

        username_input = form.cleaned_data.get('username')

        original_input = self.request.POST.get('username', '')
        if form.is_rut_format(original_input):
            messages.success(self.request, f'¡Bienvenido {user.first_name or user.username}! Sesión iniciada con RUT.')
        else:
            messages.success(self.request, f'¡Bienvenido {user.first_name or user.username}!')

        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.data.get('username', 'desconocido')
        logger.warning(f"Intento de login fallido: {username} desde IP: {get_client_ip(self.request)}")

        if settings.DEBUG:
            original_input = self.request.POST.get('username', '')
            if hasattr(form, 'is_rut_format') and form.is_rut_format(original_input):
                logger.debug(f"RUT detectado: {original_input}")
                rut_clean = form.clean_rut(original_input)
                try:
                    perfil = PerfilUsuario.objects.get(rut__icontains=rut_clean)
                    logger.debug(f"RUT encontrado en BD para usuario: {perfil.usuario.username}")
                except PerfilUsuario.DoesNotExist:
                    logger.debug(f"RUT no encontrado en BD: {rut_clean}")

        original_input = self.request.POST.get('username', '')
        if hasattr(form, 'is_rut_format') and form.is_rut_format(original_input):
            messages.error(self.request, 'RUT o contraseña incorrectos. Verifica tus datos e intenta nuevamente.')
        else:
            messages.error(self.request, 'Usuario o contraseña incorrectos. Verifica tus datos e intenta nuevamente.')

        return super().form_invalid(form)

    def get_success_url(self):
        """Personalizar URL de redirección tras login exitoso"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('dashboard')

@login_required
def dashboard(request):
    """Dashboard principal para usuarios autenticados"""
    user = request.user

    mis_avisos = Aviso.objects.filter(usuario=user, activo=True).order_by('-fecha_creacion')[:5]

    avisos_por_tipo = TipoAviso.objects.annotate(
        total=Count('avisos', filter=Q(avisos__activo=True, avisos__status='activo'))
    ).filter(activo=True)

    perfil = getattr(user, 'perfilusuario', None)
    avisos_mi_sector = []
    if perfil and perfil.sector:
        avisos_mi_sector = Aviso.objects.filter(
            activo=True,
            status='activo',
            prioridad__in=['alta', 'urgente'],
            sector__icontains=perfil.sector
        ).order_by('-fecha_creacion')[:3]

    context = {
        'mis_avisos': mis_avisos,
        'avisos_por_tipo': avisos_por_tipo,
        'avisos_mi_sector': avisos_mi_sector,
    }

    return render(request, 'avisodash.html', context)

class AvisoListView(ListView):
    model = Aviso
    template_name = 'listavisos.html'
    context_object_name = 'avisos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Aviso.objects.filter(activo=True).select_related('tipo', 'usuario')

        form = BusquedaForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            tipo = form.cleaned_data.get('tipo')
            prioridad = form.cleaned_data.get('prioridad')
            status = form.cleaned_data.get('status')

            if q:
                queryset = queryset.filter(
                    Q(titulo__icontains=q) |
                    Q(descripcion__icontains=q) |
                    Q(direccion__icontains=q) |
                    Q(sector__icontains=q)
                )

            if tipo:
                queryset = queryset.filter(tipo=tipo)

            if prioridad:
                queryset = queryset.filter(prioridad=prioridad)

            if status:
                queryset = queryset.filter(status=status)

        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BusquedaForm(self.request.GET)
        return context

class AvisoDetailView(DetailView):
    model = Aviso
    template_name = 'detalleaviso.html'
    context_object_name = 'aviso'

    def get_queryset(self):
        return Aviso.objects.filter(activo=True).select_related('tipo', 'usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comentarios'] = self.object.comentarios.filter(activo=True).select_related('usuario')
        if self.request.user.is_authenticated:
            context['comentario_form'] = ComentarioForm()
        return context

# Crear aviso
@method_decorator([login_required, csrf_protect], name='dispatch')
class AvisoCreateView(CreateView):
    model = Aviso
    form_class = AvisoForm
    template_name = 'crearavi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalle_asalto_form'] = DetalleAsaltoForm(self.request.POST)
        else:
            context['detalle_asalto_form'] = DetalleAsaltoForm()
        return context

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.ip_creacion = get_client_ip(self.request)

        logger.info(f"Aviso creado por {self.request.user.username}: {form.instance.titulo}")

        response = super().form_valid(form)

        if form.cleaned_data['tipo'].nombre == 'asalto':
            detalle_form = DetalleAsaltoForm(self.request.POST)
            if detalle_form.is_valid():
                detalle = detalle_form.save(commit=False)
                detalle.aviso = self.object
                detalle.save()

        messages.success(self.request, 'Aviso creado exitosamente!')
        return response

@method_decorator([login_required, csrf_protect], name='dispatch')
class AvisoUpdateView(UserPassesTestMixin, UpdateView):
    model = Aviso
    form_class = AvisoForm
    template_name = 'editaravisos.html'

    def test_func(self):
        aviso = self.get_object()
        return self.request.user == aviso.usuario or self.request.user.is_staff

    def form_valid(self, form):
        logger.info(f"Aviso editado por {self.request.user.username}: {form.instance.titulo}")
        messages.success(self.request, 'Aviso actualizado exitosamente!')
        return super().form_valid(form)

@login_required
@require_POST
@csrf_protect
def agregar_comentario(request, aviso_id):
    """Vista para agregar comentarios via AJAX"""
    try:
        aviso = get_object_or_404(Aviso, id=aviso_id, activo=True)
        form = ComentarioForm(request.POST)

        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.aviso = aviso
            comentario.usuario = request.user
            comentario.ip_creacion = get_client_ip(request)
            comentario.save()

            logger.info(f"Comentario agregado por {request.user.username} en aviso {aviso.id}")

            foto_perfil_url = None
            try:
                if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.foto_perfil:
                    foto_perfil_url = request.user.perfilusuario.foto_perfil.url
            except:
                pass  # Si no tiene perfil o foto, quedará como None

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'mensaje': 'Comentario agregado exitosamente',
                    'comentario': {
                        'usuario': comentario.usuario.get_full_name() or comentario.usuario.username,
                        'contenido': comentario.contenido,
                        'fecha': comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                        'foto_perfil': foto_perfil_url
                    }
                })
            else:
                messages.success(request, 'Comentario agregado exitosamente!')
                return redirect('aviso_detalle', pk=aviso.id)

        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errores': form.errors
                })
            else:
                messages.error(request, 'Error al agregar comentario.')
                return redirect('aviso_detalle', pk=aviso.id)

    except Exception as e:
        logger.error(f"Error al agregar comentario: {str(e)} - Usuario: {request.user.username}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'mensaje': 'Error interno del servidor'
            })
        else:
            messages.error(request, 'Error al agregar comentario.')
            return redirect('aviso_detalle', pk=aviso_id)
@login_required
def mis_avisos(request):
    """Vista para mostrar los avisos del usuario actual"""
    avisos = Aviso.objects.filter(
        usuario=request.user,
        activo=True
    ).order_by('-fecha_creacion')

    paginator = Paginator(avisos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_avisos = avisos.count()
    avisos_activos = avisos.filter(status='activo').count()
    avisos_resueltos = avisos.filter(status='resuelto').count()
    avisos_en_proceso = avisos.filter(status='en_proceso').count()

    context = {
        'avisos': page_obj,
        'total_avisos': total_avisos,
        'avisos_activos': avisos_activos,
        'avisos_resueltos': avisos_resueltos,
        'avisos_en_proceso': avisos_en_proceso,
    }

    return render(request, 'misavisos.html', context)

@login_required
@csrf_protect
def perfil_usuario(request):
    """Vista para mostrar y editar el perfil del usuario"""
    perfil, created = PerfilUsuario.objects.get_or_create(
        usuario=request.user,
        defaults={
            'telefono': '',
            'sector': '',
        }
    )

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            try:
                perfil = form.save()

                logger.info(f"Perfil actualizado por {request.user.username}")

                messages.success(request, '¡Perfil actualizado exitosamente!')
                return redirect('perfil_usuario')

            except Exception as e:
                logger.error(f"Error al actualizar perfil: {str(e)} - Usuario: {request.user.username}")
                messages.error(request, "Error al actualizar el perfil. Intente nuevamente.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_label = form[field].label if field in form.fields else field
                        messages.error(request, f"{field_label}: {error}")
    else:
        form = PerfilUsuarioForm(instance=perfil)

    context = {
        'form': form,
        'perfil': perfil,
    }

    return render(request, 'perfil.html', context)

@login_required
@require_POST
def eliminar_foto_perfil(request):
    """Vista para eliminar la foto de perfil via AJAX"""
    try:
        perfil, created = PerfilUsuario.objects.get_or_create(
            usuario=request.user,
            defaults={
                'telefono': '',
                'sector': '',
            }
        )

        if perfil.foto_perfil:
            perfil.foto_perfil.delete()
            perfil.save()

            logger.info(f"Foto de perfil eliminada por {request.user.username}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'mensaje': 'Foto de perfil eliminada exitosamente'
                })
            else:
                messages.success(request, 'Foto de perfil eliminada exitosamente.')
                return redirect('perfil_usuario')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'mensaje': 'No hay foto de perfil para eliminar'
                })
            else:
                messages.warning(request, 'No hay foto de perfil para eliminar.')
                return redirect('perfil_usuario')

    except Exception as e:
        logger.error(f"Error al eliminar foto de perfil: {str(e)} - Usuario: {request.user.username}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'mensaje': 'Error interno del servidor'
            }, status=500)
        else:
            messages.error(request, 'Error al eliminar la foto de perfil.')
            return redirect('perfil_usuario')

@require_http_methods(["GET"])
def api_tipos_aviso(request):
    """API para obtener tipos de aviso activos"""
    tipos = TipoAviso.objects.filter(activo=True).values('id', 'nombre')
    tipos_con_display = []
    for tipo in tipos:
        tipos_con_display.append({
            'id': tipo['id'],
            'nombre': tipo['nombre'],
            'display_name': dict(TipoAviso.TIPOS_CHOICES)[tipo['nombre']]
        })

    return JsonResponse({'tipos': tipos_con_display})

@login_required
@require_POST
def eliminar_aviso(request, aviso_id):
    """Vista para eliminar (desactivar) un aviso"""
    try:
        aviso = get_object_or_404(Aviso, id=aviso_id, activo=True)

        if request.user != aviso.usuario and not request.user.is_staff:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'mensaje': 'No tienes permisos para eliminar este aviso'
                }, status=403)
            else:
                messages.error(request, 'No tienes permisos para eliminar este aviso.')
                return redirect('aviso_detalle', pk=aviso_id)

        aviso.activo = False
        aviso.save()

        logger.info(f"Aviso eliminado por {request.user.username}: {aviso.titulo} (ID: {aviso.id})")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'mensaje': 'Aviso eliminado exitosamente'
            })
        else:
            messages.success(request, 'Aviso eliminado exitosamente.')
            return redirect('mis_avisos')

    except Exception as e:
        logger.error(f"Error al eliminar aviso: {str(e)} - Usuario: {request.user.username}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'mensaje': 'Error interno del servidor'
            }, status=500)
        else:
            messages.error(request, 'Error al eliminar el aviso.')
            return redirect('aviso_detalle', pk=aviso_id)

@login_required
@require_POST
def cambiar_estado_aviso(request, aviso_id):
    """Vista para cambiar el estado de un aviso"""
    try:
        aviso = get_object_or_404(Aviso, id=aviso_id, activo=True)

        if request.user != aviso.usuario and not request.user.is_staff:
            data = json.loads(request.body) if request.body else {}
            nuevo_estado = data.get('estado') or request.POST.get('estado')

            if nuevo_estado != 'resuelto':
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'mensaje': 'Solo puedes marcar avisos como resueltos'
                    }, status=403)
                else:
                    messages.error(request, 'Solo puedes marcar avisos como resueltos.')
                    return redirect('aviso_detalle', pk=aviso_id)

        if request.content_type == 'application/json':
            data = json.loads(request.body)
            nuevo_estado = data.get('estado')
        else:
            nuevo_estado = request.POST.get('estado')

        estados_validos = [choice[0] for choice in Aviso.STATUS_CHOICES]
        if nuevo_estado not in estados_validos:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'mensaje': 'Estado no válido'
                }, status=400)
            else:
                messages.error(request, 'Estado no válido.')
                return redirect('aviso_detalle', pk=aviso_id)

        estado_anterior = aviso.status

        aviso.status = nuevo_estado
        aviso.save()

        logger.info(f"Estado de aviso cambiado por {request.user.username}: {aviso.titulo} (ID: {aviso.id}) de '{estado_anterior}' a '{nuevo_estado}'")

        estado_display = dict(Aviso.STATUS_CHOICES)[nuevo_estado]

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'mensaje': f'Estado cambiado a {estado_display}',
                'nuevo_estado': nuevo_estado,
                'estado_display': estado_display
            })
        else:
            messages.success(request, f'Estado del aviso cambiado a {estado_display}.')
            return redirect('aviso_detalle', pk=aviso_id)

    except Exception as e:
        logger.error(f"Error al cambiar estado: {str(e)} - Usuario: {request.user.username}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'mensaje': 'Error al cambiar el estado'
            }, status=500)
        else:
            messages.error(request, 'Error al cambiar el estado.')
            return redirect('aviso_detalle', pk=aviso_id)

@login_required
@require_POST
def restaurar_aviso(request, aviso_id):
    """Vista para restaurar un aviso eliminado (solo admins)"""
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'mensaje': 'No tienes permisos para esta acción'
            }, status=403)
        else:
            messages.error(request, 'No tienes permisos para esta acción.')
            return redirect('home')

    try:
        aviso = get_object_or_404(Aviso, id=aviso_id, activo=False)

        aviso.activo = True
        aviso.save()

        logger.info(f"Aviso restaurado por admin {request.user.username}: {aviso.titulo} (ID: {aviso.id})")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'mensaje': 'Aviso restaurado exitosamente'
            })
        else:
            messages.success(request, 'Aviso restaurado exitosamente.')
            return redirect('aviso_detalle', pk=aviso_id)

    except Exception as e:
        logger.error(f"Error al restaurar aviso: {str(e)} - Usuario: {request.user.username}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'mensaje': 'Error interno del servidor'
            }, status=500)
        else:
            messages.error(request, 'Error al restaurar el aviso.')
            return redirect('home')

@login_required
def mis_avisos_estadisticas(request):
    """Vista para obtener estadísticas de los avisos del usuario"""
    try:
        avisos = Aviso.objects.filter(usuario=request.user, activo=True)

        estadisticas = {
            'total': avisos.count(),
            'activos': avisos.filter(status='activo').count(),
            'resueltos': avisos.filter(status='resuelto').count(),
            'en_proceso': avisos.filter(status='en_proceso').count(),
            'por_prioridad': {
                'baja': avisos.filter(prioridad='baja').count(),
                'media': avisos.filter(prioridad='media').count(),
                'alta': avisos.filter(prioridad='alta').count(),
                'urgente': avisos.filter(prioridad='urgente').count(),
            }
        }

        return JsonResponse({
            'success': True,
            'estadisticas': estadisticas
        })

    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)} - Usuario: {request.user.username}")
        return JsonResponse({
            'success': False,
            'mensaje': 'Error al obtener estadísticas'
        }, status=500)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard principal del admin"""
    total_usuarios = User.objects.count()
    total_avisos = Aviso.objects.filter(activo=True).count()
    total_comentarios = Comentario.objects.filter(activo=True).count()

    hace_24h = timezone.now() - timedelta(hours=24)
    hace_7d = timezone.now() - timedelta(days=7)
    hace_30d = timezone.now() - timedelta(days=30)

    nuevos_usuarios_24h = User.objects.filter(date_joined__gte=hace_24h).count()
    nuevos_avisos_24h = Aviso.objects.filter(fecha_creacion__gte=hace_24h, activo=True).count()
    nuevos_avisos_7d = Aviso.objects.filter(fecha_creacion__gte=hace_7d, activo=True).count()

    avisos_activos = Aviso.objects.filter(status='activo', activo=True).count()
    avisos_proceso = Aviso.objects.filter(status='en_proceso', activo=True).count()
    avisos_resueltos = Aviso.objects.filter(status='resuelto', activo=True).count()

    avisos_urgentes = Aviso.objects.filter(prioridad='urgente', activo=True).count()
    avisos_alta = Aviso.objects.filter(prioridad='alta', activo=True).count()

    avisos_recientes = Aviso.objects.filter(activo=True).order_by('-fecha_creacion')[:10]

    usuarios_recientes = User.objects.order_by('-date_joined')[:10]

    comentarios_recientes = Comentario.objects.filter(activo=True).order_by('-fecha_creacion')[:10]

    avisos_por_tipo = TipoAviso.objects.annotate(
        total=Count('avisos', filter=Q(avisos__activo=True))
    ).order_by('-total')

    context = {
        'total_usuarios': total_usuarios,
        'total_avisos': total_avisos,
        'total_comentarios': total_comentarios,

        'nuevos_usuarios_24h': nuevos_usuarios_24h,
        'nuevos_avisos_24h': nuevos_avisos_24h,
        'nuevos_avisos_7d': nuevos_avisos_7d,

        'avisos_activos': avisos_activos,
        'avisos_proceso': avisos_proceso,
        'avisos_resueltos': avisos_resueltos,

        'avisos_urgentes': avisos_urgentes,
        'avisos_alta': avisos_alta,

        'avisos_recientes': avisos_recientes,
        'usuarios_recientes': usuarios_recientes,
        'comentarios_recientes': comentarios_recientes,

        'avisos_por_tipo': avisos_por_tipo,
    }

    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_avisos_list(request):
    """Lista de avisos en admin"""
    avisos = Aviso.objects.select_related('usuario', 'tipo').order_by('-fecha_creacion')

    status = request.GET.get('status')
    prioridad = request.GET.get('prioridad')
    tipo = request.GET.get('tipo')
    search = request.GET.get('search')
    activo = request.GET.get('activo')

    if status:
        avisos = avisos.filter(status=status)
    if prioridad:
        avisos = avisos.filter(prioridad=prioridad)
    if tipo:
        avisos = avisos.filter(tipo_id=tipo)
    if search:
        avisos = avisos.filter(
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(usuario__username__icontains=search)
        )
    if activo is not None:
        avisos = avisos.filter(activo=activo == 'true')

    paginator = Paginator(avisos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'avisos': page_obj,
        'tipos': TipoAviso.objects.filter(activo=True),
        'current_filters': {
            'status': status,
            'prioridad': prioridad,
            'tipo': tipo,
            'search': search,
            'activo': activo,
        }
    }

    return render(request, 'admin/avisos_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_usuarios_list(request):
    """Lista de usuarios en admin"""
    usuarios = User.objects.select_related('perfilusuario').order_by('-date_joined')

    search = request.GET.get('search')
    is_active = request.GET.get('is_active')
    is_staff = request.GET.get('is_staff')

    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    if is_active is not None:
        usuarios = usuarios.filter(is_active=is_active == 'true')
    if is_staff is not None:
        usuarios = usuarios.filter(is_staff=is_staff == 'true')

    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'usuarios': page_obj,
        'current_filters': {
            'search': search,
            'is_active': is_active,
            'is_staff': is_staff,
        }
    }

    return render(request, 'admin/usuarios_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_comentarios_list(request):
    """Lista de comentarios en admin"""
    comentarios = Comentario.objects.select_related('usuario', 'aviso').order_by('-fecha_creacion')

    search = request.GET.get('search')
    activo = request.GET.get('activo')

    if search:
        comentarios = comentarios.filter(
            Q(contenido__icontains=search) |
            Q(usuario__username__icontains=search) |
            Q(aviso__titulo__icontains=search)
        )
    if activo is not None:
        comentarios = comentarios.filter(activo=activo == 'true')

    paginator = Paginator(comentarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'comentarios': page_obj,
        'current_filters': {
            'search': search,
            'activo': activo,
        }
    }

    return render(request, 'admin/comentarios_list.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_toggle_aviso(request, aviso_id):
    """Activar/desactivar aviso"""
    aviso = get_object_or_404(Aviso, id=aviso_id)
    aviso.activo = not aviso.activo
    aviso.save()

    return JsonResponse({
        'success': True,
        'nuevo_estado': aviso.activo,
        'mensaje': f'Aviso {"activado" if aviso.activo else "desactivado"}'
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_toggle_usuario(request, user_id):
    """Activar/desactivar usuario"""
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = not usuario.is_active
    usuario.save()

    return JsonResponse({
        'success': True,
        'nuevo_estado': usuario.is_active,
        'mensaje': f'Usuario {"activado" if usuario.is_active else "desactivado"}'
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_toggle_comentario(request, comentario_id):
    """Activar/desactivar comentario"""
    comentario = get_object_or_404(Comentario, id=comentario_id)
    comentario.activo = not comentario.activo
    comentario.save()

    return JsonResponse({
        'success': True,
        'nuevo_estado': comentario.activo,
        'mensaje': f'Comentario {"activado" if comentario.activo else "desactivado"}'
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_verificar_usuario(request, user_id):
    """Verificar/desverificar usuario"""
    usuario = get_object_or_404(User, id=user_id)
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
    perfil.verificado = not perfil.verificado
    perfil.save()

    return JsonResponse({
        'success': True,
        'nuevo_estado': perfil.verificado,
        'mensaje': f'Usuario {"verificado" if perfil.verificado else "no verificado"}'
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_cambiar_estado_aviso(request, aviso_id):
    """Cambiar estado de aviso"""
    aviso = get_object_or_404(Aviso, id=aviso_id)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado in dict(Aviso.STATUS_CHOICES):
        aviso.status = nuevo_estado
        aviso.save()

        return JsonResponse({
            'success': True,
            'nuevo_estado': nuevo_estado,
            'mensaje': f'Estado cambiado a {aviso.get_status_display()}'
        })

    return JsonResponse({
        'success': False,
        'mensaje': 'Estado no válido'
    })

@login_required
@user_passes_test(is_admin)
def admin_estadisticas(request):
    """Vista de estadísticas avanzadas con datos reales"""

    avisos_por_mes = []
    usuarios_por_mes = []

    for i in range(12):
        fecha_inicio = timezone.now().replace(day=1) - timedelta(days=30*i)
        fecha_fin = fecha_inicio + timedelta(days=31)

        avisos_mes = Aviso.objects.filter(
            fecha_creacion__gte=fecha_inicio,
            fecha_creacion__lt=fecha_fin,
            activo=True
        ).count()

        usuarios_mes = User.objects.filter(
            date_joined__gte=fecha_inicio,
            date_joined__lt=fecha_fin
        ).count()

        avisos_por_mes.append({
            'mes': fecha_inicio.strftime('%B %Y'),
            'count': avisos_mes
        })

        usuarios_por_mes.append({
            'mes': fecha_inicio.strftime('%B %Y'),
            'count': usuarios_mes
        })

    estados_avisos = {
        'activos': Aviso.objects.filter(status='activo', activo=True).count(),
        'en_proceso': Aviso.objects.filter(status='en_proceso', activo=True).count(),
        'resueltos': Aviso.objects.filter(status='resuelto', activo=True).count(),
    }

    prioridades_avisos = {
        'urgente': Aviso.objects.filter(prioridad='urgente', activo=True).count(),
        'alta': Aviso.objects.filter(prioridad='alta', activo=True).count(),
        'media': Aviso.objects.filter(prioridad='media', activo=True).count(),
        'baja': Aviso.objects.filter(prioridad='baja', activo=True).count(),
    }

    tipos_avisos = TipoAviso.objects.filter(activo=True).annotate(
        total=Count('avisos', filter=Q(avisos__activo=True))
    ).values('nombre', 'total').order_by('-total')

    actividad_por_hora = []
    for hora in range(24):
        count = Aviso.objects.filter(
            fecha_creacion__hour=hora,
            activo=True
        ).count()
        actividad_por_hora.append(count)

    top_usuarios = User.objects.annotate(
        total_avisos=Count('aviso', filter=Q(aviso__activo=True)),
        total_comentarios=Count('comentario', filter=Q(comentario__activo=True)),
        total_actividad=Count('aviso', filter=Q(aviso__activo=True)) + Count('comentario', filter=Q(comentario__activo=True))
    ).filter(total_actividad__gt=0).order_by('-total_actividad')[:10]

    total_avisos = Aviso.objects.filter(activo=True).count()
    total_usuarios = User.objects.count()
    total_comentarios = Comentario.objects.filter(activo=True).count()

    hace_30_dias = timezone.now() - timedelta(days=30)
    avisos_recientes = Aviso.objects.filter(
        fecha_creacion__gte=hace_30_dias,
        activo=True
    ).count()
    usuarios_recientes = User.objects.filter(
        date_joined__gte=hace_30_dias
    ).count()
    comentarios_recientes = Comentario.objects.filter(
        fecha_creacion__gte=hace_30_dias,
        activo=True
    ).count()

    context = {
        'avisos_por_mes': list(reversed(avisos_por_mes)),
        'usuarios_por_mes': list(reversed(usuarios_por_mes)),
        'estados_avisos': estados_avisos,
        'prioridades_avisos': prioridades_avisos,
        'tipos_avisos': list(tipos_avisos),
        'actividad_por_hora': actividad_por_hora,
        'top_usuarios': top_usuarios,
        'total_avisos': total_avisos,
        'total_usuarios': total_usuarios,
        'total_comentarios': total_comentarios,
        'avisos_recientes': avisos_recientes,
        'usuarios_recientes': usuarios_recientes,
        'comentarios_recientes': comentarios_recientes,
    }

    return render(request, 'admin/estadisticas.html', context)