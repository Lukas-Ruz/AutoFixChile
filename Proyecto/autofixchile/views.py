from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from .forms import RegistroForm, LoginForm, PerfilForm
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required


# Create your views here.
def Inicio(request):
    return render(request, 'index.html')

def Contacto(request):
    return render(request, 'paginas/contacto.html')

def Contratacion(request):
    return render(request, 'paginas/contratacion.html')

def Servicios(request):
    return render(request, 'paginas/servicios.html')

def Recuperar(request):
    return render(request, 'usuario/recuperar.html')

def Registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.refresh_from_db() 
                auth_login(request, user)
                messages.success(request, '¡Registro exitoso! Bienvenido a AutoFixChile.')
                return redirect('Inicio')
            except IntegrityError:
                messages.error(request, 'El RUN o email ya está registrado. Elige otro.')
                form.add_error(None, 'Error: RUN o email duplicado.')
            except ValueError as e:
                messages.error(request, f'Error en los datos: {str(e)}')
                form.add_error(None, str(e))
            except Exception as e:
                messages.error(request, f'Error inesperado al registrar: {str(e)}')
                form.add_error(None, 'Error interno. Intenta de nuevo.')

        messages.error(request, 'ERROR FORMULARIO')
    else:

        form = RegistroForm()
        return render(request, 'usuario/registro.html')

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

def Logout(request):
    
    auth_logout(request)
    messages.success(request, 'Sesión cerrada exitosamente') 
    return redirect('Inicio')

@login_required
def Perfil(request):
    user = request.user 
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=user) 
        if form.is_valid():
            try:
                form.save() 
                messages.success(request, '¡Perfil actualizado exitosamente!')
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
