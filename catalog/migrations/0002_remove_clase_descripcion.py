# Generated by Django 5.0.3 on 2024-10-12 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clase',
            name='descripcion',
        ),
    ]
