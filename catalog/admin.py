from django.contrib import admin
from .models import Horario, Clase, ClaseInstancia

# Personalización para mostrar ClaseInstancia en forma de tabla dentro de Clase
class ClaseInstanciaInline(admin.TabularInline):
    model = ClaseInstancia  # Modelo relacionado
    extra = 0  # No mostrar instancias extra vacías para agregar nuevas por defecto
    fields = ['id', 'horario', 'status', 'alumno']  # Campos a mostrar en la tabla
    readonly_fields = ['id']  # Hacer el ID solo de lectura

# Personalización para el modelo Clase
@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor')  # Mostrar el nombre de la clase y el profesor asignado
    list_filter = ('profesor',)  # Filtros por profesor
    filter_horizontal = ('horario',)  # Permitir la selección de varios horarios de manera horizontal
    inlines = [ClaseInstanciaInline]  # Mostrar las instancias de clases como un Inline dentro de Clase

# Personalización para el modelo Horario
@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('dia', 'hora_inicio', 'hora_fin')  # Campos que se muestran en la lista de horarios
    list_filter = ('dia',)  # Filtros por día de la semana

# Personalización para el modelo ClaseInstancia
@admin.register(ClaseInstancia)
class ClaseInstanciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'clase', 'horario', 'status', 'alumno')  # Mostrar ID, clase, horario, estado y alumno
    list_filter = ('status', 'clase', 'horario')  # Filtrar por estado, clase y horario
    ordering = ['clase', 'horario']  # Ordenar por clase y horario