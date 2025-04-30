# gestion_obra/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from asistencia.views import bienvenido_view  # Asegúrate de que esté definida

# Vista simple para la página principal (opcional)
def home(request):
    return HttpResponse("Bienvenido a Costructora Electromecánica TASAL - Centro de Gestión")

urlpatterns = [
    path('admin/', admin.site.urls),
    # Rutas de autenticación:
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Página principal (opcional)
    path('', home, name='home'),
    # Vista de bienvenida:
    path('bienvenido/', bienvenido_view, name='bienvenido'),
    # Incluir las rutas de la app "asistencia":
    path('api/', include('asistencia.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
