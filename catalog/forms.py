from django import forms
from .models import Clase, Horario
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class ClaseForm(forms.ModelForm):
    num_instancias = forms.IntegerField(min_value=1, label="Número de sitios disponibles", initial=1)

    class Meta:
        model = Clase
        fields = ['nombre', 'horario']  # Los campos que deseas mostrar en el formulario

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Captura el usuario que pasa la vista
        super(ClaseForm, self).__init__(*args, **kwargs)
        
        if user:
            # Filtrar los horarios para mostrar solo los horarios del profesor logueado
            self.fields['horario'].queryset = Horario.objects.filter(profesor=user)

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['dia', 'hora_inicio', 'hora_fin']

        widgets = {
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

        labels = {
            'hora_inicio': 'Hora de Inicio',
            'hora_fin': 'Hora de Fin',
        }

class RegistroForm(UserCreationForm):
    OPCIONES_ROL = [
        ('profesor', 'Profesor'),
        ('alumno', 'Alumno')
    ]
    rol = forms.ChoiceField(choices=OPCIONES_ROL, widget=forms.RadioSelect, label="¿Eres profesor o alumno?")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'rol']
        help_texts = {
            'username': 'Introduce un nombre de usuario único.',
        }

    # Sobrescribir los campos de contraseña para personalizar sus help_text
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].help_text = 'Introduce la contraseña de nuevo'

    def save(self, commit=True):
        # Guardamos el usuario pero aún no lo asignamos a un grupo
        user = super().save(commit=False)
        rol = self.cleaned_data['rol']

        if commit:
            user.save()
            # Asignamos el grupo según el rol seleccionado
            if rol == 'profesor':
                grupo = Group.objects.get(name='Profesores')  # Obtener el grupo "Profesores"
            else:
                grupo = Group.objects.get(name='Alumnos')  # Obtener el grupo "Alumnos"

            user.groups.add(grupo)  # Añadir el usuario al grupo correspondiente

        return user
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Añadir los campos que deseas permitir actualizar
        help_texts = {

        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }