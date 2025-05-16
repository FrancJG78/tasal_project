import os
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models


class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Dispositivo(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    nombre    = models.CharField(max_length=100, blank=True)
    proyectos = models.ManyToManyField(Proyecto, related_name="dispositivos")

    def __str__(self):
        return self.device_id


class SesionAsistencia(models.Model):
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.CASCADE,
        related_name="sesiones"
    )
    proyecto   = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="sesiones"
    )
    fecha      = models.DateField()
    hora_base  = models.DateTimeField()

    class Meta:
        unique_together = ("dispositivo", "proyecto", "fecha")
        ordering = ["fecha"]


class Trabajador(models.Model):
    nombre           = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    categoria        = models.CharField(max_length=100)
    telefono         = models.CharField(max_length=20)
    fotografia       = models.ImageField(upload_to='trabajadores/', null=True, blank=True)
    proyectos        = models.ManyToManyField(Proyecto, related_name='trabajadores')
    codigo_qr        = models.ImageField(upload_to='codigos_qr/', null=True, blank=True)

    # NUEVOS CAMPOS:
    curp = models.CharField(max_length=18, null=True, blank=True)
    nss  = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codigo_qr:
            qr_data = f"http://127.0.0.1:8000/api/registrar-qr/{self.id}/?device_id={device_id}"
            qr_img  = qrcode.make(qr_data)
            buffer  = BytesIO()
            qr_img.save(buffer, format="PNG")
            filename = f"trabajador_{self.id}_qr.png"
            self.codigo_qr.save(filename, File(buffer), save=False)
            buffer.close()
            super().save(*args, **kwargs)


class Asistencia(models.Model):
    trabajador   = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='asistencias')
    proyecto     = models.ForeignKey(Proyecto,   on_delete=models.CASCADE, related_name='asistencias')
    fecha        = models.DateField()
    presente     = models.BooleanField(default=False)
    tipo_retraso = models.CharField(
        max_length=20,
        choices=[
            ('puntual',      'Puntual'),
            ('retardo_leve', 'Retardo leve'),
            ('retardo_alto', 'Retardo alto'),
        ],
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('trabajador', 'proyecto', 'fecha')
        ordering = ['fecha']

    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        return f"{self.trabajador} - {self.fecha}: {estado}"
