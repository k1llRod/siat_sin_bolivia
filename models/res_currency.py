# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class Currency(models.Model):
    """
    Extension de la clase Currency para adicionar un campo con relacion al modelo de siat
    """
    _inherit = 'res.currency'

    siat_codigo_moneda = fields.Many2one('tipo.moneda', string="Codigo de moneda")
    siat_tipo_cambio = fields.Integer(string="Tipo de cambio", default=1)
