# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

class ProductUOM(models.Model):
    """
    Extension de la clase product_oum para adicionar un campo con relacion al modelo de unidad de medida de siat
    """
    _inherit = 'product.uom'

    siat_product_uom_id = fields.Many2one('unidad.medida', string="Unidad de medidad siat")