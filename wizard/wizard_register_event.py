# -*- coding: utf-8 -*-
# from datetime import datetime_
from openerp.exceptions import ValidationError
from openerp import fields, api, models, _
# from openerp.exceptions import UserError


class RegisterEventoSignificativo(models.TransientModel):
    _name = "register.evento.significativo"

    siat_cuis_id = fields.Many2one('siat.cuis', string='Invoice Channel')
    company_id = fields.Many2one('res.company', string='Compañia')

    environment_code = fields.Selection([(1, 'PRODUCCIÓN'), (2, 'PRUEBAS')], string='Enviroment Code', related='company_id.environment_code')
    system_code = fields.Char('System Code', related='company_id.system_code')
    siat_nit = fields.Char('NIT', required=True, related='company_id.siat_nit', help='Tax Identification Number idenfy unequivocally that allows taxpayers and will consist of control codes issued by the tax authorities, depending on the type of taxpayer.')
    cuis = fields.Char('CUIS')
    cufd = fields.Char('CUFD')
    branch_code = fields.Integer('Sucursal')
    selling_point_code = fields.Integer('Selling Point Code', related='siat_cuis_id.selling_point_code')
    evento_significativo_id = fields.Many2one('eventos.significativos', string='Tipo de Evento', required=True)
    descripcion = fields.Char(string="Descripcion")
    date_start = fields.Datetime(string='Fecha Inicio Evento', required=True)
    date_end = fields.Datetime(string='Fecha Fin Evento', required=True)
    cufd_event = fields.Char(string='Cufd Evento')
    siat_cafc = fields.Char(string="Cafc")

    def action_register_event(self):
        if self.evento_significativo_id.codigo_clasificador in [1, 2, 3, 4]:
            raise ValidationError('Este procedimiento solamente funciona para los tipos de evento 5, 6 y 7.')
        sin_dt = self.siat_cuis_id.get_information_fecha_hora()
        self.siat_cuis_id.get_cufd_data(sin_dt, force_cufd=True)
        value = {'siat_cuis_id': self.siat_cuis_id.id,
                 'company_id': self.company_id.id,
                 'evento_significativo_id': self.evento_significativo_id.id,
                 'descripcion': self.descripcion,
                 'cuis': self.cuis,
                 'cufd': self.siat_cuis_id.cufd_code,
                 'cufd_event': self.cufd,
                 'branch_code': self.branch_code,
                 'selling_point_code': self.selling_point_code,
                 'date_start': self.date_start,
                 'date_end': self.date_end,
                 'environment_code': self.environment_code,
                 'siat_cafc': self.siat_cafc,
                 'siat_nit': str(self.siat_nit)}
        res = self.env['siat.eventos.significativos'].create(value)
        res.invoice_ids = self.env['account.invoice'].browse(self._context['active_ids'])
        res.action_register_event_significant()
        return {
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(self.env.ref('siat_sin_bolivia.siat_eventos_significativos_form_view').id, 'form')],
            'res_model': 'siat.eventos.significativos',
            'type': 'ir.actions.act_window',
            'res_id': res.id

        }



        # for line in self.env['account.invoice'].search([('id', 'in', context['active_ids'])]):
        #     line.write({'siat_evento_significativo_id': res.id})
