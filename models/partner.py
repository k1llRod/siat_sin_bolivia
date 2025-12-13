# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
import random


class res_partner(models.Model):
    _inherit = 'res.partner'

    cod_cliente_siat = fields.Char(string='Codigo cliente', compute='_compute_cod_cliente')
    type_doc_identidad = fields.Many2one('documento.identidad', string='Documento identidad')

    # _sql_constraints = [
    #     ('siat_code_uniq', 'unique(cod_cliente_siat, company_id)', 'El codigo siat debe ser unico'),
    # ]

    # @api.model
    # def create(self, vals):
    #     self.validar_nit_cero(vals)
    #     return super(res_partner, self).create(vals)
    #
    # @api.multi
    # def write(self, vals):
    #     self.validar_nit_cero(vals)
    #     return super(res_partner, self).write(vals)
    #
    # def validar_nit_cero(self, vals):
    #     """Validacion para verificar si el nit del partner esta en 0, esto para cumplir con validacion de impuestos"""
    #     if 'nit' in vals and str(vals['nit']) == '0':
    #         raise ValidationError(_('No se puede dejar en valor 0 el NIT'))

    @api.one
    @api.depends('name')
    def _compute_cod_cliente(self):
        if self.name:
            self.cod_cliente_siat = "%s%s" % (self.name[:4], random.randint(10000, 99999))
