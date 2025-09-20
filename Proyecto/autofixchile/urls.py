from django.urls import path
from .views import Inicio, Contratacion, Contacto, Servicios

urlpatterns = [
    path('Inicio', Inicio, name='Inicio'),
    path('Inicio/Contratacion', Contratacion, name= 'Contratacion'),
    path('Inicio/Contacto', Contacto, name= 'Contacto'),
    path('Inicio/Servicios', Servicios, name= 'Servicios')
]