# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class SiatServicioFacturacionComputarizada(models.Model):
    _name = 'siat.servicio.facturacion.computarizada'
    _inherit = 'siat.soap.base'
    _description = 'Servicio Facturacion'

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        wsdl = self.env.user.company_id.wsdl_computerized_billing
        if not wsdl:
            raise ValidationError(
                'No tiene configurada la ruta de conexion con Impuestos Nacionales. \n Contactese con su administrador.')
        return wsdl

    # ************************* METODOS *******************************
    # adicion de exception a la funcion recepcion_paquete_factura
    def recepcion_paquete_factura(self, wsdl=False, cuis=False, code_doc_sector=False, code_emition=False,
                                  cufd=False, nit=False, type_invo_doc=False, archivo=False, send_date=False,
                                  hash_archivo=False, cafc=False, qty_facturas=False, code_event=False,):
        # res = response.service.recepcionPaqueteFactura()
        """
        metodo: obtencion recepcion paquete factura
        return: dic respuesta recepcion paquete factura
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.recepcionPaqueteFactura({
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
                'cafc': cafc,
                'cantidadFacturas': qty_facturas,
                'codigoEvento': code_event,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    def verificar_comunicacion(self, wsdl=False):
        # # res = response.service.verificarComunicacion()
        """
        metodo: verificarComunicacion
        return: Devuelve un warning con respuesta de conexion
        """
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        # res = client.service.verificarComunicacion()
        # return self.check_response(res)
        try:
            res = client.service.verificarComunicacion()
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    def btn_verificar_comunicacion(self):
        return self.msj_conexion_test(self.check_transaction(self.verificar_comunicacion()))

    # adicion de exception a la funcion recepcion_factura
    def recepcion_factura(self, company_id=False, wsdl=False, cuis=False, code_doc_sector=False, code_emition=False,
                          type_invo_doc=False, archivo=False, send_date=False,
                          hash_archivo=False):

        # res = response.service.recepcionFactura()
        """
        metodo: obtencion recepcion factura
        return: dic respuesta recepcion factura
        """
        # company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.recepcionFactura({
                'codigoAmbiente': company_id.environment_code,
                'codigoDocumentoSector': code_doc_sector,
                'codigoEmision': code_emition,
                'codigoModalidad': company_id.mode_constant,
                'codigoPuntoVenta': company_id.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': company_id.branch_code,
                'cufd': cuis.cufd_code,
                'cuis': cuis.cuis,
                'nit': str(company_id.siat_nit),
                'tipoFacturaDocumento': type_invo_doc,
                'archivo': archivo,
                'fechaEnvio': send_date,#todo revisar porque se mandaba una fecha fija '2022-03-11' envez el parametro
                'hashArchivo': hash_archivo,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    # adicion de exception a la funcion validacion_recepcion_factura
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
        try:
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
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    # adicion de exception a la funcion recepcion_masiva_factura
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
        try:
            res = client.service.recepcionMasivaFactura({
                'codigoAmbiente': company_id.environment_code,
                'codigoDocumentoSector': code_doc_sector,
                'codigoEmision': code_emition,
                'codigoModalidad': company_id.mode_constant,
                'codigoPuntoVenta': company_id.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': company_id.branch_code,
                'cufd': cuis.cufd_code,
                'cuis': cuis.cuis,
                'nit': nit,
                'tipoFacturaDocumento': type_invo_doc,
                'archivo': archivo,
                'fechaEnvio': send_date,
                'hashArchivo': hash_archivo,
                'cantidadFacturas': qty_facturas,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    # adicion de exception a la funcion verificacion_estado_factura
    def verificacion_estado_factura(self, wsdl=False,
                                    company_id=False,
                                    code_doc_sector=False,
                                    code_emition=False,
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
        try:
            res = client.service.verificacionEstadoFactura({
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
                'cuf': cuf,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return self.check_response(res)
        else:
            raise ValidationError(str_error)

    # adicion de exception a la funcion validacion_recepcion_paquete_factura
    def validacion_recepcion_paquete_factura(self, wsdl=False, cuis=False, code_doc_sector=False, code_emition=False,
                                            cufd=False, nit=False, type_invo_doc=False, code_reception=False):

        # res = response.service.validacionRecepcionPaqueteFactura()
        """
        metodo: obtencion validacion recepcion paquete factura
        return: dic respuesta validacion recepcion paquete factura
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.validacionRecepcionPaqueteFactura({
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
                'codigoEmision': code_emition,
                'codigoModalidad': company_id.mode_constant,
                'codigoPuntoVenta': company_id.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': company_id.branch_code,
                'cufd': cuis.cufd_code,
                'cuis': cuis.cuis,
                'nit': nit,
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
            raise ValidationError(str_error)






