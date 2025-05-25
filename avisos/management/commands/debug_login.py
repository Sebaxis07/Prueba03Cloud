# Crea este archivo en: avisos/management/commands/debug_login.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avisos.models import PerfilUsuario
import re

class Command(BaseCommand):
    help = 'Debug login issues with RUT'

    def handle(self, *args, **options):
        self.stdout.write("=== DEBUG LOGIN RUT ===\n")
        
        # 1. Verificar usuarios y perfiles
        total_users = User.objects.count()
        total_perfiles = PerfilUsuario.objects.count()
        perfiles_con_rut = PerfilUsuario.objects.exclude(rut='').exclude(rut__isnull=True)
        
        self.stdout.write(f"Total usuarios: {total_users}")
        self.stdout.write(f"Total perfiles: {total_perfiles}")
        self.stdout.write(f"Perfiles con RUT: {perfiles_con_rut.count()}\n")
        
        # 2. Mostrar perfiles con RUT
        if perfiles_con_rut.exists():
            self.stdout.write("--- USUARIOS CON RUT ---")
            for perfil in perfiles_con_rut:
                self.stdout.write(f"Usuario: {perfil.usuario.username}")
                self.stdout.write(f"RUT: '{perfil.rut}'")
                self.stdout.write(f"Nombre: {perfil.usuario.first_name} {perfil.usuario.last_name}")
                self.stdout.write("---")
        else:
            self.stdout.write("❌ NO HAY USUARIOS CON RUT GUARDADO")
            
        # 3. Verificar estructura de la tabla
        self.stdout.write("\n--- CAMPOS DEL MODELO PerfilUsuario ---")
        fields = PerfilUsuario._meta.get_fields()
        for field in fields:
            self.stdout.write(f"- {field.name}: {field.__class__.__name__}")
            
        # 4. Crear usuario de prueba si no existe
        test_rut = "12345678-9"
        test_username = "test_rut_user"
        
        if not User.objects.filter(username=test_username).exists():
            self.stdout.write(f"\n--- CREANDO USUARIO DE PRUEBA ---")
            user = User.objects.create_user(
                username=test_username,
                password="test123",
                first_name="Usuario",
                last_name="Prueba"
            )
            
            perfil, created = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={'rut': test_rut}
            )
            
            if created:
                self.stdout.write(f"✅ Usuario creado: {test_username}")
                self.stdout.write(f"✅ RUT asignado: {test_rut}")
            else:
                perfil.rut = test_rut
                perfil.save()
                self.stdout.write(f"✅ RUT actualizado: {test_rut}")
        else:
            self.stdout.write(f"\n--- USUARIO DE PRUEBA YA EXISTE ---")
            user = User.objects.get(username=test_username)
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            if not perfil.rut:
                perfil.rut = test_rut
                perfil.save()
                self.stdout.write(f"✅ RUT asignado al usuario existente: {test_rut}")
            else:
                self.stdout.write(f"RUT ya existe: {perfil.rut}")
                
        # 5. Probar la lógica de búsqueda de RUT
        self.stdout.write(f"\n--- PROBANDO BÚSQUEDA DE RUT ---")
        ruts_to_test = [
            "12345678-9",
            "12.345.678-9", 
            "123456789",
            "12345678-9",
        ]
        
        for rut_test in ruts_to_test:
            self.stdout.write(f"\nProbando RUT: '{rut_test}'")
            
            # Limpiar RUT
            rut_clean = re.sub(r'[^0-9kK]', '', rut_test.upper())
            self.stdout.write(f"  RUT limpio: '{rut_clean}'")
            
            # Buscar exacto
            perfil_exacto = PerfilUsuario.objects.filter(rut=rut_test).first()
            if perfil_exacto:
                self.stdout.write(f"  ✅ Encontrado exacto: {perfil_exacto.usuario.username}")
            else:
                self.stdout.write(f"  ❌ No encontrado exacto")
                
            # Buscar con icontains
            perfil_contains = PerfilUsuario.objects.filter(rut__icontains=rut_clean).first()
            if perfil_contains:
                self.stdout.write(f"  ✅ Encontrado con contains: {perfil_contains.usuario.username}")
            else:
                self.stdout.write(f"  ❌ No encontrado con contains")
                
        self.stdout.write(f"\n=== FIN DEBUG ===")
        self.stdout.write(f"Ahora prueba hacer login con:")
        self.stdout.write(f"Usuario: {test_username} | Contraseña: test123")
        self.stdout.write(f"O con RUT: {test_rut} | Contraseña: test123")