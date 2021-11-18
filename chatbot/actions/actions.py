from typing import Any, Text, Dict, List
from django.core.mail import send_mail
from psycopg2 import connect, DatabaseError
import re
import requests
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import json
from django.core.serializers.json import DjangoJSONEncoder


class ActionSaludo(Action):
    def name(self) -> Text:
        return "action_saludo"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        dni = tracker.sender_id

        response_deudor = requests.get('https://www.deacuerdo.com.ar/web.php?action=getInfo&dni=%s&dato=deudor' % dni)
        deudor = response_deudor.json()

        response = requests.get('https://www.deacuerdo.com.ar/web.php?action=getInfo&dni=%s&dato=info' % dni)
        deudas = response.json()

        msg = "Hola <b>" + deudor['nyap'] + "</b>. ¡Bienvenido/a!<br>"

        conn = connect("dbname=vnc_db host='74.207.227.51' user=postgres password=Holamundo31")

        cur = conn.cursor()
        cur.execute("SELECT * FROM VNC_EMPRESA WHERE ID = 1")
        vnc = cur.fetchone()
        vnc = json.dumps(vnc, cls=DjangoJSONEncoder)

        if len(deudas) == 1:
            deuda = deudas[0]

            cur = conn.cursor()
            cur.execute("SELECT * FROM VNC_EMPRESA WHERE ID = %s", [deuda['empresa_id']])
            empresa = cur.fetchone()

            conn.close()

            if deuda['tipo_deuda'] == 'deuda_monetaria':
                msg_deuda = "Tienes en 'bajo gestión' una deuda con <b>" + empresa[1] + "</b>, por un valor de <b>$" + \
                            deuda['saldo'] + "</b>"
            else:
                msg_deuda = "Tienes pendiente con <b>" + empresa[1] + "</b> la devolución de: <br>" + \
                            deuda['cantidad'] + " " + deuda['tipo'] + " N° de serie " + deuda['nro_serie']

            msg += msg_deuda + ".<br>Por favor, elige una opción para ayudarte con tu consulta"

            dispatcher.utter_message(text=msg)
            empresa = json.dumps(empresa, cls=DjangoJSONEncoder)

            return [SlotSet("deudor", deudor), SlotSet("deuda", deuda), SlotSet("empresa", empresa),
                    SlotSet("mult_deudas", False), SlotSet("vnc", vnc)]
        elif len(deudas) > 1:
            conn.close()

            msg += "El estado de tu cuenta registra las siguientes deudas. Por favor, elige una para continuar."

            dispatcher.utter_message(text=msg)

            return [SlotSet("deudor", deudor), SlotSet("deudas", deudas), SlotSet("mult_deudas", True), SlotSet("vnc", vnc)]
        else:
            conn.close()

            msg = msg + "El estado de tu cuenta no registra deudas a la fecha.<br>" + \
                  "Si considera que se trata de un error puede contactarse con nosotros al 0810-999-33832."

            dispatcher.utter_message(text=msg)

            return [SlotSet("deudor", deudor), SlotSet("mult_deudas", False), SlotSet("vnc", vnc)]


class ActionOpciones(Action):
    def name(self) -> Text:
        return "action_opciones"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        deuda = tracker.get_slot('deuda')

        if deuda['tipo_deuda'] == 'deuda_monetaria':
            btns_deuda = [{"payload": "/como_pagar", "title": "¿Como puedo pagar?"},
                          {"payload": "/cupon_pago", "title": "Quiero mi cupon de pago"},
                          {"payload": "/pago_tarjeta", "title": "¿Puedo pagar con tarjeta?"},
                          {"payload": "/contacto", "title": "Necesito contactarme con ustedes"},
                          {"payload": "/ya_pague", "title": "Ya pagué"}]
        else:
            btns_deuda = [{"payload": "/como_devolver", "title": "¿Como puedo devolver el equipo?"},
                          {"payload": "/contacto", "title": "Necesito contactarme con ustedes"},
                          {"payload": "/ya_entregue", "title": "Ya entregué"}]

        dispatcher.utter_message(buttons=btns_deuda, custom={"keypad": "disabled"})

        return []


class ActionBotonCupon(Action):
    def name(self) -> Text:
        return "action_boton_cupon"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        deuda = tracker.get_slot('deuda')

        link = '<u><a href="../print_cupon/' + deuda['id'] + '/" target="_blank">Descargar mi cupón</a></u>'

        dispatcher.utter_message(text=link, custom={"keypad": "disabled"})

        return []


class ActionBotonesDeuda(Action):
    def name(self) -> Text:
        return "action_botones_deuda"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        btns_deudas = []
        deudas = tracker.get_slot('deudas')

        for idx, deuda in enumerate(deudas):
            conn = connect("dbname=vnc_db host='74.207.227.51' user=postgres password=Holamundo31")
            cur = conn.cursor()
            cur.execute("SELECT * FROM VNC_EMPRESA WHERE ID = %s", [deuda['empresa_id']])
            empresa = cur.fetchone()
            conn.close()

            if deuda['tipo_deuda'] == 'deuda_monetaria':
                msg_deuda = "Empresa: " + empresa[1] + "<br>Importe: $" + deuda['saldo']
            else:
                msg_deuda = "Empresa: " + empresa[1] + "<br>" + deuda['cantidad'] + " " + deuda['tipo'] + \
                            "<br>N° de serie " + deuda['nro_serie']

            msg_payload = '/intent_deuda{"id_deuda":"' + deuda['id'] + '"}'
            btns_deudas.append({"payload": msg_payload, "title": msg_deuda})

        dispatcher.utter_message(buttons=btns_deudas, custom={"keypad": "disabled"})

        return []


class ActionSetSlots(Action):
    def name(self) -> Text:
        return "action_set_slots"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        deudas = tracker.get_slot('deudas')
        id_deuda = tracker.get_slot('id_deuda')
        deuda = ''
        empresa = ''

        for idx, elem in enumerate(deudas):
            if elem['id'] == id_deuda:
                deuda = elem

                conn = connect("dbname=vnc_db host='74.207.227.51' user=postgres password=Holamundo31")
                cur = conn.cursor()
                cur.execute("SELECT * FROM VNC_EMPRESA WHERE ID = %s", [deuda['empresa_id']])
                empresa = json.dumps(cur.fetchone(), cls=DjangoJSONEncoder)
                conn.close()

        return [SlotSet("deuda", deuda), SlotSet("empresa", empresa)]


class ActionResetSlotsDeuda(Action):
    def name(self) -> Text:
        return "action_reset_slots_deuda"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        return [AllSlotsReset()]


class ActionOpcionesPago(Action):
    def name(self) -> Text:
        return "action_opciones_pago"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        empresa = json.loads(tracker.get_slot('empresa'))

        msg = "Las opciones de pago disponibles son: " + empresa[4]

        dispatcher.utter_message(text=msg)

        return []


class ActionProcesarCompromisoRetiro(Action):
    def name(self) -> Text:
        return "action_procesar_compromiso_retiro"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        dni = tracker.sender_id
        deudor = tracker.get_slot('deudor')
        deuda = tracker.get_slot('deuda')
        fecha = tracker.get_slot('fecha_retiro')
        equipo = deuda['cantidad'] + " - " + deuda['tipo'] + " - " + deuda['nro_serie']
        localidad_id = tracker.get_slot('localidad_id')
        vnc = json.loads(tracker.get_slot('vnc'))

        source = string.ascii_letters + string.digits
        codigo = ''.join((random.choice(source) for i in range(8)))

        conn = connect("dbname=vnc_db host='74.207.227.51' user=postgres password=Holamundo31")
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO VNC_COMPROMISO"
                        "("
                        "TIPO_COMPROMISO,ID_DEUDA,EQUIPO,DNI_CLIENTE,ID_EMPRESA_ID,FECHA,HORA,HORA_HASTA,PROVINCIA_ID,LOCALIDAD_ID,TIPO_VIVIENDA,CALLENRO,CODIGO,COMPLETADO"
                        ") VALUES ('R', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (deuda['id'], equipo, dni, deuda['empresa_id'], fecha, tracker.get_slot('hora_desde'),
                         tracker.get_slot('hora_hasta'), tracker.get_slot('provincia_id'), localidad_id,
                         tracker.get_slot('tipo_vivienda'), tracker.get_slot('callenro'), codigo, False)
                        )
            conn.commit()
        except (Exception, DatabaseError) as error:
            print(error)
            conn.rollback()

        conn.close()

        titulo = 'Solicitud de retiro de equipo/s'
        mensaje = 'Estimado ' + deudor['nyap'].strip() + ', su cita se ha programado con éxito. Un representante se presentará en su domicilio el dia ' + fecha + '. Su código de seguridad es: ' + codigo + '.'

        try:
            enviar_mail(titulo, mensaje, vnc[5], vnc[6])
        except:
            print('No se pudo enviar el email')

        return [SlotSet("codigo", codigo)]


class ActionProcesarCompromisoEntrega(Action):
    def name(self) -> Text:
        return "action_procesar_compromiso_entrega"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        dni = tracker.sender_id
        deudor = tracker.get_slot('deudor')
        deuda = tracker.get_slot('deuda')
        fecha = tracker.get_slot('fecha_entrega')
        vnc = json.loads(tracker.get_slot('vnc'))
        equipo = deuda['cantidad'] + " - " + deuda['tipo'] + " - " + deuda['nro_serie']

        conn = connect("dbname=vnc_db host='74.207.227.51' user=postgres password=Holamundo31")
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO VNC_COMPROMISO"
                        "("
                        "TIPO_COMPROMISO,ID_DEUDA,EQUIPO,DNI_CLIENTE,ID_EMPRESA_ID,FECHA,HORA,COMPLETADO"
                        ") VALUES ('E', %s, %s, %s, %s, %s, %s, %s)",
                        (deuda['id'], equipo, dni, deuda['empresa_id'], fecha, tracker.get_slot('hora_entrega'), False))
            conn.commit()
        except (Exception, DatabaseError) as error:
            print(error)
            conn.rollback()

        conn.close()

        titulo = 'Programación de entrega de equipo/s'
        mensaje = 'Estimado ' + deudor['nyap'].strip() + ', su cita se ha programado con éxito. Un representante lo recibira el dia ' + fecha + ' en la sucursal seleccionada.'

        try:
            enviar_mail(titulo, mensaje, vnc[5], vnc[6])
        except:
            print('No se pudo enviar el email')

        return []


class ActionProcesarInformePago(Action):
    def name(self) -> Text:
        return "action_procesar_informe_pago"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        dni = tracker.sender_id
        deuda = tracker.get_slot('deuda')
        fecha = tracker.get_slot('fecha_informe_pago')
        lugar = tracker.get_slot('lugar_informe_pago')
        monto = tracker.get_slot('monto_informe_pago')
        comprobante = tracker.get_slot('comprobante_pago')

        n_foto = dni + '_' + str(deuda['id']) + '.jpg'

        files = {
            'comprobante': (n_foto, comprobante)
        }

        data = {
            'action': 'sendInfo',
            'dato': 'informePago',
            'form': '{"id_deuda":' + str(deuda['id']) + ',"tipo_deuda":"deuda_monetaria","lugar":"' + lugar
                    + '","fecha":"' + fecha + '","monto":' + str(monto) + '}'
        }

        requests.post('https://www.deacuerdo.com.ar/web.php', data=data, files=files)

        msg = 'Sus datos fueron guardados con éxito para la validación, estaremos en contacto'

        dispatcher.utter_message(text=msg)

        return []


class ActionProcesarInformeEntrega(Action):
    def name(self) -> Text:
        return "action_procesar_informe_entrega"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        dni = tracker.sender_id
        deuda = tracker.get_slot('deuda')
        fecha = tracker.get_slot('fecha_informe_entrega')
        lugar = tracker.get_slot('lugar_informe_entrega')
        comprobante = tracker.get_slot('comprobante_entrega')

        n_foto = dni + '_' + str(deuda['id']) + '.jpg'

        files = {
            'comprobante': (n_foto, comprobante)
        }

        data = {
            'action': 'sendInfo',
            'dato': 'informePago',
            'form': '{"dni_deudor":' + str(dni) + ',"id_deuda":' + str(deuda['id'])
                    + ',"tipo_deuda":"recupero_equipo","lugar":"' + lugar + '","fecha":"' + fecha + '","monto":"0"}'
        }

        requests.post('https://www.deacuerdo.com.ar/web.php', data=data, files=files)

        msg = 'Sus datos fueron guardados con éxito para la validación, estaremos en contacto'

        dispatcher.utter_message(text=msg)

        return []


class ActionProcesarContacto(Action):
    def name(self) -> Text:
        return "action_procesar_contacto"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        dni = tracker.sender_id
        deudor = tracker.get_slot('deudor')
        email = tracker.get_slot('email')
        telefono = tracker.get_slot('telefono')
        vnc = json.loads(tracker.get_slot('vnc'))

        data = {
            'action': 'sendInfo',
            'dato': 'contacto',
            'form': '{"dni":' + str(dni) + ',"email":"' + email + '","telefono":"' + telefono + '"}'
        }

        req = requests.Request('GET', 'https://www.deacuerdo.com.ar/web.php', params=data)
        prepared = req.prepare()
        s = requests.Session()
        s.send(prepared)

        titulo = 'Solicitud de contacto'
        mensaje = 'Estimado ' + deudor['nyap'].strip() + ', su solicitud fue enviada. Uno de nuestros ' \
                                                             'representantes se comunicara a la brevedad.'


        try:
            enviar_mail(titulo, mensaje, vnc[5], vnc[6], email)
        except:
            print('No se pudo enviar el email')

        dispatcher.utter_message(
            text='Se ha enviado su solicitud al grupo de contacto. En breve se comunicaran con ud.')

        return []


class ActionNrosContacto(Action):
    def name(self) -> Text:
        return "action_nros_contacto"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
                  ) -> List[Dict[Text, Any]]:

        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        empresa = json.loads(tracker.get_slot('empresa'))

        msg_wpp = "" if empresa[6] == "" else "<br>- Whatsapp: " + empresa[6]
        msg_telefonos_call = "" if empresa[7] == "" else "<br>- Teléfonos de contacto: " + empresa[7]

        msg_contacto = "" if empresa[6] == "" and empresa[7] == "" else ", o a los siguientes " \
                                                                        "numeros: " + msg_wpp + \
                                                                        msg_telefonos_call

        msg = "Puede comunicarse con nosotros llamando al 0810-999-33832" + msg_contacto

        dispatcher.utter_message(text=msg)

        return []


class ValidateContactoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_contacto_form"

    def validate_email(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        regex = '^[a-zA-Z0-9]+[\._]?[a-z0-9]+[@]\w+(?:[.]\w{2,3})+$'

        if re.search(regex, slot_value):
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una dirección de correo válida")
            return {"email": None}

    def validate_telefono(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        regex = '^[ 0-9()-+]{1,20}$'

        if re.search(regex, slot_value):
            return {"telefono": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese un número de teléfono válido")
            return {"telefono": None}


class ValidateInformePagoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_informe_pago_form"

    def validate_fecha_informe_pago(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"fecha_informe_pago": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una fecha válida")
            return {"fecha_informe_pago": None}

    def validate_lugar_informe_pago(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) < 20:
            return {"lugar_informe_pago": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"lugar_informe_pago": None}

    def validate_monto_informe_pago(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if float(slot_value) < 1000000:
            return {"monto_informe_pago": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"monto_informe_pago": None}

    def validate_comprobante_pago(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"comprobante_pago": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, capture o seleccione una fotografia del comprobante de pago")
            return {"comprobante_pago": None}


class ValidateInformeEntregaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_informe_entrega_form"

    def validate_fecha_informe_entrega(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"fecha_informe_entrega": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una fecha válida")
            return {"fecha_informe_entrega": None}

    def validate_lugar_informe_entrega(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"lugar_informe_entrega": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"lugar_informe_entrega": None}

    def validate_comprobante_entrega(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"comprobante_entrega": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, capture o seleccione una fotografia del comprobante de entrega")
            return {"comprobante_entrega": None}


class ValidateRetiroForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_retiro_form"

    def validate_fecha_retiro(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"fecha_retiro": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una fecha válida")
            return {"fecha_retiro": None}

    def validate_hora_desde(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"hora_desde": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una hora válida")
            return {"hora_desde": None}

    def validate_hora_hasta(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"hora_hasta": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una hora válida")
            return {"hora_hasta": None}

    def validate_provincia(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"provincia_id": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"provincia_id": None}

    def validate_localidad(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            localidad_id = slot_value

            conn = connect("dbname=vnc_db host='74.207.227.51' user=postgres password=Holamundo31")
            cur = conn.cursor()
            cur.execute("SELECT NOMBRE FROM VNC_LOCALIDAD WHERE ID = %s", [localidad_id])
            localidad = cur.fetchone()
            conn.close()

            return {"localidad_id": localidad_id, "localidad": localidad[0]}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"localidad_id": None}

    def validate_tipo_vivienda(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"tipo_vivienda": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"tipo_vivienda": None}

    def validate_callenro(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"callenro": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, complete este campo")
            return {"callenro": None}


class ValidateEntregaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_entrega_form"

    def validate_fecha_entrega(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"fecha_entrega": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una fecha válida")
            return {"fecha_entrega": None}

    def validate_hora_entrega(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) > 0:
            return {"hora_entrega": slot_value}
        else:
            dispatcher.utter_message(text=f"Por favor, ingrese una hora válida")
            return {"hora_entrega": None}


def enviar_mail(titulo, mensaje, emisor, wpp_vnc, email='cvega@vncobranzas.com.ar'):
    msg = EmailMessage()
    msg['Subject'] = titulo
    msg['From'] = emisor
    msg['To'] = [email]
    msg.set_content("""
        <!DOCTYPE html>
        <html>
            <body>
                <p>""" + mensaje + """<br><br> Recuerde que puede contactarnos mediante <a href='""" + emisor + """'>www.deacuerdo.com.ar</a> o por whatsapp al """ + wpp_vnc + """</p>
            </body>
        </html>
        """, subtype='html')

    with smtplib.SMTP('smtp.dreamhost.com', 25) as smtp:
        smtp.login('webmaster@deacuerdo.com.ar', 'gpcuiFsS')
        smtp.send_message(msg)
