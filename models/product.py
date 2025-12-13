# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    economic_activity = fields.Many2one('codigos.actividades', string='Economic Activity')

    codigo_caeb = fields.Char(string="Codigo", related='economic_activity.codigo_caeb')

    #todo trabajar el domain
    siat_codigo_producto_sin = fields.Many2one('productos.servicios', string='Codio SIN',
                                               help="Homologado a los códigos de productos genéricos enviados por el SIN a través del servicio de sincronización.")


    product_uom_id = fields.Many2one('unidad.medida', string="Unidad de medidad")

    imei = fields.Char(string="Numero de Imei", help="Numero del Imei del celular vendido, Nulo en otro caso")

    gift_card = fields.Boolean(string="Gift Card")

    @api.onchange('economic_activity')
    def _onchange_economic_activity(self):
        self.siat_codigo_producto_sin = False

    @api.model
    def create(self, vals):
        if vals.get('categ_id'):
            category = self.env['product.category'].browse(vals['categ_id'])
            vals['economic_activity'] = category.economic_activity.id if category.economic_activity else False
            vals['siat_codigo_producto_sin'] = category.siat_codigo_producto_sin.id if category.siat_codigo_producto_sin else False
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('categ_id'):
            category = self.env['product.category'].browse(vals['categ_id'])
            economic_activity = category.economic_activity.id if category.economic_activity else False
            siat_codigo_producto_sin = category.siat_codigo_producto_sin.id if category.siat_codigo_producto_sin else False
            vals.update({'economic_activity': economic_activity,
                         'siat_codigo_producto_sin': siat_codigo_producto_sin})
        return super(ProductTemplate, self).write(vals)

    @api.constrains('economic_activity', 'siat_codigo_producto_sin')
    def _constrains_economic_activity(self):
        if self.economic_activity and self.siat_codigo_producto_sin:
            if self.siat_codigo_producto_sin.codigo_actividad != int(self.codigo_caeb):
                raise ValidationError('El codigo del producto no coincide con la actividad economica')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    economic_activity = fields.Many2one('codigos.actividades', string='Economic Activity')

    codigo_caeb = fields.Char(string="Codigo", related='economic_activity.codigo_caeb')

    siat_codigo_producto_sin = fields.Many2one('productos.servicios', string='Codio SIN',
                                               help="Homologado a los códigos de productos genéricos enviados por el SIN a través del servicio de sincronización.")

    @api.constrains('economic_activity', 'siat_codigo_producto_sin')
    def _constrains_economic_activity(self):
        if self.economic_activity and self.siat_codigo_producto_sin:
            if self.siat_codigo_producto_sin.codigo_actividad != int(self.codigo_caeb):
                raise ValidationError('El codigo del producto no coincide con la actividad economica')

    @api.multi
    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        if vals.get('economic_activity'):
            for product_template in self.product_template_ids:
                product_template.write({'economic_activity': vals.get('economic_activity')})
        if vals.get('siat_codigo_producto_sin'):
            for product_template in self.product_template_ids:
                product_template.write({'siat_codigo_producto_sin': vals.get('siat_codigo_producto_sin')})
        return res

