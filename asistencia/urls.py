from django.urls import path, include
from rest_framework import routers
from .views import (
    ProyectoViewSet,
    TrabajadorViewSet,
    AsistenciaViewSet,
    RegistrarAsistenciaView,
    ExportarAsistenciaExcelView,
    asistencia_view,
    registrar_asistencia_form_view,
    RegistrarAsistenciaQRView,
    alta_trabajador_view,
    asistencia_elegir_proyecto_view,
    bienvenido_view
)

router = routers.DefaultRouter()
router.register(r'proyectos',    ProyectoViewSet)
router.register(r'trabajadores', TrabajadorViewSet)
router.register(r'asistencias',  AsistenciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registrar/',      RegistrarAsistenciaView.as_view(),       name='registrar-asistencia'),
    path('exportar/',       ExportarAsistenciaExcelView.as_view(),   name='exportar-asistencia'),
    path('vista/<int:project_id>/', asistencia_view,                name='asistencia-view'),
    path('registrar-form/', registrar_asistencia_form_view,         name='asistencia-form-post'),
    path('registrar-qr/<int:trabajador_id>/', RegistrarAsistenciaQRView.as_view(), name='registrar-qr'),
    path('alta-trabajador/', alta_trabajador_view,                  name='alta-trabajador'),
    path('asistencia-elegir/', asistencia_elegir_proyecto_view,     name='asistencia-elegir'),
    path('bienvenido/',      bienvenido_view,                       name='bienvenido'),
]
