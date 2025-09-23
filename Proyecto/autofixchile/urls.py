from django.urls import path
from .views import Inicio, Contratacion, Contacto, Servicios, Login, Perfil, Recuperar, Registro
from . import views


urlpatterns = [
    path('Inicio', Inicio, name='Inicio'),
    path('Inicio/Contratacion', Contratacion, name= 'Contratacion'),
    path('Inicio/Contacto', Contacto, name= 'Contacto'),
    path('Inicio/Servicios', Servicios, name= 'Servicios'),
    path('Inicio/Usuarios/Login', Login, name= 'Login'),
    path('Inicio/Usuarios/Perfil', Perfil, name= 'Perfil'),
    path('Inicio/Usuarios/RecuperarContraseña', Recuperar, name= 'Recuperar'),
    path('Inicio/Usuarios/Registro', Registro, name= 'Registro'),
    path('logout/', views.Logout, name='Logout'),
]