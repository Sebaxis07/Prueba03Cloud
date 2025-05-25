# authentication.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import re

User = get_user_model()

class UsernameOrRutBackend(ModelBackend):
    """
    Backend de autenticación que permite login con username o RUT
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        clean_username = username.strip()
        
        try:
            user = User.objects.get(username=clean_username)
        except User.DoesNotExist:
            if self.is_rut_format(clean_username):
                clean_rut = self.clean_rut(clean_username)
                try:
                    formatted_rut = self.format_rut(clean_rut)
                    user = User.objects.get(
                        Q(perfilusuario__rut=clean_rut) | 
                        Q(perfilusuario__rut=formatted_rut) |
                        Q(perfilusuario__rut__icontains=clean_rut[:8])  # Sin dígito verificador
                    )
                except User.DoesNotExist:
                    return None
                except Exception:
                    try:
                        user = User.objects.get(username=clean_username)
                    except User.DoesNotExist:
                        return None
            else:
                return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def is_rut_format(self, value):
        """Detectar si el input parece ser un RUT"""
        clean_value = re.sub(r'[.-]', '', value)
        return re.match(r'^\d{7,8}[0-9kK]$', clean_value) is not None
    
    def clean_rut(self, rut):
        """Limpiar formato del RUT"""
        return re.sub(r'[^0-9kK]', '', rut.upper())
    
    def format_rut(self, rut):
        """Formatear RUT con puntos y guión"""
        if len(rut) < 8:
            return rut
            
        rut_digits = rut[:-1]
        dv = rut[-1]
        
        formatted = ""
        for i, digit in enumerate(reversed(rut_digits)):
            if i > 0 and i % 3 == 0:
                formatted = "." + formatted
            formatted = digit + formatted
        
        return f"{formatted}-{dv}"
    
    def get_user(self, user_id):
        """Obtener usuario por ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None