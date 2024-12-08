from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ClaseForm, HorarioForm, RegistroForm, ProfileForm
from .models import Clase, ClaseInstancia, Horario

import matplotlib
matplotlib.use('Agg')  # Configurar backend no interactivo antes de importar pyplot
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Count

def inicio(request):
    """
    Función vista para la página inicio del sitio.
    """
    # Genera contadores de algunos de los objetos principales
    num_clases=Clase.objects.all().count()
    num_instancias=ClaseInstancia.objects.all().count()
    # Sitios disponibles (status = 'd')
    num_instancias_disponibles=ClaseInstancia.objects.filter(status__exact='d').count()
    num_horarios=Horario.objects.all().count()

    # Renderiza la plantilla HTML inicio.html con los datos en la variable contexto
    return render(
        request,
        'inicio.html',
        context={'num_clases':num_clases,'num_instancias':num_instancias,'num_instancias_disponibles':num_instancias_disponibles, 'num_horarios':num_horarios},
    )

# Vista para listar todas las clases
@login_required
@permission_required('catalog.puede_realizar_reservas', raise_exception=True)
def clase_list(request):
    clases = Clase.objects.all()
    return render(request, 'catalog/clase_list.html', {'clases': clases})

# Vista para mostrar el detalle de una clase
@login_required
@permission_required('catalog.puede_realizar_reservas', raise_exception=True)
def clase_detail(request, clase_id):
    clase = get_object_or_404(Clase, id=clase_id)
    horarios = clase.horario.all()
    instancias = ClaseInstancia.objects.filter(clase=clase)  # Todas las instancias de la clase
    
    # Para cada horario, asociar una instancia disponible y verificar si el alumno ya tiene una reserva
    horarios_con_instancias = []
    for horario in horarios:
        # Verificar si el alumno ya tiene una reserva en este horario
        reserva_existente = instancias.filter(horario=horario, alumno=request.user).exists()

        # Obtener una instancia disponible para el horario
        instancia_disponible = instancias.filter(horario=horario, status='d').first()

        # Guardar el horario, la instancia disponible y si el alumno ya tiene una reserva
        horarios_con_instancias.append((horario, instancia_disponible, reserva_existente))

    # Pasamos la información a la plantilla
    return render(request, 'catalog/clase_detail.html', {
        'clase': clase,
        'horarios_con_instancias': horarios_con_instancias,  # Pasamos la lista de tuplas (horario, instancia)
        'instancias': instancias,  # Todas las instancias (reservadas o no)
    })

# Vista para que el alumno reserve una instancia de clase
@login_required
@permission_required('catalog.puede_realizar_reservas', raise_exception=True)
def reservar_clase(request, claseinstancia_id):
    clase_instancia = get_object_or_404(ClaseInstancia, id=claseinstancia_id, status='d')  # Solo instancias disponibles
    if request.method == 'POST':
        clase_instancia.alumno = request.user  # Asignar el alumno que reserva
        clase_instancia.status = 'r'  # Cambiar el estado a reservada
        clase_instancia.save()
        messages.success(request, 'Reserva realizada correctamente.')
        return redirect('mis_reservas')  # Redirigir al listado de reservas del alumno

    return render(request, 'catalog/reservar_clase.html', {'clase_instancia': clase_instancia})

# Vista para mostrar las reservas del alumno
@login_required
@permission_required('catalog.puede_ver_reservas_alumno')
def mis_reservas(request):
    # Obtener las reservas del usuario
    reservas = ClaseInstancia.objects.filter(alumno=request.user)

    # Contar reservas por profesor
    reservas_por_profesor = reservas.values('clase__profesor__username').annotate(total=Count('id')).order_by('clase__profesor__username')

    # Preparar datos para gráfico circular de profesores
    profesores = [r['clase__profesor__username'] for r in reservas_por_profesor]
    num_reservas_profesor = [r['total'] for r in reservas_por_profesor]

    # Generar el gráfico circular
    def generar_grafico(labels, data):
        fig, ax = plt.subplots()
        ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Mantener el gráfico circular
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return image_base64

    grafico_profesor = generar_grafico(profesores, num_reservas_profesor)

    # Renderizar la plantilla con las reservas y el gráfico
    return render(request, 'catalog/mis_reservas.html', {
        'reservas': reservas,
        'grafico_profesor': grafico_profesor,
    })

@login_required
@permission_required('catalog.puede_realizar_reservas', raise_exception=True)
def cancelar_reserva(request, claseinstancia_id):
    # Obtener la instancia de clase que se desea cancelar
    clase_instancia = get_object_or_404(ClaseInstancia, id=claseinstancia_id)

    # Asegurarse de que el usuario que está intentando cancelar la reserva sea el mismo que reservó
    if clase_instancia.alumno != request.user:
        return redirect('mis_reservas')  # Redirigir al listado de reservas si no es el dueño de la reserva

    if request.method == 'POST':
        clase_instancia.alumno = None  # Eliminar el alumno de la reserva
        clase_instancia.status = 'd'  # Cambiar el estado a disponible
        clase_instancia.save()

        # Mensaje de éxito
        messages.success(request, 'Has cancelado tu reserva correctamente.')

        return redirect('mis_reservas')  # Redirigir al listado de reservas tras cancelar

    return render(request, 'catalog/cancelar_reserva.html', {'clase_instancia': clase_instancia})

@login_required
@permission_required('catalog.puede_gestionar_clases')
def gestionar_clases(request):
    if request.method == 'POST':
        form = ClaseForm(request.POST, user=request.user)  # Pasar el usuario al formulario
        if form.is_valid():
            clase = form.save(commit=False)
            clase.profesor = request.user  # Asignar el profesor a la clase
            clase.save()
            form.save_m2m()

            # Crear instancias de la clase y asociarlas a los horarios
            num_instancias = form.cleaned_data['num_instancias']
            horarios = clase.horario.all()  # Obtener los horarios asociados a la clase

            for i in range(num_instancias):
                for horario in horarios:
                    ClaseInstancia.objects.create(clase=clase, horario=horario, status='d')
    
            messages.success(request, 'La clase ha sido creada correctamente.')
            return redirect('gestionar_clases')
    else:
        form = ClaseForm(user=request.user)  # Pasar el usuario al formulario

    clases = Clase.objects.filter(profesor=request.user)
    return render(request, 'catalog/gestionar_clases.html', {'form': form, 'clases': clases})

@login_required
@permission_required('catalog.puede_ver_reservas_profesor')
def ver_reservas_profesor(request):
    clases = Clase.objects.filter(profesor=request.user)  # Clases impartidas por el profesor logueado
    instancias = ClaseInstancia.objects.filter(clase__profesor=request.user).select_related('alumno', 'horario')

    return render(request, 'catalog/ver_reservas_profesor.html', {
        'clases': clases,
        'instancias': instancias
    })

@login_required
@permission_required('catalog.puede_gestionar_clases')  # Asegúrate de que solo los profesores tengan acceso
def gestionar_horarios(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.profesor = request.user  # Asigna el profesor al horario
            horario.save()
            messages.success(request, 'El horario ha sido creado correctamente.')
            return redirect('gestionar_horarios')  # Redirige tras guardar el horario
    else:
        form = HorarioForm()

    # Filtrar los horarios del profesor actual
    horarios = Horario.objects.filter(profesor=request.user)

    return render(request, 'catalog/gestionar_horarios.html', {'form': form, 'horarios': horarios})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guardamos el usuario y lo asignamos al grupo correcto
            login(request, user)  # Autenticamos y logueamos automáticamente
            return redirect('inicio')  # Redirigir a la página de inicio
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})

@login_required
def perfil_usuario(request):
    # Definir los formularios antes de procesar el POST
    form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        # Comprobamos si es una actualización de perfil
        if 'update_profile' in request.POST:
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
                return redirect('perfil_usuario')

        # Comprobamos si es un cambio de contraseña
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
                return redirect('perfil_usuario')

    return render(request, 'catalog/perfil_usuario.html', {
        'form': form,
        'password_form': password_form,
    })