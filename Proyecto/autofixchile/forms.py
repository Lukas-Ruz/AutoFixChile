from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import RegistroUsuario
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

#FORMULARIO PARA REGISTRAR USUARIO EN LA BASE DE DATOS
class RegistroForm(UserCreationForm):

    run = forms.CharField(max_length=20, help_text="Ingresa tu RUT (ej: 12345678-9)")
    nombre = forms.CharField(max_length=100, required=True)
    apellido = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    telefono = forms.CharField(max_length=20, required=False)
    direccion = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = RegistroUsuario
        fields = ('run', 'nombre', 'apellido', 'email', 'fecha_nacimiento', 'telefono', 'direccion', 'password1', 'password2')
        field_order = ['run', 'nombre', 'apellido', 'email', 'fecha_nacimiento', 'telefono', 'direccion', 'password1', 'password2']


def save(self, commit=True):
    user = super().save(commit=False)
    user.run = self.cleaned_data['run']
    user.nombre = self.cleaned_data['nombre']
    user.apellido = self.cleaned_data['apellido']
    user.email = self.cleaned_data['email']
    user.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
    user.telefono = self.cleaned_data.get('telefono')
    user.direccion = self.cleaned_data.get('direccion')

    user.is_active = True
    user.date_joined = timezone.now()
    
    if commit:
        user.save() 
    return user

#FORMULARIO PARA INICIAR SESION SI ES QUE ESTA REGISTRADO EN LA BASE DE DATOS

class LoginForm(AuthenticationForm):
    
    username = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',  # Para HTML y jQuery
            'placeholder': '12345678-9 (tu RUN)',
            'autofocus': True,
            'required': True
        }),
        label="RUN"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': 'Tu contraseña',
            'required': True
        }),
        label="Contraseña"
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        
        self.username_field = RegistroUsuario._meta.get_field('run')

    def clean(self):
        username = self.cleaned_data.get('username')  # Esto es el RUN ingresado
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_user(self):
        return self.user_cache 

#FORMULARIO PERFIL

class PerfilForm(forms.ModelForm):
    class Meta:
        model = RegistroUsuario
        fields = ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'nombrePerfil',
                'required': True,
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'apellidosPerfil', 
                'required': True,
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'fechaNacimientoPerfil',
                'type': 'date',
                'required': True,
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'telefonoPerfil',
                'required': True,
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'direccionPerfil',
                'required': True,
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellidos',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.startswith('56') and len(telefono) < 10:
            raise ValidationError('Teléfono inválido. Usa formato +569xxxxxxxx.')
        return telefono