# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from ..tools import siat_tools
import base64
from datetime import date, datetime
from datetime import datetime, timedelta
import pytz



class SiatEventosSignificativos(models.Model):

    _name = 'siat.eventos.significativos'


    siat_cuis_id = fields.Many2one('siat.cuis', string='Siat Cuis', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Compañia', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    environment_code = fields.Selection([(1, 'PRODUCCIÓN'), (2, 'PRUEBAS')], string='Enviroment Code', related='company_id.environment_code', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    system_code = fields.Char('System Code', related='company_id.system_code', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    siat_nit = fields.Char('NIT', required=True, related='company_id.siat_nit', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    cuis = fields.Char('CUIS', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    cufd = fields.Char('CUFD', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    branch_code = fields.Integer('Branch Code', default=0, related='siat_cuis_id.branch_code', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    selling_point_code = fields.Integer('Selling Point Code', default=0, readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    evento_significativo_id = fields.Many2one('eventos.significativos', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    descripcion = fields.Char(string="Descripcion", readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    date_start = fields.Datetime(string='Fecha Inicio Evento', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    date_end = fields.Datetime(string='Fecha Fin Evento', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    cufd_event = fields.Char(string='Cufd Evento', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    state = fields.Selection([('draft', 'Borrador'),
                              ('send', 'Enviado'),
                              ('validated', 'Validado'),
                              ('failed', 'Fallido'),], default='draft')
    reception_code = fields.Char(string='Codigo de recepcion', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    package_reception_code = fields.Char(string='Codigo de recepcion paquete factura', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    invoice_ids = fields.One2many('account.invoice', 'siat_evento_significativo_id', string='Facturas', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    tar_file = fields.Binary(string="Tar", readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    tar_filename = fields.Char(string="Tar", readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    package_sent = fields.Boolean("Paquete enviado", default=False)
    siat_cafc = fields.Char(string="Cafc", states={'draft': [('readonly', False)], 'send': [('readonly', False)]})

    # @api.model
    # def create(self, vals):
    #     res = super(SiatEventosSignificativos, self).create(vals)
    #     # if res.evento_significativo_id.codigo_clasificador in [5, 6, 7]:
    #     #     res.cufd_event = self.env['historial.cufd'].get_my_date_cufd(res.siat_cuis_id.id, res.cuis, res.branch_code,res.selling_point_code, res.date_start)
    #     return res

    def action_register_event_significant(self):
        obj_ope = self.env['siat.servicio.facturacion.operaciones']
        
        # Convertir fechas a zona horaria de Bolivia
        user_tz = pytz.timezone(self.env.user.tz or 'America/La_Paz')
        start_dt = fields.Datetime.from_string(self.date_start).replace(tzinfo=pytz.utc).astimezone(user_tz)
        end_dt = fields.Datetime.from_string(self.date_end).replace(tzinfo=pytz.utc).astimezone(user_tz)
        
        # Validar duración máxima (24 horas)
        if (end_dt - start_dt) > timedelta(hours=72):
            raise UserError("El evento no puede durar más de 72 horas")
        
        res = obj_ope.registro_evento_significativo(
            siat_cuis=self.cuis,
            siat_cufd=self.cufd,
            branch_code=self.branch_code,
            cufd_code=self.cufd_event,
            selling_point_code=self.selling_point_code,
            event_date_start=start_dt.strftime('%Y-%m-%dT%H:%M:%S'),
            event_date_end=end_dt.strftime('%Y-%m-%dT%H:%M:%S'),
            description=self.descripcion,
            code_event=self.evento_significativo_id.codigo_clasificador
        )
        
        if 'transaccion' in res and res['transaccion']:
            self.write({
                'state': 'send',
                'reception_code': str(res['codigoRecepcionEventoSignificativo'])
            })
        else:
            self.write({'state': 'failed'})
            error_msg = res.get('mensajesList', [{}])[0].get('descripcion', 'Error desconocido')
            raise UserError("Error registrando evento:")
    def action_register_package_invoices(self):
        self.register_package_invoices(self.company_id,
                                       self.invoice_ids,
                                       self.siat_cuis_id,
                                       self.reception_code)

    def register_package_invoices(self, company, invoices, channel, code_event):
        send_date = channel.get_information_fecha_hora()
        if len(invoices) == 0:
            raise ValidationError("No hay facturas para procesar")
        if len(invoices) > 500:
            raise ValidationError("No se puede procesar mas de 500 facturas")
        tar_file = siat_tools.action_generator_file_tar([x.siat_xml_file for x in invoices])
        self.tar_file = tar_file
        # gun_zip = siat_tools.generate_file_gzip(self.tar_file, 'paquete.tar.gz')
        # convertimos el gzip en binary
        gun_zip_binary = tar_file
        # gun_zip_binary = self.tar_file

        self.tar_filename = 'paquete.tar.gz'
        hash_256 = siat_tools.action_generator_hash(self.tar_file, 'hash_256')

        obj = self.env['siat.servicio.facturacion']
        res = obj.recepcion_paquete_factura(company_id=company,
                                            code_doc_sector=channel.type_doc_sector.codigo_clasificador,
                                            code_emition=2, #TODO:talvez deberiamos de parametrizar
                                            mode_constant=channel.mode_constant,
                                            selling_point_code=channel.selling_point_code,
                                            branch_code=channel.branch_code,
                                            cufd=channel.cufd_code,
                                            cuis=channel.cuis,
                                            type_invo_doc=channel.type_factura,
                                            archivo=gun_zip_binary,
                                            send_date=send_date,
                                            hash_archivo=hash_256,
                                            cafc=None if not self.siat_cafc else self.siat_cafc,
                                            qty_facturas=len(invoices),
                                            code_event=code_event)
        if 'transaccion' in res and res['transaccion']:
            self.write({'package_reception_code': str(res['codigoRecepcion']),
                        'package_sent': True})

    def action_inv_package_receipt_validation(self):
        self.inv_package_receipt_validation(self.company_id,
                                            self.siat_cuis_id,
                                            self.package_reception_code)

    def inv_package_receipt_validation(self, company, channel, pkg_code):
        obj = self.env['siat.servicio.facturacion']
        res = obj.validacion_recepcion_paquete_factura(company_id=company,
                                                       code_doc_sector=channel.type_doc_sector.codigo_clasificador,
                                                       code_emition=2, #TODO:talvez deberiamos de parametrizar
                                                       mode_constant=channel.mode_constant,
                                                       selling_point_code=channel.selling_point_code,
                                                       branch_code=channel.branch_code,
                                                       cufd=channel.cufd_code,
                                                       cuis=channel.cuis,
                                                       type_invo_doc=channel.type_factura.codigo_clasificador,
                                                       code_reception=pkg_code)
        if 'transaccion' in res and res['transaccion']:
            if 'codigoEstado' in res and res['codigoEstado'] == 908:
                self.write({'state': 'validated'})
            else:
                _, msj = obj.validate_response(res, force_msj=True)
                raise ValidationError(str(res['codigoEstado']) + ' ' + str(res['codigoDescripcion']) + '\n' + msj)

    def action_consulta_evento_significativo(self):
        if not self.date_start and self.cuis:
            raise ValidationError("Datos insuficientes")
        return self.consulta_evento_significativo(self.siat_cuis_id, siat_tools.strdt_utc_to_dt_usr_tz(self.date_start, self.env.user.tz).strftime('%Y-%m-%d'))

    def consulta_evento_significativo(self, channel, event_date):
        obj = self.env['siat.servicio.facturacion.operaciones']
        res = obj.consulta_evento_significativo(channel=channel, event_date=event_date)
        if 'transaccion' in res and res['transaccion']:
            return obj.call_custom_wizard_response('Servicio Facturacion', '\n'.join(['codigoRecepcionEventoSignificativo: ' + str(elem['codigoRecepcionEventoSignificativo']) for elem in res['listaCodigos']]))