# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from avisos.admin import admin_site  # Import the custom admin site

urlpatterns = [
     path('admin/', RedirectView.as_view(url='/', permanent=False)),  # Use custom admin site instead of default
    path('', include('avisos.urls')),
    path('panel-admin/', include('avisos.adminurls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

