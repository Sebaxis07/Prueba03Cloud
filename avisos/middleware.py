from django.http import HttpResponseForbidden
from django.shortcuts import redirect
import logging

logger = logging.getLogger('security')

class AdminProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path.startswith('/admin/') and request.path != '/admin/':
            logger.warning(f"Intento de acceso a admin desde IP: {request.META.get('REMOTE_ADDR')}")
            return HttpResponseForbidden("Acceso no autorizado")
        
        if request.path.startswith('/secure-admin-costa-laguna/'):
            if not request.user.is_authenticated:
                return redirect('/login/')
            if not request.user.is_staff:
                return redirect('/')
        
        return self.get_response(request)