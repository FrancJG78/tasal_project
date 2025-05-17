# gestion_obra/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from asistencia.views import bienvenido_view

# Vista sencilla para la página principal
def home(request):
    return HttpResponse("Bienvenido a Constructora Electromecánica TASAL - Centro de Gestión")

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Login / Logout
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='registration/login.html'),
         name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    # Home y Bienvenida
    path('', home, name='home'),
    path('bienvenido/', bienvenido_view, name='bienvenido'),

    # API REST (ModelViewSets)
    path('api/', include('asistencia.api_urls')),

    # Vistas web de la app Asistencia (scanner, formularios…)
    path('asistencia/', include('asistencia.urls')),
]

# Servir media en DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
