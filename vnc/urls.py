from django.urls import path
from vnc import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # USUARIOS
    path('', views.login_deudor, name="login_deudor"),
    path('login/cliente/', views.login_cliente, name="login_cliente"),
    path('login/', views.login_deudor, name="login_deudor"),
    path('completar_registro/', views.completar_registro, name="completar_registro"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('listados/', views.listado_general, name="listado_general"),
    path('nuevo/usuario/', views.cre_usuario, name="cre_usuario"),
    path('eliminar/usuario/<int:usuario_id>', views.eliminar_usuario, name="eliminar_usuario"),
    path('modificar/usuario/<int:usuario_id>', views.mod_usuario, name="mod_usuario"),
    path('nueva/empresa/', views.cre_empresa, name="cre_empresa"),
    path('modificar/empresa/<int:empresa_id>', views.mod_empresa, name="mod_empresa"),
    path('eliminar/empresa/<int:empresa_id>', views.eliminar_empresa, name="eliminar_empresa"),
    path('compromiso/estado/<int:id_compromiso>/<str:estado>', views.estado_compromiso, name="estado_compromiso"),

    # UTILES
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('inicio/', views.inicio, name='inicio'),
    path('listar_equipos/<str:fecha_desde>/<str:fecha_hasta>/<str:t_comp>/', views.listar_equipos, name='listar_equipos'),
    path('get_deudas/', views.get_deudas, name="get_deudas"),
    path('print_cupon/<int:deuda_id>/', views.cupon_pdf, name='print_cupon'),
    path('enviar_cupon/<int:deuda_id>/', views.enviar_pdf, name='enviar_cupon'),
    path('get_empresa/<int:empresa_id>/', views.get_empresa, name='get_empresa'),
    path('listar_provincias/', views.listar_provincias, name='listar_provincias'),
    path('listar_localidades/<int:provincia_id>/', views.listar_localidades, name='listar_localidades'),
    path('listar_localidades_front/<int:provincia_id>/', views.listar_localidades_front, name='listar_localidades_front')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Para encontrar los archivos .csv

handler404 = "vnc.views.page_not_found_view"
