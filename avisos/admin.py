from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TipoAviso, Aviso, Comentario, PerfilUsuario

class CustomAdminSite(admin.AdminSite):
    site_header = "Costa Laguna Segura - Administración"
    site_title = "Admin Costa Laguna"
    index_title = "Panel de Administración"

admin_site = CustomAdminSite(name='custom_admin')

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fields = ('rut', 'telefono', 'direccion', 'sector', 'notificaciones_email', 'verificado')

class UserAdmin(BaseUserAdmin):
    inlines = [PerfilUsuarioInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'get_telefono')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    def get_telefono(self, obj):
        try:
            return obj.perfilusuario.telefono or '-'
        except PerfilUsuario.DoesNotExist:
            return '-'
    get_telefono.short_description = 'Teléfono'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(TipoAviso)
class TipoAvisoAdmin(admin.ModelAdmin):
    list_display = ('get_display_name_formatted', 'nombre', 'get_icono_preview', 'get_color_badge', 'activo', 'get_avisos_count')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('nombre',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'activo')
        }),
        ('Vista Previa', {
            'fields': ('get_preview_badge',),
            'description': 'Vista previa de cómo se verá el tipo de aviso'
        }),
    )
    
    readonly_fields = ('get_preview_badge',)
    
    def get_display_name_formatted(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.get_display_name(),
            obj.nombre
        )
    get_display_name_formatted.short_description = 'Tipo'
    
    def get_icono_preview(self, obj):
        return format_html(
            '<i data-lucide="{}" style="width: 20px; height: 20px;"></i>',
            obj.get_icono()
        )
    get_icono_preview.short_description = 'Icono'
    
    def get_color_badge(self, obj):
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {}">'
            '{}</span>',
            obj.get_color_classes(),
            obj.get_color().title()
        )
    get_color_badge.short_description = 'Color'
    
    def get_avisos_count(self, obj):
        count = obj.avisos.filter(activo=True).count()
        if count > 0:
            return format_html(
                '<span style="background-color: #3B82F6; color: white; padding: 2px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
                count
            )
        return '0'
    get_avisos_count.short_description = 'Avisos'
    
    def get_preview_badge(self, obj):
        return format_html(obj.get_badge_html())
    get_preview_badge.short_description = 'Vista Previa del Badge'

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    fields = ('usuario', 'contenido', 'fecha_creacion', 'activo')
    readonly_fields = ('fecha_creacion',)
    can_delete = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'get_tipo_badge', 'get_prioridad_badge', 'get_status_badge', 
        'usuario', 'sector', 'fecha_creacion', 'get_comentarios_count', 'activo'
    )
    list_filter = (
        'tipo', 'prioridad', 'status', 'activo', 'es_anonimo', 
        'verificado_por_admin', 'fecha_creacion'
    )
    search_fields = (
        'titulo', 'descripcion', 'direccion', 'sector', 
        'usuario__username', 'usuario__first_name', 'usuario__last_name'
    )
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    list_per_page = 25
    
    readonly_fields = (
        'fecha_creacion', 'fecha_actualizacion', 'ip_creacion', 
        'get_imagen_preview', 'get_user_info'
    )
    
    inlines = [ComentarioInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('titulo', 'descripcion', 'tipo', 'prioridad', 'status')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'sector')
        }),
        ('Contacto', {
            'fields': ('telefono_contacto',)
        }),
        ('Usuario y Configuración', {
            'fields': ('usuario', 'get_user_info', 'es_anonimo', 'verificado_por_admin', 'activo')
        }),
        ('Imagen', {
            'fields': ('imagen', 'get_imagen_preview'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'ip_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_resuelto', 'marcar_como_verificado', 'desactivar_avisos']
    
    def get_tipo_badge(self, obj):
        """Mostrar badge del tipo con icono y color"""
        if obj.tipo:
            return format_html(obj.tipo.get_badge_html())
        return format_html('<span class="text-gray-500">Sin tipo</span>')
    get_tipo_badge.short_description = 'Tipo'
    
    def get_prioridad_badge(self, obj):
        colors = {
            'baja': '#10B981',      
            'media': '#F59E0B',     
            'alta': '#F97316',      
            'urgente': '#EF4444'   
        }
        color = colors.get(obj.prioridad, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_prioridad_display()
        )
    get_prioridad_badge.short_description = 'Prioridad'
    
    def get_status_badge(self, obj):
        colors = {
            'activo': '#EF4444',        
            'en_proceso': '#F59E0B',    
            'resuelto': '#10B981'       
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    get_status_badge.short_description = 'Estado'
    
    def get_comentarios_count(self, obj):
        count = obj.comentarios.filter(activo=True).count()
        if count > 0:
            return format_html(
                '<span style="background-color: #3B82F6; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px;">{}</span>',
                count
            )
        return '0'
    get_comentarios_count.short_description = 'Comentarios'
    
    def get_imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover; border-radius: 8px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    get_imagen_preview.short_description = 'Vista previa'
    
    def get_user_info(self, obj):
        if obj.es_anonimo:
            return format_html(
                '<span style="color: #6B7280; font-style: italic;">Reporte anónimo</span>'
            )
        else:
            user_link = reverse('admin:auth_user_change', args=[obj.usuario.pk])
            return format_html(
                '<a href="{}" target="_blank">{}</a><br>'
                '<small style="color: #6B7280;">Email: {}</small>',
                user_link,
                obj.usuario.get_full_name() or obj.usuario.username,
                obj.usuario.email
            )
    get_user_info.short_description = 'Info del Usuario'
    
    def marcar_como_resuelto(self, request, queryset):
        updated = queryset.update(status='resuelto')
        self.message_user(request, f'{updated} avisos marcados como resueltos.')
    marcar_como_resuelto.short_description = "Marcar avisos seleccionados como resueltos"
    
    def marcar_como_verificado(self, request, queryset):
        updated = queryset.update(verificado_por_admin=True)
        self.message_user(request, f'{updated} avisos marcados como verificados.')
    marcar_como_verificado.short_description = "Marcar avisos como verificados"
    
    def desactivar_avisos(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} avisos desactivados.')
    desactivar_avisos.short_description = "Desactivar avisos seleccionados"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'tipo'
        ).prefetch_related('comentarios')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = (
        'get_aviso_title', 'usuario', 'get_contenido_preview', 
        'fecha_creacion', 'activo'
    )
    list_filter = ('activo', 'fecha_creacion')
    search_fields = (
        'contenido', 'aviso__titulo', 'usuario__username', 
        'usuario__first_name', 'usuario__last_name'
    )
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    list_per_page = 50
    
    readonly_fields = ('fecha_creacion', 'ip_creacion', 'get_aviso_link')
    
    fieldsets = (
        ('Comentario', {
            'fields': ('contenido', 'activo')
        }),
        ('Relaciones', {
            'fields': ('aviso', 'get_aviso_link', 'usuario')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'ip_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_aviso_title(self, obj):
        return obj.aviso.titulo[:50] + '...' if len(obj.aviso.titulo) > 50 else obj.aviso.titulo
    get_aviso_title.short_description = 'Aviso'
    
    def get_contenido_preview(self, obj):
        return obj.contenido[:100] + '...' if len(obj.contenido) > 100 else obj.contenido
    get_contenido_preview.short_description = 'Contenido'
    
    def get_aviso_link(self, obj):
        if obj.aviso:
            aviso_link = reverse('admin:avisos_aviso_change', args=[obj.aviso.pk])
            return format_html(
                '<a href="{}" target="_blank">Ver aviso completo</a>',
                aviso_link
            )
        return "Sin aviso"
    get_aviso_link.short_description = 'Enlace al Aviso'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'aviso')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_name', 'rut', 'telefono', 'sector', 'notificaciones_email', 
        'verificado', 'fecha_creacion'
    )
    list_filter = ('verificado', 'notificaciones_email', 'fecha_creacion')
    search_fields = (
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'rut', 'telefono', 'sector', 'direccion'
    )
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    
    readonly_fields = ('fecha_creacion', 'get_user_link')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'get_user_link', 'verificado')
        }),
        ('Información Personal', {
            'fields': ('rut',)
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'direccion', 'sector')
        }),
        ('Preferencias', {
            'fields': ('notificaciones_email',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_name(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    get_user_name.short_description = 'Usuario'
    
    def get_user_link(self, obj):
        if obj.usuario:
            user_link = reverse('admin:auth_user_change', args=[obj.usuario.pk])
            return format_html(
                '<a href="{}" target="_blank">Editar usuario</a>',
                user_link
            )
        return "Sin usuario"
    get_user_link.short_description = 'Enlace al Usuario'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

admin_site.register(User, UserAdmin)
admin_site.register(TipoAviso, TipoAvisoAdmin)
admin_site.register(Aviso, AvisoAdmin)
admin_site.register(Comentario, ComentarioAdmin)
admin_site.register(PerfilUsuario, PerfilUsuarioAdmin)

def admin_view(request):
    """Vista personalizada para el admin dashboard"""
    from django.shortcuts import render
    
    # Estadísticas básicas
    context = {
        'total_avisos': Aviso.objects.filter(activo=True).count(),
        'avisos_urgentes': Aviso.objects.filter(prioridad='urgente', activo=True).count(),
        'avisos_sin_resolver': Aviso.objects.filter(status='activo', activo=True).count(),
        'usuarios_activos': User.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/dashboard.html', context)