# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class SiatServicioRecepcionCompras(models.Model):
    _name = 'siat.servicio.recepcion.compras'
    _inherit = 'siat.soap.base'
    _description = 'Servicio Recepcion Compras'

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        wsdl = self.env.user.company_id.wsdl_receipt_of_purchases
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

    def validacion_recepcion_paquete_compras(self, wsdl=False, cufd=False, cuis=False, nit=False, code_recepcion=False):

        # res = response.validacionRecepcionPaqueteCompras()
        """
        metodo: obtencion de anulacion compra
        return: dic informacion anulacion compra
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.validacionRecepcionPaqueteCompras({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'codigoRecepcion': code_recepcion,
        })
        return self.check_response(res)

    def recepcion_paquete_compras(self, wsdl=False, cufd=False, cuis=False, nit=False, archivo=False,
                                  qty_facturas=False, send_date=False, gestion=False, hash_archivo=False,
                                  periodo=False):

        # res = response.recepcionPaqueteCompras()
        """
        metodo: obtencion de recepcion paquete compras
        return: dic informacion recepcion paquete compras
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.recepcionPaqueteCompras({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'archivo': archivo,
            'cantidadFacturas': qty_facturas,
            'fechaEnvio': send_date,
            'gestion': gestion,
            'hashArchivo': hash_archivo,
            'periodo': periodo,
        })
        return self.check_response(res)

    def anulacion_compra(self, wsdl=False, cufd=False, cuis=False, nit=False, cod_autorizacion=False, nit_proveedor=False,
                         nro_duidim=False, nro_factura=False):

        # res = response.anulacionCompra()
        """
        metodo: obtencion de anulacion compra
        return: dic informacion anulacion compra
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.anulacionCompra({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'codAutorizacion': cod_autorizacion,
            'nitProveedor': nit_proveedor,
            'nroDuiDim': nro_duidim,
            'nroFactura': nro_factura,
        })
        return self.check_response(res)

    def confirmacion_compras(self, wsdl=False, cufd=False, cuis=False, nit=False, archivo=False, qty_facturas=False,
                             send_date=False, gestion=False, hash_archivo=False, periodo=False):

        # res = response.confirmacionCompras()
        """
        metodo: obtencion de confirmacion compras
        return: dic informacion confirmacion compras
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.confirmacionCompras({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'archivo': archivo,
            'cantidadFacturas': qty_facturas,
            'fechaEnvio': send_date,
            'gestion': gestion,
            'hashArchivo': hash_archivo,
            'periodo': periodo,
        })
        return self.check_response(res)

    def consulta_compras(self, wsdl=False, cufd=False, cuis=False, nit=False, event_date=False):

        # res = response.consultaCompras()
        """
        metodo: obtencion de consulta compras
        return: dic informacion consulta compras
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.consultaCompras({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cufd': cufd,
            'cuis': cuis,
            'nit': nit,
            'fechaEvento': event_date,
        })
        return self.check_response(res)

    def recepcion_anexos(self, wsdl=False, code_doc_sector=False, code_emition=False, cufd=False, cuis=False, nit=False,
                         type_invo_doc=False, code=False, code_product=False, code_product_sin=False, tipo_code=False,
                         cuf=False):

        # res = response.recepcionAnexos()
        """
        metodo: obtencion de crecepcion anexos
        return: dic informacion crecepcion anexos
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.recepcionAnexos({
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
            'code': code,
            'codigoProducto': code_product,
            'codigoProductoSin': code_product_sin,
            'tipoCodigo': tipo_code,
            'cuf': cuf,
        })
        return self.check_response(res)
