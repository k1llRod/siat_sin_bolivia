# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Currency(models.Model):
    _inherit = "res.currency"

    siat_sincronizar = fields.Many2one('tipo.moneda', string='Tipo de Moneda')


class ResCountry(models.Model):
    _inherit = 'res.country'

    siat_sincronizar = fields.Many2one('pais.origen', string='Pais de Origen')


class ProductUOM(models.Model):
    _inherit = 'product.uom'
    siat_sincronizar = fields.Many2one('unidad.medida', string='Unidad de Medida')
