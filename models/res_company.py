# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    """
    Extension de la clase res.company para adicionar capos tecnicos respecto a la nueva normativa V2 del SIN
    """
    _inherit = "res.company"

    # direccion servicio siat documentacion ServicioFacturacion
    wsdl_computerized_billing = fields.Text(string='WDSL Facturacion',
                                 default='https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionComputarizada?wsdl',
                                 help='Here goes the wsdl url SOAP Service to use')

    # SERVICIO DE SINCRONIZACIÓN DE DATOS
    wsdl_data_sync = fields.Text(string='WDSL Data Sync',
                                 default='https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl',)

    # SERVICIO DE RECEPCIÓN DE COMPRAS
    wsdl_receipt_of_purchases = fields.Text(string='WDSL Receipt of purchases',
                                            default='https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioRecepcionCompras?wsdl',)

    # SERVICIO DE OPERACIONES
    wsdl_operations = fields.Text(string='WDSL Operations',
                                  default='https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl',)

    # SERVICIO DE OBTENCIÓN DE CÓDIGOS
    wsdl_codes_procurements = fields.Text(string='WDSL Codes procurement',
                                          default='https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionCodigos?wsdl',)

    # SERVICIO de FACTURA COMPRA-VENTA
    wsdl_in_out_invoice = fields.Text(string='WDSL Purchase & Sale Invoicing',
                                 default='https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionCompraVenta?wsdl',)

    # RMC: LINK DE IMPUESTO PARA SETEARLO Y CONCATENAR EN EL QR
    lnk_st_qr = fields.Text(string='RUTA de la pagina a impuestos',
                            default='https://pilotosiat.impuestos.gob.bo/consulta/QR?',
                            help="ruta o enlace a los servicios de la Administración Tributaria")

    # CONSTANTES DE AMBIENTES
    # todo: cambiar el dafault cuando sea necesario
    environment_code = fields.Selection([(1, 'PRODUCCIÓN'), (2, 'PRUEBAS')], string='Enviroment Code', default=2)

    # CONSTANTES DE MODALIDADES
    # todo: cambiar el dafault cuando sea necesario
    mode_constant = fields.Selection([(1, 'ELECTRÓNICA EN LÍNEA'), (2, 'COMPUTARIZADA EN LÍNEA')],
                                     string='Mode Constant', default=2)

    # CÓDIGO DE SISTEMA
    system_code = fields.Char('System Code')

    # Codigo de Sucursal
    branch_code = fields.Integer('Branch Code', default=0)

    # CODIGO DE PUNTO DE VENTA
    selling_point_code = fields.Integer('Selling Point Code', default=0)

    # Token Delegado
    delegated_token = fields.Text(string='Delegated Token')

    # Código Único de Inicio de Sistemas
    cuis = fields.Char('CUIS')

    # Fecha de vencimiento CUIS
    cuis_effecive_date = fields.Datetime('CUIS Effective Date')

    # Código Único de Facturación Diario
    cufd = fields.Char('CUFD')

    # Fecha de vencimiento CUFD
    cufd_effecive_date = fields.Datetime('CUFD Effective Date')

    # codigo de control CUFD
    cufd_cod_control = fields.Char('CUFD Code Control')

    # direccion CUFD
    cufd_address = fields.Char('CUFD Address')

    # actividad economica
    #todo: por ahora ponemos este campo aca, pero es necesario crear un modelo de actividades donde registrar este campo ademas de su dosificacion y su logica
    economic_activity = fields.Many2one('codigos.actividades', string='Economic Activity')

    siat_cuis_ids = fields.One2many('siat.cuis', 'company_id', string='Siat Cuis')

    siat_nit = fields.Char('NIT', required=True,
                           help='Tax Identification Number idenfy unequivocally that allows taxpayers and will consist of control codes issued by the tax authorities, depending on the type of taxpayer.')

    siat_razon_social = fields.Char(string='Business name',
                                    required=False,
                                    size=150,
                                    default='',
                                    help="Business name, for example for a 'Empresa Unipersonal': \n"
                                         "'DE: JUAN PEREZ' or 'TIENDA AMIGA S.R.L.'")
    siat_use_razon_social = fields.Boolean(string="Usar razon social", default=False)

    siat_cuis_id = fields.Many2one('siat.cuis', string='Cuis')
    
    # @api.one
    # @api.constrains('environment_code')
    # def constrains_environment_code(self):
    #     """TODO: quitar o adecuar este constrain cuando pasemos las validaciones o proceso de desarrollo este implementado"""
    #     if self.environment_code == 1:
    #         raise ValidationError(
    #             "El código de constante de PRODUCCION no esta habilitado aun, por favor seleccione la constante de PRUEBAS")

    # @api.one
    # @api.constrains('mode_constant')
    # def constrains_mode_constant(self):
    #     """TODO: quitar o adecuar este constrain cuando el metodo de facturacion electronica en lina este implementado"""
    #     if self.mode_constant == 1:
    #         raise ValidationError("El metod de facturacion electronica en linea no esta habilitado aun, por favor seleccione el metodo de facturacion computarizada en linea")

    @api.one
    @api.constrains('siat_nit')
    def constrains_siat_nit(self):
        if self.siat_nit:
            return self.siat_nit
        else:
            raise UserError("El NIT factura no esta configurado")

    # metodos siat documentacion
    def test_wsdl_computerized_billing(self):
        soap_obj = self.env['siat.servicio.facturacion.computarizada']
        res = soap_obj.btn_verificar_comunicacion()
        return res

    def test_wsdl_data_sync(self):
        soap_obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = soap_obj.btn_verificar_comunicacion()
        return res

    def test_wsdl_receipt_of_purchases(self):
        soap_obj = self.env['siat.servicio.recepcion.compras']
        res = soap_obj.btn_verificar_comunicacion()
        return res

    def test_wsdl_operations(self):
        soap_obj = self.env['siat.servicio.facturacion.operaciones']
        res = soap_obj.btn_verificar_comunicacion()
        return res

    def test_wsdl_codes_procurements(self):
        soap_obj = self.env['siat.servicio.facturacion.codigos']
        res = soap_obj.btn_verificar_comunicacion()
        return res

    def test_wsdl_in_out_invoice(self):
        soap_obj = self.env['siat.servicio.facturacion']
        res = soap_obj.btn_verificar_comunicacion()
        return res

    def action_sincronizar_lista_productos_servicios(self):
        '''
        '''
        self.action_sincronizar_lista_productos_servicios_act(self.siat_cuis_id)

    def action_sincronizar_lista_productos_servicios_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de produtos servicios
        y los registra en el modelo productos_servicios
        '''
        # self.env['siat.servicio.facturacion.codigos'].cuis()
        res = self.env['siat.servicio.facturacion.sincronizacion'].sincronizar_lista_productos_servicios(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_producto = self.env['productos.servicios']
        for line in res['listaCodigos']:
            res_producto = obj_producto.search([('codigo_producto', '=', line['codigoProducto'])])
            if not len(res_producto) > 0:
                value = {'codigo_actividad': line['codigoActividad'],
                         'codigo_producto': line['codigoProducto'],
                         'descripcion_producto': line['descripcionProducto']}
                obj_producto.create(value)

    def action_sincronizar_codigos_actividades(self):
        '''
        '''
        self.action_sincronizar_codigos_actividades_act(self.siat_cuis_id)

    def action_sincronizar_codigos_actividades_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat la lista de codigos de actividades
        y los registra en su respectivo modelo
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_actividades(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['codigos.actividades']
        self.action_sincronizacion_codigos_actividades(res['listaActividades'], obj_model)

    def action_sincronizar_leyendas_facturas(self):
        '''
        '''
        self.action_sincronizar_leyendas_facturas_act(self.siat_cuis_id)

    def action_sincronizar_leyendas_facturas_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat la lista de leyendas de facturas
        y los registra en su respectivo modelo
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_lista_leyendas_factura(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['leyenda.factura']
        self.action_sincronizacion_leyendas_facturas(res['listaLeyendas'], obj_model)

    def action_sincronizar_lista_mensajes_servicios(self):
        '''
        '''
        self.action_sincronizar_lista_mensajes_servicios_act(self.siat_cuis_id)

    def action_sincronizar_lista_mensajes_servicios_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de mensajes servicios
        y los registra en el modelo mensajes_servicios
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_lista_mensajes_servicios(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['mensajes.servicios']
        self.action_sincronizacion_mensajes_servicios(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_eventos_significativos(self):
        '''
        '''
        self.action_sincronizar_parametrica_eventos_significativos_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_eventos_significativos_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica eventos significativos
        y los registra en el modelo eventos_significativos
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_eventos_significativos(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['eventos.significativos']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_motivo_anulacion(self):
        '''
        '''
        self.action_sincronizar_parametrica_motivo_anulacion_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_motivo_anulacion_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica motivos anulacion
        y los registra en el modelo motivo_anulacion
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_motivos_anulacion(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['motivo.anulacion']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_pais_origen(self):
        '''
        '''
        self.action_sincronizar_parametrica_pais_origen_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_pais_origen_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica motivos anulacion
        y los registra en el modelo motivo_anulacion
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_pais_origen(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['pais.origen']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_documento_identidad(self):
        '''
        '''
        self.action_sincronizar_parametrica_documento_identidad_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_documento_identidad_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo documento identidad
        y los registra en el modelo documento_identidad
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_documento_identidad(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['documento.identidad']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_param_tipo_documento_sector(self):
        '''
        '''
        self.action_sincronizar_parametrica_documento_sector_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_documento_sector_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo documento sector
        y los registra en el modelo documento_sector
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_documento_sector(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['documento.sector']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_param_cod_actividad_documento_sector(self):
        self.sincronizar_param_cod_actividad_documento_sector(self.siat_cuis_id)

    def sincronizar_param_cod_actividad_documento_sector(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica Códigos de Tipo Documento Sector
        y los registra en el modelo documento_sector
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_lista_actividades_documento_sector(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['actividades.documento.sector']
        self.action_sincronizacion_cod_actividad_documento_sector(res['listaActividadesDocumentoSector'], obj_model)

    def action_sincronizar_parametrica_tipo_emision(self):
        '''
        '''
        self.action_sincronizar_parametrica_tipo_emision_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_tipo_emision_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo emision
        y los registra en el modelo tipo_emision
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_emision(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['tipo.emision']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_tipo_habitacion(self):
        '''
        '''
        self.action_sincronizar_parametrica_tipo_habitacion_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_tipo_habitacion_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo habitacion
        y los registra en el modelo yipo_habitacion
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_habitacion(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['tipo.habitacion']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_tipo_metodo_pago(self):
        '''
        '''
        self.action_sincronizar_parametrica_tipo_metodo_pago_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_tipo_metodo_pago_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo metodo pago
        y los registra en el modelo tipo_metodo_pago
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_metodo_pago(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['tipo.metodo.pago']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_tipo_moneda(self):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo moneda
        y los registra en el modelo tipo_moneda
        '''
        self.action_sincronizar_parametrica_tipo_moneda_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_tipo_moneda_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo moneda
        y los registra en el modelo tipo_moneda
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_moneda(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['tipo.moneda']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_tipo_punto_venta(self):
        '''
        '''
        self.action_sincronizar_parametrica_tipo_punto_venta_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_tipo_punto_venta_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipo punto venta
        y los registra en el modelo tipo_punto_venta
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipo_punto_venta(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['tipo.punto.venta']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_tipos_factura(self):
        '''
        '''
        self.action_sincronizar_parametrica_tipos_factura_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_tipos_factura_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica tipos factura
        y los registra en el modelo tipos_factura
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_tipos_factura(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['tipos.factura']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    def action_sincronizar_parametrica_unidad_medida(self):
        '''
        '''
        self.action_sincronizar_parametrica_unidad_medida_act(self.siat_cuis_id)

    def action_sincronizar_parametrica_unidad_medida_act(self, siat_cuis_id):
        '''
        Funcion que consulta al siat  la lista de parametrica unidad medidad
        y los registra en el modelo unidad_medida
        '''
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_parametrica_unidad_medida(cuis=siat_cuis_id, nit=self.siat_nit)
        obj_model = self.env['unidad.medida']
        self.action_sincronizacion(res['listaCodigos'], obj_model)

    # ----------- Logica de resgitro de informacion obtenida -----------

    def action_sincronizacion(self, lines, obj_model):
        '''
        Funcion Base para registrar la informacion obtenidad por el servicio web
        :param lines: array de registros
        :param obj_model: modelo en el cual se registrara la informacion
        '''
        for line in lines:
            res_eventos = obj_model.search([('codigo_clasificador', '=', line['codigoClasificador'])])
            if not len(res_eventos) > 0:
                value = {'codigo_clasificador': line['codigoClasificador'],
                         'descripcion': line['descripcion']}
                obj_model.create(value)

    def action_sincronizacion_mensajes_servicios(self, lines, obj_model):
        '''
        Funcion Base para registrar la informacion obtenidad por el servicio web
        :param lines: array de registros
        :param obj_model: modelo en el cual se registrara la informacion
        '''
        for line in lines:
            res_eventos = obj_model.search([('codigo_clasificador', '=', line['codigoClasificador'])])
            if not len(res_eventos) > 0:
                value = {'codigo_clasificador': line['codigoActividad'],
                         'descripcion': line['descripcion']}
                obj_model.create(value)

    def action_sincronizacion_leyendas_facturas(self, lines, obj_model):
        '''
        Funcion Base para registrar la informacion obtenidad por el servicio web
        :param lines: array de registros
        :param obj_model: modelo en el cual se registrara la informacion
        '''
        for line in lines:
            res_eventos = obj_model.search([('codigo_actividad', '=', line['codigoActividad'])])
            if not len(res_eventos) > 0:
                value = {'codigo_actividad': line['codigoActividad'],
                         'descripcion_leyenda': line['descripcionLeyenda']}
                obj_model.create(value)

    def action_sincronizacion_codigos_actividades(self, lines, obj_model):
        '''
        Funcion Base para registrar la informacion obtenidad por el servicio web
        :param lines: array de registros
        :param obj_model: modelo en el cual se registrara la informacion
        '''
        for line in lines:
            res_eventos = obj_model.search([('codigo_caeb', '=', line['codigoCaeb'])])
            if not len(res_eventos) > 0:
                value = {'codigo_caeb': line['codigoCaeb'],
                         'descripcion': line['descripcion'],
                         'tipo_actividad': line['tipoActividad']}
                obj_model.create(value)

    def action_sincronizacion_cod_actividad_documento_sector(self, lines, obj_model):
        '''
        Funcion Base para registrar la informacion obtenidad por el servicio web
        :param lines: array de registros
        :param obj_model: modelo en el cual se registrara la informacion
        '''
        for line in lines:
            res_eventos = obj_model.search([('codigo_actividad', '=', line['codigoActividad'])])
            if not len(res_eventos) > 0:
                value = {'codigo_actividad': line['codigoActividad'],
                         'codigo_documento_sector': int(line['codigoDocumentoSector']),
                         'tipo_documento_sector': line['tipoDocumentoSector']}
                obj_model.create(value)

    def action_consulta_punto_venta(self):
        obj = self.env['siat.servicio.facturacion.operaciones']
        res = obj.consulta_punto_venta(company_id=self,
                                       cuis=self.siat_cuis_id.cuis)
        if res['transaccion'] == True:
            msj = ''
            for line in res['listaPuntosVentas']:
                msj += str(line['codigoPuntoVenta']).ljust(10) + '   ' +str(line['nombrePuntoVenta']) + '   ' + str(line['tipoPuntoVenta']) +' ' + "\n"
            raise UserError(msj)

    def action_get_informationfecha_hora(self):
        dt = self.siat_cuis_id.get_information_fecha_hora()
        if dt:
            title = 'Fecha y Hora'
            message = str(dt)
            return self.env['siat.soap.base'].call_custom_wizard_response(title, message)






