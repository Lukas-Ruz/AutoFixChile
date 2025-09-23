from django.contrib import admin
from .models import Especialidad, Cliente, Mecanico, Atencion, PagoAtencion, Vehiculo
# Register your models here.

admin.site.register(Cliente)
admin.site.register(Especialidad)
admin.site.register(Mecanico)
admin.site.register(Atencion)
admin.site.register(PagoAtencion)
admin.site.register(Vehiculo)