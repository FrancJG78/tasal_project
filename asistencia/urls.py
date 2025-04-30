# asistencia/urls.py
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
    bienvenido_view  # Asegúrate de que esté definida en views.py
)

router = routers.DefaultRouter()
router.register(r'proyectos', ProyectoViewSet)
router.register(r'trabajadores', TrabajadorViewSet)
router.register(r'asistencias', AsistenciaViewSet)

urlpatterns = [
    # Rutas de los ViewSets de la API REST:
    path('', include(router.urls)),
    # Endpoint para registrar asistencia vía JSON:
    path('registrar/', RegistrarAsistenciaView.as_view(), name='registrar-asistencia'),
    # Endpoint para exportar asistencia a Excel:
    path('exportar/', ExportarAsistenciaExcelView.as_view(), name='exportar-asistencia'),
    # Vista web para mostrar la asistencia de un proyecto:
    path('vista/<int:project_id>/', asistencia_view, name='asistencia-view'),
    # Vista para procesar el formulario de asistencia manual:
    path('registrar-form/', registrar_asistencia_form_view, name='asistencia-form-post'),
    # Endpoint para registrar asistencia vía QR:
    path('registrar-qr/<int:trabajador_id>/', RegistrarAsistenciaQRView.as_view(), name='registrar-qr'),
    # Vista para dar de alta un trabajador:
    path('alta-trabajador/', alta_trabajador_view, name='alta-trabajador'),
    # Vista para seleccionar proyecto y registrar asistencia:
    path('asistencia-elegir/', asistencia_elegir_proyecto_view, name='asistencia-elegir'),
    # Vista de bienvenida:
    path('bienvenido/', bienvenido_view, name='bienvenido'),
]
