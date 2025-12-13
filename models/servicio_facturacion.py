# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


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

    def recepcion_factura(self, company_id=False,wsdl=False, cuis=False, code_doc_sector=False, code_emition=2,
                          cufd=False, nit=False, type_invo_doc=False, archivo=False, send_date=False, branch_code=0,
                          hash_archivo=False):

        # res = response.service.recepcionFactura()
        """
        metodo: obtencion recepcion factura
        return: dic respuesta recepcion factura
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.recepcionFactura({
            'codigoAmbiente': company_id.environment_code,
            'codigoDocumentoSector': code_doc_sector,
            'codigoEmision': code_emition,
            'codigoModalidad': company_id.mode_constant,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': branch_code,
            'cufd': cuis.cufd_code,
            'cuis': cuis.cuis,
            'nit': str(company_id.siat_nit),
            'tipoFacturaDocumento': type_invo_doc,
            'archivo': archivo,
            'fechaEnvio': send_date,
            'hashArchivo': hash_archivo,
        })

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
