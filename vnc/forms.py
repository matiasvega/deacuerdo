from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from vnc.models import *
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 15})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "maxlength": 20})
    )


class LoginDeudorForm(forms.Form):
    dni = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1000000, "max": 39999999999})
    )


class DeudorForm(forms.Form):
    nyap = forms.CharField(
        label='(*) Nombre y Apellido',
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 35})
    )
    dni = forms.IntegerField(
        label='DNI',
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1000000, "max": 39999999999, "readonly": True})
    )
    email = forms.CharField(
        label='(*) Email',
        widget=forms.EmailInput(attrs={"class": "form-control", "maxlength": 35})
    )
    telefono = forms.CharField(
        label='(*) Teléfono',
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 16})
    )
    calle = forms.CharField(
        label='Calle',
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 50}),
        required=False
    )
    numero = forms.CharField(
        label='Número',
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 50}),
        required=False
    )
    piso = forms.CharField(
        label='Piso',
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 2}),
        required=False
    )
    departamento = forms.CharField(
        label='Departamento',
        widget=forms.TextInput(attrs={"class": "form-control", "maxlength": 4}),
        required=False
    )


class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"})
        }


class UsuarioEmpresaCreateForm(forms.ModelForm):
    class Meta:
        model = UsuarioEmpresa
        fields = ("role", "empresa", "dni", "fecha_nac", "cargo", "telefonos_contacto")
        widgets = {
            "role": forms.Select(attrs={"class": "form-control select-generico"}),
            "empresa": forms.Select(attrs={"class": "form-control select-generico"}),
            "dni": forms.NumberInput(attrs={"class": "form-control", "min": 1000000, "max": 39999999999}),
            "fecha_nac": forms.TextInput(attrs={"class": "form-control datepicker"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "telefonos_contacto": forms.TextInput(attrs={"class": "form-control"})
        }
        labels = {
            'role': _('Rol'),
            'empresa': _('Empresa'),
            'dni': _('DNI/CUIT'),
            'fecha_nac': _('Fecha de nacimiento'),
            'cargo': _('Cargo'),
            'telefonos_contacto': _('Teléfonos de contacto')
        }


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = UsuarioEmpresa
        fields = ("first_name", "last_name", "email", "role", "empresa", "dni", "fecha_nac", "cargo",
                  "telefonos_contacto")
        widgets = {
            "role": forms.Select(choices=ROLE_CHOICES, attrs={"class": "form-control select-generico"}),
            "empresa": forms.Select(attrs={"class": "form-control select-generico"}),
            "dni": forms.NumberInput(attrs={"class": "form-control", "min": 1000000, "max": 39999999999}),
            "fecha_nac": forms.TextInput(attrs={"class": "form-control datepicker"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "telefonos_contacto": forms.TextInput(attrs={"class": "form-control"})
        }
        labels = {
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Email'),
            'role': _('Rol'),
            'empresa': _('Empresa'),
            'dni': _('DNI/CUIT'),
            'fecha_nac': _('Fecha de nacimiento'),
            'cargo': _('Cargo'),
            'telefonos_contacto': _('Teléfonos de contacto')
        }


class EmpresaCreateForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ('id', 'nombre_fantasia', 'denominacion_legal', 'cuit', 'medio_pago', 'correo', 'nro_wpp',
                  'telefonos_call', 'mensaje_extra', 'paleta_color_1', 'paleta_color_2', 'paleta_texto', 'logo',
                  'permite_retiro', 'permite_entrega', 'hora_minima', 'hora_maxima')
        widgets = {
            'id': forms.TextInput(attrs={"class": "form-control"}),
            'nombre_fantasia': forms.TextInput(attrs={"class": "form-control"}),
            'denominacion_legal': forms.TextInput(attrs={"class": "form-control"}),
            'cuit': forms.NumberInput(attrs={"class": "form-control"}),
            'medio_pago': forms.TextInput(attrs={"class": "form-control"}),
            'correo': forms.EmailInput(attrs={"class": "form-control"}),
            'nro_wpp': forms.TextInput(attrs={"class": "form-control"}),
            'telefonos_call': forms.TextInput(attrs={"class": "form-control"}),
            'mensaje_extra': forms.TextInput(attrs={"class": "form-control"}),
            'paleta_color_1': forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            'paleta_color_2': forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            'paleta_texto': forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            'hora_minima': forms.TextInput(attrs={"class": "form-control timepicker"}),
            'hora_maxima': forms.TextInput(attrs={"class": "form-control timepicker"}),
        }
        labels = {
            'medio_pago': _('Medios de pago'),
            'nro_wpp': _('Número de whatsapp'),
            'telefonos_call': _('Teléfonos de contacto'),
            'paleta_color_1': _('Paleta de color 1'),
            'paleta_color_2': _('Paleta de color 2'),
            'paleta_texto': _('Paleta de color para texto'),
            'hora_minima': _('Hora mínima de atención'),
            'hora_maxima': _('Hora máxima de atención')
        }


class EmpresaUpdateForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ('id', 'nombre_fantasia', 'denominacion_legal', 'cuit', 'medio_pago', 'correo', 'nro_wpp', 'telefonos_call',
                  'mensaje_extra', 'paleta_color_1', 'paleta_color_2', 'paleta_texto', 'logo', 'permite_retiro', 'permite_entrega')
        widgets = {
            'id': forms.TextInput(attrs={"class": "form-control"}),
            'nombre_fantasia': forms.TextInput(attrs={"class": "form-control"}),
            'denominacion_legal': forms.TextInput(attrs={"class": "form-control"}),
            'cuit': forms.NumberInput(attrs={"class": "form-control"}),
            'medio_pago': forms.TextInput(attrs={"class": "form-control"}),
            'correo': forms.EmailInput(attrs={"class": "form-control"}),
            'nro_wpp': forms.TextInput(attrs={"class": "form-control"}),
            'telefonos_call': forms.TextInput(attrs={"class": "form-control"}),
            'mensaje_extra': forms.TextInput(attrs={"class": "form-control"}),
            'paleta_color_1': forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            'paleta_color_2': forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            'paleta_texto': forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            'hora_minima': forms.TextInput(attrs={"class": "form-control timepicker"}),
            'hora_maxima': forms.TextInput(attrs={"class": "form-control timepicker"}),
        }
        labels = {
            'medio_pago': _('Medios de pago'),
            'nro_wpp': _('Número de whatsapp'),
            'telefonos_call': _('Teléfonos de contacto'),
            'paleta_color_1': _('Paleta de color 1'),
            'paleta_color_2': _('Paleta de color 2'),
            'paleta_texto': _('Paleta de color para texto'),
            'hora_minima': _('Hora mínima de atención'),
            'hora_maxima': _('Hora máxima de atención')
        }


class InformeForm(forms.Form):
    id_deuda = forms.CharField(
        widget=forms.TextInput(attrs={"hidden": True})
    )
    tipo_deuda = forms.CharField(
        widget=forms.TextInput(attrs={"hidden": True})
    )
    lugar = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    fecha = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    foto = forms.FileField(
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"})
    )


class InformePagoForm(InformeForm):
    monto = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0.01, "max": 999999.99})
    )


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Compromiso
        fields = ('tipo_compromiso', 'id_deuda', 'equipo', 'dni_cliente', 'id_empresa', 'fecha', 'hora')
        required = 'hora'
        widgets = {
            'tipo_compromiso': forms.TextInput(attrs={"value": "E", "hidden": "true"}),
            'id_deuda': forms.TextInput(attrs={"hidden": "true"}),
            'equipo': forms.TextInput(attrs={"hidden": "true"}),
            'dni_cliente': forms.NumberInput(attrs={"hidden": "true"}),
            'id_empresa': forms.NumberInput(attrs={"hidden": "true"}),
            'fecha': forms.TextInput(attrs={"class": "form-control"}),
            'hora': forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            'fecha': _('(*) Fecha'),
            'hora': _('(*) Hora')
        }


class RetiroForm(forms.ModelForm):
    class Meta:
        model = Compromiso
        fields = ('tipo_compromiso', 'id_deuda', 'equipo', 'dni_cliente', 'id_empresa', 'fecha', 'hora', 'hora_hasta',
                  'provincia', 'localidad', 'tipo_vivienda', 'callenro', 'piso', 'departamento', 'entre_calle_1', 'entre_calle_2', 'codigo')
        required = ('fecha', 'provincia', 'localidad', 'callenro')
        widgets = {
            'tipo_compromiso': forms.TextInput(attrs={"value": "R", "hidden": "true"}),
            'id_deuda': forms.TextInput(attrs={"hidden": "true"}),
            'equipo': forms.TextInput(attrs={"hidden": "true"}),
            'dni_cliente': forms.NumberInput(attrs={"hidden": "true"}),
            'id_empresa': forms.NumberInput(attrs={"hidden": "true"}),
            'fecha': forms.TextInput(attrs={"class": "form-control"}),
            'hora': forms.TextInput(attrs={"type": "time", "class": "form-control"}),
            'hora_hasta': forms.TextInput(attrs={"type": "time", "class": "form-control"}),
            'provincia': forms.Select(attrs={"class": "form-control select-generico"}),
            'localidad': forms.Select(attrs={"class": "form-control select-generico"}),
            'tipo_vivienda': forms.Select(attrs={"class": "form-control select-generico"}),
            'callenro': forms.TextInput(attrs={"class": "form-control", "required": "true"}),
            'piso': forms.NumberInput(attrs={"class": "form-control"}),
            'departamento': forms.TextInput(attrs={"class": "form-control"}),
            'entre_calle_1': forms.TextInput(attrs={"class": "form-control"}),
            'entre_calle_2': forms.TextInput(attrs={"class": "form-control"}),
            'codigo': forms.TextInput(attrs={"hidden": "true"})
        }
        labels = {
            'fecha': _('(*) Fecha'),
            'hora': _('Rango de hora'),
            'provincia': _('(*) Provincia'),
            'localidad': _('(*) Localidad'),
            'tipo_vivienda': _('Tipo de vivienda'),
            'callenro': _('(*) Calle y Número'),
            'nro': _('(*) Número')
        }


class ContactoForm(forms.Form):
    id_empresa = forms.CharField(
        widget=forms.TextInput(attrs={"hidden": "true"})
    )
    id_deuda = forms.CharField(
        widget=forms.TextInput(attrs={"hidden": "true"})
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "required": "true"})
    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={"type": "email", "class": "form-control", "required": "true"})
    )


class FechaForm(forms.Form):
    fecha_desde = forms.DateField(
        widget=forms.SelectDateWidget(attrs={"class": "form-control sdp-inline"}),
        initial=timezone.now()
    )
    fecha_hasta = forms.DateField(
        widget=forms.SelectDateWidget(attrs={"class": "form-control sdp-inline"}),
        initial=timezone.now()
    )
