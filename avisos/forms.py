from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.contrib.auth import authenticate
import re
from .models import Aviso, Comentario, PerfilUsuario, TipoAviso, DetalleAsalto

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input pl-10 text-sm',
            'placeholder': 'tu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-10 text-sm',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-10 text-sm',
            'placeholder': 'Tu apellido'
        })
    )
    telefono = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-10 text-sm',
            'placeholder': '+56912345678'
        })
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-10 pr-10 text-sm',
            'placeholder': '12.345.678-9'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'rut', 'telefono', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS correctas a todos los campos incluyendo los de UserCreationForm
        self.fields['username'].widget.attrs.update({
            'class': 'form-input pl-10 text-sm',
            'placeholder': 'Tu nombre de usuario único'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input pl-10 pr-10 text-sm',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input pl-10 pr-10 text-sm',
            'placeholder': 'Confirma tu contraseña'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato telefónico chileno
            pattern = r'^(\+56|56)?9[0-9]{8}$'
            if not re.match(pattern, telefono):
                raise ValidationError("Formato de teléfono inválido. Use +56912345678 o 912345678")
        return telefono
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            # Primero limpiamos el RUT
            rut_limpio = rut.replace('.', '').replace('-', '')
            
            if len(rut_limpio) < 8 or len(rut_limpio) > 9:
                raise ValidationError("El RUT debe tener entre 8 y 9 dígitos.")
            
            # Separar cuerpo y dígito verificador
            cuerpo = rut_limpio[:-1]
            dv = rut_limpio[-1].upper()
            
            # Calcular dígito verificador
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
                raise ValidationError('El RUT no es válido.')
            
            # Verificar que no exista - comparar solo números sin formato
            if PerfilUsuario.objects.filter(rut__icontains=rut_limpio).exists():
                raise ValidationError('Este RUT ya está registrado.')
            
            # Formatear el RUT
            if len(cuerpo) == 7:
                rut_formateado = f"{cuerpo[0]}.{cuerpo[1:4]}.{cuerpo[4:]}-{dv}"
            else:
                rut_formateado = f"{cuerpo[:2]}.{cuerpo[2:5]}.{cuerpo[5:]}-{dv}"
            
            return rut_formateado
        return rut
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Crear perfil de usuario
            PerfilUsuario.objects.create(
                usuario=user,
                rut=self.cleaned_data.get('rut', ''),
                telefono=self.cleaned_data.get('telefono', '')
            )
        return user

import re
import logging
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario

logger = logging.getLogger(__name__)

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input pl-10 text-sm',
            'placeholder': 'Usuario o RUT (ej: 12345678-9)',
            'autocomplete': 'username',
        }),
        label="Usuario o RUT"
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input pl-10 pr-10 text-sm',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
        }),
        label="Contraseña"
    )
    
    def clean_username(self):
        username_input = self.cleaned_data.get('username', '').strip()
        
        logger.debug(f"Login attempt with input: '{username_input}'")
        
        # Si parece ser un RUT, intentar buscar usuario por RUT
        if self.is_rut_format(username_input):
            logger.debug(f"Input detected as RUT format: {username_input}")
            
            # Limpiar el RUT (quitar puntos y guiones)
            rut_clean = re.sub(r'[^0-9kK]', '', username_input.upper())
            logger.debug(f"Cleaned RUT: {rut_clean}")
            
            # Buscar usuario con este RUT de múltiples maneras
            usuario_encontrado = None
            
            # Método 1: Buscar RUT exacto tal como se ingresó
            try:
                perfil = PerfilUsuario.objects.get(rut=username_input)
                usuario_encontrado = perfil.usuario.username
                logger.debug(f"Found user by exact RUT match: {usuario_encontrado}")
            except PerfilUsuario.DoesNotExist:
                logger.debug("No exact RUT match found")
            
            # Método 2: Buscar por RUT limpio (sin formato)
            if not usuario_encontrado:
                try:
                    perfil = PerfilUsuario.objects.get(rut__icontains=rut_clean)
                    usuario_encontrado = perfil.usuario.username
                    logger.debug(f"Found user by clean RUT match: {usuario_encontrado}")
                except PerfilUsuario.DoesNotExist:
                    logger.debug("No clean RUT match found")
            
            # Método 3: Buscar RUT con formato estándar
            if not usuario_encontrado:
                rut_formateado = self.format_rut_standard(rut_clean)
                try:
                    perfil = PerfilUsuario.objects.get(rut=rut_formateado)
                    usuario_encontrado = perfil.usuario.username
                    logger.debug(f"Found user by formatted RUT match: {usuario_encontrado}")
                except PerfilUsuario.DoesNotExist:
                    logger.debug("No formatted RUT match found")
            
            # Método 4: Buscar en todos los RUTs que contengan los dígitos
            if not usuario_encontrado:
                perfiles_candidatos = PerfilUsuario.objects.filter(
                    rut__isnull=False
                ).exclude(rut='')
                
                for perfil in perfiles_candidatos:
                    rut_perfil_clean = re.sub(r'[^0-9kK]', '', perfil.rut.upper())
                    if rut_perfil_clean == rut_clean:
                        usuario_encontrado = perfil.usuario.username
                        logger.debug(f"Found user by manual comparison: {usuario_encontrado}")
                        break
            
            if usuario_encontrado:
                logger.info(f"RUT login successful mapping: {username_input} -> {usuario_encontrado}")
                return usuario_encontrado
            else:
                logger.warning(f"RUT not found in database: {username_input} (clean: {rut_clean})")
                # No encontró el RUT, pero no lanzar error aquí
                # Dejar que Django maneje la autenticación
        
        # Si no es RUT o no se encontró, devolver el input original
        logger.debug(f"Using original input as username: {username_input}")
        return username_input
    
    def is_rut_format(self, value):
        """Detectar si el input parece ser un RUT"""
        if not value:
            return False
            
        # Remover puntos y guiones para verificar
        clean_value = re.sub(r'[.-]', '', value.strip())
        
        # Verificar si termina en dígito o K y tiene la longitud correcta
        # RUT chileno: 7-8 dígitos + 1 dígito verificador
        return bool(re.match(r'^\d{7,8}[0-9kK]$', clean_value, re.IGNORECASE))
    
    def format_rut_standard(self, rut_clean):
        """Formatear RUT de manera estándar (12.345.678-9)"""
        if len(rut_clean) < 8:
            return rut_clean
            
        # Separar cuerpo y dígito verificador
        cuerpo = rut_clean[:-1]
        dv = rut_clean[-1].upper()
        
        # Formatear con puntos según la longitud
        if len(cuerpo) == 7:
            # 1.234.567-8
            rut_formateado = f"{cuerpo[0]}.{cuerpo[1:4]}.{cuerpo[4:]}-{dv}"
        elif len(cuerpo) == 8:
            # 12.345.678-9
            rut_formateado = f"{cuerpo[:2]}.{cuerpo[2:5]}.{cuerpo[5:]}-{dv}"
        else:
            # Caso inusual, devolver sin formato
            rut_formateado = f"{cuerpo}-{dv}"
            
        return rut_formateado

class AvisoForm(forms.ModelForm):
    """Formulario para crear/editar avisos - CSS sincronizado con HTML"""
    
    # Campo tipo con queryset dinámico
    tipo = forms.ModelChoiceField(
        queryset=TipoAviso.objects.filter(activo=True),
        empty_label="Selecciona un tipo...",
        widget=forms.Select(attrs={
            'class': 'form-select w-full',
            'required': True
        }),
        error_messages={
            'required': 'Debes seleccionar un tipo de aviso.',
            'invalid_choice': 'Selecciona un tipo de aviso válido.'
        }
    )
    
    class Meta:
        model = Aviso
        fields = ['titulo', 'descripcion', 'tipo', 'prioridad', 'direccion', 'sector', 
                 'telefono_contacto', 'imagen', 'es_anonimo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Describe brevemente el incidente...',
                'maxlength': '200',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'placeholder': 'Describe detalladamente lo que ocurrió. Incluye: ¿Qué pasó? ¿Cuándo? ¿Cómo? ¿Quién estuvo involucrado?',
                'maxlength': '2000',
                'required': True
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select w-full',
                'required': True
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Ej: Av. Pedro Aguirre Cerda 1234',
                'required': True
            }),
            'sector': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Ej: Costa Laguna, Manzana A, Block 15',
                'required': True
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': '+56 9 1234 5678',
                'pattern': r'^(\+56|56)?9[0-9]{8}$'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-input w-full',
                'accept': 'image/*'
            }),
            'es_anonimo': forms.CheckboxInput(attrs={
                'class': 'checkbox-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Verificar que hay tipos disponibles
        tipos_count = TipoAviso.objects.filter(activo=True).count()
        if tipos_count == 0:
            self.fields['tipo'].queryset = TipoAviso.objects.none()
            self.fields['tipo'].widget.attrs['disabled'] = True
            self.fields['tipo'].help_text = "⚠️ No hay tipos de aviso. Ejecuta: python manage.py load_initial_data"
        
        # Personalizar etiquetas del dropdown para mostrar display_name
        self.fields['tipo'].label_from_instance = lambda obj: obj.get_display_name()
    
    def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo')
        if not tipo:
            raise ValidationError("Debes seleccionar un tipo de aviso.")
        if not tipo.activo:
            raise ValidationError("El tipo de aviso seleccionado no está disponible.")
        return tipo
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        # Limpiar HTML y caracteres especiales
        titulo = strip_tags(titulo).strip()
        
        # Validar longitud
        if len(titulo) < 5:
            raise ValidationError("El título debe tener al menos 5 caracteres.")
        if len(titulo) > 200:
            raise ValidationError("El título no puede exceder 200 caracteres.")
        
        # Validar caracteres especiales peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        if any(char in titulo for char in dangerous_chars):
            raise ValidationError("El título contiene caracteres no permitidos.")
        
        return titulo
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        # Limpiar HTML
        descripcion = strip_tags(descripcion).strip()
        
        if len(descripcion) < 10:
            raise ValidationError("La descripción debe tener al menos 10 caracteres.")
        
        return descripcion
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        direccion = strip_tags(direccion).strip()
        
        if len(direccion) < 5:
            raise ValidationError("La dirección debe ser más específica.")
        
        return direccion
    
    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            # Validar tamaño (máximo 5MB)
            if imagen.size > 5 * 1024 * 1024:
                raise ValidationError("La imagen no puede ser mayor a 5MB.")
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if hasattr(imagen, 'content_type') and imagen.content_type not in allowed_types:
                raise ValidationError("Solo se permiten imágenes JPEG, PNG y GIF.")
        
        return imagen

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Escribe tu comentario...'
            })
        }
    
    def clean_contenido(self):
        contenido = self.cleaned_data.get('contenido')
        # Limpiar HTML
        contenido = strip_tags(contenido).strip()
        
        if len(contenido) < 3:
            raise ValidationError("El comentario debe tener al menos 3 caracteres.")
        
        if len(contenido) > 500:
            raise ValidationError("El comentario no puede exceder 500 caracteres.")
        
        return contenido

class BusquedaForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar avisos...'
        })
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoAviso.objects.filter(activo=True),
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    prioridad = forms.ChoiceField(
        choices=[('', 'Todas las prioridades')] + Aviso.PRIORIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Aviso.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar etiquetas para mostrar display_name
        self.fields['tipo'].label_from_instance = lambda obj: obj.get_display_name()

class PerfilUsuarioForm(forms.ModelForm):
    """Formulario para editar perfil de usuario incluyendo datos del User model"""
    
    # Campos del User model
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'w-full glassmorphism-light border border-costa-green/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-costa-green/50 focus:border-costa-green transition-all duration-300',
            'placeholder': 'Ingresa tus nombres'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'w-full glassmorphism-light border border-costa-green/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-costa-green/50 focus:border-costa-green transition-all duration-300',
            'placeholder': 'Ingresa tus apellidos'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'w-full glassmorphism-light border border-costa-green/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-costa-green/50 focus:border-costa-green transition-all duration-300',
            'placeholder': 'tu@email.com'
        })
    )
    
    foto_perfil = forms.ImageField(
        required=False,
        label="Foto de perfil",
        help_text="Formatos permitidos: JPG, PNG. Tamaño máximo: 5MB",
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'foto-perfil-input'
        })
    )

    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'sector', 'foto_perfil']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'w-full glassmorphism-light border border-costa-green/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-costa-green/50 focus:border-costa-green transition-all duration-300',
                'placeholder': '+56 9 1234 5678'
            }),
            'sector': forms.TextInput(attrs={
                'class': 'w-full glassmorphism-light border border-costa-green/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-costa-green/50 focus:border-costa-green transition-all duration-300',
                'placeholder': 'Ej: Costa Laguna Norte, Sector 5'
            }),
        }
        labels = {
            'telefono': 'Teléfono de contacto',
            'sector': 'Sector donde vives',
        }

    def __init__(self, *args, **kwargs):
        # Extraer la instancia del usuario si existe
        instance = kwargs.get('instance')
        self.user = None
        if instance and hasattr(instance, 'usuario'):
            self.user = instance.usuario
            # Inicializar los campos del usuario
            kwargs.setdefault('initial', {})
            kwargs['initial'].update({
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email,
            })
        
        super().__init__(*args, **kwargs)

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            # Validar tamaño (5MB máximo)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError("La imagen no puede superar los 5MB.")
            
            # Validar formato
            if not foto.content_type.startswith('image/'):
                raise ValidationError("El archivo debe ser una imagen válida.")
                
        return foto

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # Verificar que el email no esté en uso por otro usuario
            if User.objects.filter(email=email).exclude(id=self.user.id).exists():
                raise ValidationError("Este correo ya está registrado por otro usuario.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato telefónico chileno
            pattern = r'^(\+56|56)?9[0-9]{8}$'
            if not re.match(pattern, telefono):
                raise ValidationError("Formato de teléfono inválido. Use +56912345678 o 912345678")
        return telefono

    def save(self, commit=True):
        # Guardar el perfil
        perfil = super().save(commit=False)
        
        # Actualizar los datos del usuario
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            
            if commit:
                self.user.save()
        
        if commit:
            perfil.save()
            
        return perfil

# DetalleAsaltoForm también actualizado para consistencia
class DetalleAsaltoForm(forms.ModelForm):
    class Meta:
        model = DetalleAsalto
        fields = ['cantidad_asaltantes', 'descripcion_fisica', 'vehiculo_usado', 'direccion_huida', 'armas_usadas']
        widgets = {
            'cantidad_asaltantes': forms.NumberInput(attrs={
                'class': 'form-input w-full',
                'min': '1'
            }),
            'descripcion_fisica': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'placeholder': 'Altura aproximada, complexión, vestimenta, características distintivas...'
            }),
            'vehiculo_usado': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Ej: Moto negra, Auto blanco, A pie'
            }),
            'direccion_huida': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Hacia dónde se dirigieron'
            }),
            'armas_usadas': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Ej: Arma de fuego tipo pistola, cuchillo, etc.'
            })
        }