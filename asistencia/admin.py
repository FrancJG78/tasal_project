from django.contrib import admin
from .models import Proyecto, Trabajador, Asistencia

admin.site.register(Proyecto)
admin.site.register(Trabajador)
admin.site.register(Asistencia)
