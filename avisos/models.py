from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
from django.urls import reverse
import os
from django.shortcuts import render
import re

def user_directory_path(instance, filename):
    """Genera el path para subir la foto de perfil"""
    return f'usuarios/user_{instance.usuario.id}/{filename}'
def validar_rut_chileno(value):
    """Validador personalizado para RUT chileno"""
    rut = value.replace(".", "").replace("-", "")
    
    if not re.match(r'^[0-9]{7,8}[0-9Kk]$', rut):
        raise ValidationError('RUT inválido. Formato requerido: 12345678-9 o 12.345.678-9')
    
    cuerpo = rut[:-1]
    dv = rut[-1].upper()
    
    suma = 0
    multiplicador = 2
    
    for d in reversed(cuerpo):
        suma += int(d) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    
    dv_esperado = str(11 - (suma % 11))
    if dv_esperado == '11':
        dv_esperado = '0'
    elif dv_esperado == '10':
        dv_esperado = 'K'
    
    if dv != dv_esperado:
        raise ValidationError('RUT inválido. Dígito verificador incorrecto.')

class TipoAviso(models.Model):
    TIPOS_CHOICES = [
        ('robo_casa', 'Robo a Casa'),
        ('robo_vehiculo', 'Robo de Vehículo'),
        ('asalto', 'Asalto'),
        ('vehiculo_sospechoso', 'Vehículo Sospechoso'),
        ('persona_sospechosa', 'Persona Sospechosa'),
        ('accidente', 'Accidente de Tránsito'),
        ('emergencia_medica', 'Emergencia Médica'),
        ('incendio', 'Incendio'),
        ('vandalismo', 'Vandalismo'),
        ('problema_electrico', 'Problema Eléctrico'),
        ('otros', 'Otros')
    ]
    
    ICONOS_MAP = {
        'robo_casa': 'home',
        'robo_vehiculo': 'car',
        'asalto': 'alert-triangle',
        'vehiculo_sospechoso': 'car',
        'persona_sospechosa': 'user-x',
        'accidente': 'zap',
        'emergencia_medica': 'heart',
        'incendio': 'flame',
        'vandalismo': 'hammer',
        'problema_electrico': 'zap',
        'otros': 'info'
    }
    
    COLORES_MAP = {
        'robo_casa': 'red',
        'robo_vehiculo': 'red',
        'asalto': 'red',
        'vehiculo_sospechoso': 'orange',
        'persona_sospechosa': 'orange',
        'accidente': 'yellow',
        'emergencia_medica': 'red',
        'incendio': 'red',
        'vandalismo': 'orange',
        'problema_electrico': 'yellow',
        'otros': 'gray'
    }
    
    nombre = models.CharField(max_length=50, choices=TIPOS_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tipo de Aviso'
        verbose_name_plural = 'Tipos de Avisos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()
    
    def get_display_name(self):
        """Retorna el nombre para mostrar"""
        return self.get_nombre_display()
    
    def get_icono(self):
        """Retorna el icono correspondiente al tipo"""
        return self.ICONOS_MAP.get(self.nombre, 'alert-circle')
    
    def get_color(self):
        """Retorna el color correspondiente al tipo"""
        return self.COLORES_MAP.get(self.nombre, 'gray')
    
    def get_color_classes(self):
        """Retorna las clases CSS para el color del badge"""
        color_map = {
            'red': 'bg-red-100 text-red-800',
            'orange': 'bg-orange-100 text-orange-800',
            'yellow': 'bg-yellow-100 text-yellow-800',
            'green': 'bg-green-100 text-green-800',
            'blue': 'bg-blue-100 text-blue-800',
            'purple': 'bg-purple-100 text-purple-800',
            'gray': 'bg-gray-100 text-gray-800',
        }
        return color_map.get(self.get_color(), 'bg-blue-100 text-blue-800')
    
    def get_badge_html(self):
        """Retorna HTML completo del badge con icono y color"""
        return f'''
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {self.get_color_classes()}">
            <i data-lucide="{self.get_icono()}" class="h-3 w-3 mr-1"></i>
            {self.get_display_name()}
        </span>
        '''

class Custom429Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 429:
            return render(request, 'bloqueado.html', status=429)
        return response
class Aviso(models.Model):
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('resuelto', 'Resuelto'),
        ('en_proceso', 'En Proceso'),
    ]
    titulo = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5, "El título debe tener al menos 5 caracteres")]
    )
    descripcion = models.TextField(
        validators=[MinLengthValidator(10, "La descripción debe tener al menos 10 caracteres")]
    )
    tipo = models.ForeignKey(
        TipoAviso, 
        on_delete=models.CASCADE,
        related_name='avisos'
    )
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='activo')
    direccion = models.CharField(max_length=300)
    sector = models.CharField(
        max_length=100, 
        help_text="Ej: Costa Laguna, Manzana A, Block 15"
    )
    
    telefono_regex = RegexValidator(
        regex=r'^(\+56|56)?9[0-9]{8}$',
        message="Formato válido: +56912345678 o 912345678 (celular chileno)"
    )
    telefono_contacto = models.CharField(
        validators=[telefono_regex], 
        max_length=17, 
        blank=True,
        help_text="Teléfono de contacto opcional"
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ip_creacion = models.GenericIPAddressField(null=True, blank=True)
    imagen = models.ImageField(upload_to='avisos/%Y/%m/', blank=True, null=True)
    es_anonimo = models.BooleanField(default=False)
    verificado_por_admin = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        
    def __str__(self):
        return f"{self.titulo} - {self.tipo.nombre}"
    
    def get_absolute_url(self):
        return reverse('aviso_detalle', kwargs={'pk': self.pk})
    
    def get_prioridad_color(self):
        colors = {
            'baja': 'green',
            'media': 'yellow',
            'alta': 'orange',
            'urgente': 'red'
        }
        return colors.get(self.prioridad, 'gray')
    
    def get_prioridad_bg_color(self):
        colors = {
            'baja': 'bg-green-100 text-green-800',
            'media': 'bg-yellow-100 text-yellow-800',
            'alta': 'bg-orange-100 text-orange-800',
            'urgente': 'bg-red-100 text-red-800'
        }
        return colors.get(self.prioridad, 'bg-gray-100 text-gray-800')
    
    def tiempo_transcurrido(self):
        from django.utils.timesince import timesince
        return timesince(self.fecha_creacion)

    def get_tipo_display(self):
        """Custom method to get tipo display name"""
        return self.tipo.get_nombre_display()
class DetalleAsalto(models.Model):
        aviso = models.OneToOneField(Aviso, on_delete=models.CASCADE, related_name='detalle_asalto')
        cantidad_asaltantes = models.PositiveIntegerField(
            verbose_name="Cantidad de asaltantes",
            default=1
        )
        descripcion_fisica = models.TextField(
            verbose_name="Descripción física de los asaltantes",
            help_text="Incluye altura aproximada, contextura, vestimenta, rasgos distintivos, etc.",
            blank=True
        )
        vehiculo_usado = models.CharField(
            max_length=200,
            verbose_name="Vehículo usado",
            help_text="Marca, modelo, color y patente si es posible",
            blank=True
        )
        direccion_huida = models.CharField(
            max_length=200,
            verbose_name="Dirección de huida",
            help_text="¿Hacia dónde huyeron los asaltantes?",
            blank=True
        )
        armas_usadas = models.CharField(
            max_length=200,
            verbose_name="Armas utilizadas",
            help_text="Tipo de armas que portaban los asaltantes",
            blank=True
        )

        def __str__(self):
            return f"Detalles de asalto - {self.aviso.titulo}"
class Comentario(models.Model):
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField(
        max_length=500,
        validators=[MinLengthValidator(3, "El comentario debe tener al menos 3 caracteres")]
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    ip_creacion = models.GenericIPAddressField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
    
    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.aviso.titulo}"

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{1,2}\.?[0-9]{3}\.?[0-9]{3}-[0-9Kk]$',
                message="Formato válido: 12.345.678-9 o 12345678-9"
            ),
            validar_rut_chileno
        ],
        help_text="Ingrese RUT en formato 12.345.678-9"
    )
    telefono = models.CharField(
        max_length=17, 
        validators=[RegexValidator(
            regex=r'^(\+56|56)?9[0-9]{8}$',
            message="Formato válido: +56912345678 o 912345678"
        )],
        blank=True
    )
    foto_perfil = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
        help_text="Imagen de perfil del usuario"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    direccion = models.CharField(max_length=300, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    notificaciones_email = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    def clean(self):
        """Validación adicional a nivel de modelo"""
        super().clean()
        if self.rut:
            # Formatear RUT al formato estándar (XX.XXX.XXX-X)
            rut = self.rut.replace(".", "").replace("-", "")
            if len(rut) == 9:
                self.rut = f"{rut[0:2]}.{rut[2:5]}.{rut[5:8]}-{rut[8]}"
            else:
                self.rut = f"{rut[0]}.{rut[1:4]}.{rut[4:7]}-{rut[7]}"

    def save(self, *args, **kwargs):
        """Sobrescribir save para asegurar la validación"""
        self.full_clean()
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        # Eliminar archivo de foto al eliminar el perfil
        if self.foto_perfil:
            if os.path.isfile(self.foto_perfil.path):
                os.remove(self.foto_perfil.path)
        super().delete(*args, **kwargs)

