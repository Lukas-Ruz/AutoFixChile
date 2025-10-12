from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils import timezone

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, run, password=None, **extra_fields):
        if not run:
            raise ValueError('El RUN debe ser proporcionado.')
        user = self.model(run=run, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, run, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True.')
        return self.create_user(run, password, **extra_fields)

class Cliente(AbstractBaseUser , PermissionsMixin, models.Model):
    
    run = models.CharField(db_column='RUN_CLIENTE', max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(db_column='NOMBRE', max_length=100)
    apellido = models.CharField(db_column='APELLIDO', max_length=100)
    email = models.EmailField(db_column='EMAIL', unique=True, max_length=255)
    fecha_nacimiento = models.DateField(db_column='FECHA_NACIMIENTO', null=True, blank=True)
    telefono = models.CharField(db_column='TELEFONO', max_length=20, blank=True)
    direccion = models.TextField(db_column='DIRECCION', blank=True)
    password = models.CharField(db_column='PASSWORD', max_length=128)
 
    is_active = models.BooleanField(db_column='IS_ACTIVE', default=True, null=True, blank=True)
    is_staff = models.BooleanField(db_column='IS_STAFF', default=False, null=True, blank=True)
    is_superuser = models.BooleanField(db_column='IS_SUPERUSER', default=False, null=True, blank=True)
    
    date_joined = models.DateTimeField(db_column='DATE_JOINED', default=timezone.now, null=True, blank=True)
    last_login = models.DateTimeField(db_column='LAST_LOGIN', null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'run'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'email']

    class Meta:
        db_table = 'AUTOFIXCHILE_CLIENTE'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        managed = True

    def __str__(self):
        return f"{self.nombre} {self.apellido} (RUN: {self.run})"


class Especialidad(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    nombre_esp = models.CharField(max_length=20, null=False)

class Mecanico(models.Model):
    run_mecanico = models.CharField(max_length=10, primary_key=True, null=False)
    nombre_mc = models.CharField(max_length=20, null=False)
    apellido_mc = models.CharField(max_length=20, null=False)
    email_mc = models.CharField(max_length=50, null=False)
    fecha_nacimiento_mc = models.DateField()
    telefono_mc = models.IntegerField()
    direccion_mc = models.CharField(max_length=50, blank=True, null=True)
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.CASCADE,
        db_column='ESPECIALIDAD_id'
    )

class Vehiculo(models.Model):
    patente = models.CharField(max_length=6, primary_key=True, null=False)
    marca = models.CharField(max_length=20, null=False)
    modelo = models.CharField(max_length=20, null=False)
    fecha_encargo = models.DateField()
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='CLIENTE_run_cliente',
        related_name='vehiculos'
    )
    mecanico = models.ForeignKey(
        Mecanico,
        on_delete=models.CASCADE,
        db_column='MECANICO_run_mecanico',
        related_name='vehiculos_asignados'
    )
    areas = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'AUTOFIXCHILE_VEHICULO'
        ordering = ['-fecha_encargo']

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.areas:
            areas_list = [area.strip() for area in self.areas.split(',') if area.strip()]
            if len(areas_list) > 4 or len(areas_list) == 0:
                raise ValidationError('Seleccionar')


class Atencion(models.Model):
    id_atencion = models.AutoField(primary_key=True, null=False)
    fecha_atencion = models.DateField()
    costo = models.IntegerField(null=False)
    descripcion = models.TextField(blank=False, null=False)
    mecanico = models.ForeignKey(
        Mecanico,
        on_delete=models.CASCADE,
        db_column='MECANICO_run_mecanico',
        related_name='atenciones'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='CLIENTE_run_cliente',
        related_name='atenciones'
    )


class PagoAtencion(models.Model):
    fecha_pago = models.DateField()
    monto_pago = models.IntegerField(null=False)
    forma_pago = models.CharField(max_length=15, null=False)
    atencion = models.OneToOneField(
        Atencion,
        on_delete=models.CASCADE,
        db_column='ATENCION_id',
        primary_key=True
    )