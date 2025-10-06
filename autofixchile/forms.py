from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Vehiculo, Cliente
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model

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
        model = Cliente
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
        
        self.username_field = Cliente._meta.get_field('run')

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
        model = Cliente
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
    
    #FORMULARIO PARA REGISTRAR VEHICULO

class VehiculoForm(forms.ModelForm):

    run_cliente = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'runCliente',
            'placeholder': '12345678-0',
            'required': True,
        }),
        label='RUN Cliente'
    )
    nombre_cliente = forms.CharField( 
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'nombreCliente',
            'required': True,
        }),
        label='Nombre Cliente'
    )
    
    areas = forms.MultipleChoiceField(
        choices=[
            ('Carroceria', 'Carrocería'),
            ('Mecanica', 'Mecánica'),
            ('Electronica', 'Electrónica'),
            ('Pintura', 'Pintura'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input area-checkbox'}),
        required=True,
        help_text='Selecciona 1-4 áreas de trabajo.'
    )
    
    class Meta:
        model = Vehiculo
        fields = ['patente', 'marca', 'modelo', 'fecha_encargo', 'run_cliente', 'nombre_cliente', 'areas']
        widgets = {
            'patente': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'patente',
                'required': True,
                'maxlength': 6,
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'marca',
                'required': True,
                'maxlength': 20,
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'modelo',
                'required': True,
                'maxlength': 20,
            }),
            'fecha_encargo': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'fechaEncargo',
                'type': 'date',
                'required': True,
            }),
        }
        labels = {
            'patente': 'Patente (ej. ABC123)',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'fecha_encargo': 'Fecha Encargo',
        }
    
    def clean_run_cliente(self):
        run_cliente = self.cleaned_data.get('run_cliente')
        if run_cliente and not Cliente.objects.filter(run_cliente = run_cliente).exists(): 
            raise forms.ValidationError('RUN del cliente no existe en el sistema.')
        return run_cliente
    
    def clean_pasajero(self):
        patente = self.cleaned_data.get('patente', '').upper().replace('-', '')
        if len(patente) != 6 or not patente.isalnum():
            raise forms.ValidationError('Patente con formato invalido (ej: AB1234, ABCD12)')
        if Vehiculo.objects.filter(patente=patente).exists():
            raise forms.ValidationError('Patente ya registrada.')
        return patente
    
    def clean_areas(self):
        areas = self.cleaned_data.get('areas', [])
        if len(areas) < 1 or len(areas) > 4:
            raise forms.ValidationError('Selecciona una de las 4 areas')
        return areas
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        run_cliente = self.cleaned_data['run_cliente']
        instance.cliente = Cliente.objects.get(run_cliente = run_cliente)
        instance.areas = ', '.join(self.cleaned_data['areas'])
        if commit:
            instance.save()
        return instance
    
    #FORMULARIO PARA RECUPERAR CONTRASEÑA

Usuario = get_user_model() 

class RecuperarPasswordForm(forms.Form):
    run = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'runRecuperar',
            'placeholder': '12345678-9',
            'required': True,
        }),
        label='RUN'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'emailRecuperar',
            'required': True,
        }),
        label='Correo Electrónico'
    )

    def clean(self):
        cleaned_data = super().clean()
        run = cleaned_data.get('run')
        email = cleaned_data.get('email')
        if run and email:
            try:
                user = Usuario.objects.get(run=run, email=email)
            except Usuario.DoesNotExist:
                raise forms.ValidationError('RUN o email no coinciden con una cuenta registrada.')
        return cleaned_data

class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'nuevaContraseña',
            'required': True,
        }),
        label='Nueva Contraseña',
        help_text='Mínimo 8 caracteres, con mayúscula, número y especial.'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'nuevaContraseña2',
            'required': True,
        }),
        label='Repetir Nueva Contraseña'
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
