from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculoViewSet, AtencionViewSet
from .views import Inicio, Contacto, Servicios, Login, Perfil, Registro
from . import views

router = DefaultRouter()
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'atencion', AtencionViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('Inicio', Inicio, name='Inicio'),
    path('Inicio/Contratacion', views.Contratacion, name='Contratacion'),
    path('buscar-cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('Inicio/Contacto', Contacto, name= 'Contacto'),
    path('Inicio/Servicios', Servicios, name= 'Servicios'),
    path('Inicio/Usuarios/Login', Login, name= 'Login'),
    path('Inicio/Usuarios/Perfil', Perfil, name= 'Perfil'),
    path('Inicio/Recuperar_Contraseña/', views.recuperar, name='Recuperar'),
    path('Recuperar/<uidb64>/<token>/', views.recuperarconfirmar, name='ConfirmarRecuperar'),
    path('Inicio/Usuarios/Registro', Registro, name= 'Registro'),
    path('logout/', views.Logout, name='Logout'),
    path('ubicacion/', views.ubicacion, name='Ubicacion'),
]