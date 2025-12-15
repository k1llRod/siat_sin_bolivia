# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import pytz

try:
    unicode
except NameError:
    unicode = str

class SiatServicioFacturacionOperaciones(models.Model):
    _name = 'siat.servicio.facturacion.operaciones'
    _inherit = 'siat.soap.base'
    _description = 'Servicio Facturacion Operaciones'

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        wsdl = self.env.user.company_id.wsdl_operations
        if not wsdl:
            raise ValidationError(
                'No tiene configurada la ruta de conexion con Impuestos Nacionales. \n Contactese con su administrador.')
        return wsdl

    # ************************* METODOS *******************************

    def verificar_comunicacion(self, wsdl=False):
        # # res = response.service.verificarComunicacion()
        """
        metodo: verificarComunicacion
        return: Devuelve un warning con respuesta de conexion
        """
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.verificarComunicacion()
        return self.check_response(res)

    def btn_verificar_comunicacion(self):
        return self.msj_conexion_test(self.check_transaction(self.verificar_comunicacion()))

    def registro_punto_venta(self, wsdl=False, code_type_pdv=False, cuis=False, description=False, nit=False, nombre_puntoventa=False):

        # res = response.service.registroPuntoVenta()
        """
        metodo: obtencion registro punto de venta
        return: dic respuesta registro punto de venta
        (respuestaRegistroPuntoVenta){
           codigoPuntoVenta = 10
           transaccion = True
         }
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.registroPuntoVenta({
            'codigoAmbiente': company_id.environment_code,
            'codigoModalidad': company_id.mode_constant,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'codigoTipoPuntoVenta': code_type_pdv,
            'cuis': cuis,
            'descripcion': description,
            'nit': nit,
            'nombrePuntoVenta': nombre_puntoventa,
        })
        return self.check_response(res)

    def registro_punto_venta_comisionista(self, wsdl=False, cuis=False, description=False, comi_date_end=False,
                                          comi_date_start=False, nit=False, nit_comisionista=False, nombre_puntoventa=False,
                                          numero_contrato=False):
        # res = response.service.registroPuntoVentaComisionista()
        """
        metodo: obtencion punto venta comisionista
        return: dic respuesta punto venta comisionista
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.registroPuntoVentaComisionista({
            'codigoAmbiente': company_id.environment_code,
            'codigoModalidad': company_id.mode_constant,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cuis': cuis,
            'descripcion': description,
            'fechaFin': comi_date_end,
            'fechaInicio': comi_date_start,
            'nit': nit,
            'nitComisionista': nit_comisionista,
            'nombrePuntoVenta': nombre_puntoventa,
            'numeroContrato': numero_contrato,
        })
        return self.check_response(res)

    def cierre_operaciones_sistema(self, company_id = False,
                                         wsdl=False,
                                         cuis=False,
                                         branch_code=False,
                                         selling_point_code=False):
        """
        metodo: solicitud cierre operaciones sistema
        return: dic respuesta
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.cierreOperacionesSistema({
            'codigoAmbiente': company_id.environment_code,
            'codigoSistema': str(company_id.system_code),
            'nit': int(company_id.siat_nit),
            'codigoModalidad': company_id.mode_constant,
            'cuis': cuis,
            'codigoSucursal': branch_code,
            'codigoPuntoVenta': selling_point_code,
        })
        return self.check_response(res)

    @api.model
    def consulta_evento_significativo(self, wsdl=False, channel=False, event_date=False):
        """
        Método: consulta eventos significativos registrados en el SIN para una fecha dada.
        Retorna la respuesta del WS (dict u objeto) si es válida,
        o lanza ValidationError si hay error.
        """
        company_id = self.env.user.company_id

        if not channel:
            raise ValidationError("No se ha definido el canal SIAT (CUIS) para la consulta de eventos.")

        if not event_date:
            raise ValidationError("Debe especificar una fecha de evento para la consulta (formato YYYY-MM-DD).")

        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            res = client.service.consultaEventoSignificativo({
                'codigoAmbiente': company_id.environment_code,
                'codigoSistema': str(company_id.system_code),
                'nit': int(company_id.siat_nit),
                'cuis': channel.cuis,
                'cufd': channel.cufd_code,
                'codigoSucursal': channel.branch_code,
                'codigoPuntoVenta': channel.selling_point_code,
                'fechaEvento': event_date,
            })
        except Exception as e:
            # Normalizamos la respuesta como dict de error
            res = {
                'transaccion': False,
                'mensajesList': [{
                    'codigo': 995,
                    'descripcion': 'SERVICIO NO DISPONIBLE \n%s' % e
                }]
            }

        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        else:
            # Ya viene mensaje armado desde validate_response
            raise ValidationError(str_error)

    def consulta_punto_venta(self, company_id=False, wsdl=False, cuis=False):

        # # res = response.service.consultaPuntoVenta()
        """
        metodo: obtencion consulta punto venta
        return: dic respuesta consulta punto venta
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.consultaPuntoVenta({
            'codigoAmbiente': company_id.environment_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cuis': cuis,
            'nit': company_id.siat_nit,
        })
        return self.check_response(res)

    @api.model
    def registro_evento_significativo(self,
                                      wsdl=False,
                                      siat_cuis=False,
                                      siat_cufd=False,
                                      code_event=False,
                                      description=False,
                                      branch_code=False,
                                      cufd_code=False,
                                      selling_point_code=False,
                                      event_date_start=False,
                                      event_date_end=False):
        """
        Registro de evento significativo ante el SIN.
        """

        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        # Validaciones mínimas
        if not event_date_start or not event_date_end:
            raise ValidationError(u"Las fechas de inicio y fin son obligatorias")
        if not siat_cuis:
            raise ValidationError(u"CUIS no definido para el registro de evento.")
        if not siat_cufd:
            raise ValidationError(u"CUFD no definido para el registro de evento.")
        if not code_event:
            raise ValidationError(u"Código de evento significativo no definido.")
        if branch_code is False:
            raise ValidationError(u"Código de sucursal no definido.")
        if not cufd_code:
            raise ValidationError(u"CUFD del evento (cufdEvento) no definido.")

        # Normalizar punto de venta (si no hay, mandar 0)
        selling_point_code = selling_point_code or 0

        # Parse flexible (con o sin milisegundos)
        def _parse_dt(s):
            try:
                return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                # intenta con milisegundos
                return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")

        try:
            start_dt = _parse_dt(event_date_start)
            end_dt = _parse_dt(event_date_end)
        except Exception as e:
            raise ValidationError(u"Formato de fechas inválido: %s" % e)

        if start_dt >= end_dt:
            raise ValidationError(u"La fecha de inicio debe ser anterior a la fecha de fin")

        # Duración máxima (define aquí 24 o 72, pero que sea consistente en todo tu sistema)
        if (end_dt - start_dt) > timedelta(hours=24):
            raise ValidationError(u"El evento no puede durar más de 24 horas")

        # TZ: asumimos que la fecha de entrada está en hora local Bolivia (sin tz)
        user_tz = self.env.user.tz or 'America/La_Paz'
        bolivia_tz = pytz.timezone(user_tz)

        start_bolivia = bolivia_tz.localize(start_dt)
        end_bolivia = bolivia_tz.localize(end_dt)

        # Formato final con milisegundos (3 dígitos)
        formatted_start = start_bolivia.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        formatted_end = end_bolivia.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        try:
            res = client.service.registroEventoSignificativo({
                'codigoAmbiente': company_id.environment_code,
                'codigoSistema': unicode(company_id.system_code),
                'nit': int(company_id.siat_nit),
                'cuis': unicode(siat_cuis),
                'cufd': siat_cufd,
                'codigoSucursal': int(branch_code),
                'codigoPuntoVenta': int(selling_point_code),
                'codigoMotivoEvento': int(code_event),
                'descripcion': unicode(description or u''),
                'fechaHoraInicioEvento': formatted_start,
                'fechaHoraFinEvento': formatted_end,
                'cufdEvento': cufd_code,
            })
        except Exception as e:
            res = {
                'transaccion': False,
                'mensajesList': [{
                    'codigo': 995,
                    'descripcion': u'ERROR EN LLAMADA A registroEventoSignificativo: %s' % unicode(e)
                }]
            }

        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        raise ValidationError(str_error)

    def cierre_punto_venta(self, company_id=False,
                                 selling_point_code=False,
                                 wsdl=False,
                                 cuis=False):
        """
        metodo: solicitud cierre punto de venta
        return: dic respuesta
        """
        # company_id = company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.cierrePuntoVenta({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cuis': cuis,
            'nit': int(company_id.siat_nit),
        })
        return self.check_response(res)

