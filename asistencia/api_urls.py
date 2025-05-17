# asistencia/api_urls.py

from django.urls import include, path
from rest_framework import routers
from .views import ProyectoViewSet, TrabajadorViewSet, AsistenciaViewSet

router = routers.DefaultRouter()
router.register(r'proyectos',    ProyectoViewSet)
router.register(r'trabajadores', TrabajadorViewSet)
router.register(r'asistencias',  AsistenciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
