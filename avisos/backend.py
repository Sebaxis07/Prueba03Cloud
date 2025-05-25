# En tu app/backends.py (crear este archivo si no existe)

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import PerfilUsuario
import re

class RUTAuthBackend(ModelBackend):
    """
    Backend personalizado que permite autenticación con RUT o username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Intentar autenticación normal primero
        user = super().authenticate(request, username, password, **kwargs)
        if user:
            return user
        
        # Si no funciona, verificar si es un RUT
        if username and self.is_rut_format(username):
            try:
                # Limpiar RUT
                rut_clean = self.clean_rut(username)
                
                # Buscar por RUT en PerfilUsuario
                perfil = PerfilUsuario.objects.get(rut__icontains=rut_clean)
                user = perfil.usuario
                
                # Verificar contraseña
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except PerfilUsuario.DoesNotExist:
                pass
        
        return None
    
    def is_rut_format(self, value):
        """Detectar si el valor parece ser un RUT"""
        clean_value = re.sub(r'[.-]', '', value)
        return re.match(r'^\d{7,8}[0-9kK]$', clean_value) is not None
    
    def clean_rut(self, rut):
        """Limpiar formato del RUT"""
        return re.sub(r'[^0-9kK]', '', rut.upper())

    def get_user(self, user_id):
        """Obtener usuario por ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None