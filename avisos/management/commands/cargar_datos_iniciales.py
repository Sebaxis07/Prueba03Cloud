from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avisos.models import TipoAviso, PerfilUsuario

class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema de avisos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--crear-admin',
            action='store_true',
            help='Crear usuario administrador',
        )
        parser.add_argument(
            '--reset-tipos',
            action='store_true',
            help='Resetear tipos de aviso existentes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando carga de datos iniciales...')
        )

        if options['reset_tipos']:
            TipoAviso.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('🗑️  Tipos de aviso existentes eliminados')
            )

        created_tipos = 0
        
        for choice_value, choice_display in TipoAviso.TIPOS_CHOICES:
            tipo, created = TipoAviso.objects.get_or_create(
                nombre=choice_value,
                defaults={
                    'descripcion': f'Reportes relacionados con {choice_display.lower()}',
                    'activo': True
                }
            )
            if created:
                created_tipos += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Tipo creado: {choice_display} ({choice_value})')
                )
            else:
                if not tipo.descripcion:
                    tipo.descripcion = f'Reportes relacionados con {choice_display.lower()}'
                    tipo.save()
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Tipo ya existe: {choice_display}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'📊 Tipos procesados: {created_tipos} creados')
        )

        if options['crear_admin']:
            admin_username = 'admin'
            admin_email = 'admin@costalaguna.cl'
            admin_password = 'admin123'

            if not User.objects.filter(username=admin_username).exists():
                admin_user = User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    first_name='Administrador',
                    last_name='Sistema'
                )
                
                try:
                    PerfilUsuario.objects.get_or_create(
                        usuario=admin_user,
                        defaults={
                            'rut': '21.661.083-0',
                            'telefono': '+56912345678',
                            'direccion': 'Costa Laguna, Antofagasta',
                            'sector': 'Administración',
                            'verificado': True
                        }
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'👤 Usuario admin creado: {admin_username}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Usuario admin creado sin perfil: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('ℹ️  Usuario admin ya existe')
                )

        usuarios_ejemplo = [
            {
                'username': 'juan_costa',
                'email': 'juan@email.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'rut': '13.310.152-7',
                'telefono': '+56987654321',
                'sector': 'Costa Laguna, Manzana A'
            },
            {
                'username': 'maria_laguna',
                'email': 'maria@email.com',
                'first_name': 'María',
                'last_name': 'González',
                'rut': '15.626.862-3',
                'telefono': '+56976543210',
                'sector': 'Costa Laguna, Manzana B'
            }
        ]

        created_users = 0
        for user_data in usuarios_ejemplo:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='demo123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                
                try:
                    PerfilUsuario.objects.create(
                        usuario=user,
                        rut=user_data['rut'],
                        telefono=user_data['telefono'],
                        sector=user_data['sector'],
                        verificado=True
                    )
                    created_users += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'👤 Usuario creado: {user_data["username"]}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Usuario {user_data["username"]} creado sin perfil: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Usuario {user_data["username"]} ya existe')
                )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('🎉 DATOS INICIALES CARGADOS EXITOSAMENTE!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📊 Resumen: {created_tipos} tipos creados, {created_users} usuarios creados')
        )
        self.stdout.write(
            self.style.WARNING('💡 Usuarios demo: juan_costa / maria_laguna (password: demo123)')
        )
        if options['crear_admin']:
            self.stdout.write(
                self.style.WARNING('🔑 Admin: admin (password: admin123)')
            )