from django.contrib import admin
from .models import Proyecto, Trabajador, Asistencia
from .models import Dispositivo

admin.site.register(Proyecto)
admin.site.register(Trabajador)
admin.site.register(Asistencia)
from django.contrib import admin
from .models import Dispositivo, SesionAsistencia

# Registra ambos modelos para que los veas en el panel de Admin
admin.site.register(Dispositivo)
admin.site.register(SesionAsistencia)
