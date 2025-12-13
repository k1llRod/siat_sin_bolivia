# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime
from odoo.exceptions import ValidationError


class SiatGiftcard(models.Model):

    _name = 'siat.giftcard'
    _description = "Gift Card"

    name = fields.Char(string="Codigo", required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    date_end = fields.Date(string='Fecha de Vencimiento')
    date_start = fields.Date(string='Fecha de Incio', required=True, default=lambda self: fields.Datetime.now())
    active = fields.Boolean(string='Activo', default=True)
    amount = fields.Many2one('amount.giftcard', string="Monto", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    sold_out = fields.Boolean(string='Vendido', default=False)
    invoice_line_id = fields.Many2one('account.invoice.line')

    def validate_siat_gift_card(self):
        if self.date_end and self.date_end < datetime.datetime.now():
            self.active = False
            raise ValidationError('La Gift Card %s esta vencida.' % self.name)
        self.active = False

    def action_sell_gift_card(self):
        for line in self:
            line.update({'sold_out': True})


class AmountGiftcard(models.Model):

    _name = 'amount.giftcard'

    amount = fields.Monetary(string="Monto", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.multi
    def name_get(self):
        return [(line.id, '%s %s' % (line.amount, line.currency_id.name)) for line in self]