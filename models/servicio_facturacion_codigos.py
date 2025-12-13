# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class SiatServicioFacturacionCodigos(models.Model):
    _name = 'siat.servicio.facturacion.codigos'
    _inherit = 'siat.soap.base'
    _description = 'Servicio Recepcion Compras'

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        wsdl = self.env.user.company_id.wsdl_codes_procurements
        if not wsdl:
            raise ValidationError(
                'No tiene configurada la ruta de conexion con Impuestos Nacionales. \n Contactese con su administrador.')
        return wsdl

    # ************************* METODOS *******************************

    def verificar_nit(self, nit, channel, wsdl=False):
        """
        metodo: verificar Nit
        return: bool, verificacion de nit
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            res = client.service.verificarNit({
                'codigoAmbiente': company_id.environment_code,
                'codigoModalidad': channel.mode_constant,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': channel.branch_code,
                'cuis': channel.cuis,
                'nit': str(company_id.siat_nit),
                'nitParaVerificacion': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
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
        res = client.service.verificarComunicacion()
        return self.check_response(res)

    def btn_verificar_comunicacion(self):
        return self.msj_conexion_test(self.check_transaction(self.verificar_comunicacion()))

    def cuis_masivo(self, wsdl=False, nit=False, cuis=False):

        # # res = response.service.cuisMasivo()
        """
        metodo: obtencion de cuis masivo
        return: dic informacion cuis masivo
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.cuisMasivo({
            'codigoAmbiente': company_id.environment_code,
            'codigoModalidad': company_id.mode_constant,
            'codigoSistema': str(company_id.system_code),
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSucursal': company_id.branch_code,
            'nit': nit,
            'cuis': cuis,
        })
        return self.check_response(res)

    def cufd(self, wsdl=False, cuis=False):
        """
        metodo: obtencion de cufd
        return: dic informacion cufd
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.cufd({
            'codigoAmbiente': company_id.environment_code,
            'codigoSistema': str(company_id.system_code),
            'nit': int(company_id.siat_nit),
            'codigoModalidad': company_id.mode_constant,
            'cuis': cuis,
            'codigoSucursal': company_id.branch_code,
            'codigoPuntoVenta': company_id.selling_point_code,
        })
        return self.check_response(res)
    
    def notifica_certificado_revocado(self, wsdl=False, certificado=False, date_revocacion=False, cuis=False, nit=False,
                                      razon_revocacion=False):

        # # res = response.service.notificaCertificadoRevocado()
        """
        metodo: obtencion de notificado certificado revocado
        return: dic informacion notificado certificado revocado
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.notificaCertificadoRevocado({
            'certificado': certificado,
            'codigoAmbiente': company_id.environment_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': company_id.branch_code,
            'cuis': cuis,
            'fechaRevocacion': date_revocacion,
            'nit': nit,
            'razonRevocacion': razon_revocacion,
        })
        return self.check_response(res)

    def cuis(self, wsdl=False):
        """
        metodo: obtencion de cuis
        return: dic informacion cuis
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.cuis({
                'codigoAmbiente': company_id.environment_code,
                'codigoSistema': str(company_id.system_code),
                'nit': int(company_id.siat_nit),
                'codigoModalidad': company_id.mode_constant,
                'codigoSucursal': company_id.branch_code,
                'codigoPuntoVenta': company_id.selling_point_code,
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
        # return self.check_response(res)

    def cufd_masivo(self, wsdl=False, nit=False, cuis=False):

        # res = response.cufdMasivo()
        """
        metodo: obtencion de cufd masivo
        return: dic informacion cufd masivo
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.cufdMasivo({
            'codigoAmbiente': company_id.environment_code,
            'codigoModalidad': company_id.mode_constant,
            'codigoSistema': str(company_id.system_code),
            'codigoPuntoVenta': company_id.selling_point_code,
            'codigoSucursal': company_id.branch_code,
            'nit': nit,
            'cuis': cuis,
        })
        return self.check_response(res)
