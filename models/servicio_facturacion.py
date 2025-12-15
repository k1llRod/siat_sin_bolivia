# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import pytz
from odoo.exceptions import ValidationError

class SiatServicioFacturacion(models.Model):
    _name = 'siat.servicio.facturacion'
    _inherit = 'siat.soap.base'
    _description = 'Servicio Facturacion'

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        sector = self.env.user.company_id.siat_cuis_id.type_doc_sector
        if sector.codigo_clasificador == 11:
            wsdl = self.env.user.company_id.wsdl_computerized_billing
        else:
            wsdl = self.env.user.company_id.wsdl_in_out_invoice
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

    def recepcion_paquete_factura(self, wsdl=False,
                                  company_id=False,
                                  code_doc_sector=False,
                                  code_emition=False,
                                  mode_constant=False,
                                  selling_point_code=False,
                                  branch_code=False,
                                  cufd=False,
                                  cuis=False,
                                  type_invo_doc=False,
                                  archivo=False,
                                  send_date=False,
                                  hash_archivo=False,
                                  cafc=False,
                                  qty_facturas=False,
                                  code_event=False, ):
        # res = response.service.recepcionPaqueteFactura()
        """
        metodo: obtencion recepcion paquete factura
        return: dic respuesta recepcion paquete factura
        (respuestaRecepcion){
           codigoDescripcion = "PENDIENTE"
           codigoEstado = 901
           codigoRecepcion = "68efe004-dafb-11ec-a890-d950af40e283"
           transaccion = True
         }
        """
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.recepcionPaqueteFactura({
                'codigoAmbiente': company_id.environment_code,
                'codigoDocumentoSector': code_doc_sector,
                'codigoEmision': code_emition,
                'codigoModalidad': mode_constant,
                'codigoPuntoVenta': selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': branch_code,
                'cufd': cufd,
                'cuis': cuis,
                'nit': str(company_id.siat_nit),
                'tipoFacturaDocumento': type_invo_doc.codigo_clasificador,
                'archivo': archivo,
                'fechaEnvio': send_date,
                'hashArchivo': hash_archivo,
                'cafc': cafc,
                'cantidadFacturas': qty_facturas,
                'codigoEvento': code_event,
            })
        except Exception, e:
            res = {'transaccion': False, 'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    @api.model
    def recepcion_factura(self, company_id=False, wsdl=False,
                          cuis=False, code_doc_sector=False, code_emition=1,
                          cufd=False, nit=False, type_invo_doc=False,
                          archivo=False, send_date=False, branch_code=0,
                          hash_archivo=False):
        """
        Envío de factura en línea (recepcionFactura).
        Devuelve la respuesta ya validada con check_response.
        """

        # 1) Company por defecto
        company_id = company_id or self.env.user.company_id

        # 2) Validaciones mínimas
        if not company_id:
            raise ValidationError(u"No se ha definido la compañía para la recepción de factura.")

        if not cuis:
            raise ValidationError(u"No se ha definido el canal/CUIS para la recepción de factura.")

        if not type_invo_doc:
            raise ValidationError(u"No se ha definido el tipo de factura/documento.")

        if not archivo:
            raise ValidationError(u"No se ha enviado archivo (XML comprimido) al SIN.")

        if not hash_archivo:
            raise ValidationError(u"No se ha enviado hash del archivo al SIN.")

        # 3) Normalizar CUIS / CUFD
        #   - 'cuis' puede ser un registro de canal o un string
        cuis_code = getattr(cuis, 'cuis', None) or str(cuis)
        cufd_code = cufd or getattr(cuis, 'cufd_code', None) or getattr(cuis, 'cufd', None)

        if not cufd_code:
            raise ValidationError(u"No se ha definido el CUFD para la recepción de factura.")

        # 4) Normalizar NIT
        nit_str = str(nit or company_id.siat_nit)

        # 5) Normalizar tipo de factura (int)
        try:
            tipo_factura = int(getattr(type_invo_doc, 'codigo_clasificador', type_invo_doc))
        except Exception:
            raise ValidationError(u"Tipo de factura/documento inválido: %s" % type_invo_doc)

        # 6) Normalizar fecha de envío
        #    Si ya viene formateada "YYYY-MM-DDTHH:MM:SS(.SSS)" la usamos directo.
        #    Si viene como datetime, la convertimos a Bolivia con milisegundos.
        if not send_date:
            # por defecto: ahora en Bolivia
            tz = pytz.timezone(self.env.user.tz or 'America/La_Paz')
            dt_bol = datetime.now(tz)
            fecha_envio = dt_bol.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        else:
            if isinstance(send_date, basestring):
                # Aceptamos formatos ya bien formados tipo ISO, los mandamos directo
                # Si viene "YYYY-MM-DD HH:MM:SS", lo convertimos a ISO con 'T'
                if 'T' in send_date:
                    fecha_envio = send_date
                else:
                    # Asumimos "YYYY-MM-DD HH:MM:SS"
                    dt = fields.Datetime.from_string(send_date)
                    tz = pytz.timezone(self.env.user.tz or 'America/La_Paz')
                    dt_bol = pytz.utc.localize(dt).astimezone(tz)
                    fecha_envio = dt_bol.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            else:
                # datetime
                tz = pytz.timezone(self.env.user.tz or 'America/La_Paz')
                # si viene naive, asumimos UTC
                if send_date.tzinfo is None:
                    dt_bol = pytz.utc.localize(send_date).astimezone(tz)
                else:
                    dt_bol = send_date.astimezone(tz)
                fecha_envio = dt_bol.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        # 7) Conexión WS
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        payload = {
            'codigoAmbiente': company_id.environment_code,
            'codigoDocumentoSector': code_doc_sector,
            'codigoEmision': code_emition,  # para línea debe ser 1
            'codigoModalidad': company_id.mode_constant,
            'codigoPuntoVenta': getattr(company_id, 'selling_point_code', 0),
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': branch_code,
            'cufd': cufd_code,
            'cuis': cuis_code,
            'nit': nit_str,
            'tipoFacturaDocumento': tipo_factura,
            'archivo': archivo,
            'fechaEnvio': fecha_envio,
            'hashArchivo': hash_archivo,
        }

        try:
            res = client.service.recepcionFactura(payload)
        except Exception as e:
            # Normalizamos el error para que check_response no reviente
            res = {
                'transaccion': False,
                'mensajesList': [{
                    'codigo': 995,
                    'descripcion': u'SERVICIO NO DISPONIBLE \n%s' % e,
                }]
            }

        return self.check_response(res)

    def validacion_recepcion_masiva_factura(self, wsdl=False, cuis=False, code_doc_sector=False, code_emition=False,
                                            cufd=False, nit=False, type_invo_doc=False, code_reception=False):

        # res = response.service.validacionRecepcionMasivaFactura()
        """
        metodo: obtencion validacion recepcion masiva factura
        return: dic respuesta validacion recepcion masiva factura
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.validacionRecepcionMasivaFactura({
            'codigoAmbiente': company_id.environment_code,
            'codigoDocumentoSector': code_doc_sector,
            'codigoEmision': code_emition,
            'codigoModalidad': company_id.mode_constant,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'tipoFacturaDocumento': type_invo_doc,
            'codigoRecepcion': code_reception,
        })
        return self.check_response(res)

    def recepcion_masiva_factura(self, wsdl=False, cuis=False, code_doc_sector=False, code_emition=False,
                                 cufd=False, nit=False, type_invo_doc=False, archivo=False,
                                 send_date=False, hash_archivo=False, qty_facturas=False):
        # res = response.service.recepcionMasivaFactura()
        """
        metodo: obtencion recepcion masiva factura
        return: dic respuesta recepcion masiva factura
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.recepcionMasivaFactura({
            'codigoAmbiente': company_id.environment_code,
            'codigoDocumentoSector': code_doc_sector,
            'codigoEmision': code_emition,
            'codigoModalidad': company_id.mode_constant,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'tipoFacturaDocumento': type_invo_doc,
            'archivo': archivo,
            'fechaEnvio': send_date,
            'hashArchivo': hash_archivo,
            'cantidadFacturas': qty_facturas,
        })
        return self.check_response(res)

    def verificacion_estado_factura(self, wsdl=False,
                                    company_id=False,
                                    code_doc_sector=False,
                                    code_emition=False,
                                    mode_constant=False,
                                    selling_point_code=False,
                                    branch_code=False,
                                    cufd=False,
                                    cuis=False,
                                    nit=False,
                                    type_invo_doc=False,
                                    cuf=False):

        # res = response.service.verificacionEstadoFactura()
        """
        metodo: obtencion verificacion estado factura
        return: dic respuesta verificacion estado factura
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.verificacionEstadoFactura({
            'codigoAmbiente': company_id.environment_code,
            'codigoDocumentoSector': code_doc_sector,
            'codigoEmision': code_emition,
            'codigoModalidad': mode_constant,
            'codigoPuntoVenta': selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': str(company_id.siat_nit),
            'tipoFacturaDocumento': type_invo_doc,
            'cuf': cuf,
        })
        return self.check_response(res)

    def validacion_recepcion_paquete_factura(self, wsdl=False,
                                             company_id=False,
                                             code_doc_sector=False,
                                             code_emition=False,
                                             mode_constant=False,
                                             selling_point_code=False,
                                             branch_code=False,
                                             cufd=False,
                                             cuis=False,
                                             type_invo_doc=False,
                                             code_reception=False):

        # res = response.service.validacionRecepcionPaqueteFactura()
        """
        metodo: obtencion validacion recepcion paquete factura
        return: dic respuesta validacion recepcion paquete factura
        (respuestaRecepcion){
               codigoDescripcion = "VALIDADA"
               codigoEstado = 908
               codigoRecepcion = "4e4a8d71-dbcd-11ec-a98e-6dce1f23297b"
               transaccion = True
             }
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.validacionRecepcionPaqueteFactura({
                'codigoAmbiente': company_id.environment_code,
                'codigoDocumentoSector': code_doc_sector,
                'codigoEmision': code_emition,
                'codigoModalidad': mode_constant,
                'codigoPuntoVenta': selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': branch_code,
                'cufd': cufd,
                'cuis': cuis,
                'nit': str(company_id.siat_nit),
                'tipoFacturaDocumento': type_invo_doc,
                'codigoRecepcion': code_reception,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    def anulacion_factura(self, wsdl=False,
                                company_id=False,
                                code_doc_sector=False,
                                code_emition=False,
                                cuis=False, nit=False,
                                type_invo_doc=False,
                                code_motivo=False,
                                branch_code=0,
                                cuf=False):

        # res = response.service.anulacionFactura()
        """
        metodo: obtencion anulacion factura
        return: dic respuesta anulacion factura
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            res = client.service.anulacionFactura({
                'codigoAmbiente': company_id.environment_code,
                'codigoDocumentoSector': code_doc_sector,
                'codigoEmision': 1,
                'codigoModalidad': company_id.mode_constant,
                'codigoPuntoVenta': company_id.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': branch_code,
                'cufd': cuis.cufd_code,
                'cuis': cuis.cuis,
                'nit': str(company_id.siat_nit),
                'tipoFacturaDocumento': type_invo_doc,
                'codigoMotivo': code_motivo,
                'cuf': cuf,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)
