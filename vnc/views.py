import json
from django.shortcuts import render, redirect
import pandas as pd
from django.contrib.auth import authenticate, login
from .forms import *
from datetime import datetime
from .filters import *
from django.http import JsonResponse
from django.core import serializers
import io
import requests
import base64
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.views.decorators.cache import never_cache
import django
from django.core.cache import cache

django.setup()  # Needed to make django ready from the external script
cache.clear()  # Flush all the old cache entry


@never_cache
def login_deudor(request):
    request.session.flush()
    msg = 'OK'
    form = LoginDeudorForm(request.POST or None)

    if request.method == 'POST':
        dni = request.POST['dni']

        response = requests.get('https://www.deacuerdo.com.ar/web.php?action=getInfo&dni=%s&dato=deudor' % dni)
        if response.text != '':
            deudor = response.json()
            deudor['nyap'] = deudor['nyap'].strip()
            request.session['dni'] = int(dni)
            request.session['deudor'] = deudor
            request.session['primer_ingreso'] = int(deudor["Primer Ingreso"])

            if deudor["Primer Ingreso"] == '0':
                return redirect('completar_registro')
            else:
                return redirect('get_deudas')
        else:
            msg = 'ERROR'

    return render(request, "accounts/login_deudor.html", {"msg": msg, "form": form})


@never_cache
def login_cliente(request):
    request.session.flush()
    form = LoginForm(request.POST or None)
    msg = ''

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['dni'] = 0
                return redirect('get_deudas')
            else:
                msg = 'Nombre de usuario/contraseña incorrecto'

    return render(request, "accounts/login_cliente.html", {"form": form, "msg": msg})


@never_cache
def completar_registro(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    dni = request.session['dni']

    deudor = request.session['deudor']
    form = DeudorForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = request.POST['email']
            telefono = request.POST['telefono']
            calle = request.POST['calle']
            numero = request.POST['numero']
            piso = request.POST['piso']
            departamento = request.POST['departamento']

            data = {
                'action': 'sendInfo',
                'dato': 'deudor',
                'form': '{"primer_ingreso":1,"dni":' + str(dni) + ',"email":"' + email + '","telefono":"' + telefono
                        + '",calle":"' + calle + '",numero":"' + numero + '",piso":"' + piso + '","departamento":"' + departamento + '"}'
            }

            req = requests.Request('GET', 'https://www.deacuerdo.com.ar/web.php', params=data)
            prepared = req.prepare()
            s = requests.Session()
            s.send(prepared)

            return redirect('get_deudas')

    form = DeudorForm(initial={'nyap': deudor['nyap'], 'dni': deudor['dni'], 'email': deudor['email'],
                               'telefono': deudor['telefono'], 'calle': deudor['calle'], 'nro': deudor['nro'],
                               'piso': deudor['piso']})

    return render(request, "accounts/primer_ingreso.html", {"form": form})


@never_cache
def get_deudas(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    deudas = ''
    saldo = False
    equipos = False
    dni = request.session['dni']
    if dni > 0:
        if request.session['primer_ingreso'] == 1:
            response = requests.get('https://www.deacuerdo.com.ar/web.php?action=getInfo&dni=%s&dato=deudor' % dni)
            deudor = response.json()
            request.session['deudor'] = deudor

        response = requests.get('https://www.deacuerdo.com.ar/web.php?action=getInfo&dni=%s&dato=info' % dni)
        deudas = response.json()

        if len(deudas) == 0:
            empresa_id = 1

        else:
            empresa_id = deudas[0]['empresa_id']

            for deuda in deudas:
                if deuda['tipo_deuda'] == 'deuda_monetaria':
                    saldo = True
                if deuda['tipo_deuda'] == 'recupero_equipo':
                    equipos = True

                empresa_dict = json.loads(serializers.serialize('json', Empresa.objects.filter(id=deuda['empresa_id'])))
                deuda['empresa'] = empresa_dict[0]['fields']

                if deuda['empresa_id'] != empresa_id:
                    empresa_id = 1

    else:
        empresa_id = request.user.usuarioempresa.empresa.id

    request.session['deudas'] = deudas
    request.session['saldo'] = saldo
    request.session['equipos'] = equipos

    empresa_dict = json.loads(serializers.serialize('json', Empresa.objects.filter(id=empresa_id)))
    request.session['empresa'] = empresa_dict[0]['fields']

    instance_vnc = Empresa.objects.get(id=1)

    request.session['wpp_vnc'] = instance_vnc.nro_wpp
    request.session['mail_vnc'] = instance_vnc.correo

    return redirect('inicio')


@never_cache
def inicio(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    dni = request.session['dni']

    compromisos = Compromiso.objects.filter(dni_cliente=dni).select_related('id_empresa')

    form_retiro = RetiroForm(request.POST or None)
    form_entrega = EntregaForm(request.POST or None)
    form_informe = InformeForm(request.POST, request.FILES)
    form_informe_pago = InformePagoForm(request.POST, request.FILES)
    form_fecha = FechaForm(request.POST or None)
    form_contacto = ContactoForm(request.POST or None)
    form_deudor = DeudorForm(request.POST or None)

    if request.method == 'POST':
        if request.POST.get("tipo_form") == "R":
            form = form_retiro
        elif request.POST.get("tipo_form") == "E":
            form = form_entrega
        elif request.POST.get("tipo_form") == "D":
            form = form_deudor
        elif request.POST.get("tipo_form") == "C":
            form = form_contacto
        elif request.POST.get("tipo_form") == "IP":
            form = form_informe_pago
        else:
            form = InformeForm(request.POST, request.FILES)

        if form.is_valid():
            if request.POST.get("tipo_form") in ('R', 'E'):
                comp = form.save()

                deudor = request.session['deudor']

                if request.POST.get("tipo_form") == 'R':
                    tit = 'Solicitud de retiro de equipo/s'
                    msg = 'Estimado ' + deudor['nyap'].strip() + ', su cita se ha programado con éxito. Un ' \
                                                                'representante se presentará en su domicilio el dia ' \
                          + comp.fecha.strftime("%d-%m-%Y") + '. Su código de seguridad es: ' + comp.codigo
                else:
                    tit = 'Programación de entrega de equipo/s'
                    msg = 'Estimado ' + deudor['nyap'].strip() + ', su cita se ha programado con éxito. Un ' \
                                                                'representante lo recibira el dia ' \
                          + comp.fecha.strftime("%d-%m-%Y") + ' en la sucursal seleccionada.'

                instance_emp = Empresa.objects.get(id=comp.id_empresa.id)

                try:
                    func_enviar_mail(tit, msg, request.session['mail_vnc'], request.session['wpp_vnc'])
                except:
                    print('No se pudo enviar el email')

            elif request.POST.get("tipo_form") == 'D':
                email = request.POST['email']
                telefono = request.POST['telefono']
                calle = request.POST['calle']
                numero = request.POST['numero']
                piso = request.POST['piso']
                departamento = request.POST['departamento']

                data = {
                    'action': 'sendInfo',
                    'dato': 'deudor',
                    'form': '{"primer_ingreso":1,"dni":' + str(dni) + ',"email":"' + email + '","telefono":"' + telefono
                            + '",calle":"' + calle + '",numero":"' + numero + '",piso":"' + piso + '","departamento":"' + departamento + '"}'
                }

                req = requests.Request('GET', 'https://www.deacuerdo.com.ar/web.php', params=data)
                prepared = req.prepare()
                s = requests.Session()
                s.send(prepared)

                return redirect('get_deudas')
            elif request.POST.get("tipo_form") == "C":
                id_deuda = request.POST['id_deuda']
                email = request.POST['email']
                telefono = request.POST['telefono']

                data = {
                    'action': 'sendInfo',
                    'dato': 'contacto',
                    'form': '{"dni":"' + str(dni) + '","id_deuda":"' + id_deuda + '","email":"' + email + '","telefono":"' + telefono + '"}'
                }

                req = requests.Request('GET', 'https://www.deacuerdo.com.ar/web.php', params=data)
                prepared = req.prepare()
                s = requests.Session()
                s.send(prepared)

                deudor = request.session['deudor']

                tit = 'Pago con tarjeta'
                msg = 'Estimado ' + deudor['nyap'].strip() + ', su solicitud fue enviada. Uno de nuestros ' \
                                                             'representantes se comunicara a la brevedad para ' \
                                                             'continuar la gestión de pago.'

                try:
                    func_enviar_mail(tit, msg, request.session['mail_vnc'], request.session['wpp_vnc'], email)
                except:
                    print('No se pudo enviar el email')

            elif request.POST.get("tipo_form") == 'IP':
                foto = request.FILES['foto']

                id_deuda = request.POST['id_deuda']
                lugar = request.POST['lugar']
                fecha = request.POST['fecha']
                monto = request.POST['monto']
                comprobante = base64.b64encode(foto.read())

                n_foto = str(dni) + '_' + str(id_deuda) + '.jpg'

                files = {
                    'comprobante': (n_foto, io.BytesIO(comprobante))
                }

                data = {
                    'action': 'sendInfo',
                    'dato': 'informePago',
                    'form': '{"dni":' + str(dni) + ',"id_deuda":' + str(
                        id_deuda) + ',"lugar":"' + lugar + '","fecha":"' + fecha + '","monto":' + str(monto) + '}'
                }

                requests.post('https://www.deacuerdo.com.ar/web.php', data=data, files=files)

            elif request.POST.get("tipo_form") == 'IE':
                foto = request.FILES['foto']

                id_deuda = request.POST['id_deuda']
                lugar = request.POST['lugar']
                fecha = request.POST['fecha']
                n_foto = str(dni) + '_' + str(id_deuda) + '.jpg'

                files = {
                    'comprobante': (n_foto, io.BytesIO(foto.read()))
                }

                data = {
                    'action': 'sendInfo',
                    'dato': 'informePago',
                    'form': '{"dni":' + str(dni) + ',"id_deuda":' + str(
                        id_deuda) + ',"lugar":"' + lugar + '","fecha":"' + fecha + '","monto": "0"}'
                }

                requests.post('https://www.deacuerdo.com.ar/web.php', data=data, files=files)

            return redirect('inicio')
    else:
        if 'deudor' in request.session:
            deudor = request.session['deudor']
            form_deudor = DeudorForm(initial={'nyap': deudor['nyap'], 'dni': deudor['dni'], 'email': deudor['email'],
                                              'telefono': deudor['telefono'], 'callenro': deudor['calle'],
                                              'piso': deudor['piso']})

        form_informe = InformeForm()
        form_informe_pago = InformePagoForm()

    return render(request, "vnc/inicio.html", {"compromisos": compromisos, "formEntrega": form_entrega,
                                               "formRetiro": form_retiro, "formInforme": form_informe,
                                               "formInformePago": form_informe_pago, "formFecha": form_fecha,
                                               'formDeudor': form_deudor, "formContacto": form_contacto})


@never_cache
def actualizar_datos(request, archivo):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    try:
        file = io.StringIO(archivo)
        df_archivo = pd.read_csv(file, sep=";")

        # Se itera en el DF.
        for index, row in df_archivo.iterrows():
            data_dict = row.to_dict()
            obj = Empresa() if 'nombre_fantasia' in df_archivo.columns else UsuarioEmpresa()
            for (key, value) in data_dict.items():
                setattr(obj, key, value)

            # Se pregunta por nombre_fantasia porque esa columna solamente esta en empresa.
            if 'nombre_fantasia' in df_archivo.columns:
                resul = Empresa.objects.get(id=data_dict['id']).update(**data_dict)

                if not resul:
                    # no existe el obj para actualizar, se guarda derecho en la base.
                    obj.save()

            else:
                try:
                    user = User.objects.get(username=data_dict['username'])
                except:
                    user = None

                # Agrega o Modifica el usuario_empresa
                user_empresa = UsuarioEmpresa()
                user_empresa.role = data_dict['rol']
                user_empresa.dni = data_dict['dni']
                user_empresa.fecha_nac = datetime.strptime(data_dict['fecha_nac'], "%d/%m/%Y").strftime("%Y-%m-%d")
                user_empresa.cargo = data_dict['cargo']
                user_empresa.telefonos_contacto = data_dict['telefonos_contacto']

                if not user:  # No existe, primera vez que viene por .csv
                    user = User.objects.create_user(username=data_dict['username'],
                                                    password=data_dict['pass'],
                                                    first_name=data_dict['nombre'],
                                                    last_name=data_dict['apellido'], )
                    user_empresa.user = user
                    user_empresa.save()

                    empresas = data_dict['empresa_id'].split(",")

                    for e in empresas:
                        # query a la empresa
                        try:
                            empresa = Empresa.objects.get(id=e)
                        except:
                            empresa = None

                        user_empresa.empresa = empresa
                else:
                    # se eliminan claves innecesarias en la conversion a dict. y se actualiza el obj.
                    del user_empresa.__dict__['_state']
                    del user_empresa.__dict__['user_id']
                    del user_empresa.__dict__['id']

                    resul = UsuarioEmpresa.objects.filter(user__username=data_dict['username']).update(
                        **user_empresa.__dict__)

                    # si se cambio la contraseña en el archivo
                    user.set_password(data_dict['pass'])
                    user.save()

    except Exception as e:
        print(e)


@never_cache
def upload_csv(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    """
    Vista Upload
    """
    msg = ""

    if request.method == 'POST':
        csv_file = request.FILES['docfile']
        file_data = csv_file.read().decode("utf-8")
        actualizar_datos(file_data)
        msg = "El archivo se cargó correctamente"

    return render(request, "accounts/administracion/subir_archivo.html", {"msg": msg})


@never_cache
def listado_general(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    contexto = {'filtro_usuarios': UserFilter(request.GET, queryset=User.objects.all()),
                'filtro_empresas': EmpresaFilter(request.GET, queryset=Empresa.objects.all())}

    return render(request, "accounts/administracion/admin_usuarios.html", contexto)


@never_cache
def cre_usuario(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    if request.method == "POST":
        form = UsuarioCreateForm(request.POST)
        form2 = UsuarioEmpresaCreateForm(request.POST)
        if form.is_valid() and form2.is_valid():
            usuario = form.save()
            usuarioEmpresa = form2.save(commit=False)
            usuarioEmpresa.user = usuario
            usuarioEmpresa.save()
            return redirect('listado_general')
        else:
            return render(request, "accounts/administracion/cre_usuario.html", {"form": form, "form2": form2})
    else:
        form = UsuarioCreateForm()
        form2 = UsuarioEmpresaCreateForm()

    return render(request, "accounts/administracion/cre_usuario.html", {"form": form, "form2": form2})


@never_cache
def mod_usuario(request, usuario_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    msg = None

    if request.method == "POST":
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(id=usuario_id)
                user.first_name = form.cleaned_data.get("first_name")
                user.last_name = form.cleaned_data.get("last_name")
                user.email = form.cleaned_data.get("email")
                user.save()

                empresa_form = form.cleaned_data.get("empresa")
                empresa = Empresa.objects.get(id=empresa_form.id)

                user_empresa = UsuarioEmpresa.objects.get(user__id=usuario_id)
                user_empresa.dni = form.cleaned_data.get("dni")
                user_empresa.role = form.cleaned_data.get("role")
                user_empresa.empresa = empresa
                user_empresa.fecha_nac = form.cleaned_data.get("fecha_nac")
                user_empresa.cargo = form.cleaned_data.get("cargo")
                user_empresa.telefonos_contacto = form.cleaned_data.get("telefonos_contacto")
                user_empresa.save()

                return redirect('listado_general')
            except Exception as e:
                msg = 'Se ha producido un error guardando el usuario'
                print(e)
        else:
            msg = 'El Formulario no es válido'
    else:
        usuario = User.objects.get(id=usuario_id)
        usuario_fecha_nac = usuario.usuarioempresa.fecha_nac.strftime(
            "%d/%m/%Y") if usuario.usuarioempresa.fecha_nac else None

        form = UserUpdateForm(initial={'first_name': usuario.first_name,
                                       'last_name': usuario.last_name,
                                       'email': usuario.email,
                                       'dni': usuario.usuarioempresa.dni,
                                       'empresa': usuario.usuarioempresa.empresa,
                                       'role': usuario.usuarioempresa.role,
                                       'fecha_nac': usuario_fecha_nac,
                                       'cargo': usuario.usuarioempresa.cargo,
                                       'telefonos_contacto': usuario.usuarioempresa.telefonos_contacto,
                                       })

    return render(request, "accounts/administracion/mod_usuario.html", {"form": form, "msg": msg})


@never_cache
def eliminar_usuario(request, usuario_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    contexto = {}

    try:
        User.objects.get(id=usuario_id).delete()
        msj = "El usuario se ha eliminado correctamente."
        contexto['ok'] = True

    except Exception as e:
        msj = "Se produjo un error al intentar eliminar el usuario."
        contexto['ok'] = False
        print(e)

    contexto['msj'] = msj
    return JsonResponse(contexto, safe=False)


@never_cache
def cre_empresa(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    if request.method == "POST":
        form = EmpresaCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listado_general')
        else:
            return render(request, "accounts/administracion/mod_empresa.html", {"form": form})
    else:
        form = EmpresaCreateForm()

    return render(request, "accounts/administracion/mod_empresa.html", {"form": form})


@never_cache
def mod_empresa(request, empresa_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    empresa = Empresa.objects.get(id=empresa_id)

    if request.method == "POST":
        form = EmpresaUpdateForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            try:
                form.save()
                return redirect('get_deudas')
            except Exception as e:
                print(e)
        else:
            return render(request, "accounts/administracion/mod_empresa.html",
                          {"form": form})
    else:
        form = EmpresaUpdateForm(instance=empresa)

    return render(request, "accounts/administracion/mod_empresa.html", {"form": form})


@never_cache
def get_empresa(request, empresa_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    empresa = json.loads(serializers.serialize('json', Empresa.objects.filter(id=empresa_id)))
    empresa_dict = json.dumps(empresa[0]['fields'])

    return HttpResponse(empresa_dict)


@never_cache
def eliminar_empresa(request, empresa_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    Empresa.objects.get(id=empresa_id).delete()


@never_cache
def listar_equipos(request, fecha_desde, fecha_hasta, t_comp):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    id_empresa = request.user.usuarioempresa.empresa.id

    form_fecha = FechaForm(request.POST or None)

    compromisos = Compromiso.objects.filter(fecha__range=[fecha_desde, fecha_hasta], tipo_compromiso=t_comp,
                                            id_empresa=id_empresa)
    return render(request, "vnc/compromisos_cliente.html", {"compromisos": compromisos, "formFecha": form_fecha})


@never_cache
def estado_compromiso(request, id_compromiso, estado):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    compromiso = Compromiso.objects.get(id=id_compromiso)

    if estado == 'T':
        compromiso.completado = True
    else:
        compromiso.completado = False

    compromiso.save()

    return HttpResponse('')


@never_cache
@csrf_exempt
def cupon_pdf(request, deuda_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    deudas = request.session['deudas']
    deudor = request.session['deudor']
    deuda = ''
    venc = ''
    empresa = ''

    for el in deudas:
        if int(el['id']) == deuda_id:
            deuda = el
            venc = datetime.strptime(deuda['vencimiento'], '%Y-%m-%d')
            empresa = Empresa.objects.values_list('nombre_fantasia', flat=True).get(id=deuda['empresa_id'])

    context = {'deudor': deudor, 'deuda': deuda, 'venc': venc, 'empresa': empresa}
    html = render_to_string("vnc/cupon_pdf.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; report.pdf"

    font_config = FontConfiguration()
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response, font_config=font_config)

    return response


@never_cache
@csrf_exempt
def enviar_pdf(request, deuda_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    deudas = request.session['deudas']
    deudor = request.session['deudor']
    deuda = ''
    venc = ''

    mail_vnc = request.session['mail_vnc']

    for el in deudas:
        if int(el['id']) == deuda_id:
            deuda = el
            venc = datetime.strptime(deuda['vencimiento'], '%Y-%m-%d')

    context = {'deudor': deudor, 'deuda': deuda, 'venc': venc}
    html = render_to_string("vnc/cupon_pdf.html", context)

    msg = 'Estimado ' + deudor['nyap'] + ',  adjuntamos cupón para realizar sus pagos.'

    html_template = render_to_string('vnc/template_mail.html', context={'msg': msg, 'mail_vnc': mail_vnc, 'wpp_vnc': request.session['wpp_vnc'], 'cupon': 'S'})

    font_config = FontConfiguration()
    adjunto = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf('cupon.pdf', font_config=font_config)

    email = EmailMultiAlternatives(
        'Cupón de pago',
        '',
        'info@deacuerdo.com.ar',
        ['mzkzrrw@gmail.com']
    )

    email.attach_alternative(html_template, "text/html")
    email.attach_file('cupon.pdf', adjunto)
    email.send()

    return HttpResponse('')


@never_cache
def listar_provincias(request):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    provincias = Provincia.objects.all()

    provincias_opts = ''

    for provincia in provincias:
        provincias_opts += '<option value="' + str(provincia.id) + '" selected>' + provincia.nombre + '</option>'

    return HttpResponse(provincias_opts)


def listar_localidades(request, provincia_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    localidades = Localidad.objects.filter(provincia__id=provincia_id)

    localidades_opts = ''

    for localidad in localidades:
        localidades_opts += '<option value="' + str(localidad.id) + '" selected>' + localidad.nombre + '</option>'

    return HttpResponse(localidades_opts)


@csrf_exempt
def listar_localidades_front(request, provincia_id):
    if 'dni' not in request.session:
        return redirect('login_deudor')

    localidades = Localidad.objects.filter(provincia__id=provincia_id)

    localidades_opts = ''

    for localidad in localidades:
        localidades_opts += '<option value="' + str(localidad.id) + '" selected>' + localidad.nombre + '</option>'

    return HttpResponse(localidades_opts)


def func_enviar_mail(tit, msg, emisor, wpp_vnc, email='cvega@vncobranzas.com.ar'):
    html_template = render_to_string('vnc/template_mail.html', context={'msg': msg, 'mail_vnc': emisor, 'wpp_vnc': wpp_vnc})
    send_mail(tit,"",emisor,[email],fail_silently=True, html_message=html_template)


@never_cache
def page_not_found_view(request, exception):
    return render(request, 'vnc/404.html', status=404)
