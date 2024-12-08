from django.db import models
from datetime import date
from django.contrib.auth.models import User

# Create your models here.
from django.urls import reverse #Used to generate URLs by reversing the URL patterns

class Horario(models.Model):
    
    dia = models.CharField(max_length=10, choices=[
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'), ('Viernes', 'Viernes')], null=True, blank=True)
    # dia = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='horarios', null=True, blank=True)

    def __str__(self):
        return f'{self.dia} ({self.hora_inicio} - {self.hora_fin})'

class Clase(models.Model):

    nombre = models.CharField(max_length=200)
    profesor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    horario = models.ManyToManyField(Horario)

    class Meta:
        permissions = [
            ("puede_gestionar_clases", "Puede gestionar las clases"),
            ("puede_ver_reservas_profesor", "Puede ver las reservas de los alumnos en las clases del profesor"),
            ("puede_realizar_reservas", "Puede realizar reservas"),
            ("puede_ver_reservas_alumno", "Puede ver sus reservas que ha hecho"),
        ]

    def __str__(self):
        
        return self.nombre


    def get_absolute_url(self):
        """
        Devuelve el URL a una instancia particular de Clase
        """
        return reverse('clase-detail', args=[str(self.id)])
    
import uuid # Requerida para las instancias

class ClaseInstancia(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="ID único para este hueco de la clase")
    clase = models.ForeignKey('Clase', on_delete=models.SET_NULL, null=True)
    horario = models.ForeignKey('Horario', on_delete=models.SET_NULL, null=True, help_text="Horario asignado para esta instancia de la clase")
    alumno = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')
   
    # Definimos los estados posibles del hueco de la clase
    CLASE_STATUS = (
        ('d', 'Disponible'),
        ('r', 'Reservada'),
    )

    status = models.CharField(
        max_length=1,
        choices=CLASE_STATUS,
        blank=True,
        default='d',  # Por defecto, un hueco está disponible
        help_text='Estado del hueco de la clase'
    )

    def __str__(self):
        if self.clase:
            return '%s (%s)' % (self.id, self.clase.nombre)
        else:
            return '%s (Clase no asignada)' % (self.id)