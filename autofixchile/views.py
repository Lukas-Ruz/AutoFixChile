from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from .forms import RegistroForm, LoginForm, PerfilForm, VehiculoForm, RecuperarPasswordForm, ResetPasswordForm
from .models import Cliente, Mecanico, Vehiculo, Atencion
from .serializers import VehiculoSerializer, AtencionSerializer
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.
def Inicio(request):
    return render(request, 'index.html')

def Contacto(request):
    return render(request, 'paginas/contacto.html')

def Servicios(request):
    return render(request, 'paginas/servicios.html')

# REGISTRAR USUARIO

def Registro(request):
      form = RegistroForm()
      if request.method == 'POST':
          form = RegistroForm(request.POST)
          if form.is_valid():
              user = form.save()
              cliente = Cliente.objects.create(
                  user=user,
                  run=form.cleaned_data.get('run', ''),
                  nombre=form.cleaned_data.get('nombre', ''),
                  apellido=form.cleaned_data.get('apellido', ''),
                  direccion=form.cleaned_data.get('direccion', ''),
                  telefono=form.cleaned_data.get('telefono', ''),
                  fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento', None),

              )
              auth_login(request, user)
              messages.success(request, 'Registro exitoso. Bienvenido!')
              return redirect('Inicio')

      return render(request, 'usuario/registro.html', {'form': form})

# INICIAR SESION
def Login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido, {user.nombre}')
            if user.is_staff:
              return redirect('/admin')
            else:
             return redirect('Inicio')
        else:
            messages.error(request, 'ERRORES EN EL FORMULARIO')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LoginForm()
    return render(request, 'usuario/iniciarsesion.html', {'form': form})

# CERRAR SESION
def Logout(request):

    auth_logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('Login')

# INICIO DE SESION REQUERIDO
@login_required
def Perfil(request):
    user = request.user

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente')
                return redirect('Perfil')
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PerfilForm(instance=user)
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'usuario/perfil.html', context)

#REGISTRAR VEHICULO

@login_required
def Contratacion(request):
    if not hasattr(request.user, 'run_cliente') or not request.user.run_cliente:
        messages.error(request, 'Tu cuenta no tiene RUN asignado. Contacta al administrador.')
        return redirect('Inicio')

    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            try:
                # Guardar con mecánico auto-asignado (pasa request.user al save)
                vehiculo = form.save(mecanico=request.user)
                cliente_nombre = form.cleaned_data['nombre_cliente']
                messages.success(
                    request, 
                    f'Vehículo {vehiculo.patente} ({vehiculo.marca} {vehiculo.modelo}) '
                    f'registrado exitosamente para el cliente {cliente_nombre}.'
                )
                return redirect('Inicio')
            except Exception as e:
                messages.error(request, f'Error al guardar el vehículo: {str(e)}. Intenta de nuevo.')
                # Opcional: loguea el error con logger
        else:
            # Errores específicos del form
            errores = [str(err) for field in form for err in field.errors]
            messages.error(request, f'Corrige los errores en el formulario: {" | ".join(errores)}')
    else:
        form = VehiculoForm()

    # Context: Form + info del mecánico (para HTML)
    context = {
        'form': form,
        'mecanico_nombre': f"{request.user.nombre} {request.user.apellido} ({request.user.run_cliente})"
    }
    return render(request, 'paginas/contratacion.html', context)


@csrf_exempt  # Solo para GET
def cliente_by_run(request, run):
    try:
        cliente = Cliente.objects.get(run_cliente=run)
        return JsonResponse({'nombre': cliente.nombre})
    except Cliente.DoesNotExist:
        return JsonResponse({'nombre': ''}, status=404)

# RECUPERAR CONTRASEÑA

def recuperar(request):
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            run = form.cleaned_data['run']
            email = form.cleaned_data['email']
            user = Cliente.objects.get(run=run, email=email)

            # Genera token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(
                reverse('reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Envía email
            subject = 'Recuperación de Contraseña - AutoFixChile'
            message = f"""
            Hola {user.nombre},

            Para restablecer tu contraseña, haz clic en el siguiente enlace:
            {reset_url}

            Equipo AutoFixChile
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Hemos enviado un email con instrucciones para restablecer tu contraseña. Revisa tu bandeja (incluyendo spam).')
            return redirect('Login')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = RecuperarPasswordForm()

    return render(request, 'usuario/recuperar.html', {'form': form})

def recuperarconfirmar(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(Cliente, run=uid)
    except (TypeError, ValueError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(user, request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, '¡Contraseña restablecida exitosamente! Puedes iniciar sesión ahora.')
                return redirect('Login')
            else:
                messages.error(request, 'Por favor corrige los errores.')
        else:
            form = ResetPasswordForm(user)
        return render(request, 'usuario/restablecer.html', {'form': form})
    else:
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return redirect('usuario/recuperar.html')

def ubicacion(request):
    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'paginas/ubicacion.html', context)

# API RESTS
class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Vehiculo.objects.filter(usuario=self.request.user)
        return Vehiculo.objects.none()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class AtencionViewSet(viewsets.ModelViewSet):
    queryset = Atencion.objects.all()
    serializer_class = AtencionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Atencion.objects.filter(vehiculo__usuario=self.request.user)
        return Atencion.objects.none()

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        servicios = Atencion.objects.filter(vehiculo__isnull=True)
        serializer = AtencionSerializer(servicios, many=True)
        return Response(serializer.data)
