# Generated by Django 5.0.3 on 2024-10-14 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_clase_profesor_alter_claseinstancia_alumno'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clase',
            options={'permissions': [('puede_gestionar_clases', 'Puede gestionar las clases'), ('puede_ver_reservas_profesor', 'Puede ver las reservas de los alumnos en las clases del profesor')]},
        ),
    ]
