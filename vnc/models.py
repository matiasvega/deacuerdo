from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator


class Provincia(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    nombre = models.CharField(max_length=75)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Localidad(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=75)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    nombre_fantasia = models.CharField(max_length=100)
    denominacion_legal = models.CharField(max_length=100, blank=True)
    cuit = models.PositiveBigIntegerField(validators=[MinValueValidator(20000000000), MaxValueValidator(39999999999)])
    medio_pago = models.CharField(max_length=300)
    correo = models.EmailField(max_length=35)
    nro_wpp = models.CharField(max_length=20)
    telefonos_call = models.CharField(max_length=100, blank=True)
    mensaje_extra = models.CharField(blank=True, max_length=300)
    elem_extra = models.CharField(blank=True, max_length=300)
    paleta_color_1 = models.CharField(max_length=7)
    paleta_color_2 = models.CharField(max_length=7, blank=True)
    paleta_texto = models.CharField(max_length=7, blank=True)
    permite_retiro = models.BooleanField(default=True)
    permite_entrega = models.BooleanField(default=True)
    hora_minima = models.TimeField(default=datetime.time(9, 00))
    hora_maxima = models.TimeField(default=datetime.time(18, 00))
    logo = models.FileField(null=True, blank=True)

    def __str__(self):
        return str(self.id) + " - " + self.nombre_fantasia


VACIO = 0
EMPRESA_DEUDA = 1
EMPRESA_EQUIPOS = 2
ADMIN = 3
ADMINGRAL = 4

ROLE_CHOICES = (
      (VACIO, '------------------'),
      (EMPRESA_DEUDA, 'Gestión de deudas'),
      (EMPRESA_EQUIPOS, 'Gestión de equipos'),
      (ADMIN, 'Admin'),
      (ADMINGRAL, 'Admin general'),
)


class UsuarioEmpresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=VACIO)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    dni = models.PositiveBigIntegerField(validators=[MinValueValidator(1000000), MaxValueValidator(39000000000)])
    fecha_nac = models.DateField(null=True, blank=True)
    cargo = models.CharField(max_length=50)
    telefonos_contacto = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


VIV_CHOICES = (
    ('DEPTO', 'DEPTO'),
    ('CASA', 'CASA'),
    ('OTRO', 'OTRO')
)


class Compromiso(models.Model):
    tipo_compromiso = models.CharField(max_length=1, null=True, blank=True)
    id_deuda = models.PositiveBigIntegerField()
    equipo = models.CharField(max_length=100, null=True, blank=True)
    dni_cliente = models.PositiveBigIntegerField(validators=[MinValueValidator(1000000), MaxValueValidator(39000000000)])
    id_empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    hora = models.TimeField(null=True, blank=True)
    hora_hasta = models.TimeField(null=True, blank=True)
    provincia = models.ForeignKey(Provincia, null=True, blank=True, on_delete=models.SET_NULL)
    localidad = models.ForeignKey(Localidad, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_vivienda = models.CharField(null=True, blank=True, max_length=10, choices=VIV_CHOICES, default='DEPTO')
    callenro = models.CharField(max_length=50, null=True, blank=True)
    piso = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99)])
    departamento = models.CharField(null=True, blank=True, max_length=4)
    entre_calle_1 = models.CharField(max_length=50, null=True, blank=True)
    entre_calle_2 = models.CharField(max_length=50, null=True, blank=True)
    codigo = models.CharField(max_length=25, null=True, blank=True)
    completado = models.BooleanField(default=False)

    def __str__(self):
        return "Id deuda: " + str(self.id_deuda) + " - Dni deudor: " + str(self.dni_cliente)

