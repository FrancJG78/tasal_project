# asistencia/models.py

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

class Trabajador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    fotografia = models.ImageField(upload_to='trabajadores/', null=True, blank=True)
    proyectos = models.ManyToManyField(Proyecto, related_name='trabajadores')
    codigo_qr = models.ImageField(upload_to='codigos_qr/', null=True, blank=True)

    # NUEVOS CAMPOS:
    curp = models.CharField(max_length=18, null=True, blank=True)
    nss = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codigo_qr:
            qr_data = f"http://127.0.0.1:8000/api/registrar-qr/{self.id}/"
            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            filename = f"trabajador_{self.id}_qr.png"
            self.codigo_qr.save(filename, File(buffer), save=False)
            buffer.close()
            super().save(*args, **kwargs)

class Asistencia(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='asistencias')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    presente = models.BooleanField(default=False)

    class Meta:
        unique_together = ('trabajador', 'proyecto', 'fecha')
        ordering = ['fecha']

    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        return f"{self.trabajador} - {self.fecha}: {estado}"
