from django.shortcuts import render

# Create your views here.
def Inicio(request):
    return render(request, 'index.html')

def Contacto(request):
    return render(request, 'paginas/contacto.html')

def Contratacion(request):
    return render(request, 'paginas/contratacion.html')

def Servicios(request):
    return render(request, 'paginas/servicios.html')

