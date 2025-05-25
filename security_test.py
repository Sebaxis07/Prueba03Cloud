
import requests
import json
import time
import random
import string
from urllib.parse import urljoin
import os
import sys

class SecurityTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.csrf_token = None
        self.vulnerabilities = []
        
        print(f"🎯 Iniciando pruebas de seguridad en: {self.base_url}")
        print("=" * 60)
    
    def get_csrf_token(self, url="/login/"):
        """Obtener token CSRF para pruebas"""
        try:
            response = self.session.get(urljoin(self.base_url, url))
            if 'csrfmiddlewaretoken' in response.text:
                import re
                match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
                if match:
                    self.csrf_token = match.group(1)
                    print(f"✅ Token CSRF obtenido: {self.csrf_token[:20]}...")
                    return True
        except Exception as e:
            print(f"❌ Error obteniendo CSRF token: {e}")
        return False
    
    def test_sql_injection(self):
        """🔍 Test 1: Inyección SQL"""
        print("\n🔍 TEST 1: INYECCIÓN SQL")
        print("-" * 30)
        
        sql_payloads = [
            "'; DROP TABLE avisos; --",
            "' OR '1'='1' --",
            "admin'/*",
            "' UNION SELECT username, password FROM auth_user--",
            "1' AND (SELECT COUNT(*) FROM auth_user) > 0--"
        ]
        
        for payload in sql_payloads:
            try:
                # Test en búsqueda
                response = self.session.get(
                    urljoin(self.base_url, "/avisos/"),
                    params={'q': payload}
                )
                
                # Verificar respuesta
                if response.status_code == 200:
                    if "error" in response.text.lower() or "sql" in response.text.lower():
                        self.vulnerabilities.append(f"Posible SQL Injection en búsqueda: {payload}")
                        print(f"⚠️  Posible vulnerabilidad con: {payload}")
                    else:
                        print(f"✅ Payload bloqueado: {payload}")
                
                time.sleep(0.5)  # No sobrecargar
                
            except Exception as e:
                print(f"❌ Error en test SQL: {e}")
    
    def test_xss(self):
        """🔍 Test 2: Cross-Site Scripting (XSS)"""
        print("\n🔍 TEST 2: CROSS-SITE SCRIPTING (XSS)")
        print("-" * 40)
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'+alert('XSS')+'",
            "<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        # Test en formulario de comentarios (requiere login)
        if self.login_test_user():
            for payload in xss_payloads:
                try:
                    # Intentar crear aviso con payload XSS
                    data = {
                        'titulo': payload,
                        'descripcion': f'Test XSS: {payload}',
                        'direccion': 'Test Address',
                        'sector': 'Test Sector',
                        'tipo': '1',  # Asumiendo que existe
                        'prioridad': 'media',
                        'csrfmiddlewaretoken': self.csrf_token
                    }
                    
                    response = self.session.post(
                        urljoin(self.base_url, "/aviso/crear/"),
                        data=data
                    )
                    
                    if payload in response.text and '<script>' in response.text:
                        self.vulnerabilities.append(f"XSS en título: {payload}")
                        print(f"⚠️  XSS no filtrado: {payload}")
                    else:
                        print(f"✅ XSS bloqueado: {payload}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Error en test XSS: {e}")
    
    def test_csrf(self):
        """🔍 Test 3: Cross-Site Request Forgery"""
        print("\n🔍 TEST 3: CROSS-SITE REQUEST FORGERY (CSRF)")
        print("-" * 45)
        
        # Intentar hacer request sin token CSRF
        try:
            data = {
                'titulo': 'Test CSRF',
                'descripcion': 'Test sin token CSRF',
                'direccion': 'Test Address',
                'sector': 'Test Sector',
                'tipo': '1',
                'prioridad': 'media'
                # Sin csrfmiddlewaretoken
            }
            
            response = self.session.post(
                urljoin(self.base_url, "/aviso/crear/"),
                data=data
            )
            
            if response.status_code == 403:
                print("✅ Protección CSRF activa - Request rechazado")
            elif "CSRF" in response.text:
                print("✅ CSRF detectado y bloqueado")
            else:
                self.vulnerabilities.append("CSRF: Request sin token fue aceptado")
                print("⚠️  CSRF: Request sin token fue aceptado")
                
        except Exception as e:
            print(f"❌ Error en test CSRF: {e}")
    
    def test_authentication_bypass(self):
        """🔍 Test 4: Bypass de Autenticación"""
        print("\n🔍 TEST 4: BYPASS DE AUTENTICACIÓN")
        print("-" * 35)
        
        protected_urls = [
            "/dashboard/",
            "/aviso/crear/",
            "/mis-avisos/",
            "/aviso/1/editar/",
            "/aviso/1/eliminar/"
        ]
        
        for url in protected_urls:
            try:
                response = self.session.get(urljoin(self.base_url, url))
                
                if response.status_code == 200 and "login" not in response.url:
                    self.vulnerabilities.append(f"Acceso sin autenticación: {url}")
                    print(f"⚠️  Acceso sin login: {url}")
                elif response.status_code == 302 or "login" in response.url:
                    print(f"✅ Protegido: {url}")
                else:
                    print(f"🔍 Respuesta: {response.status_code} para {url}")
                    
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
    
    def test_brute_force(self):
        """🔍 Test 5: Ataque de Fuerza Bruta"""
        print("\n🔍 TEST 5: ATAQUE DE FUERZA BRUTA")
        print("-" * 30)
        
        common_passwords = [
            "admin", "password", "123456", "admin123", 
            "password123", "12345", "qwerty", "abc123"
        ]
        
        login_attempts = 0
        for password in common_passwords[:5]:  # Solo 5 intentos para no sobrecargar
            try:
                if not self.csrf_token:
                    self.get_csrf_token()
                
                data = {
                    'username': 'admin',
                    'password': password,
                    'csrfmiddlewaretoken': self.csrf_token
                }
                
                response = self.session.post(
                    urljoin(self.base_url, "/login/"),
                    data=data
                )
                
                login_attempts += 1
                
                if response.status_code == 200 and "dashboard" in response.url:
                    self.vulnerabilities.append(f"Contraseña débil encontrada: admin/{password}")
                    print(f"⚠️  Contraseña débil: admin/{password}")
                    break
                else:
                    print(f"✅ Intento fallido: admin/{password}")
                
                time.sleep(1)  # Esperar para evitar rate limiting
                
            except Exception as e:
                print(f"❌ Error en brute force: {e}")
        
        if login_attempts >= 5:
            print("🔍 Rate limiting test: Se realizaron múltiples intentos")
    
    def test_file_upload_vulnerabilities(self):
        """🔍 Test 6: Vulnerabilidades en Subida de Archivos"""
        print("\n🔍 TEST 6: SUBIDA DE ARCHIVOS MALICIOSOS")
        print("-" * 35)
        
        if not self.login_test_user():
            print("❌ No se pudo hacer login para test de archivos")
            return
        
        # Crear archivos de test maliciosos
        malicious_files = {
            'script.php': b'<?php system($_GET["cmd"]); ?>',
            'shell.jsp': b'<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>',
            'test.exe': b'MZ\x90\x00',  # Ejecutable Windows
            'fake.jpg': b'<?php echo "PHP in image"; ?>',  # PHP disfrazado
        }
        
        for filename, content in malicious_files.items():
            try:
                # Crear archivo temporal
                with open(f'/tmp/{filename}', 'wb') as f:
                    f.write(content)
                
                # Intentar subir archivo
                files = {'imagen': open(f'/tmp/{filename}', 'rb')}
                data = {
                    'titulo': f'Test archivo {filename}',
                    'descripcion': 'Test de archivo malicioso',
                    'direccion': 'Test Address',
                    'sector': 'Test Sector',
                    'tipo': '1',
                    'prioridad': 'media',
                    'csrfmiddlewaretoken': self.csrf_token
                }
                
                response = self.session.post(
                    urljoin(self.base_url, "/aviso/crear/"),
                    data=data,
                    files=files
                )
                
                if response.status_code == 200 and "exitosamente" in response.text:
                    self.vulnerabilities.append(f"Archivo malicioso aceptado: {filename}")
                    print(f"⚠️  Archivo malicioso subido: {filename}")
                else:
                    print(f"✅ Archivo rechazado: {filename}")
                
                # Limpiar archivo temporal
                os.remove(f'/tmp/{filename}')
                
            except Exception as e:
                print(f"❌ Error testing {filename}: {e}")
    
    def test_information_disclosure(self):
        """🔍 Test 7: Divulgación de Información"""
        print("\n🔍 TEST 7: DIVULGACIÓN DE INFORMACIÓN")
        print("-" * 35)
        
        sensitive_urls = [
            "/.env",
            "/settings.py",
            "/admin/",
            "/debug/",
            "/.git/config",
            "/robots.txt",
            "/sitemap.xml",
            "/../../../etc/passwd",
            "/static/admin/",
        ]
        
        for url in sensitive_urls:
            try:
                response = self.session.get(urljoin(self.base_url, url))
                
                if response.status_code == 200:
                    if "SECRET_KEY" in response.text or "password" in response.text.lower():
                        self.vulnerabilities.append(f"Información sensible expuesta: {url}")
                        print(f"⚠️  Información expuesta en: {url}")
                    else:
                        print(f"🔍 Accesible pero seguro: {url}")
                else:
                    print(f"✅ Protegido: {url} ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
    
    def login_test_user(self):
        """Helper: Login con usuario de test"""
        try:
            if not self.csrf_token:
                self.get_csrf_token()
            
            # Intentar login con credenciales de demo
            data = {
                'username': 'juan_costa',
                'password': 'demo123',
                'csrfmiddlewaretoken': self.csrf_token
            }
            
            response = self.session.post(
                urljoin(self.base_url, "/login/"),
                data=data
            )
            
            return "dashboard" in response.url or response.status_code == 302
            
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def test_directory_traversal(self):
        """🔍 Test 8: Directory Traversal"""
        print("\n🔍 TEST 8: DIRECTORY TRAVERSAL")
        print("-" * 30)
        
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        for payload in traversal_payloads:
            try:
                # Test en parámetros de búsqueda
                response = self.session.get(
                    urljoin(self.base_url, "/avisos/"),
                    params={'file': payload}
                )
                
                if "root:" in response.text or "localhost" in response.text:
                    self.vulnerabilities.append(f"Directory traversal: {payload}")
                    print(f"⚠️  Directory traversal: {payload}")
                else:
                    print(f"✅ Payload bloqueado: {payload}")
                    
            except Exception as e:
                print(f"❌ Error en traversal test: {e}")
    
    def generate_report(self):
        """📊 Generar reporte final"""
        print("\n" + "=" * 60)
        print("📊 REPORTE DE SEGURIDAD")
        print("=" * 60)
        
        if not self.vulnerabilities:
            print("🎉 ¡EXCELENTE! No se encontraron vulnerabilidades críticas.")
            print("✅ Tu aplicación pasó todos los tests básicos de seguridad.")
        else:
            print(f"⚠️  Se encontraron {len(self.vulnerabilities)} vulnerabilidades:")
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"   {i}. {vuln}")
        
        print("\n📋 RECOMENDACIONES GENERALES:")
        print("   • Mantén Django actualizado")
        print("   • Usa HTTPS en producción")
        print("   • Configura rate limiting")
        print("   • Implementa logging de seguridad")
        print("   • Realiza backups regulares")
        print("   • Monitorea accesos sospechosos")
        
        print(f"\n🏁 Tests completados en: {self.base_url}")
    
    def run_all_tests(self):
        """🚀 Ejecutar todos los tests"""
        print("🚀 INICIANDO EVALUACIÓN COMPLETA DE SEGURIDAD")
        print("=" * 60)
        
        # Obtener token CSRF inicial
        self.get_csrf_token()
        
        # Ejecutar todos los tests
        self.test_sql_injection()
        self.test_xss()
        self.test_csrf()
        self.test_authentication_bypass()
        self.test_brute_force()
        self.test_file_upload_vulnerabilities()
        self.test_information_disclosure()
        self.test_directory_traversal()
        
        # Generar reporte
        self.generate_report()

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://127.0.0.1:8000"
    
    print("🛡️  COSTA LAGUNA SEGURA - SECURITY TESTER")
    print("==========================================")
    print("⚠️  SOLO PARA USO ÉTICO EN TU PROPIA APP")
    print(f"🎯 Target: {base_url}")
    print()
    
    # Confirmar que es su propia aplicación
    confirm = input("¿Confirmas que esta es TU aplicación? (si/no): ")
    if confirm.lower() not in ['si', 's', 'yes', 'y']:
        print("❌ Test cancelado. Solo usa esto en tus propias aplicaciones.")
        return
    
    # Ejecutar tests
    tester = SecurityTester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()

"""
📖 INSTRUCCIONES DE USO:
=======================

1. Asegúrate de que tu aplicación Django esté corriendo:
   python manage.py runserver

2. Instala requests si no lo tienes:
   pip install requests

3. Ejecuta este script:
   python security_test.py http://127.0.0.1:8000

4. Revisa el reporte de vulnerabilidades

5. Implementa las correcciones sugeridas

⚠️  IMPORTANTE: Solo usar en aplicaciones propias
🎯 Este script es para evaluación ética de seguridad
"""