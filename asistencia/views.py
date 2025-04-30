# asistencia/views.py

from django.http import HttpResponse
from django.contrib import messages
from rest_framework import viewsets
from .models import Proyecto, Trabajador, Asistencia
from .serializers import ProyectoSerializer, TrabajadorSerializer, AsistenciaSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime, date, timedelta

# =======================================================
# ViewSets para API REST
# =======================================================
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer

class TrabajadorViewSet(viewsets.ModelViewSet):
    queryset = Trabajador.objects.all()
    serializer_class = TrabajadorSerializer

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer

# =======================================================
# Vista para seleccionar proyecto y mostrar asistencia
# =======================================================
def asistencia_elegir_proyecto_view(request):
    """
    Vista para seleccionar un proyecto mediante un formulario.
    Si se selecciona un proyecto (vía GET), se muestran sus trabajadores.
    """
    proyectos = Proyecto.objects.all().order_by('nombre')
    project_id = request.GET.get('project_id')
    selected_project = None
    trabajadores = []

    if project_id:
        selected_project = get_object_or_404(Proyecto, pk=project_id)
        trabajadores = selected_project.trabajadores.all().order_by('apellido_paterno', 'apellido_materno')

    context = {
        'proyectos': proyectos,
        'selected_project': selected_project,
        'trabajadores': trabajadores,
    }
    return render(request, 'asistencia/asistencia_elegir.html', context)

# =======================================================
# Registrar asistencia vía JSON (API)
# =======================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegistrarAsistenciaView(APIView):
    """
    Endpoint para registrar la asistencia diaria de los trabajadores de un proyecto.
    Se espera un payload JSON con la siguiente estructura:
    {
      "project": <project_id>,
      "date": "YYYY-MM-DD",
      "asistencias": [
         {"trabajador": <trabajador_id>, "presente": true/false},
         ...
      ]
    }
    """
    def post(self, request):
        data = request.data
        project_id = data.get("project")
        fecha_str = data.get("date")
        asistencias_data = data.get("asistencias", [])

        if not project_id or not fecha_str:
            return Response({"error": "Project and date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Date format must be YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        proyecto = get_object_or_404(Proyecto, pk=project_id)
        results = []

        for item in asistencias_data:
            trabajador_id = item.get("trabajador")
            presente = item.get("presente", False)
            try:
                trabajador = Trabajador.objects.get(pk=trabajador_id)
            except Trabajador.DoesNotExist:
                results.append({"trabajador": trabajador_id, "error": "Trabajador not found."})
                continue

            asistencia, created = Asistencia.objects.update_or_create(
                trabajador=trabajador,
                proyecto=proyecto,
                fecha=fecha,
                defaults={"presente": presente}
            )
            results.append({"trabajador": trabajador_id, "created": created, "presente": presente})

        return Response({"status": "success", "results": results}, status=status.HTTP_200_OK)

# =======================================================
# Exportar asistencia a Excel (versión simple)
# =======================================================
import openpyxl

class ExportarAsistenciaExcelView(APIView):
    """
    Endpoint para exportar la asistencia a Excel según un rango de fechas y proyecto (versión simple).
    Se esperan los parámetros GET: project_id, start_date, end_date.
    """
    def get(self, request):
        project_id = request.GET.get('project_id')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not project_id or not start_date_str or not end_date_str:
            return HttpResponse("project_id, start_date, and end_date are required parameters.", status=400)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Date format must be YYYY-MM-DD.", status=400)

        proyecto = get_object_or_404(Proyecto, pk=project_id)
        trabajadores = proyecto.trabajadores.all().order_by('apellido_paterno', 'apellido_materno')
        delta = end_date - start_date
        fechas = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Asistencia"

        # Encabezados simples
        ws.cell(row=1, column=1, value="Nombre Completo")
        ws.cell(row=1, column=2, value="Categoría")
        for idx, fecha in enumerate(fechas, start=3):
            day_mapping = {0: "L", 1: "M", 2: "MX", 3: "J", 4: "V", 5: "S", 6: "D"}
            day_abbr = day_mapping[fecha.weekday()]
            fecha_str = fecha.strftime("%d/%m/%y")
            ws.cell(row=1, column=idx, value=f"{day_abbr} {fecha_str}")

        # Llenar datos
        for row_idx, trabajador in enumerate(trabajadores, start=2):
            nombre_completo = f"{trabajador.nombre} {trabajador.apellido_paterno} {trabajador.apellido_materno}"
            ws.cell(row=row_idx, column=1, value=nombre_completo)
            ws.cell(row=row_idx, column=2, value=trabajador.categoria)
            for col_idx, fecha in enumerate(fechas, start=3):
                try:
                    asistencia = Asistencia.objects.get(trabajador=trabajador, proyecto=proyecto, fecha=fecha)
                    celda_valor = "✓" if asistencia.presente else "X"
                except Asistencia.DoesNotExist:
                    celda_valor = ""
                ws.cell(row=row_idx, column=col_idx, value=celda_valor)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        filename = f"asistencia_{project_id}_{start_date_str}_to_{end_date_str}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

# =======================================================
# Vista web para mostrar asistencia (una sola lista)
# =======================================================
@login_required
def asistencia_view(request, project_id):
    proyecto = get_object_or_404(Proyecto, pk=project_id)
    trabajadores = proyecto.trabajadores.all().order_by('apellido_paterno', 'apellido_materno')
    fecha_actual = date.today().strftime("%Y-%m-%d")
    context = {
        'proyecto': proyecto,
        'trabajadores': trabajadores,
        'fecha': fecha_actual,
    }
    return render(request, 'asistencia/asistencia.html', context)

# =======================================================
# Registrar asistencia desde un formulario (manual)
# =======================================================
def registrar_asistencia_form_view(request):
    """
    Procesa el formulario enviado desde la plantilla de asistencia y registra la asistencia.
    """
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        fecha_str = request.POST.get("fecha")

        if not project_id or not fecha_str:
            messages.error(request, "Faltan datos para registrar la asistencia.")
            return redirect('alta_trabajador')

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return redirect('alta_trabajador')

        proyecto = get_object_or_404(Proyecto, pk=project_id)
        trabajadores = proyecto.trabajadores.all()

        for trabajador in trabajadores:
            checkbox_name = f"asistencia_{trabajador.id}"
            presente = checkbox_name in request.POST  # True si el checkbox está marcado
            Asistencia.objects.update_or_create(
                trabajador=trabajador,
                proyecto=proyecto,
                fecha=fecha,
                defaults={"presente": presente}
            )

        messages.success(request, "Asistencia registrada con éxito.")
        from django.urls import reverse
        url_asistencia_elegir = reverse('asistencia-elegir')
        return redirect(f"{url_asistencia_elegir}?project_id={project_id}")

    return redirect('alta_trabajador')

# =======================================================
# Alta de trabajador (con foto base64)
# =======================================================
import base64
import io
from PIL import Image
import qrcode
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.core.files.base import ContentFile

from .models import Proyecto, Trabajador, Asistencia

def alta_trabajador_view(request):
    proyectos = Proyecto.objects.all()
    if request.method == "POST":
        # Recopilar los datos del formulario
        nombre = request.POST.get('nombre')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        categoria = request.POST.get('categoria')
        telefono = request.POST.get('telefono')
        curp = request.POST.get('curp')
        nss = request.POST.get('nss')
        proyectos_ids = request.POST.getlist('proyectos')

        # Crear el objeto trabajador (sin guardar aún)
        trabajador = Trabajador(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            categoria=categoria,
            telefono=telefono,
            curp=curp,
            nss=nss
        )

        # Procesar la fotografía (suponiendo que se recibe en base64)
        foto_data = request.POST.get('fotografia')
        if foto_data:
            try:
                format, imgstr = foto_data.split(';base64,')
                img_data = base64.b64decode(imgstr)
                image = Image.open(io.BytesIO(img_data))
                image = image.resize((300, 400))
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                trabajador.fotografia.save(
                    "trabajador_foto.png",
                    ContentFile(buffer.getvalue()),
                    save=False
                )
            except Exception as e:
                messages.error(request, "Error al procesar la fotografía.")

        # Guardar el trabajador y asignar proyectos, si los hay
        trabajador.save()
        if proyectos_ids:
            trabajador.proyectos.set(proyectos_ids)
            
        messages.success(request, "Trabajador dado de alta correctamente.")

        # --- GENERACIÓN DEL CÓDIGO QR ---
        # Aquí se genera el QR con la información que usarás en la asistencia diaria.
        # Por ejemplo, puedes incluir el ID, nombre y/o algún token único.
        qr_data = f"{trabajador.id}-{trabajador.nombre} {trabajador.apellido_paterno}"
        qr_img = qrcode.make(qr_data)
        buffer_qr = io.BytesIO()
        qr_img.save(buffer_qr, format='PNG')
        qr_image_base64 = base64.b64encode(buffer_qr.getvalue()).decode("utf-8")
        # --- FIN GENERACIÓN DEL QR ---

        # Preparamos un contexto en el que además del listado de proyectos incluimos
        # 'nueva_credencial' con el trabajador recién creado y la imagen QR.
        context = {
            'proyectos': proyectos,
            'nueva_credencial': trabajador,
            'qr_image_base64': qr_image_base64,
        }
        return render(request, 'asistencia/alta_trabajador.html', context)
    else:
        # GET: Mostrar el formulario vacío
        return render(request, 'asistencia/alta_trabajador.html', {'proyectos': proyectos})

# =======================================================
# Registrar Asistencia vía QR
# =======================================================
class RegistrarAsistenciaQRView(APIView):
    """
    Endpoint para registrar la asistencia de un trabajador automáticamente al escanear su código QR.
    Se registra la asistencia para la fecha actual.
    """
    def get(self, request, trabajador_id):
        trabajador = get_object_or_404(Trabajador, pk=trabajador_id)
        proyecto = trabajador.proyectos.first()
        if not proyecto:
            return Response(
                {"error": "El trabajador no está asignado a ningún proyecto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        asistencia, created = Asistencia.objects.update_or_create(
            trabajador=trabajador,
            proyecto=proyecto,
            fecha=date.today(),
            defaults={"presente": True}
        )
        message = "Asistencia registrada." if created else "Asistencia actualizada."
        return Response({"message": message, "trabajador_id": trabajador.id}, status=status.HTTP_200_OK)

# =======================================================
# Vista de Bienvenida
# =======================================================
def bienvenido_view(request):
    return render(request, 'bienvenido.html')

# =======================================================
# Exportar asistencia a Excel (versión avanzada con estilos)
# =======================================================
from openpyxl.utils import get_column_letter
class ExportarAsistenciaExcelView(APIView):
    """
    Endpoint para exportar la asistencia a Excel con estilos, según un rango de fechas y proyecto.
    Parámetros GET esperados:
      - project_id: ID del proyecto.
      - start_date: Fecha de inicio en formato YYYY-MM-DD.
      - end_date: Fecha de fin en formato YYYY-MM-DD.
      - filter_days (opcional): días a filtrar, por ejemplo 0,2,4 (lunes, miércoles, viernes).
    """
    def get(self, request):
        from django.http import HttpResponse
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        project_id = request.GET.get('project_id')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        filter_days_str = request.GET.get('filter_days')  # Opcional

        if not project_id or not start_date_str or not end_date_str:
            return HttpResponse("project_id, start_date, and end_date are required parameters.", status=400)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Date format must be YYYY-MM-DD.", status=400)

        proyecto = get_object_or_404(Proyecto, pk=project_id)
        trabajadores = proyecto.trabajadores.all().order_by('apellido_paterno', 'apellido_materno')

        delta = end_date - start_date
        fechas = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

        if filter_days_str:
            try:
                filter_days = set(int(x.strip()) for x in filter_days_str.split(",") if x.strip() != "")
                fechas = [f for f in fechas if f.weekday() in filter_days]
            except ValueError:
                return HttpResponse("filter_days must be a comma-separated list of numbers (0-6).", status=400)

        wb = Workbook()
        ws = wb.active
        ws.title = "Asistencia"

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center")
        thick_border = Border(
            left=Side(style='thick'),
            right=Side(style='thick'),
            top=Side(style='thick'),
            bottom=Side(style='thick')
        )

        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4 + len(fechas))
        title_cell = ws.cell(row=1, column=1, value=f"TASAL - Reporte de Asistencia - Proyecto: {proyecto.nombre}")
        title_cell.font = Font(bold=True, size=14)
        title_cell.alignment = center_align
        title_cell.border = thick_border

        header_row = 3

        headers = ["Nombre Completo", "Categoría", "CURP", "NSS"]
        for col_idx, header_text in enumerate(headers, start=1):
            cell = ws.cell(row=header_row, column=col_idx, value=header_text)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thick_border

        day_mapping = {0: "L", 1: "M", 2: "MX", 3: "J", 4: "V", 5: "S", 6: "D"}
        for idx, fecha in enumerate(fechas, start=5):
            day_abbr = day_mapping.get(fecha.weekday(), "")
            fecha_str = fecha.strftime("%d/%m/%y")
            cell = ws.cell(row=header_row, column=idx, value=f"{day_abbr} {fecha_str}")
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thick_border

        ws.column_dimensions['A'].width = 30  # Nombre
        ws.column_dimensions['B'].width = 25  # Categoría
        ws.column_dimensions['C'].width = 25  # CURP
        ws.column_dimensions['D'].width = 25  # NSS

        # Ajustar ancho de las columnas de fechas a 15
        for col in range(5, 5 + len(fechas)):
            col_letter = get_column_letter(col)
            ws.column_dimensions[col_letter].width = 15

        row_idx = header_row + 1
        for trabajador in trabajadores:
            nombre_completo = f"{trabajador.nombre} {trabajador.apellido_paterno} {trabajador.apellido_materno}"
            cell_A = ws.cell(row=row_idx, column=1, value=nombre_completo)
            cell_A.border = thick_border

            cell_B = ws.cell(row=row_idx, column=2, value=trabajador.categoria)
            cell_B.border = thick_border

            cell_C = ws.cell(row=row_idx, column=3, value=(trabajador.curp or ""))
            cell_C.border = thick_border

            cell_D = ws.cell(row=row_idx, column=4, value=(trabajador.nss or ""))
            cell_D.border = thick_border

            col_idx = 5
            for fecha in fechas:
                try:
                    asistencia = Asistencia.objects.get(
                        trabajador=trabajador,
                        proyecto=proyecto,
                        fecha=fecha
                    )
                    if asistencia.presente:
                        celda_valor = 1
                        fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    else:
                        celda_valor = 0
                        fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                except Asistencia.DoesNotExist:
                    celda_valor = ""
                    fill = None

                cell = ws.cell(row=row_idx, column=col_idx, value=celda_valor)
                cell.border = thick_border
                cell.alignment = center_align
                if fill:
                    cell.fill = fill
                col_idx += 1

            row_idx += 1

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        filename = f"asistencia_{project_id}_{start_date_str}_to_{end_date_str}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response
