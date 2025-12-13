# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import pytz
from ..tools import siat_tools

class SiatServicioFacturacionSincronizacion(models.Model):
    _name = 'siat.servicio.facturacion.sincronizacion'
    _inherit = 'siat.soap.base'
    _description = 'Servicio Facturacion'

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        wsdl = self.env.user.company_id.wsdl_data_sync
        if not wsdl:
            raise ValidationError(
                'No tiene configurada la ruta de conexion con Impuestos Nacionales. \n Contactese con su administrador.')
        return wsdl

    # ************************* METODOS *******************************

    def sincronizar_actividades(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarActividades()
        """
        metodo: obtencion de lista actividades documento sector
        return: dic informacion lista actividades documento sector
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.sincronizarActividades({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': cuis.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': cuis.branch_code,
            'cuis': cuis.cuis,
            'nit': nit,
        })
        return self.check_response(res)

    def sincronizar_fecha_hora(self, company=False, cuis=False, sucursal=False, puntoventa=False):
        """
    metodo: obtencion de lista actividades documento sector
    return: dic informacion lista actividades documento sector
        """
        company_id = company if company else self.env.user.company_id
        connection, client = self.connect_wsdl(api_key=True)
        self.conection_validation(connection, client)
        try:
            res = client.service.sincronizarFechaHora({
            'codigoAmbiente': company_id.environment_code,
            'codigoSistema': str(company_id.system_code),
            'nit': long(company_id.siat_nit),
            'codigoPuntoVenta': puntoventa,
            'codigoSucursal': sucursal,
            'cuis': cuis,
            })
        except Exception, e:
        # SOLUCIÓN: Verificar y establecer zona horaria predeterminada
            user_tz = self.env.user.tz or 'America/La_Paz'  # Zona horaria predeterminada para Bolivia
        
            ahora = siat_tools.convert_dt_tz_to_custom_tz(
            siat_tools.add_utc_tz_to_dt(datetime.now()), 
            pytz.timezone(user_tz)  # Usar la variable con zona horaria válida
            )
            fecha = ahora.strftime("%Y-%m-%dT%H:%M:%S.%f")
            res = {'transaccion': True, 'fechaHora': fecha}
            return res
        
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        else:
        # podemos aplicar evaluacion propias del metodo
        # -------
        # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def action_get_information_cuis(self, company=False, modalidad=False, sucursal=False, puntoventa=False):
        """
        metodo: obtencion de cuis
        return: dic informacion cuis
        """
        company_id = company if company else self.env.user.company_id
        obj = self.env['siat.servicio.facturacion.codigos']
        connection, client = obj.connect_wsdl(api_key=True)
        obj.conection_validation(connection, client)
        try:
            # my code
            res = client.service.cuis({
                'codigoAmbiente': company_id.environment_code,
                'codigoSistema': str(company_id.system_code),
                'nit': long(company_id.siat_nit),
                'codigoModalidad': modalidad,
                'codigoSucursal': sucursal,
                'codigoPuntoVenta': puntoventa,
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

    def action_get_information_cufd(self, cuis=False, company=False, modalidad=False, sucursal=False, puntoventa=False):
        """
        metodo: obtencion de cufd
        return: dic informacion cufd
        """
        company_id = company if company else self.env.user.company_id
        obj = self.env['siat.servicio.facturacion.codigos']
        connection, client = obj.connect_wsdl(api_key=True)
        obj.conection_validation(connection, client)
        try:
            # my code
            res = client.service.cufd({
                'codigoAmbiente': company_id.environment_code,
                'codigoSistema': str(company_id.system_code),
                'nit': int(company_id.siat_nit),
                'codigoModalidad': modalidad,
                'cuis': cuis,
                'codigoSucursal': sucursal,
                'codigoPuntoVenta': puntoventa,
            })
        except Exception, e:
            res = {'transaccion': False, 'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)
    def sincronizar_lista_leyendas_factura(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarListaLeyendasFactura()
        """
        metodo: obtencion de lista actividades documento sector
        return: dic informacion lista actividades documento sector
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.sincronizarListaLeyendasFactura({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': cuis.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': cuis.branch_code,
            'cuis': cuis.cuis,
            'nit': nit,
        })
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_habitacion(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoHabitacion()
        """
        metodo: obtencion de lista actividades documento sector
        return: dic informacion lista actividades documento sector
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTipoHabitacion({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False, 'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_lista_actividades_documento_sector(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarListaActividadesDocumentoSector()
        """
        Códigos de Actividades Documento Sector
        metodo: obtencion de lista actividades documento sector
        return: dic informacion lista actividades documento sector

        (actividadesDocumentoSectorDto){
                                       codigoActividad = "465000"
                                       codigoDocumentoSector = 1
                                       tipoDocumentoSector = "FCV"
                                     }
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarListaActividadesDocumentoSector({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_documento_identidad(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoDocumentoIdentidad()
        """
        metodo: obtencion de tipo documento identidad
        return: dic informacion tipo documento identidad
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        try:
            # my code
            res = client.service.sincronizarParametricaTipoDocumentoIdentidad({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_unidad_medida(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaUnidadMedida()
        """
        metodo: obtencion de unidad de medida
        return: dic informacion unidad de medida
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaUnidadMedida({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_documento_sector(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoDocumentoSector()
        """
        Códigos de Tipo Documento Sector
        metodo: obtencion de tipo documento sector
        return: dic informacion tipo documento sector
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTipoDocumentoSector({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipos_factura(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTiposFactura()
        """
        metodo: obtencion de tipos de factura
        return: dic informacion tipos de factura
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTiposFactura({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
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

    def sincronizar_lista_mensajes_servicios(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarListaMensajesServicios()
        """
        metodo: obtencion del tipo metodo de pago
        return: dic informacion tipo metodo de pago
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)
        res = client.service.sincronizarListaMensajesServicios({
            'codigoAmbiente': company_id.environment_code,
            'codigoPuntoVenta': cuis.selling_point_code,
            'codigoSistema': str(company_id.system_code),
            'codigoSucursal': cuis.branch_code,
            'cuis': cuis.cuis,
            'nit': nit,
        })
        res_validated, str_error = self.validate_response(res)
        if res_validated:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_metodo_pago(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoMetodoPago()
        """
        metodo: obtencion del tipo metodo de pago
        return: dic informacion tipo metodo de pago
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTipoMetodoPago({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_eventos_significativos(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaEventosSignificativos()
        """
        metodo: obtencion de eventos significativos
        return: dic informacion eventos significativos
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaEventosSignificativos({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_punto_venta(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoPuntoVenta()
        """
        metodo: obtencion del tipo punto de venta
        return: dic informacion tipo punto de venta
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTipoPuntoVenta({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_lista_productos_servicios(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarListaProductosServicios()
        """
        metodo: obtencion del producto servicios
        return: dic informacion producto servicios
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarListaProductosServicios({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_emision(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoEmision()
        """
        metodo: obtencion del tipo de emision
        return: dic informacion tipo de emision
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTipoEmision({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_pais_origen(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaPaisOrigen()
        """
        metodo: obtencion del pais de origen
        return: dic informacion pais de origen
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaPaisOrigen({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_tipo_moneda(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaTipoMoneda()
        """
        metodo: obtencion del tipo de moneda
        return: dic informacion tipo de moneda
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaTipoMoneda({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)

    def sincronizar_parametrica_motivos_anulacion(self, wsdl=False, cuis=False, nit=False):

        # res = response.service.sincronizarParametricaMotivoAnulacion()
        """
        metodo: obtencion de motivos anulacion
        return: dic informacion motivos anulacion
        """
        company_id = self.env.user.company_id
        connection, client = self.connect_wsdl(wsdl=wsdl, api_key=True)
        self.conection_validation(connection, client)

        try:
            # my code
            res = client.service.sincronizarParametricaMotivoAnulacion({
                'codigoAmbiente': company_id.environment_code,
                'codigoPuntoVenta': cuis.selling_point_code,
                'codigoSistema': str(company_id.system_code),
                'codigoSucursal': cuis.branch_code,
                'cuis': cuis.cuis,
                'nit': nit,
            })
        except Exception, e:
            res = {'transaccion': False,
                   'mensajesList': [{'codigo': 995, 'descripcion': 'SERVICIO NO DISPONIBLE \n' + str(e)}]}
        res_validated, str_error = self.validate_response(res)
        if res_validated or res['mensajesList'][0]['codigo'] == 995:
            return res
        else:
            # podemos aplicar evaluacion propias del metodo
            # -------
            # caso contrario simplemente devolvemos los mensajes por defecto de la respuesta
            raise ValidationError(str_error)
