# Generated by Django 5.1.7 on 2025-04-04 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0002_trabajador_codigo_qr'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='curp',
            field=models.CharField(blank=True, max_length=18, null=True),
        ),
        migrations.AddField(
            model_name='trabajador',
            name='nss',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
