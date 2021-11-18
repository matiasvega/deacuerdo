from django.contrib.auth.models import User
import django_filters
from .models import Empresa


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', ]


class EmpresaFilter(django_filters.FilterSet):
    class Meta:
        model = Empresa
        fields = ['nombre_fantasia', 'denominacion_legal', 'cuit', ]
